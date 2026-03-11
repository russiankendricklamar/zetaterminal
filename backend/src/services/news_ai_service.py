"""
News & AI Service — NewsAPI, Currents API, Hugging Face Inference

Proxies news feeds and ML inference endpoints.
"""

import re
from typing import Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.services.secrets_service import get_key_sync
from src.utils.http_client import get_session

NEWSAPI_BASE = "https://newsapi.org/v2"

CURRENTS_BASE = "https://api.currentsapi.services/v1"

HF_BASE = "https://api-inference.huggingface.co/models"


def _newsapi_key() -> str: return get_key_sync("NEWSAPI_KEY")
def _currents_key() -> str: return get_key_sync("CURRENTS_API_KEY")
def _hf_token() -> str: return get_key_sync("HUGGINGFACE_TOKEN")


# ─── NewsAPI ──────────────────────────────────────────────────────────────────

async def newsapi_top_headlines(
    country: str = "us",
    category: str | None = None,
    q: str | None = None,
    page_size: int = 20,
) -> dict[str, Any]:
    """Get top headlines from NewsAPI."""
    key = make_cache_key("newsapi", "headlines", country, category, q, page_size)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {
        "country": country,
        "pageSize": page_size,
        "apiKey": _newsapi_key(),
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
    from_date: str | None = None,
    to_date: str | None = None,
    sort_by: str = "publishedAt",
    page_size: int = 20,
    language: str = "en",
) -> dict[str, Any]:
    """Search all articles from NewsAPI."""
    key = make_cache_key("newsapi", "everything", q, from_date, to_date, sort_by, page_size)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {
        "q": q,
        "sortBy": sort_by,
        "pageSize": page_size,
        "language": language,
        "apiKey": _newsapi_key(),
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
    keywords: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    """Get latest news from Currents API."""
    key = make_cache_key("currents", "latest", language, keywords, category)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {
        "language": language,
        "apiKey": _currents_key(),
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
) -> dict[str, Any]:
    """Search news from Currents API."""
    key = make_cache_key("currents", "search", keywords, language)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {
        "keywords": keywords,
        "language": language,
        "apiKey": _currents_key(),
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

_HF_MODEL_RE = re.compile(r"^[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\.]+$")


async def hf_inference(model_id: str, inputs: str) -> Any:
    """Run inference on a Hugging Face model."""
    if not _HF_MODEL_RE.match(model_id):
        raise ValueError(f"Invalid HuggingFace model_id: {model_id}")
    headers = {"Authorization": f"Bearer {_hf_token()}"}
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


async def hf_sentiment(text: str) -> dict[str, Any]:
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


async def hf_summarize(text: str, max_length: int = 150) -> dict[str, Any]:
    """Summarize text using facebook/bart-large-cnn."""
    headers = {"Authorization": f"Bearer {_hf_token()}"}
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
