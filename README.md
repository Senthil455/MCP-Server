# MCP Server + Web Terminal

A local [Model Context Protocol](https://modelcontextprotocol.io) server exposing **33 tools** (Excel, email, Google Docs, unit/currency conversion, regex, JSON, text stats, password strength, Wikipedia, weather, IP lookup, color utilities and more), plus two ways to use them:

- **Web terminal UI** — a browser-based command line served by Flask
- **CLI chatbot** — an interactive terminal client

```
Browser (templates/index.html)
        │  HTTP POST /chat
        ▼
Flask app (app.py)  ──stdio──►  MCP server (server.py)  ──►  external APIs
        ▲
        │  stdio
CLI client (chatbot.py)
```

## Project structure

| File | Purpose |
| --- | --- |
| `server.py` | The MCP server. Defines all tools/resources with `MCPServer`. Runs over stdio (no port). |
| `app.py` | Flask web app. Serves the terminal UI and forwards each command to the MCP server. |
| `chatbot.py` | Minimal terminal client that lists the available tools and supports a few commands. |
| `templates/index.html` | The web terminal (single page, no build step). |
| `requirements.txt` | Python dependencies (`mcp`, Flask, httpx, openpyxl). |
| `README.md` | This file. |

## Requirements

- Python **3.10+**
- **MCP Python SDK 2.x** (`mcp>=2`). The server uses the `MCPServer` API; the old `FastMCP` import was removed in SDK 2.0.
- Internet access for the tools that call external APIs (Wikipedia, currency rates, weather, IP lookup)

## Setup

From the project root (`MCP-Server/`):

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` pins `mcp>=2.0,<3.0` plus Flask, httpx and openpyxl. If you already installed dependencies by hand, make sure the SDK is version 2 or newer:

```bash
pip install "mcp>=2"
```

Optional, only for Google Docs support:

```bash
pip install google-api-python-client google-auth google-auth-oauthlib
```

> No `.venv`? Activating one is recommended but not required — just make sure `python` on your PATH has the packages from `requirements.txt`.

## Run the web UI

**Run this from the project root**, because `app.py` launches `server.py` with a relative path.

```powershell
python app.py
```

You should see Flask start:

```
 * Running on http://127.0.0.1:5000
```

Open **http://localhost:5000** in your browser. You get a terminal-style page:

1. Type a command at the `❯` prompt and press **Enter**.
2. Output appears in a numbered block under the command.
3. Use **↑ / ↓** to walk through previous commands.
4. For example, type `add 5 3`, then `wiki python`, then `weather London`.

Keep the terminal window running while you use the UI. Stop the server with **Ctrl+C**.

### If port 5000 is already in use

Change the last line of `app.py`:

```python
app.run(debug=True, port=5001)
```

Then open http://localhost:5001.

## Run the CLI chatbot

```powershell
python chatbot.py
```

It prints the name/description of every tool the server exposes, then accepts:

- `add <a> <b>`
- `hello <name>`
- `wiki <query>`
- `page <title>`
- `quit` / `exit` / `q`

The CLI is a small demo — for the full command set use the web UI or an MCP client.

## Run the MCP server on its own

`server.py` speaks MCP over stdio, so it is normally launched by a client, not run by hand.

**MCP Inspector** (browser devtools for MCP):

```bash
npx @modelcontextprotocol/inspector python server.py
```

**Claude Desktop** — add to `claude_desktop_config.json` (use the absolute path to `server.py`):

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": [
        "C:\\Users\\you\\Downloads\\Projects\\Org_Projects-Phase1\\MCP-Server\\server.py"
      ]
    }
  }
}
```

Restart the app afterwards. The tools will be available to the model directly.

## UI command reference

These are the commands the Flask UI understands. Anything unrecognized prints the built-in help.

| Category | Command | Description |
| --- | --- | --- |
| Basic | `add <a> <b>` | Add two integers |
| Basic | `hello <name>` | Read the `greeting://<name>` resource |
| Excel | `xls <path>` | List the sheets in a workbook (creates the file if missing) |
| Excel | `xls-new <path>` | Create a new workbook |
| Excel | `xls! <path> <value>` | Write a value to cell `A1` of `Sheet1` |
| Email | `email-setup <email> <app-password>` | Save SMTP credentials (Gmail app password) |
| Email | `email <to> <subject> [body]` | Send an email |
| Google Docs | `docs <url-or-id>` | Read a document |
| Google Docs | `docs new <title>` | Create a document |
| Google Docs | `docs append <url-or-id> <text>` | Append text to a document |
| Units | `convert <value> <from> <to>` | Convert units, e.g. `convert 100 km mi` |
| Units | `units` | List supported units |
| Currency | `currency <amount> <from> <to>` | Convert currency, e.g. `currency 100 usd inr` |
| Currency | `currencies` | List common currency codes |
| Regex | `regex <pattern> <text>` | Find all matches |
| Regex | `rg <pattern> <text>` | Show matches with capture groups |
| Text | `stats <text>` | Word/char/line counts and reading time |
| Text | `diff <text1> \|\|\| <text2>` | Unified diff (separator is three pipes) |
| Text | `md <markdown>` | Convert Markdown to HTML |
| Security | `pass <text>` | Password strength score and tips |
| JSON | `fmt <json>` | Pretty-print/validate JSON |
| JSON | `min <json>` | Minify JSON |
| JSON | `keys <json>` | List all keys in dot notation |
| Network | `ip [address]` | IP geolocation (blank = your own) |
| Wiki | `wiki <query>` | Search Wikipedia |
| Wiki | `page <title>` | Wikipedia article summary (article title, not a URL) |
| Weather | `weather <city>` | One-line current weather |
| Weather | `weather+ <city>` | Weather with humidity and wind |
| Color | `hex <#rrggbb>` | Hex to RGB |
| Color | `rgb <r> <g> <b>` | RGB to hex |
| Color | `palette <#rrggbb>` | Complementary/analogous/triadic palette |

The MCP server additionally offers tools that the UI does not route to, such as `excel_add_row`, `excel_write` with an explicit sheet/cell, and `excel_create` with headers. Use them through an MCP client, or add a branch in `app.py` — see [Adding a tool](#adding-a-tool).

## Optional integrations

### Gmail / SMTP

1. Enable 2-Step Verification on your Google account.
2. Create an **App Password**: https://myaccount.google.com/apppasswords
3. In the UI, run:

   ```
   email-setup you@gmail.com abcd efgh ijkl mnop
   ```

   This writes `email_config.json` in the project root (git-ignored). The tool sends through `smtp.gmail.com:587` with STARTTLS.
4. Send mail with `email friend@example.com Subject Hello there`.

`email-setup` and `email` are printed in the UI help under "Email"; credentials are stored as plain text in `email_config.json`, so keep it local.

### Google Docs

Google Docs support needs an OAuth client from Google Cloud:

1. In Google Cloud Console, enable the **Google Docs API**.
2. Create an **OAuth client ID** of type *Desktop app* and download the JSON.
3. Set the environment variable before starting the app/server:

   ```powershell
   $env:DOCS_CREDS_PATH = "C:\path\to\client_secret.json"
   python app.py
   ```

   ```bash
   export DOCS_CREDS_PATH=/path/to/client_secret.json
   python app.py
   ```

4. The first Docs command opens a browser for consent and caches a token next to the credentials file (`docs_token.json`).

`server.py` reads `DOCS_CREDS_PATH` when it starts, so set it *before* launching `app.py`. The `docs-setup` tool only returns these instructions; it does not set the variable for you.

## Configuration and paths

- **Working directory matters.** `app.py` runs `server.py` from the current directory, and relative Excel paths are resolved against that directory. Start the app from the project root, or pass absolute paths.
- **No spaces in UI arguments.** Commands are split on whitespace, so Excel/Docs paths containing spaces are not supported in the UI. Use the MCP tool directly for those.
- **Secrets** — `email_config.json` and `*.xlsx` are listed in `.gitignore`. Keep it that way.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'mcp'` (or `flask`) | Activate the virtualenv first, or `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'mcp.server.mcpserver'` | Your MCP SDK is 1.x. Run `pip install "mcp>=2"` (this server uses the 2.x `MCPServer` API) |
| `Error: unhandled errors in a TaskGroup (1 sub-exception)` in the UI | `server.py` crashed while starting. Run `.\.venv\Scripts\python.exe server.py` to see the real traceback; the usual cause is the SDK version mismatch above |
| `python: command not found` | Try `py app.py` (Windows launcher) or `python3 app.py` |
| `Address already in use` / port 5000 busy | Run on another port (see above) or stop the other process: `netstat -ano \| findstr :5000` |
| UI loads but every command returns `Error: ...` | Make sure you started `python app.py` from the project root so `server.py` can be found |
| `xls` cannot find a file that exists | The UI handler passes the whole argument as one path; use an absolute path with no spaces |
| Weather/currency/Wikipedia fail | These tools call public APIs — check your internet connection or rate limits |
| `wiki` says `Wikipedia rate limit reached. Try again in N seconds` | Wikipedia throttled your IP (common on shared/carrier networks). Wait `N` seconds and retry; `page` uses a different endpoint and usually still works |
| Email fails with `Username and password not accepted` | Use a Google **app password**, not your normal account password, and enable 2FA first |

## Adding a tool

Define it in `server.py`:

```python
@mcp.tool()
def shout(text: str) -> str:
    """Uppercase some text."""
    return text.upper()
```

To expose it in the web UI, add a branch in the `/chat` handler in `app.py`:

```python
elif cmd == "shout" and arg:
    return jsonify({"reply": asyncio.run(call("shout", {"text": arg}))})
```

and mention it in the `HELP` string at the bottom of `app.py`. Restart `python app.py` to pick up both changes.
