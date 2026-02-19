"""
ETF Data Router — Russian + International ETFs.

Prefix: /api/etf
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.services.etf_service import (
    moex_etf_list,
    etf_candles,
    POPULAR_INTL_ETFS,
)

router = APIRouter()


@router.get("/list")
async def list_etfs():
    """List Russian ETFs from MOEX TQTF board."""
    try:
        return await moex_etf_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candles/{ticker}")
async def get_candles(
    ticker: str,
    interval: int = Query(24, description="1,10,60,24(day),7(week),31(month)"),
    from_date: Optional[str] = Query(None, alias="from"),
    till_date: Optional[str] = Query(None, alias="till"),
    limit: int = Query(100),
):
    """Get OHLCV candles for a MOEX ETF."""
    try:
        return await etf_candles(ticker, interval, from_date, till_date, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular-international")
async def popular_international():
    """List popular international ETF tickers (use market-data API for prices)."""
    return {"tickers": POPULAR_INTL_ETFS, "note": "Use /api/market-data for price data"}


@router.get("/health")
async def health():
    return {"status": "ok", "service": "etf"}
