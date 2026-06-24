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
                    parts = user_input.split()
                    if parts[0].lower() == "add" and len(parts) == 3:
                        a, b = int(parts[1]), int(parts[2])
                        result = await session.call_tool("add", {"a": a, "b": b})
                        print(f"Bot: {result.content[0].text}\n")
                    elif parts[0].lower() == "hello" and len(parts) == 2:
                        name = parts[1]
                        result = await session.read_resource(f"greeting://{name}")
                        print(f"Bot: {result.contents[0].text}\n")
                    else:
                        print("Bot: I can do two things:\n"
                              "  - 'add <num1> <num2>' - add two numbers\n"
                              "  - 'hello <name>' - get a greeting\n")
                except Exception as e:
                    print(f"Bot: Error - {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
