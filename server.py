from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("my-server")

WIKI_API = "https://en.wikipedia.org/api/rest_v1"

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool()
def wiki_search(query: str, limit: int = 5) -> list[dict]:
    """Search Wikipedia for articles matching the query."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json",
    }
    headers = {"User-Agent": "MCPServer/1.0 (https://github.com/example; contact@example.com)"}
    resp = httpx.get(url, params=params, headers=headers)
    data = resp.json()
    results = data.get("query", {}).get("search", [])
    return [{"title": r["title"], "snippet": r["snippet"]} for r in results]

@mcp.tool()
def wiki_get_page(title: str) -> str:
    """Get the summary of a Wikipedia article."""
    url = f"{WIKI_API}/page/summary/{title}"
    headers = {"User-Agent": "MCPServer/1.0 (https://github.com/example; contact@example.com)"}
    resp = httpx.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("extract", "No content found.")
    return f"Article '{title}' not found."

if __name__ == "__main__":
    mcp.run()