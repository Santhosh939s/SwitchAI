import logging
import httpx
from typing import List, Dict
from duckduckgo_search import DDGS

logger = logging.getLogger("switchai.search")

def search_wikipedia(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Fallback 100% free search using Wikipedia REST API.
    """
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "format": "json",
            "srsearch": query,
            "srlimit": max_results
        }
        with httpx.Client(timeout=4.0) as client:
            res = client.get(url, params=params)
            if res.status_code == 200:
                data = res.json()
                results = []
                for item in data.get("query", {}).get("search", []):
                    title = item.get("title", "")
                    snippet = item.get("snippet", "").replace('<span class="searchmatch">', '').replace('</span>', '')
                    page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": page_url
                    })
                return results
    except Exception as e:
        logger.warning(f"Wikipedia fallback search error: {e}")
    return []

def search_web_ddg(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    100% Free DuckDuckGo web search with Wikipedia fallback.
    Returns list of dicts with 'title', 'snippet', and 'url'.
    """
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", r.get("snippet", "")),
                    "url": r.get("href", r.get("link", ""))
                })
        if results:
            return results
    except Exception as e:
        logger.warning(f"DuckDuckGo search error, attempting Wikipedia fallback: {e}")

    # Fallback to Wikipedia API if DuckDuckGo is rate-limited or empty
    return search_wikipedia(query, max_results=max_results)
