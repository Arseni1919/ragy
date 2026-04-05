import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import Field

API_BASE = "http://localhost:8000/api/v1"

server = Server("ragy-mcp-server")

@server.tool()
async def list_collections() -> str:
    """List all available collections in the database.

    Returns a comma-separated list of collection names that can be used
    for extract, search, or other operations."""
    try:
        response = requests.get(f"{API_BASE}/extract/collections")
        response.raise_for_status()
        data = response.json()
        collections = data.get('collections', [])
        if not collections:
            return "No collections found in database."
        return f"Available collections ({len(collections)}): {', '.join(collections)}"
    except requests.HTTPError as e:
        return f"Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def search_web(query: str = Field(description="Search query")) -> str:
    """Search the web for current information using Tavily API.

    Returns relevant web results including titles and URLs."""
    try:
        response = requests.post(
            f"{API_BASE}/search/web",
            json={"query": query}
        )
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        if not results:
            return f"No results found for query: {query}"
        output = [f"Search results for '{query}':\n"]
        for r in results:
            output.append(f"• {r['title']}")
            output.append(f"  URL: {r['url']}")
            if 'content' in r:
                snippet = r['content'][:150] + "..." if len(r['content']) > 150 else r['content']
                output.append(f"  {snippet}")
            output.append("")
        return "\n".join(output)
    except requests.HTTPError as e:
        return f"Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def extract_all(
    query: str = Field(description="Search query to find relevant days"),
    collection_name: str = Field(description="Collection to search"),
    top_k: int = Field(default=10, description="Number of results to return")
) -> str:
    """Extract relevant days from a collection based on similarity search.

    Searches the specified collection for documents most similar to the query
    and returns the top K results with dates, scores, and content."""
    try:
        response = requests.post(
            f"{API_BASE}/extract/all",
            json={
                "query": query,
                "collection_name": collection_name,
                "top_k": top_k
            }
        )
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        if not results:
            return f"No results found in collection '{collection_name}' for query: {query}"
        output = [f"Top {len(results)} results from '{collection_name}' for '{query}':\n"]
        for i, r in enumerate(results, 1):
            date = r.get('date', 'N/A')
            score = r.get('score', 0)
            content = r.get('content', '')
            content_preview = content[:200] + "..." if len(content) > 200 else content
            output.append(f"{i}. Date: {date} | Score: {score:.3f}")
            output.append(f"   {content_preview}")
            output.append("")
        return "\n".join(output)
    except requests.HTTPError as e:
        return f"Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_database_stats() -> str:
    """Get comprehensive database statistics.

    Returns information about all collections including document counts,
    total documents in database, and collection names."""
    try:
        response = requests.get(f"{API_BASE}/database/stats")
        response.raise_for_status()
        data = response.json()
        total_docs = data.get('total_documents', 0)
        collections = data.get('collections', [])

        if not collections:
            return "Database is empty - no collections found."

        output = [f"Database Statistics:\n"]
        output.append(f"Total documents: {total_docs}")
        output.append(f"Total collections: {len(collections)}\n")
        output.append("Collections:")
        for col in collections:
            name = col.get('name', 'N/A')
            count = col.get('document_count', 0)
            output.append(f"  • {name}: {count} documents")
        return "\n".join(output)
    except requests.HTTPError as e:
        return f"Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def health_check() -> str:
    """Check API server health status.

    Verifies that the RagyApp API server is running and accessible."""
    try:
        response = requests.get(f"{API_BASE}/system/health")
        response.raise_for_status()
        data = response.json()
        status = data.get('status', 'unknown')
        return f"API server status: {status}"
    except requests.HTTPError as e:
        return f"Error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error: API server is not accessible - {str(e)}"

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
