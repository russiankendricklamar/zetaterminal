"""
API endpoints для Finnhub — real-time и исторические рыночные данные.

Используется для web-дашбордов, near-real-time quotes, SPA-клиентов.
Балансируется с Alpaca для разгрузки.
"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.finnhub_service import (
    finnhub_candles,
    finnhub_company_profile,
    finnhub_crypto_candles,
    finnhub_forex_rates,
    finnhub_market_news,
    finnhub_quote,
    finnhub_search,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


class FinnhubCandleRequest(BaseModel):
    """Запрос на получение свечей из Finnhub."""
    symbol: str = Field(..., description="Тикер (AAPL, MSFT)")
    resolution: str = Field("D", description="Разрешение: 1, 5, 15, 30, 60, D, W, M")
    from_ts: int | None = Field(None, description="Unix timestamp начала")
    to_ts: int | None = Field(None, description="Unix timestamp конца")


class FinnhubCryptoCandleRequest(BaseModel):
    """Запрос на крипто-свечи Finnhub."""
    symbol: str = Field(..., description="Символ (BINANCE:BTCUSDT, COINBASE:ETH-USD)")
    resolution: str = Field("D", description="Разрешение: 1, 5, 15, 30, 60, D, W, M")
    from_ts: int | None = Field(None, description="Unix timestamp начала")
    to_ts: int | None = Field(None, description="Unix timestamp конца")


@router.get("/quote/{symbol}", response_model=dict[str, Any])
@limiter.limit("60/minute")
@service_endpoint("Finnhub Quote")
async def get_quote(request: Request, symbol: str):
    """
    Получить котировку акции в реальном времени.

    Возвращает текущую цену, изменение, high/low, open, previous close.
    """
    return await finnhub_quote(symbol)


@router.post("/candles", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Finnhub Candles")
async def get_candles(request: Request, body: FinnhubCandleRequest):
    """
    Получить OHLCV-свечи акции.

    Разрешения: 1, 5, 15, 30, 60 минут; D (день), W (неделя), M (месяц).
    """
    return await finnhub_candles(
        symbol=body.symbol,
        resolution=body.resolution,
        from_ts=body.from_ts,
        to_ts=body.to_ts,
    )


@router.get("/profile/{symbol}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Finnhub Company Profile")
async def get_company_profile(request: Request, symbol: str):
    """Получить профиль компании: название, отрасль, капитализация, лого."""
    return await finnhub_company_profile(symbol)


@router.get("/news", response_model=list[dict[str, Any]])
@limiter.limit("20/minute")
@service_endpoint("Finnhub Market News")
async def get_market_news(request: Request, category: str = "general"):
    """
    Получить рыночные новости.

    Категории: general, forex, crypto, merger.
    """
    return await finnhub_market_news(category)


@router.get("/forex/{base}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Finnhub Forex Rates")
async def get_forex_rates(request: Request, base: str = "USD"):
    """Получить валютные курсы относительно базовой валюты."""
    return await finnhub_forex_rates(base)


@router.post("/crypto/candles", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Finnhub Crypto Candles")
async def get_crypto_candles(request: Request, body: FinnhubCryptoCandleRequest):
    """
    Получить OHLCV-свечи криптовалюты.

    Формат символа: EXCHANGE:PAIR (BINANCE:BTCUSDT, COINBASE:ETH-USD).
    """
    return await finnhub_crypto_candles(
        symbol=body.symbol,
        resolution=body.resolution,
        from_ts=body.from_ts,
        to_ts=body.to_ts,
    )


@router.get("/search", response_model=list[dict[str, Any]])
@limiter.limit("30/minute")
@service_endpoint("Finnhub Search")
async def search_symbols(request: Request, q: str):
    """Поиск тикеров по названию или символу. До 20 результатов."""
    return await finnhub_search(q)


@router.get("/health")
async def health():
    """Health check для Finnhub сервиса."""
    return {"status": "ok", "service": "finnhub", "provider": "finnhub.io"}
