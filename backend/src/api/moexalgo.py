"""
MOEX ISS Router — Russian stock market data.

Prefix: /api/moexalgo
"""


from fastapi import APIRouter, Query

from src.services.moexalgo_service import (
    moex_candles,
    moex_futures_oi,
    moex_index,
    moex_orderbook,
    moex_securities,
    moex_trades,
)

from src.utils.error_handler import service_endpoint

router = APIRouter()


@router.get("/securities")
@service_endpoint("Securities")
async def securities(
    board: str = Query("TQBR", description="Board ID (TQBR=shares, TQTF=ETFs)"),
    market: str = Query("shares"),
    engine: str = Query("stock"),
    limit: int = Query(100),
):
    """List securities on a MOEX board."""
    return await moex_securities(board, market, engine, limit)
@router.get("/candles/{ticker}")
@service_endpoint("Candles")
async def candles(
    ticker: str,
    board: str = Query("TQBR"),
    market: str = Query("shares"),
    engine: str = Query("stock"),
    interval: int = Query(24, description="Candle interval: 1,10,60,24(day),7(week),31(month)"),
    from_date: str | None = Query(None, alias="from"),
    till_date: str | None = Query(None, alias="till"),
    limit: int = Query(100),
):
    """Get OHLCV candles for a ticker."""
    return await moex_candles(ticker, board, market, engine, interval, from_date, till_date, limit)
@router.get("/orderbook/{ticker}")
@service_endpoint("Orderbook")
async def orderbook(
    ticker: str,
    board: str = Query("TQBR"),
    market: str = Query("shares"),
    engine: str = Query("stock"),
):
    """Get order book for a ticker."""
    return await moex_orderbook(ticker, board, market, engine)
@router.get("/trades/{ticker}")
@service_endpoint("Trades")
async def trades(
    ticker: str,
    board: str = Query("TQBR"),
    market: str = Query("shares"),
    engine: str = Query("stock"),
    limit: int = Query(50),
):
    """Get recent trades for a ticker."""
    return await moex_trades(ticker, board, market, engine, limit)
@router.get("/index/{index_id}")
@service_endpoint("Index Analytics")
async def index_analytics(
    index_id: str,
    limit: int = Query(100),
    from_date: str | None = Query(None, alias="from"),
    till_date: str | None = Query(None, alias="till"),
):
    """Get MOEX index analytics (IMOEX, RTSI, etc.)."""
    return await moex_index(index_id, limit, from_date, till_date)
@router.get("/futures/oi/{ticker}")
@service_endpoint("Futures Oi")
async def futures_oi(ticker: str):
    """Get futures open interest data."""
    return await moex_futures_oi(ticker)
@router.get("/health")
async def health():
    return {"status": "ok", "service": "moexalgo"}
