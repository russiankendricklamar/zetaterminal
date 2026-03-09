"""
API proxy for Gemini AI — keeps API key server-side.
"""
import os
import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional

from src.middleware.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class CandleInput(BaseModel):
    time: float
    open: float
    high: float
    low: float
    close: float
    volume: float


class GenerateRequest(BaseModel):
    candles: List[CandleInput] = Field(..., description="OHLCV candle data")
    prompt: Optional[str] = Field(None, description="Custom prompt override")


@router.post("/analyze")
@limiter.limit("10/minute")
async def analyze_market(http_request: Request, request: GenerateRequest):
    """Proxy market analysis to Gemini API with server-side key."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Gemini API not configured")

    try:
        import aiohttp

        recent = request.candles[-20:] if len(request.candles) > 20 else request.candles
        data_str = ", ".join(
            f"t={c.time} o={c.open:.1f} h={c.high:.1f} l={c.low:.1f} c={c.close:.1f} v={c.volume:.2f}"
            for c in recent
        )

        prompt = request.prompt or (
            "Analyze this crypto market data (OHLCV). "
            "Identify the short-term trend, provide a confidence score (0-100), "
            "key support/resistance levels, and a brief reasoning string (max 20 words). "
            f"Data: {data_str}"
        )

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                params={"key": GEMINI_API_KEY},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    logger.error("Gemini API error: %s", await resp.text())
                    raise HTTPException(status_code=502, detail="Gemini API error")
                result = await resp.json()

        text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")

        import json
        return json.loads(text)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Gemini proxy error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def gemini_health():
    return {"status": "healthy", "configured": GEMINI_API_KEY is not None}
