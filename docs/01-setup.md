# 1 · Install and connect

About 30 minutes. You need a Mac (or Linux/Windows PC), the phone with your WhatsApp, and Claude Desktop or Claude Code.

Commands below are for macOS. Replace `YOU` with your user name.

## 1. Install the tools

```bash
brew install go uv ffmpeg
```

- **Go** (1.26 or newer) builds the bridge.
- **uv** runs the Python MCP server and installs its packages by itself.
- **ffmpeg** is optional. Only needed to send voice notes.

No Homebrew yet? Install it from [brew.sh](https://brew.sh) first.

**Windows:** install Go, uv and [MSYS2](https://www.msys2.org/) (the bridge's database driver needs a C compiler), then run `go env -w CGO_ENABLED=1` once.

## 2. Download the software

Pick a folder that is **not** synced to a cloud drive. I use `~/code`.

```bash
mkdir -p ~/code && cd ~/code
git clone https://github.com/verygoodplugins/whatsapp-mcp.git
```

## 3. Start the bridge and scan the QR code

```bash
cd ~/code/whatsapp-mcp/whatsapp-bridge
go run .
```

A QR code appears in the terminal. On your phone:

**WhatsApp → Settings → Linked devices → Link a device** → scan it.

Then leave the terminal open. The bridge downloads your recent history. With a lot of chats this takes several minutes. You will see messages scroll by.

What just happened on disk, inside `whatsapp-bridge/store/`:

| File | What it is |
|---|---|
| `whatsapp.db` | The login session. Whoever has this file is logged in as you. |
| `messages.db` | Your messages. This is what Claude reads. |
| `.bridge-token` | A password between the MCP server and the bridge. Created by itself. |
| folders per chat | Media you asked to download. |

Tip: before scanning you can give the linked device a recognisable name, so it does not show up on your phone as "whatsmeow":

```bash
WHATSAPP_DEVICE_NAME="Claude bridge" go run .
```

## 4. Tell Claude about it

### Claude Desktop

Open **Settings → Developer → Edit Config**. That opens `claude_desktop_config.json`
(on macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`). Add:

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "/Users/YOU/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/YOU/code/whatsapp-mcp/whatsapp-mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```

Use the full path to `uv` (find it with `which uv`). Claude Desktop does not see your terminal's PATH, and a bare `uv` is the most common reason the server does not start.

The same file is in [`templates/claude_desktop_config.json`](../templates/claude_desktop_config.json).

Quit Claude Desktop completely and open it again.

### Claude Code

```bash
claude mcp add whatsapp --scope user -- uv --directory ~/code/whatsapp-mcp/whatsapp-mcp-server run main.py
```

Check with `claude mcp list`.

## 5. Test it

The bridge must be running (the terminal from step 3). Ask Claude:

> List my 5 most recent WhatsApp chats.

Claude asks permission to use the WhatsApp tool. Allow it. You should see your chats.

Then try a real question:

> Read my chat with [name] from the last 7 days and tell me what I promised to do.

## 6. Lock down sending — do this now, not later

The server gives Claude tools that read and tools that act:

| Reads | Acts |
|---|---|
| `search_contacts`, `get_contact` | `send_message` |
| `list_chats`, `get_chat` | `send_file` |
| `list_messages`, `get_message_context` | `send_audio_message` |
| `get_direct_chat_by_contact`, `get_contact_chats` | `send_reaction` |
| `get_last_interaction` | `mark_messages_read` |
| `download_media`, `view_media`, `transcribe_audio` | |

- **Claude Desktop:** when Claude first asks to use a tool, choose "Allow always" only for the read tools. For the five tools on the right, never choose "always". Better: turn them off in the tool list for the WhatsApp server.
- **Claude Code:** copy [`templates/claude-code-settings.json`](../templates/claude-code-settings.json) into `~/.claude/settings.json` (or merge it). It allows the read tools and denies the five acting tools. A deny rule cannot be talked around by anything Claude reads.

My own rule: Claude drafts, I send. The one exception I made was my own "message yourself" chat, and I later moved even that elsewhere.

Next: [keep it running in the background](02-run-as-service.md).
