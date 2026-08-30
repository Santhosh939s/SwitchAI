import logging
from typing import List, Dict
from duckduckgo_search import DDGS

logger = logging.getLogger("switchai.search")

def search_web_ddg(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    100% Free DuckDuckGo web search without API keys.
    Returns list of dicts with 'title', 'snippet', and 'url'.
    """
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", r.get("snippet", "")),
                    "url": r.get("href", r.get("link", ""))
                })
        return results
    except Exception as e:
        logger.warning(f"DuckDuckGo search error: {e}")
        return []
