#!/bin/bash
# Daily backup of the WhatsApp bridge store (messages, session, media).
# The backup holds your login session and all messages: keep DEST on an encrypted disk, outside any cloud folder.
set -euo pipefail
SRC="$HOME/code/whatsapp-mcp/whatsapp-bridge/store"
DEST="$HOME/Backups/whatsapp-mcp"
KEEP_DAYS=30
STAMP=$(date +%Y-%m-%d_%H%M)

umask 077
mkdir -p "$DEST/snapshots/$STAMP" "$DEST/media"

# Consistent database snapshots (safe while the bridge is running)
for db in messages.db whatsapp.db; do
  [ -f "$SRC/$db" ] && /usr/bin/sqlite3 "$SRC/$db" ".backup '$DEST/snapshots/$STAMP/$db'"
done
[ -f "$SRC/.bridge-token" ] && cp "$SRC/.bridge-token" "$DEST/snapshots/$STAMP/"

# Media: additive copy, never deletes from the backup
/usr/bin/rsync -a --exclude='*.db' --exclude='*.db-*' --exclude='.bridge-token' "$SRC/" "$DEST/media/"

# Drop database snapshots older than KEEP_DAYS
find "$DEST/snapshots" -mindepth 1 -maxdepth 1 -type d -mtime +$KEEP_DAYS -exec rm -rf {} +

echo "$(date '+%F %T') backup ok -> $DEST/snapshots/$STAMP" >> "$DEST/backup.log"
