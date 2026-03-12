"""
ETF Data Router — Russian + International ETFs.

Prefix: /api/etf
"""


from fastapi import APIRouter, Query, Request

from src.middleware.rate_limit import limiter
from src.services.etf_service import (
    POPULAR_INTL_ETFS,
    etf_candles,
    moex_etf_list,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


@router.get("/list")
@limiter.limit("30/minute")
@service_endpoint("List Etfs")
async def list_etfs(request: Request):
    """List Russian ETFs from MOEX TQTF board."""
    return await moex_etf_list()
@router.get("/candles/{ticker}")
@limiter.limit("30/minute")
async def get_candles(
    request: Request,
    ticker: str,
    interval: int = Query(24, description="1,10,60,24(day),7(week),31(month)"),
    from_date: str | None = Query(None, alias="from"),
    till_date: str | None = Query(None, alias="till"),
    limit: int = Query(100),
):
    """Get OHLCV candles for a MOEX ETF."""
    return await etf_candles(ticker, interval, from_date, till_date, limit)
@router.get("/popular-international")
@limiter.limit("30/minute")
@service_endpoint("Popular International")
async def popular_international(request: Request):
    """List popular international ETF tickers (use market-data API for prices)."""
    return {"tickers": POPULAR_INTL_ETFS, "note": "Use /api/market-data for price data"}


@router.get("/health")
async def health():
    return {"status": "ok", "service": "etf"}
