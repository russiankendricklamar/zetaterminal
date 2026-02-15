"""
Market Feeds Router — Alpha Vantage, Twelve Data, Polygon.io

Prefix: /api/market-feeds
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.services.market_feeds_service import (
    alpha_vantage_quote,
    alpha_vantage_time_series,
    alpha_vantage_forex,
    alpha_vantage_technicals,
    twelve_data_quote,
    twelve_data_time_series,
    twelve_data_forex_pairs,
    polygon_ticker_details,
    polygon_aggregates,
    polygon_options_chain,
    polygon_news,
)

router = APIRouter()


# ─── Alpha Vantage ────────────────────────────────────────────────────────────

@router.get("/alpha-vantage/quote")
async def av_quote(symbol: str = Query(..., description="Ticker symbol")):
    """Real-time quote from Alpha Vantage."""
    try:
        return await alpha_vantage_quote(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alpha-vantage/time-series")
async def av_time_series(
    symbol: str = Query(...),
    interval: str = Query("daily", description="daily | weekly | monthly"),
    outputsize: str = Query("compact", description="compact | full"),
):
    """Historical OHLCV from Alpha Vantage."""
    try:
        return await alpha_vantage_time_series(symbol, interval, outputsize)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alpha-vantage/forex")
async def av_forex(
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
):
    """FX exchange rate from Alpha Vantage."""
    try:
        return await alpha_vantage_forex(from_currency, to_currency)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alpha-vantage/technicals")
async def av_technicals(
    symbol: str = Query(...),
    indicator: str = Query("SMA", description="SMA, EMA, RSI, MACD, etc."),
    interval: str = Query("daily"),
    time_period: int = Query(20),
    series_type: str = Query("close"),
):
    """Technical indicators from Alpha Vantage."""
    try:
        return await alpha_vantage_technicals(symbol, indicator, interval, time_period, series_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Twelve Data ──────────────────────────────────────────────────────────────

@router.get("/twelve-data/quote")
async def td_quote(symbol: str = Query(...)):
    """Real-time quote from Twelve Data."""
    try:
        return await twelve_data_quote(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/twelve-data/time-series")
async def td_time_series(
    symbol: str = Query(...),
    interval: str = Query("1day"),
    outputsize: int = Query(30),
):
    """Historical time series from Twelve Data."""
    try:
        return await twelve_data_time_series(symbol, interval, outputsize)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/twelve-data/forex-pairs")
async def td_forex_pairs():
    """Available forex pairs from Twelve Data."""
    try:
        return await twelve_data_forex_pairs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Polygon.io ───────────────────────────────────────────────────────────────

@router.get("/polygon/ticker/{ticker}")
async def poly_ticker(ticker: str):
    """Ticker details from Polygon."""
    try:
        return await polygon_ticker_details(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/polygon/aggs/{ticker}")
async def poly_aggs(
    ticker: str,
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    timespan: str = Query("day"),
    multiplier: int = Query(1),
):
    """Aggregated OHLCV bars from Polygon."""
    try:
        return await polygon_aggregates(ticker, from_date, to_date, timespan, multiplier)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/polygon/options/{ticker}")
async def poly_options(
    ticker: str,
    expiration_date: Optional[str] = Query(None),
    strike_price: Optional[float] = Query(None),
    contract_type: Optional[str] = Query(None),
    limit: int = Query(50),
):
    """Options chain from Polygon."""
    try:
        return await polygon_options_chain(ticker, expiration_date, strike_price, contract_type, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/polygon/news")
async def poly_news(
    ticker: Optional[str] = Query(None),
    limit: int = Query(20),
):
    """Ticker news from Polygon."""
    try:
        return await polygon_news(ticker, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok", "service": "market-feeds"}
