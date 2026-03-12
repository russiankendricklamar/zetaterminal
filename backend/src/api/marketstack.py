"""
API endpoints для Marketstack — EOD котировки глобальных акций.

Лёгкое REST-API для end-of-day данных в небольших сервисах.
"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.marketstack_service import (
    marketstack_eod,
    marketstack_eod_latest,
    marketstack_tickers,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


class MarketstackEODRequest(BaseModel):
    """Запрос на EOD-данные."""
    symbol: str = Field(..., description="Тикер (AAPL, MSFT)")
    date_from: str | None = Field(None, description="Начальная дата YYYY-MM-DD")
    date_to: str | None = Field(None, description="Конечная дата YYYY-MM-DD")
    limit: int = Field(100, ge=1, le=1000, description="Макс. записей")


class MarketstackLatestRequest(BaseModel):
    """Запрос на последние EOD-данные нескольких тикеров."""
    symbols: list[str] = Field(..., max_length=50, description="Список тикеров")


@router.post("/eod", response_model=dict[str, Any])
@limiter.limit("20/minute")
@service_endpoint("Marketstack EOD")
async def get_eod(request: Request, body: MarketstackEODRequest):
    """Получить end-of-day исторические данные."""
    return await marketstack_eod(
        symbol=body.symbol,
        date_from=body.date_from,
        date_to=body.date_to,
        limit=body.limit,
    )


@router.post("/eod/latest", response_model=dict[str, Any])
@limiter.limit("20/minute")
@service_endpoint("Marketstack Latest")
async def get_eod_latest(request: Request, body: MarketstackLatestRequest):
    """Получить последние EOD-данные для нескольких тикеров."""
    return await marketstack_eod_latest(body.symbols)


@router.get("/tickers", response_model=dict[str, Any])
@limiter.limit("20/minute")
@service_endpoint("Marketstack Tickers")
async def search_tickers(request: Request, search: str | None = None, limit: int = 50):
    """Поиск доступных тикеров на Marketstack."""
    return await marketstack_tickers(search=search, limit=limit)


@router.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "marketstack", "provider": "marketstack.com"}
