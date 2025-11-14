# app/services/search.py

from serpapi import GoogleSearch
from app.core.config import settings

def get_serp_competitors(query: str, num_results: int = 5):
    """Return top organic competitors from Google Search using SerpAPI."""
    params = {
        "engine": "google",
        "q": query,
        "api_key": settings.SERPAPI_KEY,
        "num": num_results,
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        organic = results.get("organic_results", [])

        competitors = []
        for r in organic:
            url = r.get("link")
            title = r.get("title")
            if url:
                competitors.append({
                    "title": title,
                    "url": url
                })

        return competitors

    except Exception as e:
        print("SerpAPI error:", e)
        return []
