"""
ETF Data Router — Russian + International ETFs.

Prefix: /api/etf
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.services.etf_service import (
    POPULAR_INTL_ETFS,
    etf_candles,
    moex_etf_list,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/list")
async def list_etfs():
    """List Russian ETFs from MOEX TQTF board."""
    try:
        return await moex_etf_list()
    except Exception as e:
        logger.error("ETF operation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/candles/{ticker}")
async def get_candles(
    ticker: str,
    interval: int = Query(24, description="1,10,60,24(day),7(week),31(month)"),
    from_date: str | None = Query(None, alias="from"),
    till_date: str | None = Query(None, alias="till"),
    limit: int = Query(100),
):
    """Get OHLCV candles for a MOEX ETF."""
    try:
        return await etf_candles(ticker, interval, from_date, till_date, limit)
    except Exception as e:
        logger.error("ETF operation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/popular-international")
async def popular_international():
    """List popular international ETF tickers (use market-data API for prices)."""
    return {"tickers": POPULAR_INTL_ETFS, "note": "Use /api/market-data for price data"}


@router.get("/health")
async def health():
    return {"status": "ok", "service": "etf"}
