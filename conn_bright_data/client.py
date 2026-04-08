from dotenv import load_dotenv
from brightdata import BrowserAPI
from bs4 import BeautifulSoup

load_dotenv()

_browser_api = None

def _get_browser_api():
    global _browser_api
    if _browser_api is None:
        _browser_api = BrowserAPI()
    return _browser_api

def _parse_google_results(html: str, max_results: int = 5) -> list[dict]:
    try:
        soup = BeautifulSoup(html, 'lxml')
        results = []

        result_divs = soup.select('div.g')
        if not result_divs:
            result_divs = soup.select('div.tF2Cxc')

        for div in result_divs[:max_results * 2]:
            h3 = div.find('h3')
            if not h3:
                continue
            title = h3.get_text(strip=True)

            a_tag = div.find('a', href=True)
            if not a_tag:
                continue
            url = a_tag['href']

            if not url.startswith('http') or '/search' in url:
                continue

            snippet_div = div.find('div', class_='VwiC3b') or div.find('span', class_='aCOpRe')
            snippet = snippet_div.get_text(strip=True) if snippet_div else ""

            results.append({
                "title": title or "No title",
                "url": url,
                "raw_content": snippet or "No content"
            })

            if len(results) >= max_results:
                break

        return results

    except Exception as e:
        print(f"HTML parsing error: {e}")
        return []

async def search(query: str, max_results: int = 5) -> dict:
    try:
        browser = _get_browser_api()
        google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        result = await browser.fetch_async(google_url)

        if not result.success or not result.data:
            print(f"Bright Data fetch failed: {result.status} - {result.error}")
            return {"query": query, "results": []}

        parsed_results = _parse_google_results(result.data, max_results)

        return {"query": query, "results": parsed_results}

    except Exception as e:
        print(f"Bright Data search error: {e}")
        return {"query": query, "results": []}

client = type('BrightDataClient', (), {
    'search': staticmethod(search)
})()
