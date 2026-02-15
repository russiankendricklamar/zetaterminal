"""
News & AI Service — NewsAPI, Currents API, Hugging Face Inference

Proxies news feeds and ML inference endpoints.
"""

import os
from typing import Optional, Dict, Any, List
from src.utils.http_client import get_session

from src.services.cache_service import cache_get, cache_set, make_cache_key

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_BASE = "https://newsapi.org/v2"

CURRENTS_KEY = os.getenv("CURRENTS_API_KEY", "")
CURRENTS_BASE = "https://api.currentsapi.services/v1"

HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
HF_BASE = "https://api-inference.huggingface.co/models"


# ─── NewsAPI ──────────────────────────────────────────────────────────────────

async def newsapi_top_headlines(
    country: str = "us",
    category: Optional[str] = None,
    q: Optional[str] = None,
    page_size: int = 20,
) -> Dict[str, Any]:
    """Get top headlines from NewsAPI."""
    key = make_cache_key("newsapi", "headlines", country, category, q, page_size)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: Dict[str, Any] = {
        "country": country,
        "pageSize": page_size,
        "apiKey": NEWSAPI_KEY,
    }
    if category:
        params["category"] = category
    if q:
        params["q"] = q

    session = await get_session()
    async with session.get(f"{NEWSAPI_BASE}/top-headlines", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    articles = []
    for a in data.get("articles", []):
        articles.append({
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "url": a.get("url", ""),
            "urlToImage": a.get("urlToImage", ""),
            "publishedAt": a.get("publishedAt", ""),
            "source": a.get("source", {}).get("name", ""),
            "author": a.get("author", ""),
            "content": a.get("content", ""),
        })

    result = {
        "totalResults": data.get("totalResults", 0),
        "articles": articles,
        "provider": "newsapi",
    }
    cache_set(key, result, ttl_seconds=300)
    return result


async def newsapi_everything(
    q: str = "",
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    sort_by: str = "publishedAt",
    page_size: int = 20,
    language: str = "en",
) -> Dict[str, Any]:
    """Search all articles from NewsAPI."""
    key = make_cache_key("newsapi", "everything", q, from_date, to_date, sort_by, page_size)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: Dict[str, Any] = {
        "q": q,
        "sortBy": sort_by,
        "pageSize": page_size,
        "language": language,
        "apiKey": NEWSAPI_KEY,
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    session = await get_session()
    async with session.get(f"{NEWSAPI_BASE}/everything", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    articles = []
    for a in data.get("articles", []):
        articles.append({
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "url": a.get("url", ""),
            "urlToImage": a.get("urlToImage", ""),
            "publishedAt": a.get("publishedAt", ""),
            "source": a.get("source", {}).get("name", ""),
            "author": a.get("author", ""),
        })

    result = {
        "totalResults": data.get("totalResults", 0),
        "articles": articles,
        "provider": "newsapi",
    }
    cache_set(key, result, ttl_seconds=300)
    return result


# ─── Currents API ─────────────────────────────────────────────────────────────

async def currents_latest(
    language: str = "en",
    keywords: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """Get latest news from Currents API."""
    key = make_cache_key("currents", "latest", language, keywords, category)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: Dict[str, Any] = {
        "language": language,
        "apiKey": CURRENTS_KEY,
    }
    if keywords:
        params["keywords"] = keywords
    if category:
        params["category"] = category

    session = await get_session()
    async with session.get(f"{CURRENTS_BASE}/latest-news", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    articles = []
    for n in data.get("news", []):
        articles.append({
            "title": n.get("title", ""),
            "description": n.get("description", ""),
            "url": n.get("url", ""),
            "image": n.get("image", ""),
            "publishedAt": n.get("published", ""),
            "source": n.get("author", ""),
            "category": n.get("category", []),
            "language": n.get("language", ""),
        })

    result = {
        "status": data.get("status", ""),
        "articles": articles,
        "provider": "currents",
    }
    cache_set(key, result, ttl_seconds=300)
    return result


async def currents_search(
    keywords: str = "",
    language: str = "en",
) -> Dict[str, Any]:
    """Search news from Currents API."""
    key = make_cache_key("currents", "search", keywords, language)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: Dict[str, Any] = {
        "keywords": keywords,
        "language": language,
        "apiKey": CURRENTS_KEY,
    }

    session = await get_session()
    async with session.get(f"{CURRENTS_BASE}/search", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    articles = []
    for n in data.get("news", []):
        articles.append({
            "title": n.get("title", ""),
            "description": n.get("description", ""),
            "url": n.get("url", ""),
            "image": n.get("image", ""),
            "publishedAt": n.get("published", ""),
            "source": n.get("author", ""),
        })

    result = {"articles": articles, "provider": "currents"}
    cache_set(key, result, ttl_seconds=300)
    return result


# ─── Hugging Face ─────────────────────────────────────────────────────────────

async def hf_inference(model_id: str, inputs: str) -> Any:
    """Run inference on a Hugging Face model."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    session = await get_session()
    async with session.post(
        f"{HF_BASE}/{model_id}",
        json={"inputs": inputs},
        headers=headers
    ) as resp:
        data = await resp.json(content_type=None)
        # HF returns 503 with estimated_time when model is loading
        if resp.status == 503:
            return {
                "loading": True,
                "estimated_time": data.get("estimated_time", 30),
                "error": "Model is loading, please retry",
            }
        resp.raise_for_status()
        return data


async def hf_sentiment(text: str) -> Dict[str, Any]:
    """Run financial sentiment analysis using ProsusAI/finbert."""
    result = await hf_inference("ProsusAI/finbert", text)
    if isinstance(result, dict) and result.get("loading"):
        return result
    # finbert returns [[{label, score}, ...]]
    scores = result[0] if isinstance(result, list) and len(result) > 0 else []
    return {
        "text": text[:200],
        "scores": scores,
        "provider": "huggingface",
        "model": "ProsusAI/finbert",
    }


async def hf_summarize(text: str, max_length: int = 150) -> Dict[str, Any]:
    """Summarize text using facebook/bart-large-cnn."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    session = await get_session()
    async with session.post(
        f"{HF_BASE}/facebook/bart-large-cnn",
        json={"inputs": text, "parameters": {"max_length": max_length}},
        headers=headers
    ) as resp:
        data = await resp.json(content_type=None)
        if resp.status == 503:
            return {"loading": True, "estimated_time": data.get("estimated_time", 30)}
        resp.raise_for_status()

    summary = data[0].get("summary_text", "") if isinstance(data, list) and len(data) > 0 else ""
    return {
        "summary": summary,
        "provider": "huggingface",
        "model": "facebook/bart-large-cnn",
    }
