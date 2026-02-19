"""
MOEX ISS Router — Russian stock market data.

Prefix: /api/moexalgo
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.services.moexalgo_service import (
    moex_securities,
    moex_candles,
    moex_orderbook,
    moex_trades,
    moex_index,
    moex_futures_oi,
)

router = APIRouter()


@router.get("/securities")
async def securities(
    board: str = Query("TQBR", description="Board ID (TQBR=shares, TQTF=ETFs)"),
    market: str = Query("shares"),
    engine: str = Query("stock"),
    limit: int = Query(100),
):
    """List securities on a MOEX board."""
    try:
        return await moex_securities(board, market, engine, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candles/{ticker}")
async def candles(
    ticker: str,
    board: str = Query("TQBR"),
    market: str = Query("shares"),
    engine: str = Query("stock"),
    interval: int = Query(24, description="Candle interval: 1,10,60,24(day),7(week),31(month)"),
    from_date: Optional[str] = Query(None, alias="from"),
    till_date: Optional[str] = Query(None, alias="till"),
    limit: int = Query(100),
):
    """Get OHLCV candles for a ticker."""
    try:
        return await moex_candles(ticker, board, market, engine, interval, from_date, till_date, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orderbook/{ticker}")
async def orderbook(
    ticker: str,
    board: str = Query("TQBR"),
    market: str = Query("shares"),
    engine: str = Query("stock"),
):
    """Get order book for a ticker."""
    try:
        return await moex_orderbook(ticker, board, market, engine)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/{ticker}")
async def trades(
    ticker: str,
    board: str = Query("TQBR"),
    market: str = Query("shares"),
    engine: str = Query("stock"),
    limit: int = Query(50),
):
    """Get recent trades for a ticker."""
    try:
        return await moex_trades(ticker, board, market, engine, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index/{index_id}")
async def index_analytics(
    index_id: str,
    limit: int = Query(100),
    from_date: Optional[str] = Query(None, alias="from"),
    till_date: Optional[str] = Query(None, alias="till"),
):
    """Get MOEX index analytics (IMOEX, RTSI, etc.)."""
    try:
        return await moex_index(index_id, limit, from_date, till_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/futures/oi/{ticker}")
async def futures_oi(ticker: str):
    """Get futures open interest data."""
    try:
        return await moex_futures_oi(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok", "service": "moexalgo"}
