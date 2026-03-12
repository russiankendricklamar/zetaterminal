"""
Market Feeds Router — Alpha Vantage, Twelve Data, Polygon.io

Prefix: /api/market-feeds
"""


from fastapi import APIRouter, Query, Request

from src.middleware.rate_limit import limiter
from src.services.market_feeds_service import (
    alpha_vantage_forex,
    alpha_vantage_quote,
    alpha_vantage_technicals,
    alpha_vantage_time_series,
    polygon_aggregates,
    polygon_news,
    polygon_options_chain,
    polygon_ticker_details,
    twelve_data_forex_pairs,
    twelve_data_quote,
    twelve_data_time_series,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


# ─── Alpha Vantage ────────────────────────────────────────────────────────────

@router.get("/alpha-vantage/quote")
@limiter.limit("5/minute")
@service_endpoint("Av Quote")
async def av_quote(request: Request, symbol: str = Query(..., description="Ticker symbol")):
    """Real-time quote from Alpha Vantage."""
    return await alpha_vantage_quote(symbol)
@router.get("/alpha-vantage/time-series")
@limiter.limit("5/minute")
async def av_time_series(
    request: Request,
    symbol: str = Query(...),
    interval: str = Query("daily", description="daily | weekly | monthly"),
    outputsize: str = Query("compact", description="compact | full"),
):
    """Historical OHLCV from Alpha Vantage."""
    return await alpha_vantage_time_series(symbol, interval, outputsize)
@router.get("/alpha-vantage/forex")
@limiter.limit("5/minute")
@service_endpoint("Av Forex")
async def av_forex(
    request: Request,
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
):
    """FX exchange rate from Alpha Vantage."""
    return await alpha_vantage_forex(from_currency, to_currency)
@router.get("/alpha-vantage/technicals")
@limiter.limit("5/minute")
@service_endpoint("Av Technicals")
async def av_technicals(
    request: Request,
    symbol: str = Query(...),
    indicator: str = Query("SMA", description="SMA, EMA, RSI, MACD, etc."),
    interval: str = Query("daily"),
    time_period: int = Query(20),
    series_type: str = Query("close"),
):
    """Technical indicators from Alpha Vantage."""
    return await alpha_vantage_technicals(symbol, indicator, interval, time_period, series_type)
# ─── Twelve Data ──────────────────────────────────────────────────────────────

@router.get("/twelve-data/quote")
@limiter.limit("20/minute")
@service_endpoint("Td Quote")
async def td_quote(request: Request, symbol: str = Query(...)):
    """Real-time quote from Twelve Data."""
    return await twelve_data_quote(symbol)
@router.get("/twelve-data/time-series")
@limiter.limit("20/minute")
async def td_time_series(
    request: Request,
    symbol: str = Query(...),
    interval: str = Query("1day"),
    outputsize: int = Query(30),
):
    """Historical time series from Twelve Data."""
    return await twelve_data_time_series(symbol, interval, outputsize)
@router.get("/twelve-data/forex-pairs")
@limiter.limit("20/minute")
@service_endpoint("Td Forex Pairs")
async def td_forex_pairs(request: Request):
    """Available forex pairs from Twelve Data."""
    return await twelve_data_forex_pairs()
# ─── Polygon.io ───────────────────────────────────────────────────────────────

@router.get("/polygon/ticker/{ticker}")
@limiter.limit("20/minute")
@service_endpoint("Poly Ticker")
async def poly_ticker(request: Request, ticker: str):
    """Ticker details from Polygon."""
    return await polygon_ticker_details(ticker)
@router.get("/polygon/aggs/{ticker}")
@limiter.limit("20/minute")
async def poly_aggs(
    request: Request,
    ticker: str,
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    timespan: str = Query("day"),
    multiplier: int = Query(1),
):
    """Aggregated OHLCV bars from Polygon."""
    return await polygon_aggregates(ticker, from_date, to_date, timespan, multiplier)
@router.get("/polygon/options/{ticker}")
@limiter.limit("20/minute")
@service_endpoint("Poly Options")
async def poly_options(
    request: Request,
    ticker: str,
    expiration_date: str | None = Query(None),
    strike_price: float | None = Query(None),
    contract_type: str | None = Query(None),
    limit: int = Query(50),
):
    """Options chain from Polygon."""
    return await polygon_options_chain(ticker, expiration_date, strike_price, contract_type, limit)
@router.get("/polygon/news")
@limiter.limit("20/minute")
@service_endpoint("Poly News")
async def poly_news(
    request: Request,
    ticker: str | None = Query(None),
    limit: int = Query(20),
):
    """Ticker news from Polygon."""
    return await polygon_news(ticker, limit)
@router.get("/health")
async def health():
    return {"status": "ok", "service": "market-feeds"}
