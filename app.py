import asyncio
from flask import Flask, render_template, request, jsonify
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

app = Flask(__name__)

server_params = StdioServerParameters(command="python", args=["server.py"])

async def call(name: str, args: dict):
    async with stdio_client(server_params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            return (await s.call_tool(name, args)).content[0].text

async def read_resource(uri: str):
    async with stdio_client(server_params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            return (await s.read_resource(uri)).contents[0].text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "").strip()
    parts = msg.split(maxsplit=1)
    cmd = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else ""

    try:
        # ── Excel ──
        if cmd == "xls" and arg:
            return jsonify({"reply": asyncio.run(call("excel_read", {"path": arg}))})
        elif cmd == "xls" and " " in msg.split(maxsplit=2)[-1:]:
            p = msg.split(maxsplit=2)
            return jsonify({"reply": asyncio.run(call("excel_read", {"path": p[1], "sheet": p[2]}))})
        elif cmd == "xls" and not arg:
            return jsonify({"reply": "Usage: xls <path> [sheet] [cell]"})
        elif cmd == "xls" and " " in arg and arg.count(" ") >= 1:
            p = arg.split()
            return jsonify({"reply": asyncio.run(call("excel_read", {"path": p[0], "sheet": p[1]}))})
        elif cmd == "xls" and " " in arg and arg.count(" ") >= 2:
            p = arg.split()
            return jsonify({"reply": asyncio.run(call("excel_read", {"path": p[0], "sheet": p[1], "cell": p[2]}))})

        elif cmd == "xls!":
            p2 = msg.split(maxsplit=2)
            if len(p2) >= 3:
                a, b = p2[1], p2[2]
                return jsonify({"reply": asyncio.run(call("excel_write", {"path": a, "sheet": "Sheet1", "cell": "A1", "value": b}))})
            return jsonify({"reply": "Usage: xls! <path> <value>"})

        elif cmd == "xls+":
            return jsonify({"reply": "Usage:\n  xls <path>               list sheets\n  xls <path> <sheet>      read sheet\n  xls <path> <sheet> A1   read cell\n  xls! <path> <value>    write to A1\n  xls-new <path>         create file\n  xls-new <path> h1,h2   create with headers"})

        elif cmd == "xls-new" and arg:
            return jsonify({"reply": asyncio.run(call("excel_create", {"path": arg}))})
        elif cmd == "xls-new" and arg and "," in arg:
            p = arg.split(None, 1)
            return jsonify({"reply": asyncio.run(call("excel_create", {"path": p[0], "headers": p[1]}))})

        # ── Email ──
        elif cmd == "email-setup" and arg:
            p = arg.split(None, 1)
            return jsonify({"reply": asyncio.run(call("email_setup", {"email": p[0], "password": p[1] if len(p) > 1 else ""}))})
        elif cmd == "email-setup":
            return jsonify({"reply": "Usage: email-setup <email> <app-password>\nFor Gmail: https://myaccount.google.com/apppasswords"})

        elif cmd == "email" and arg and " " in arg:
            p = msg.split(None, 3)
            if len(p) >= 3:
                return jsonify({"reply": asyncio.run(call("email_send", {"to": p[1], "subject": p[2], "body": p[3] if len(p) > 3 else ""}))})
            return jsonify({"reply": "Usage: email <to> <subject>"})
        elif cmd == "email":
            return jsonify({"reply": "Usage: email <to> <subject> [body]\nSet env: SMTP_EMAIL and SMTP_PASSWORD"})

        # ── Google Docs ──
        elif cmd == "docs-setup" and arg:
            return jsonify({"reply": asyncio.run(call("docs_setup", {"creds_path": arg}))})

        elif cmd == "docs" and arg and arg.startswith("new"):
            t = arg.split(None, 1)
            title = t[1] if len(t) > 1 else "Untitled"
            return jsonify({"reply": asyncio.run(call("docs_create", {"title": title}))})

        elif cmd == "docs" and arg and arg.startswith("append"):
            p2 = arg.split(None, 2)
            if len(p2) >= 3:
                return jsonify({"reply": asyncio.run(call("docs_append", {"doc_url_or_id": p2[1], "text": p2[2]}))})
            return jsonify({"reply": "Usage: docs append <url/id> <text>"})

        elif cmd == "docs" and arg:
            return jsonify({"reply": asyncio.run(call("docs_read", {"doc_url_or_id": arg}))})

        elif cmd == "docs":
            return jsonify({"reply": "Usage:\n  docs <url/id>         read doc\n  docs new <title>      create doc\n  docs append <id> text  append text"})

        # ── Converter ──
        elif cmd == "convert" and " " in arg:
            p = arg.split()
            v, fr, to = float(p[0]), p[1], p[2]
            return jsonify({"reply": asyncio.run(call("convert", {"value": v, "from_unit": fr, "to_unit": to}))})
        elif cmd == "units":
            return jsonify({"reply": asyncio.run(call("units", {}))})

        # ── Currency ──
        elif cmd == "currency" and " " in arg:
            p = arg.split()
            return jsonify({"reply": asyncio.run(call("currency", {"amount": float(p[0]), "from_curr": p[1], "to_curr": p[2]}))})
        elif cmd == "currencies":
            return jsonify({"reply": asyncio.run(call("currencies", {}))})

        # ── Regex ──
        elif cmd == "regex" and " " in arg:
            p = arg.split(" ", 1)
            return jsonify({"reply": asyncio.run(call("regex", {"pattern": p[0], "text": p[1]}))})
        elif cmd == "rg" and " " in arg:
            p = arg.split(" ", 1)
            return jsonify({"reply": asyncio.run(call("regex_groups", {"pattern": p[0], "text": p[1]}))})

        # ── Stats ──
        elif cmd == "stats" and arg:
            return jsonify({"reply": asyncio.run(call("text_stats", {"text": arg}))})

        # ── Diff ──
        elif cmd == "diff" and "|||" in arg:
            p = arg.split("|||", 1)
            return jsonify({"reply": asyncio.run(call("diff", {"text1": p[0].strip(), "text2": p[1].strip()}))})

        # ── Password ──
        elif cmd == "pass" and arg:
            return jsonify({"reply": asyncio.run(call("password_strength", {"password": arg}))})
        elif cmd == "pass":
            return jsonify({"reply": asyncio.run(call("password_strength", {"password": "password"}))})

        # ── Markdown ──
        elif cmd == "md" and arg:
            return jsonify({"reply": asyncio.run(call("markdown_to_html", {"text": arg}))})

        # ── JSON ──
        elif cmd == "fmt" and arg:
            return jsonify({"reply": asyncio.run(call("json_format", {"text": arg}))})
        elif cmd == "min" and arg:
            return jsonify({"reply": asyncio.run(call("json_minify", {"text": arg}))})
        elif cmd == "keys" and arg:
            return jsonify({"reply": asyncio.run(call("json_keys", {"text": arg}))})

        # ── IP ──
        elif cmd == "ip" and arg:
            return jsonify({"reply": asyncio.run(call("ip_info", {"ip": arg}))})
        elif cmd == "ip":
            return jsonify({"reply": asyncio.run(call("public_ip", {}))})

        # ── Wiki ──
        elif cmd == "add" and " " in arg:
            p = arg.split()
            return jsonify({"reply": asyncio.run(call("add", {"a": int(p[0]), "b": int(p[1])}))})
        elif cmd == "hello" and arg:
            return jsonify({"reply": asyncio.run(read_resource(f"greeting://{arg}"))})
        elif cmd == "wiki" and arg:
            return jsonify({"reply": asyncio.run(call("wiki_search", {"query": arg}))})
        elif cmd == "page" and arg:
            return jsonify({"reply": asyncio.run(call("wiki_get_page", {"title": arg.replace(" ", "_")}))})

        # ── Weather ──
        elif cmd == "weather" and arg:
            return jsonify({"reply": asyncio.run(call("weather", {"city": arg}))})
        elif cmd == "weather+":
            return jsonify({"reply": asyncio.run(call("weather_detail", {"city": arg}))})

        # ── Color ──
        elif cmd == "hex" and arg:
            return jsonify({"reply": asyncio.run(call("hex_to_rgb", {"hex_color": arg}))})
        elif cmd == "rgb" and " " in arg:
            p = arg.split()
            return jsonify({"reply": asyncio.run(call("rgb_to_hex", {"r": int(p[0]), "g": int(p[1]), "b": int(p[2])}))})
        elif cmd == "palette" and arg:
            return jsonify({"reply": asyncio.run(call("color_palette", {"hex_color": arg}))})

        else:
            return jsonify({"reply": HELP})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

HELP = """Commands:
  Basic:       add <a> <b>, hello <name>
  Excel:       xls <path> [sheet], xls! <path> <val>, xls-new <path>
  Email:       email <to> <sub> [body], email-setup <email> <pass>
  Docs:        docs <url>, docs new <title>, docs append <id>, docs-setup
  Convert:     convert, currency, units, currencies
  Text:        regex, rg, stats, diff, md, wiki, page
  Security:    pass <text>
  JSON:        fmt, min, keys
  Network:     ip, weather, palette"""

if __name__ == "__main__":
    app.run(debug=True, port=5000)
