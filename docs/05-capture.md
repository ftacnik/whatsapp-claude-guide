# 5 · Capture into notes (optional)

Steps 1–3 give you a Claude that can look into WhatsApp when you ask. This step makes WhatsApp flow into your notes by itself.

## Why a script and not Claude

My first version asked Claude to page through every approved chat each morning through the MCP tools. It worked, and it was slow and expensive: the model read thousands of raw messages to find the twenty that mattered.

Now a plain Python script does the copying. No AI involved. It reads the same database, takes only the allowlisted chats, and writes short text files. Claude then reads only those files. It is faster, costs a fraction, and Claude never sees the chats that are not on the list.

Rule of thumb I took from this: **use the MCP tools for questions, use a script for routine.**

## Try it

```bash
cp templates/whatsapp-allowlist.example.md whatsapp-allowlist.md
# edit whatsapp-allowlist.md: your real chats and their jid numbers

python3 scripts/capture_whatsapp.py --allowlist whatsapp-allowlist.md --out notes-inbox --dry-run
```

`--dry-run` shows which files it would write and how many messages, and writes nothing. Remove it to write.

To find a chat's jid, ask Claude: "List my WhatsApp chats with their jid." For a person it is the phone number without the plus sign. For a group it is a long number starting with 120363.

Each run writes one file per chat that had new messages:

```
---
source: whatsapp
chat: Anna Example
jid: 85200000001@s.whatsapp.net
from: 2026-11-13 09:02
to: 2026-11-13 09:40
---
09:02 Anna Example: Can you confirm the Friday booking?
09:40 me: Confirmed, 19:30 for six.
```

The script remembers when it last ran (`capture-state.json`), so the next run takes only what is new. Photos, voice notes and documents show up as `[image]`, `[audio]`, `[document name]`. Nothing is downloaded.

## Run it on a schedule

Every 15 minutes during the day is what I use. On macOS that is a launchd job with `StartInterval` 900 (copy the backup plist from `templates/` and change the program and the interval); on Linux a cron line:

```
*/15 7-22 * * *  cd ~/whatsapp-notes && python3 capture_whatsapp.py --allowlist whatsapp-allowlist.md --out notes-inbox
```

## Then let Claude file it

Point Claude at the folder. A prompt to start from:

> Read every file in notes-inbox/. For each one: update the page of the client or project it belongs to with what was agreed, list anything I promised with a date, list anything they promised me, then move the file to notes-inbox/done/. Do not send any message to anyone.

In my own system this is where it connects to the rest: client pages, a task list, and a morning brief that says "Anna is waiting for your answer since yesterday."

## What my full version adds

The script here is the simple form of what I run. Mine also handles replies and reactions, a "note to self" chat as a quick capture channel, per-chat backfill dates, and a lock so two runs never overlap. Start with the simple one. Add things when you miss them.
