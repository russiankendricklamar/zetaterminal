"""
API endpoints для Massive (Stock Market API) — global tick + historical data.

Используется для экспериментов с tick-уровнем через WS, low-код/LLM агентов.
"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.massive_service import (
    massive_history,
    massive_quote,
    massive_search,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


class MassiveHistoryRequest(BaseModel):
    """Запрос на исторические данные Massive."""
    symbol: str = Field(..., description="Тикер глобальной акции")
    date_from: str | None = Field(None, description="Начальная дата YYYY-MM-DD")
    date_to: str | None = Field(None, description="Конечная дата YYYY-MM-DD")


@router.get("/quote/{symbol}", response_model=dict[str, Any])
@limiter.limit("60/minute")
@service_endpoint("Massive Quote")
async def get_quote(request: Request, symbol: str):
    """Получить котировку глобальной акции."""
    return await massive_quote(symbol)


@router.post("/history", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Massive History")
async def get_history(request: Request, body: MassiveHistoryRequest):
    """Получить исторические OHLCV-данные глобальной акции."""
    return await massive_history(
        symbol=body.symbol,
        date_from=body.date_from,
        date_to=body.date_to,
    )


@router.get("/search", response_model=list[dict[str, Any]])
@limiter.limit("30/minute")
@service_endpoint("Massive Search")
async def search_symbols(request: Request, query: str):
    """Поиск тикеров глобальных акций."""
    return await massive_search(query)


@router.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "massive", "provider": "stockmarketapi.com"}
