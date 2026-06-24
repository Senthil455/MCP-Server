import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()

            print("Chatbot ready! Type 'quit' to exit.\n")

            while True:
                user_input = input("You: ").strip()
                if user_input.lower() in ("quit", "exit", "q"):
                    break
                if not user_input:
                    continue

                try:
                    parts = user_input.split(maxsplit=1)
                    cmd = parts[0].lower() if parts else ""

                    if cmd == "add" and len(parts) == 2:
                        nums = parts[1].split()
                        a, b = int(nums[0]), int(nums[1])
                        result = await session.call_tool("add", {"a": a, "b": b})
                        print(f"Bot: {result.content[0].text}\n")

                    elif cmd == "hello" and len(parts) == 2:
                        name = parts[1]
                        result = await session.read_resource(f"greeting://{name}")
                        print(f"Bot: {result.contents[0].text}\n")

                    elif cmd == "wiki" and len(parts) == 2:
                        result = await session.call_tool("wiki_search", {"query": parts[1]})
                        text = result.content[0].text
                        print(f"Bot:\n{text}\n")

                    elif cmd == "page" and len(parts) == 2:
                        result = await session.call_tool("wiki_get_page", {"title": parts[1]})
                        print(f"Bot: {result.content[0].text}\n")

                    else:
                        print("Bot: Commands:\n"
                              "  - 'add <num1> <num2>' - add two numbers\n"
                              "  - 'hello <name>' - get a greeting\n"
                              "  - 'wiki <query>' - search Wikipedia\n"
                              "  - 'page <title>' - get Wikipedia page\n")
                except Exception as e:
                    print(f"Bot: Error - {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
