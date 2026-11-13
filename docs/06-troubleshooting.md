# 6 · When something breaks

| What you see | Why | Fix |
|---|---|---|
| Claude shows no WhatsApp tools | The MCP server did not start. Almost always the path to `uv`. | Put the full path from `which uv` into the config. Quit Claude Desktop fully and reopen. |
| Tools are there but new messages are missing | The bridge is not running. | Check the log (`tail ~/Library/Logs/whatsapp-bridge.log`), restart the service. Reading old messages works without the bridge; new ones need it. |
| "401 Unauthorized" from the bridge | The MCP server cannot read `.bridge-token`. | Restart the bridge, then restart Claude. |
| QR code does not appear | Terminal cannot draw it, or the bridge is already paired. | Restart the bridge in a normal terminal window. |
| Phone says "check your connection" after scanning | WhatsApp refreshed the code. | Scan the new code the bridge prints ("QR code refreshed"). |
| Pairing fails with "Client outdated" or 405 | WhatsApp raised the minimum version. | `git pull`, rebuild the bridge, pair again. |
| "Device limit reached" | Too many linked devices. | Phone → Linked devices → remove one. |
| It worked, then the bridge keeps disconnecting | Two bridges on the same session (terminal + service). | Stop one. |
| Old history is missing | WhatsApp sends a linked device only recent history. | Stop the bridge, back up `store/`, remove `store/whatsapp.db`, start with `--full-history-pair`, scan again, wait for "History sync complete". |
| Group messages show numbers, not names | New WhatsApp privacy IDs ("LID"). | Current versions resolve them; update the software. |
| Voice note cannot be transcribed | No local speech model configured. | Install whisper.cpp and set `WHISPER_MODEL` (see the upstream README), or skip voice notes. |

Full reference: the [upstream README](https://github.com/verygoodplugins/whatsapp-mcp#troubleshooting).
