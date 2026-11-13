# 2 · Keep it running in the background

After step 1 the bridge lives in a terminal window. Close the window and Claude stops seeing new messages. I ran it like that for a month and kept forgetting. Make it a service: it starts when you log in and restarts if it dies.

Two ways. Pick one.

## Option A — the installer that ships with the software (simplest)

```bash
cd ~/code/whatsapp-mcp
scripts/install-launchd-macos.sh
```

It builds the bridge, installs two background jobs (the bridge, and a monitor that sends a macOS notification when the bridge is down or needs a new QR scan) and writes logs to `~/Library/Logs/whatsapp-mcp/`. No `sudo`. Remove it with `scripts/uninstall-launchd-macos.sh`; your messages and session stay.

## Option B — my version (keeps message text out of the logs)

The bridge prints every message it sees. Option A writes that output into a log file, so your messages end up in a second place. I did not want that, so my wrapper keeps only connection lines, warnings and errors.

1. Build the binary:

   ```bash
   cd ~/code/whatsapp-mcp/whatsapp-bridge
   go build -o ~/.local/bin/whatsapp-bridge .
   ```

2. Copy [`templates/whatsapp-bridge-run.sh`](../templates/whatsapp-bridge-run.sh) to `~/.local/bin/` and make it executable:

   ```bash
   cp templates/whatsapp-bridge-run.sh ~/.local/bin/
   chmod +x ~/.local/bin/whatsapp-bridge-run.sh
   ```

3. Copy [`templates/com.example.whatsapp-bridge.plist`](../templates/com.example.whatsapp-bridge.plist) to `~/Library/LaunchAgents/`, replace `YOU` with your user name inside it, then load it:

   ```bash
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.whatsapp-bridge.plist
   ```

4. Stop the terminal bridge from step 1 first (Ctrl+C). Two bridges on one session knock each other offline.

Check it:

```bash
tail ~/Library/Logs/whatsapp-bridge.log
```

You want to see `bridge starting` and a connected line.

**After you update the software** (`git pull`), rebuild the binary (step 1 above) and restart the job:

```bash
launchctl kickstart -k gui/$(id -u)/com.example.whatsapp-bridge
```

## Back it up

`messages.db` only contains what the bridge saw while it was linked. If the file is lost, older history does not fully come back. I take a daily snapshot:

- [`templates/whatsapp-backup.sh`](../templates/whatsapp-backup.sh) copies both databases safely while the bridge is running (SQLite's `.backup`), adds new media, and keeps 30 days.
- [`templates/com.example.whatsapp-backup.plist`](../templates/com.example.whatsapp-backup.plist) runs it every day at 13:00.

The backup contains your login session and all messages. Keep it on an encrypted disk, not in a cloud folder.

## When WhatsApp asks to pair again

Linked devices get logged out now and then (long time offline, a WhatsApp update, you removed the device on the phone). Then:

```bash
launchctl bootout gui/$(id -u)/com.example.whatsapp-bridge
cd ~/code/whatsapp-mcp/whatsapp-bridge && ~/.local/bin/whatsapp-bridge
# scan the QR code, wait for "connected", Ctrl+C
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.whatsapp-bridge.plist
```

Your message history stays.

## Linux and Windows

Same idea, different tool: a `systemd --user` service on Linux, Task Scheduler ("At log on", restart on failure) on Windows. The command to run is the built `whatsapp-bridge` binary, with the working directory set to `whatsapp-bridge/`, because the bridge looks for `store/` relative to where it starts.

Next: [safety rules](03-safety.md).
