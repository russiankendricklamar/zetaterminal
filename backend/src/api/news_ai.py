"""
News & AI Router — NewsAPI, Currents API, Hugging Face Inference

Prefix: /api/news-ai
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional
from pydantic import BaseModel

from src.services.news_ai_service import (
    newsapi_top_headlines,
    newsapi_everything,
    currents_latest,
    currents_search,
    hf_inference,
    hf_sentiment,
    hf_summarize,
)

router = APIRouter()


# ─── NewsAPI ──────────────────────────────────────────────────────────────────

@router.get("/newsapi/headlines")
async def news_headlines(
    country: str = Query("us"),
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page_size: int = Query(20),
):
    """Top headlines from NewsAPI."""
    try:
        return await newsapi_top_headlines(country, category, q, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/newsapi/everything")
async def news_everything(
    q: str = Query(""),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    sort_by: str = Query("publishedAt"),
    page_size: int = Query(20),
    language: str = Query("en"),
):
    """Search all articles from NewsAPI."""
    try:
        return await newsapi_everything(q, from_date, to_date, sort_by, page_size, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Currents API ─────────────────────────────────────────────────────────────

@router.get("/currents/latest")
async def curr_latest(
    language: str = Query("en"),
    keywords: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    """Latest news from Currents API."""
    try:
        return await currents_latest(language, keywords, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/currents/search")
async def curr_search(
    keywords: str = Query(""),
    language: str = Query("en"),
):
    """Search news from Currents API."""
    try:
        return await currents_search(keywords, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Hugging Face ─────────────────────────────────────────────────────────────

class InferenceRequest(BaseModel):
    model_id: str
    inputs: str

class SentimentRequest(BaseModel):
    text: str

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 150


@router.post("/huggingface/inference")
async def hf_infer(req: InferenceRequest):
    """Run arbitrary HF model inference."""
    try:
        return await hf_inference(req.model_id, req.inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/huggingface/sentiment")
async def hf_sent(req: SentimentRequest):
    """Financial sentiment analysis (ProsusAI/finbert)."""
    try:
        return await hf_sentiment(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/huggingface/summarize")
async def hf_sum(req: SummarizeRequest):
    """Text summarization (facebook/bart-large-cnn)."""
    try:
        return await hf_summarize(req.text, req.max_length)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok", "service": "news-ai"}
