"""
MOEX ISS API Service — Russian stock market data.

Public API (no key required): https://iss.moex.com/iss
"""

from typing import Optional, Dict, Any, List

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.utils.http_client import get_session

MOEX_BASE = "https://iss.moex.com/iss"


async def moex_securities(
    board: str = "TQBR",
    market: str = "shares",
    engine: str = "stock",
    limit: int = 100,
) -> Dict[str, Any]:
    """Get list of securities from MOEX board."""
    key = make_cache_key("moex", "securities", engine, market, board, limit)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{MOEX_BASE}/engines/{engine}/markets/{market}/boards/{board}/securities.json"
    params = {"iss.meta": "off", "iss.only": "securities,marketdata", "securities.columns": "SECID,SHORTNAME,ISIN,LOTSIZE,PREVPRICE,CURRENCYID", "marketdata.columns": "SECID,LAST,OPEN,HIGH,LOW,VOLTODAY,VALTODAY,CHANGE,CHANGEPCT,UPDATETIME", "start": 0}

    session = await get_session()
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    sec_cols = data.get("securities", {}).get("columns", [])
    sec_rows = data.get("securities", {}).get("data", [])
    md_cols = data.get("marketdata", {}).get("columns", [])
    md_rows = data.get("marketdata", {}).get("data", [])

    securities_map = {}
    for row in sec_rows:
        item = dict(zip(sec_cols, row))
        securities_map[item.get("SECID", "")] = item

    securities = []
    for row in md_rows:
        md = dict(zip(md_cols, row))
        secid = md.get("SECID", "")
        sec = securities_map.get(secid, {})
        securities.append({
            "secid": secid,
            "name": sec.get("SHORTNAME", ""),
            "isin": sec.get("ISIN", ""),
            "lot_size": sec.get("LOTSIZE", 1),
            "currency": sec.get("CURRENCYID", "SUR"),
            "prev_price": sec.get("PREVPRICE"),
            "last": md.get("LAST"),
            "open": md.get("OPEN"),
            "high": md.get("HIGH"),
            "low": md.get("LOW"),
            "volume": md.get("VOLTODAY"),
            "value": md.get("VALTODAY"),
            "change": md.get("CHANGE"),
            "change_pct": md.get("CHANGEPCT"),
            "update_time": md.get("UPDATETIME", ""),
        })

    result = {"board": board, "market": market, "engine": engine, "securities": securities[:limit], "provider": "moex_iss"}
    cache_set(key, result, ttl_seconds=60)
    return result


async def moex_candles(
    ticker: str,
    board: str = "TQBR",
    market: str = "shares",
    engine: str = "stock",
    interval: int = 24,
    from_date: Optional[str] = None,
    till_date: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Get OHLCV candles for a MOEX ticker."""
    key = make_cache_key("moex", "candles", ticker, board, interval, from_date, till_date, limit)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{MOEX_BASE}/engines/{engine}/markets/{market}/boards/{board}/securities/{ticker}/candles.json"
    params: Dict[str, Any] = {"iss.meta": "off", "interval": interval, "start": 0}
    if from_date:
        params["from"] = from_date
    if till_date:
        params["till"] = till_date

    session = await get_session()
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    cols = data.get("candles", {}).get("columns", [])
    rows = data.get("candles", {}).get("data", [])

    candles = []
    for row in rows[:limit]:
        c = dict(zip(cols, row))
        candles.append({
            "open": c.get("open"),
            "close": c.get("close"),
            "high": c.get("high"),
            "low": c.get("low"),
            "volume": c.get("value"),
            "begin": c.get("begin", ""),
            "end": c.get("end", ""),
        })

    result = {"ticker": ticker, "board": board, "interval": interval, "candles": candles, "provider": "moex_iss"}
    cache_set(key, result, ttl_seconds=120)
    return result


async def moex_orderbook(
    ticker: str,
    board: str = "TQBR",
    market: str = "shares",
    engine: str = "stock",
) -> Dict[str, Any]:
    """Get order book (bids/asks) for a MOEX ticker."""
    key = make_cache_key("moex", "orderbook", ticker, board)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{MOEX_BASE}/engines/{engine}/markets/{market}/boards/{board}/securities/{ticker}/orderbook.json"
    params = {"iss.meta": "off"}

    session = await get_session()
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    cols = data.get("orderbook", {}).get("columns", [])
    rows = data.get("orderbook", {}).get("data", [])

    bids = []
    asks = []
    for row in rows:
        entry = dict(zip(cols, row))
        item = {"price": entry.get("PRICE"), "quantity": entry.get("QUANTITY")}
        if entry.get("BUYSELL") == "B":
            bids.append(item)
        else:
            asks.append(item)

    result = {"ticker": ticker, "board": board, "bids": bids, "asks": asks, "provider": "moex_iss"}
    cache_set(key, result, ttl_seconds=15)
    return result


async def moex_trades(
    ticker: str,
    board: str = "TQBR",
    market: str = "shares",
    engine: str = "stock",
    limit: int = 50,
) -> Dict[str, Any]:
    """Get recent trades for a MOEX ticker."""
    key = make_cache_key("moex", "trades", ticker, board, limit)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{MOEX_BASE}/engines/{engine}/markets/{market}/boards/{board}/securities/{ticker}/trades.json"
    params = {"iss.meta": "off", "limit": limit, "reversed": 1}

    session = await get_session()
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    cols = data.get("trades", {}).get("columns", [])
    rows = data.get("trades", {}).get("data", [])

    trades = []
    for row in rows:
        t = dict(zip(cols, row))
        trades.append({
            "trade_no": t.get("TRADENO"),
            "time": t.get("TRADETIME", ""),
            "price": t.get("PRICE"),
            "quantity": t.get("QUANTITY"),
            "value": t.get("VALUE"),
            "side": t.get("BUYSELL", ""),
        })

    result = {"ticker": ticker, "board": board, "trades": trades, "provider": "moex_iss"}
    cache_set(key, result, ttl_seconds=15)
    return result


async def moex_index(
    index_id: str = "IMOEX",
    limit: int = 100,
    from_date: Optional[str] = None,
    till_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Get MOEX index analytics (IMOEX, RTSI, etc.)."""
    key = make_cache_key("moex", "index", index_id, limit, from_date)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{MOEX_BASE}/statistics/engines/stock/markets/index/analytics/{index_id}.json"
    params: Dict[str, Any] = {"iss.meta": "off", "limit": limit}
    if from_date:
        params["from"] = from_date
    if till_date:
        params["till"] = till_date

    session = await get_session()
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    cols = data.get("analytics", {}).get("columns", [])
    rows = data.get("analytics", {}).get("data", [])

    analytics = []
    for row in rows:
        a = dict(zip(cols, row))
        analytics.append(a)

    result = {"index_id": index_id, "analytics": analytics, "provider": "moex_iss"}
    cache_set(key, result, ttl_seconds=120)
    return result


async def moex_futures_oi(
    ticker: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """Get futures open interest from MOEX."""
    key = make_cache_key("moex", "futures_oi", ticker, limit)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{MOEX_BASE}/engines/futures/markets/forts/boards/RFUD/securities/{ticker}.json"
    params = {"iss.meta": "off", "iss.only": "securities,marketdata"}

    session = await get_session()
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    md_cols = data.get("marketdata", {}).get("columns", [])
    md_rows = data.get("marketdata", {}).get("data", [])

    futures_data = {}
    if md_rows:
        md = dict(zip(md_cols, md_rows[0]))
        futures_data = {
            "ticker": ticker,
            "last": md.get("LAST"),
            "open_interest": md.get("OPENPOSITION"),
            "oi_change": md.get("OPENPOSITIONCHANGE"),
            "volume": md.get("VOLTODAY"),
            "settlement_price": md.get("SETTLEMENTPRICE"),
        }

    result = {**futures_data, "provider": "moex_iss"}
    cache_set(key, result, ttl_seconds=60)
    return result
