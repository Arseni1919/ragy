import time
from conn_tavily.client import client as tavily_client


MAX_RETRIES = 5
RETRY_DELAYS = [1, 2, 4, 8, 16]


def search_with_retry(query: str, max_retries: int = MAX_RETRIES) -> dict:
    for attempt in range(max_retries):
        try:
            return tavily_client.search(query)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(RETRY_DELAYS[attempt])
    return None


def web_search(query: str) -> dict:
    response = tavily_client.search(query)
    results = response.get('results', [])

    if not results:
        return {"query": query, "results": []}

    formatted_results = []
    for result in results[:5]:
        formatted_results.append({
            "title": result.get('title', 'No title'),
            "url": result.get('url', 'N/A'),
            "raw_content": result.get('raw_content') or result.get('content', 'No content')
        })

    return {"query": query, "results": formatted_results}
