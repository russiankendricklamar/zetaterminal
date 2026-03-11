"""
API endpoints для получения рыночных данных через yfinance.
"""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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
    period: str = Field("1mo", description="Период (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
    interval: str = Field("1d", description="Интервал (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")


class MultipleStocksRequest(BaseModel):
    """Запрос на получение данных о нескольких акциях."""
    tickers: list[str] = Field(..., description="Список тикеров")


@router.get("/stock/{ticker}", response_model=dict[str, Any])
@service_endpoint("Get Stock")
async def get_stock(ticker: str):
    """
    Получает информацию об акции.
    
    Args:
        ticker: Тикер акции (например, 'AAPL', 'MSFT', 'SBER.ME')
    
    Returns:
        Информация об акции
    """
    return get_stock_info(ticker)
    """
    Получает исторические данные об акции.
    
    Args:
        request: Запрос с тикером, периодом и интервалом
    
    Returns:
        Исторические данные
    """
    return get_stock_history(request.ticker, request.period, request.interval)
    """
    Получает информацию о нескольких акциях одновременно.
    
    Args:
        request: Запрос со списком тикеров
    
    Returns:
        Список информации об акциях
    """
    return get_multiple_stocks(request.tickers)
    """
    Получает курс валютной пары.
    
    Args:
        base: Базовая валюта (например, 'EUR', 'RUB')
        quote: Котируемая валюта (по умолчанию 'USD')
    
    Returns:
        Информация о курсе валютной пары
    """
    return get_currency_rate(base, quote)
    """
    Получает информацию о криптовалюте.
    
    Args:
        symbol: Символ криптовалюты (например, 'BTC-USD', 'ETH-USD')
    
    Returns:
        Информация о криптовалюте
    """
    return get_crypto_info(symbol)
    """
    Получает информацию об индексе.
    
    Args:
        symbol: Символ индекса (например, '^GSPC' для S&P 500, '^DJI' для Dow Jones)
    
    Returns:
        Информация об индексе
    """
    return get_index_info(symbol)
    """
    Получает список популярных тикеров из различных индексов и бирж.
    Включает S&P 500, NASDAQ 100, Dow Jones, и другие популярные акции.
    
    Returns:
        Список популярных тикеров
    """
    return get_popular_tickers()
    """
    Получает список популярных криптовалют.
    Формат тикеров: SYMBOL-USD (например, BTC-USD, ETH-USD)
    
    Returns:
        Список популярных криптовалют
    """
    return get_popular_cryptos()
    """Health check для сервиса рыночных данных."""
    return {"status": "ok", "service": "market_data"}
