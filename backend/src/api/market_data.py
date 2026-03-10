"""
API endpoints для получения рыночных данных через yfinance.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from src.services.yfinance_service import (
    get_stock_info,
    get_stock_history,
    get_multiple_stocks,
    get_currency_rate,
    get_crypto_info,
    get_index_info,
    get_popular_tickers,
    get_popular_cryptos
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class StockHistoryRequest(BaseModel):
    """Запрос на получение истории акции."""
    ticker: str = Field(..., description="Тикер акции")
    period: str = Field("1mo", description="Период (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
    interval: str = Field("1d", description="Интервал (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")


class MultipleStocksRequest(BaseModel):
    """Запрос на получение данных о нескольких акциях."""
    tickers: List[str] = Field(..., description="Список тикеров")


@router.get("/stock/{ticker}", response_model=Dict[str, Any])
async def get_stock(ticker: str):
    """
    Получает информацию об акции.
    
    Args:
        ticker: Тикер акции (например, 'AAPL', 'MSFT', 'SBER.ME')
    
    Returns:
        Информация об акции
    """
    try:
        return get_stock_info(ticker)
    except ValueError as e:
        logger.error("Stock not found for ticker %s: %s", ticker, e, exc_info=True)
        raise HTTPException(status_code=404, detail="Ticker not found")
    except Exception as e:
        logger.error("Error in get_stock endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stock/history", response_model=List[Dict])
async def get_history(request: StockHistoryRequest):
    """
    Получает исторические данные об акции.
    
    Args:
        request: Запрос с тикером, периодом и интервалом
    
    Returns:
        Исторические данные
    """
    try:
        return get_stock_history(request.ticker, request.period, request.interval)
    except ValueError as e:
        logger.error("Stock history not found: %s", e, exc_info=True)
        raise HTTPException(status_code=404, detail="History not found")
    except Exception as e:
        logger.error("Error in get_history endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stocks/multiple", response_model=List[Dict[str, Any]])
async def get_multiple(request: MultipleStocksRequest):
    """
    Получает информацию о нескольких акциях одновременно.
    
    Args:
        request: Запрос со списком тикеров
    
    Returns:
        Список информации об акциях
    """
    try:
        return get_multiple_stocks(request.tickers)
    except ValueError as e:
        logger.error("Invalid request for multiple stocks: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid request")
    except Exception as e:
        logger.error("Error in get_multiple endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/currency/{base}/{quote}", response_model=Dict[str, Any])
async def get_currency(base: str, quote: str = "USD"):
    """
    Получает курс валютной пары.
    
    Args:
        base: Базовая валюта (например, 'EUR', 'RUB')
        quote: Котируемая валюта (по умолчанию 'USD')
    
    Returns:
        Информация о курсе валютной пары
    """
    try:
        return get_currency_rate(base, quote)
    except ValueError as e:
        logger.error("Currency pair not found %s/%s: %s", base, quote, e, exc_info=True)
        raise HTTPException(status_code=404, detail="Currency pair not found")
    except Exception as e:
        logger.error("Error in get_currency endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/crypto/{symbol}", response_model=Dict[str, Any])
async def get_crypto(symbol: str):
    """
    Получает информацию о криптовалюте.
    
    Args:
        symbol: Символ криптовалюты (например, 'BTC-USD', 'ETH-USD')
    
    Returns:
        Информация о криптовалюте
    """
    try:
        return get_crypto_info(symbol)
    except ValueError as e:
        logger.error("Crypto not found %s: %s", symbol, e, exc_info=True)
        raise HTTPException(status_code=404, detail="Crypto not found")
    except Exception as e:
        logger.error("Error in get_crypto endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/index/{symbol}", response_model=Dict[str, Any])
async def get_index(symbol: str):
    """
    Получает информацию об индексе.
    
    Args:
        symbol: Символ индекса (например, '^GSPC' для S&P 500, '^DJI' для Dow Jones)
    
    Returns:
        Информация об индексе
    """
    try:
        return get_index_info(symbol)
    except ValueError as e:
        logger.error("Index not found %s: %s", symbol, e, exc_info=True)
        raise HTTPException(status_code=404, detail="Index not found")
    except Exception as e:
        logger.error("Error in get_index endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tickers/popular", response_model=List[str])
async def get_popular_tickers_list():
    """
    Получает список популярных тикеров из различных индексов и бирж.
    Включает S&P 500, NASDAQ 100, Dow Jones, и другие популярные акции.
    
    Returns:
        Список популярных тикеров
    """
    try:
        return get_popular_tickers()
    except Exception as e:
        logger.error("Error in get_popular_tickers endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/crypto/popular", response_model=List[str])
async def get_popular_cryptos_list():
    """
    Получает список популярных криптовалют.
    Формат тикеров: SYMBOL-USD (например, BTC-USD, ETH-USD)
    
    Returns:
        Список популярных криптовалют
    """
    try:
        return get_popular_cryptos()
    except Exception as e:
        logger.error("Error in get_popular_cryptos endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check для сервиса рыночных данных."""
    return {"status": "ok", "service": "market_data"}
