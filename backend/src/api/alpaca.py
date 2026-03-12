"""
API endpoints для Alpaca Data API — US stocks, paper trading.

Используется для paper-trading/алготрейдинг по США,
бэктест + реальное исполнение. Балансируется с Finnhub.
"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.alpaca_service import (
    alpaca_account,
    alpaca_bars,
    alpaca_latest_quote,
    alpaca_latest_trade,
    alpaca_multi_bars,
    alpaca_snapshot,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


class AlpacaBarsRequest(BaseModel):
    """Запрос на исторические бары Alpaca."""
    symbol: str = Field(..., description="US тикер (AAPL, MSFT)")
    timeframe: str = Field("1Day", description="1Min, 5Min, 15Min, 30Min, 1Hour, 1Day, 1Week, 1Month")
    start: str | None = Field(None, description="Начальная дата ISO 8601")
    end: str | None = Field(None, description="Конечная дата ISO 8601")
    limit: int = Field(1000, ge=1, le=10000, description="Макс. баров")


class AlpacaMultiBarsRequest(BaseModel):
    """Запрос на бары нескольких тикеров."""
    symbols: list[str] = Field(..., max_length=50, description="Список US тикеров")
    timeframe: str = Field("1Day", description="Timeframe")
    start: str | None = Field(None, description="Начальная дата")
    end: str | None = Field(None, description="Конечная дата")
    limit: int = Field(1000, ge=1, le=10000, description="Макс. баров на тикер")


@router.post("/bars", response_model=dict[str, Any])
@limiter.limit("60/minute")
@service_endpoint("Alpaca Bars")
async def get_bars(request: Request, body: AlpacaBarsRequest):
    """Получить исторические OHLCV-бары US-акции с VWAP и trade count."""
    return await alpaca_bars(
        symbol=body.symbol,
        timeframe=body.timeframe,
        start=body.start,
        end=body.end,
        limit=body.limit,
    )


@router.get("/quote/{symbol}", response_model=dict[str, Any])
@limiter.limit("60/minute")
@service_endpoint("Alpaca Latest Quote")
async def get_latest_quote(request: Request, symbol: str):
    """Получить последнюю котировку NBBO (bid/ask) US-акции."""
    return await alpaca_latest_quote(symbol)


@router.get("/trade/{symbol}", response_model=dict[str, Any])
@limiter.limit("60/minute")
@service_endpoint("Alpaca Latest Trade")
async def get_latest_trade(request: Request, symbol: str):
    """Получить последнюю сделку US-акции."""
    return await alpaca_latest_trade(symbol)


@router.get("/snapshot/{symbol}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Alpaca Snapshot")
async def get_snapshot(request: Request, symbol: str):
    """Получить полный снапшот: quote + trade + minute bar + daily bar."""
    return await alpaca_snapshot(symbol)


@router.post("/multi-bars", response_model=dict[str, Any])
@limiter.limit("20/minute")
@service_endpoint("Alpaca Multi Bars")
async def get_multi_bars(request: Request, body: AlpacaMultiBarsRequest):
    """Получить бары для нескольких US-акций в одном запросе (до 50)."""
    return await alpaca_multi_bars(
        symbols=body.symbols,
        timeframe=body.timeframe,
        start=body.start,
        end=body.end,
        limit=body.limit,
    )


@router.get("/account", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Alpaca Account")
async def get_account(request: Request):
    """Получить информацию о paper-trading аккаунте."""
    return await alpaca_account()


@router.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "alpaca", "provider": "alpaca.markets"}
