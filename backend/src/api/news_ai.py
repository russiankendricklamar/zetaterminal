"""
News & AI Router — NewsAPI, Currents API, Hugging Face Inference

Prefix: /api/news-ai
"""


from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.middleware.rate_limit import limiter
from src.services.news_ai_service import (
    currents_latest,
    currents_search,
    hf_inference,
    hf_sentiment,
    hf_summarize,
    newsapi_everything,
    newsapi_top_headlines,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


# ─── NewsAPI ──────────────────────────────────────────────────────────────────

@router.get("/newsapi/headlines")
@limiter.limit("5/minute")
@service_endpoint("News Headlines")
async def news_headlines(
    request: Request,
    country: str = Query("us"),
    category: str | None = Query(None),
    q: str | None = Query(None),
    page_size: int = Query(20),
):
    """Top headlines from NewsAPI."""
    return await newsapi_top_headlines(country, category, q, page_size)
@router.get("/newsapi/everything")
@limiter.limit("5/minute")
@service_endpoint("News Everything")
async def news_everything(
    request: Request,
    q: str = Query(""),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    sort_by: str = Query("publishedAt"),
    page_size: int = Query(20),
    language: str = Query("en"),
):
    """Search all articles from NewsAPI."""
    return await newsapi_everything(q, from_date, to_date, sort_by, page_size, language)
# ─── Currents API ─────────────────────────────────────────────────────────────

@router.get("/currents/latest")
@limiter.limit("20/minute")
@service_endpoint("Curr Latest")
async def curr_latest(
    request: Request,
    language: str = Query("en"),
    keywords: str | None = Query(None),
    category: str | None = Query(None),
):
    """Latest news from Currents API."""
    return await currents_latest(language, keywords, category)
@router.get("/currents/search")
@limiter.limit("20/minute")
@service_endpoint("Curr Search")
async def curr_search(
    request: Request,
    keywords: str = Query(""),
    language: str = Query("en"),
):
    """Search news from Currents API."""
    return await currents_search(keywords, language)
# ─── Hugging Face ─────────────────────────────────────────────────────────────

_ALLOWED_HF_MODELS = frozenset({
    "ProsusAI/finbert",
    "facebook/bart-large-cnn",
    "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
    "yiyanghkust/finbert-tone",
})


class InferenceRequest(BaseModel):
    model_id: str = Field(..., max_length=200)
    inputs: str = Field(..., max_length=10_000)

class SentimentRequest(BaseModel):
    text: str = Field(..., max_length=10_000)

class SummarizeRequest(BaseModel):
    text: str = Field(..., max_length=50_000)
    max_length: int = Field(150, ge=10, le=2000)


@router.post("/huggingface/inference")
@limiter.limit("10/minute")
@service_endpoint("Hf Infer")
async def hf_infer(request: Request, req: InferenceRequest):
    """Run HF model inference (whitelisted models only)."""
    if req.model_id not in _ALLOWED_HF_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Model not allowed. Allowed: {', '.join(sorted(_ALLOWED_HF_MODELS))}",
        )
    return await hf_inference(req.model_id, req.inputs)
@router.post("/huggingface/sentiment")
@limiter.limit("10/minute")
@service_endpoint("Hf Sent")
async def hf_sent(request: Request, req: SentimentRequest):
    """Financial sentiment analysis (ProsusAI/finbert)."""
    return await hf_sentiment(req.text)
@router.post("/huggingface/summarize")
@limiter.limit("10/minute")
async def hf_sum(request: Request, req: SummarizeRequest):
    """Text summarization (facebook/bart-large-cnn)."""
    return await hf_summarize(req.text, req.max_length)
@router.get("/health")
async def health():
    return {"status": "ok", "service": "news-ai"}
