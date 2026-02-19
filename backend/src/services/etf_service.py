"""
ETF Data Service — Russian ETFs via MOEX ISS, foreign ETFs via yfinance.

Combines MOEX TQTF board data with yfinance for international ETFs.
"""

from typing import Optional, Dict, Any, List

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.utils.http_client import get_session

MOEX_BASE = "https://iss.moex.com/iss"


async def moex_etf_list() -> Dict[str, Any]:
    """Get list of Russian ETFs from MOEX TQTF board."""
    key = make_cache_key("etf", "moex_list")
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{MOEX_BASE}/engines/stock/markets/shares/boards/TQTF/securities.json"
    params = {
        "iss.meta": "off",
        "iss.only": "securities,marketdata",
        "securities.columns": "SECID,SHORTNAME,ISIN,PREVPRICE,CURRENCYID",
        "marketdata.columns": "SECID,LAST,OPEN,HIGH,LOW,VOLTODAY,VALTODAY,CHANGE,CHANGEPCT,UPDATETIME",
    }

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

    etfs = []
    for row in md_rows:
        md = dict(zip(md_cols, row))
        secid = md.get("SECID", "")
        sec = securities_map.get(secid, {})
        etfs.append({
            "ticker": secid,
            "name": sec.get("SHORTNAME", ""),
            "isin": sec.get("ISIN", ""),
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
            "market": "MOEX",
        })

    result = {"etfs": etfs, "count": len(etfs), "provider": "moex_iss"}
    cache_set(key, result, ttl_seconds=60)
    return result


async def etf_candles(
    ticker: str,
    interval: int = 24,
    from_date: Optional[str] = None,
    till_date: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Get ETF candles from MOEX TQTF board."""
    key = make_cache_key("etf", "candles", ticker, interval, from_date, till_date, limit)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{MOEX_BASE}/engines/stock/markets/shares/boards/TQTF/securities/{ticker}/candles.json"
    params: Dict[str, Any] = {"iss.meta": "off", "interval": interval}
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

    result = {"ticker": ticker, "interval": interval, "candles": candles, "provider": "moex_iss"}
    cache_set(key, result, ttl_seconds=120)
    return result


# Popular international ETFs for quick reference
POPULAR_INTL_ETFS = [
    "SPY", "QQQ", "IWM", "VTI", "VOO", "VEA", "VWO", "EFA", "EEM",
    "GLD", "SLV", "TLT", "HYG", "LQD", "XLF", "XLE", "XLK", "XLV",
    "ARKK", "IBIT", "ETHA",
]
