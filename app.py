import asyncio
import json
from flask import Flask, render_template, request, jsonify
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

app = Flask(__name__)

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)

async def call_mcp(tool_name: str, arguments: dict):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

async def read_mcp_resource(uri: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.read_resource(uri)
            return result.contents[0].text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").strip()
    parts = message.split(maxsplit=1)
    cmd = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else ""

    try:
        if cmd == "add" and " " in arg:
            nums = arg.split()
            a, b = int(nums[0]), int(nums[1])
            result = asyncio.run(call_mcp("add", {"a": a, "b": b}))
            return jsonify({"reply": result})

        elif cmd == "hello" and arg:
            result = asyncio.run(read_mcp_resource(f"greeting://{arg}"))
            return jsonify({"reply": result})

        elif cmd == "wiki" and arg:
            result = asyncio.run(call_mcp("wiki_search", {"query": arg}))
            return jsonify({"reply": result})

        elif cmd == "page" and arg:
            result = asyncio.run(call_mcp("wiki_get_page", {"title": arg.replace(" ", "_")}))
            return jsonify({"reply": result})

        else:
            return jsonify({"reply": "Commands:\n  add <num1> <num2>\n  hello <name>\n  wiki <query>\n  page <title>"})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
