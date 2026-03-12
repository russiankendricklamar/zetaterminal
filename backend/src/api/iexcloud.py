"""
API endpoints для IEX Cloud — US equities focused data.

Используется для US-центричного дашборда и портфель-трекера.
"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.iexcloud_service import (
    iex_batch,
    iex_company,
    iex_historical,
    iex_key_stats,
    iex_quote,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


class IEXHistoryRequest(BaseModel):
    """Запрос на исторические данные IEX."""
    symbol: str = Field(..., description="US тикер (AAPL, MSFT)")
    range: str = Field("1m", description="Период: 5d, 1m, 3m, 6m, ytd, 1y, 2y, 5y, max")


class IEXBatchRequest(BaseModel):
    """Запрос на пакетные данные IEX."""
    symbols: list[str] = Field(..., max_length=100, description="Список тикеров (макс. 100)")
    types: str = Field("quote", description="Типы данных: quote, chart, company, stats")


@router.get("/quote/{symbol}", response_model=dict[str, Any])
@limiter.limit("60/minute")
@service_endpoint("IEX Quote")
async def get_quote(request: Request, symbol: str):
    """Получить котировку US-акции в реальном времени."""
    return await iex_quote(symbol)


@router.post("/history", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("IEX Historical")
async def get_historical(request: Request, body: IEXHistoryRequest):
    """Получить исторические дневные цены US-акции."""
    return await iex_historical(symbol=body.symbol, range_period=body.range)


@router.get("/company/{symbol}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("IEX Company")
async def get_company(request: Request, symbol: str):
    """Получить информацию о компании: сектор, индустрия, CEO, описание."""
    return await iex_company(symbol)


@router.get("/stats/{symbol}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("IEX Key Stats")
async def get_key_stats(request: Request, symbol: str):
    """Получить ключевые финансовые показатели: P/E, beta, dividend yield, EPS."""
    return await iex_key_stats(symbol)


@router.post("/batch", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("IEX Batch")
async def get_batch(request: Request, body: IEXBatchRequest):
    """Пакетный запрос данных для нескольких тикеров (до 100)."""
    return await iex_batch(symbols=body.symbols, types=body.types)


@router.get("/health")
async def health():
    """Health check для IEX Cloud сервиса."""
    return {"status": "ok", "service": "iex_cloud", "provider": "iexcloud.io"}
