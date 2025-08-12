from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-server")

@mcp.tool()
def bible_search(query: str) -> str:
    """Fetch the content of the specified Bible verse reference"""
    import requests
    response = requests.get(f"https://bible-api.com/{query}")
    if response.status_code == 200:
        data = response.json()
        search_results = data.get("text", "Verse not found.")
    else:
        search_results = "Error fetching verse."
    return search_results


if __name__ == "__main__":
    mcp.run(transport="stdio")