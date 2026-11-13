#!/bin/bash
# Runs the WhatsApp bridge for launchd. The bridge prints every message it sees to stdout, so only
# connection lines, warnings and errors are kept in the log: message text stays in the store alone.
#
# Rebuild after updating the repo:
#   cd ~/code/whatsapp-mcp/whatsapp-bridge && go build -o ~/.local/bin/whatsapp-bridge .
cd "$HOME/code/whatsapp-mcp/whatsapp-bridge" || exit 2     # the bridge looks for store/ relative to this folder
LOG="$HOME/Library/Logs/whatsapp-bridge.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') bridge starting" >> "$LOG"
"$HOME/.local/bin/whatsapp-bridge" 2>&1 \
  | grep --line-buffered -E "WARN|ERROR|FATAL|panic|[Cc]onnected|[Dd]isconnect|[Ll]ogged|QR|pair|REST|listening|Starting" \
  | grep --line-buffered -v -E "^\[[0-9]{4}-|Message content" >> "$LOG"
rc=${PIPESTATUS[0]}
echo "$(date '+%Y-%m-%d %H:%M:%S') bridge exited rc=$rc" >> "$LOG"
exit "$rc"
