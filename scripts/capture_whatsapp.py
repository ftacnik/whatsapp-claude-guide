#!/usr/bin/env python3
"""Copy new WhatsApp messages from allowlisted chats into a notes folder, without any AI model.

Reads the bridge's SQLite store read-only, takes only the chats named in the allowlist, and writes one
Markdown file per chat per run:

    notes-inbox/2026-11-13-whatsapp-anna-example.md
        ---
        source: whatsapp
        chat: Anna Example
        jid: 85200000001@s.whatsapp.net
        from: 2026-11-13 09:02
        to: 2026-11-13 09:40
        ---
        09:02 Anna Example: Can you confirm the Friday booking?
        09:40 me: Confirmed, 19:30 for six.

Media is never fetched: it appears as [image], [audio], [document name]. Deleted messages are skipped.
Claude (or a person) then files these notes. The model never has to page through raw chats.

Usage:
    python3 capture_whatsapp.py --allowlist whatsapp-allowlist.md --out notes-inbox [--dry-run] [--since 2026-11-01]

    --store     folder with messages.db and whatsapp.db (default ~/code/whatsapp-mcp/whatsapp-bridge/store)
    --state     file that remembers the last run (default capture-state.json next to the allowlist)
    --since     read from this date instead of the last run; the state file is not updated
    --dry-run   print what would be written (chat and message count only), write nothing

Allowlist: any line containing "(jid 12345...)" allows that chat. Everything else in the file is for humans.
A section heading starting with "## Never" ends the list.
Only the Python standard library is used.
"""
import argparse
import datetime as dt
import json
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

DEFAULT_STORE = Path.home() / "code" / "whatsapp-mcp" / "whatsapp-bridge" / "store"
JID_RE = re.compile(r"^\s*-\s*(?P<name>[^(]+?)\s*\(jid\s+(?P<jid>[\d\-]+)(?:@[\w.]+)?\)")


def read_allowlist(path):
    """→ {bare jid: display name} for every '- Name (jid N)' line above a '## Never' heading."""
    allowed = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.lower().startswith("## never"):
            break
        m = JID_RE.match(line)
        if m:
            allowed[m["jid"]] = m["name"].strip()
    return allowed


def ro(path):
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def contact_names(store):
    """whatsmeow's own store → ({lid: phone}, {phone: name}). Empty when the file is missing."""
    lids, names = {}, {}
    db = store / "whatsapp.db"
    if not db.exists():
        return lids, names
    try:
        with ro(db) as c:
            for lid, pn in c.execute("select lid, pn from whatsmeow_lid_map"):
                lids[str(lid).split("@")[0]] = str(pn).split("@")[0]
            for jid, full, push in c.execute("select their_jid, full_name, push_name from whatsmeow_contacts"):
                name = (full or push or "").strip()
                if name:
                    names[str(jid).split("@")[0]] = name
    except sqlite3.Error:
        pass
    return lids, names


def slug(text, maxlen=48):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:maxlen] or "chat"


def line_for(row, names, lids):
    ts = dt.datetime.fromisoformat(row["timestamp"])
    if row["is_from_me"]:
        who = "me"
    else:
        number = lids.get(row["sender"], row["sender"])
        who = names.get(number, number)
    text = (row["content"] or "").strip().replace("\n", " ⏎ ")
    if row["media_type"]:
        label = f"[{row['media_type']}{' ' + row['filename'] if row['media_type'] == 'document' and row['filename'] else ''}]"
        text = f"{label} {text}".strip()
    return ts, f"{ts:%H:%M} {who}: {text}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--allowlist", required=True)
    ap.add_argument("--out", default="notes-inbox")
    ap.add_argument("--store", default=str(DEFAULT_STORE))
    ap.add_argument("--state")
    ap.add_argument("--since")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    store, out = Path(a.store), Path(a.out)
    state_path = Path(a.state) if a.state else Path(a.allowlist).with_name("capture-state.json")
    allowed = read_allowlist(a.allowlist)
    if not allowed:
        sys.exit("The allowlist names no chats: nothing is captured.")

    started = dt.datetime.now().astimezone()
    if a.since:
        floor = dt.datetime.fromisoformat(a.since).astimezone()
    elif state_path.exists():
        floor = dt.datetime.fromisoformat(json.loads(state_path.read_text())["last_run"])
    else:
        floor = started - dt.timedelta(days=1)          # first run: the last 24 hours

    lids, names = contact_names(store)
    with ro(store / "messages.db") as conn:
        chats = {r["jid"]: r["name"] for r in conn.execute("select jid, name from chats")}
        jids = [j for j in chats if j.split("@")[0] in allowed]
        marks = ",".join("?" * len(jids))
        rows = conn.execute(
            "select chat_jid, sender, content, timestamp, is_from_me, media_type, filename from messages "
            f"where chat_jid in ({marks}) and deleted_at is null order by timestamp, id", jids).fetchall()

    per_chat = {}
    for r in rows:
        ts, line = line_for(r, names, lids)
        if floor <= ts < started:                        # compared as real times, whatever the stored offset
            per_chat.setdefault(r["chat_jid"], []).append((ts, line))

    written = []
    for jid, items in per_chat.items():
        name = allowed[jid.split("@")[0]]
        body = "\n".join([
            "---", "source: whatsapp", f"chat: {name}", f"jid: {jid}",
            f"from: {items[0][0]:%Y-%m-%d %H:%M}", f"to: {items[-1][0]:%Y-%m-%d %H:%M}", "---",
            *[line for _, line in items], ""])
        base = f"{started:%Y-%m-%d}-whatsapp-{slug(name)}"
        target, n = out / f"{base}.md", 1
        while target.exists():                           # never overwrite an earlier capture
            n += 1
            target = out / f"{base}-{n}.md"
        if a.dry_run:
            print(f"would write {target.name}: {len(items)} messages")
        else:
            out.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(".tmp")
            tmp.write_text(body, encoding="utf-8")
            tmp.rename(target)                           # whole files only, so a reader never sees half of one
        written.append(target.name)

    if not a.dry_run and not a.since:
        state_path.write_text(json.dumps({"last_run": started.isoformat()}))
    print(json.dumps({"chats_allowed": len(allowed), "chats_found": len(jids), "files": len(written),
                      "messages": sum(len(v) for v in per_chat.values()), "since": floor.isoformat(),
                      "mode": "dry-run" if a.dry_run else "write"}))


if __name__ == "__main__":
    main()
