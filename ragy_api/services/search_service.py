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


def web_search(query: str, max_results: int = 5) -> dict:
    response = tavily_client.search(query, max_results=max_results)
    results = response.get('results', [])

    if not results:
        return {"query": query, "results": []}

    formatted_results = []
    for result in results:
        formatted_results.append({
            "title": result.get('title', 'No title'),
            "url": result.get('url', 'N/A'),
            "raw_content": result.get('raw_content') or result.get('content', 'No content')
        })

    return {"query": query, "results": formatted_results}


def yfinance_search(query: str, max_results: int = 5) -> dict:
    """Search financial data using yfinance."""
    import yfinance as yf

    search = yf.Search(query, max_results=max_results)

    formatted_results = []

    # Add news articles
    for article in search.news:
        if len(formatted_results) >= max_results:
            break

        title = article.get('title', 'N/A')
        link = article.get('link', '')
        publisher = article.get('publisher', 'Unknown')
        related_tickers = article.get('relatedTickers', [])

        # Build content string with structured information
        content = f"Title: {title}\n"
        content += f"Publisher: {publisher}\n"
        if related_tickers:
            content += f"Related Tickers: {', '.join(related_tickers)}\n"
        content += f"Link: {link}"

        formatted_results.append({
            "title": title,
            "url": link,
            "raw_content": content
        })

    # Add quote results
    for quote in search.quotes:
        if len(formatted_results) >= max_results:
            break

        symbol = quote.get('symbol', 'N/A')
        name = quote.get('shortname', quote.get('longname', 'N/A'))
        quote_type = quote.get('quoteType', 'N/A')
        exchange = quote.get('exchange', 'N/A')

        content = f"Symbol: {symbol}\n"
        content += f"Name: {name}\n"
        content += f"Type: {quote_type}\n"
        content += f"Exchange: {exchange}"

        formatted_results.append({
            "title": f"{symbol} - {name}",
            "url": f"https://finance.yahoo.com/quote/{symbol}",
            "raw_content": content
        })

    return {"query": query, "results": formatted_results}


async def bright_data_search(query: str, max_results: int = 5) -> dict:
    """Search the web using Bright Data."""
    from conn_bright_data.client import client as bright_data_client

    response = await bright_data_client.search(query, max_results=max_results)
    results = response.get('results', [])

    if not results:
        return {"query": query, "results": []}

    formatted_results = []
    for result in results[:max_results]:
        formatted_results.append({
            "title": result.get('title', 'No title'),
            "url": result.get('url', 'N/A'),
            "raw_content": result.get('raw_content', 'No content')
        })

    return {"query": query, "results": formatted_results}


def bright_data_search_with_retry(query: str, max_results: int = 5, max_retries: int = MAX_RETRIES) -> dict:
    """Search with retry logic for Bright Data (sync wrapper)."""
    import asyncio

    for attempt in range(max_retries):
        try:
            return asyncio.run(bright_data_search(query, max_results))
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(RETRY_DELAYS[attempt])
    return {"query": query, "results": []}


async def bright_data_search_with_retry_async(query: str, max_results: int = 5, max_retries: int = MAX_RETRIES) -> dict:
    """Search with retry logic for Bright Data (async)."""
    import asyncio

    for attempt in range(max_retries):
        try:
            return await bright_data_search(query, max_results)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(RETRY_DELAYS[attempt])
    return {"query": query, "results": []}
