"""
API endpoints для получения рыночных данных через yfinance.
"""
import asyncio
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.yfinance_service import (
    get_crypto_info,
    get_currency_rate,
    get_index_info,
    get_multiple_stocks,
    get_popular_cryptos,
    get_popular_tickers,
    get_stock_history,
    get_stock_info,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


class StockHistoryRequest(BaseModel):
    """Запрос на получение истории акции."""
    ticker: str = Field(..., description="Тикер акции")
    period: str = Field(
        "1mo",
        description="Период (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
    )
    interval: str = Field(
        "1d",
        description="Интервал (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)",
    )


class MultipleStocksRequest(BaseModel):
    """Запрос на получение данных о нескольких акциях."""
    tickers: list[str] = Field(..., description="Список тикеров", max_length=50)


@router.get("/stock/{ticker}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Get Stock")
async def get_stock(http_request: Request, ticker: str):
    """Получает информацию об акции."""
    return await asyncio.to_thread(get_stock_info, ticker)


@router.post("/stock/history", response_model=list[dict[str, Any]])
@limiter.limit("20/minute")
@service_endpoint("Stock History")
async def get_stock_history_endpoint(http_request: Request, request: StockHistoryRequest):
    """Получает исторические данные об акции."""
    return await asyncio.to_thread(
        get_stock_history, request.ticker, request.period, request.interval
    )


@router.post("/stocks/multiple", response_model=list[dict[str, Any]])
@limiter.limit("10/minute")
@service_endpoint("Multiple Stocks")
async def get_multiple_stocks_endpoint(http_request: Request, request: MultipleStocksRequest):
    """Получает информацию о нескольких акциях одновременно."""
    return await asyncio.to_thread(get_multiple_stocks, request.tickers)


@router.get("/currency/{base}/{quote}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Currency Rate")
async def get_currency(http_request: Request, base: str, quote: str = "USD"):
    """Получает курс валютной пары."""
    return await asyncio.to_thread(get_currency_rate, base, quote)


@router.get("/crypto/{symbol}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Crypto Info")
async def get_crypto(http_request: Request, symbol: str):
    """Получает информацию о криптовалюте."""
    return await asyncio.to_thread(get_crypto_info, symbol)


@router.get("/index/{symbol:path}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Index Info")
async def get_index(http_request: Request, symbol: str):
    """Получает информацию об индексе (например, ^GSPC для S&P 500)."""
    return await asyncio.to_thread(get_index_info, symbol)


@router.get("/tickers/popular", response_model=list[str])
@limiter.limit("30/minute")
@service_endpoint("Popular Tickers")
async def popular_tickers(http_request: Request):
    """Получает список популярных тикеров."""
    return get_popular_tickers()


@router.get("/crypto/popular", response_model=list[str])
@limiter.limit("30/minute")
@service_endpoint("Popular Cryptos")
async def popular_cryptos(http_request: Request):
    """Получает список популярных криптовалют."""
    return get_popular_cryptos()


@router.get("/health")
async def health():
    """Health check для сервиса рыночных данных."""
    return {"status": "ok", "service": "market_data"}
