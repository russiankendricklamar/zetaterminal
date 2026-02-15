"""
Market Feeds Service — Alpha Vantage, Twelve Data, Polygon.io

Proxies real-time and historical market data from three providers.
"""

import os
from typing import Optional, Dict, Any, List
from src.utils.http_client import get_session

from src.services.cache_service import cache_get, cache_set, make_cache_key

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"

TWELVE_DATA_KEY = os.getenv("TWELVE_DATA_API_KEY", "")
TWELVE_DATA_BASE = "https://api.twelvedata.com"

POLYGON_KEY = os.getenv("POLYGON_API_KEY", "")
POLYGON_BASE = "https://api.polygon.io"


# ─── Alpha Vantage ────────────────────────────────────────────────────────────

async def alpha_vantage_quote(symbol: str) -> Dict[str, Any]:
    """Get real-time quote for a symbol."""
    key = make_cache_key("av", "quote", symbol)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_KEY,
    }
    session = await get_session()
    async with session.get(ALPHA_VANTAGE_BASE, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    quote_raw = data.get("Global Quote", {})
    result = {
        "symbol": quote_raw.get("01. symbol", symbol),
        "price": float(quote_raw.get("05. price", 0)),
        "open": float(quote_raw.get("02. open", 0)),
        "high": float(quote_raw.get("03. high", 0)),
        "low": float(quote_raw.get("04. low", 0)),
        "volume": int(quote_raw.get("06. volume", 0)),
        "latest_trading_day": quote_raw.get("07. latest trading day", ""),
        "previous_close": float(quote_raw.get("08. previous close", 0)),
        "change": float(quote_raw.get("09. change", 0)),
        "change_percent": quote_raw.get("10. change percent", "0%"),
        "provider": "alpha_vantage",
    }
    cache_set(key, result, ttl_seconds=60)
    return result


async def alpha_vantage_time_series(
    symbol: str,
    interval: str = "daily",
    outputsize: str = "compact"
) -> Dict[str, Any]:
    """Get historical time series data."""
    key = make_cache_key("av", "ts", symbol, interval, outputsize)
    cached = cache_get(key)
    if cached is not None:
        return cached

    func_map = {
        "daily": "TIME_SERIES_DAILY",
        "weekly": "TIME_SERIES_WEEKLY",
        "monthly": "TIME_SERIES_MONTHLY",
    }
    function = func_map.get(interval, "TIME_SERIES_DAILY")
    ts_key_map = {
        "daily": "Time Series (Daily)",
        "weekly": "Weekly Time Series",
        "monthly": "Monthly Time Series",
    }
    ts_key = ts_key_map.get(interval, "Time Series (Daily)")

    params = {
        "function": function,
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": ALPHA_VANTAGE_KEY,
    }
    session = await get_session()
    async with session.get(ALPHA_VANTAGE_BASE, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    raw_series = data.get(ts_key, {})
    series = []
    for date_str, vals in raw_series.items():
        series.append({
            "date": date_str,
            "open": float(vals.get("1. open", 0)),
            "high": float(vals.get("2. high", 0)),
            "low": float(vals.get("3. low", 0)),
            "close": float(vals.get("4. close", 0)),
            "volume": int(vals.get("5. volume", 0)),
        })

    result = {"symbol": symbol, "interval": interval, "series": series, "provider": "alpha_vantage"}
    cache_set(key, result, ttl_seconds=300)
    return result


async def alpha_vantage_forex(from_currency: str, to_currency: str) -> Dict[str, Any]:
    """Get real-time FX exchange rate."""
    key = make_cache_key("av", "fx", from_currency, to_currency)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_currency,
        "to_currency": to_currency,
        "apikey": ALPHA_VANTAGE_KEY,
    }
    session = await get_session()
    async with session.get(ALPHA_VANTAGE_BASE, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    raw = data.get("Realtime Currency Exchange Rate", {})
    result = {
        "from": raw.get("1. From_Currency Code", from_currency),
        "to": raw.get("3. To_Currency Code", to_currency),
        "rate": float(raw.get("5. Exchange Rate", 0)),
        "last_refreshed": raw.get("6. Last Refreshed", ""),
        "provider": "alpha_vantage",
    }
    cache_set(key, result, ttl_seconds=120)
    return result


async def alpha_vantage_technicals(
    symbol: str,
    indicator: str = "SMA",
    interval: str = "daily",
    time_period: int = 20,
    series_type: str = "close"
) -> Dict[str, Any]:
    """Get technical indicators (SMA, EMA, RSI, MACD, etc.)."""
    key = make_cache_key("av", "tech", symbol, indicator, interval, time_period)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {
        "function": indicator.upper(),
        "symbol": symbol,
        "interval": interval,
        "time_period": time_period,
        "series_type": series_type,
        "apikey": ALPHA_VANTAGE_KEY,
    }
    session = await get_session()
    async with session.get(ALPHA_VANTAGE_BASE, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    # Find the technical analysis key in the response
    ta_key = None
    for k in data:
        if "Technical Analysis" in k:
            ta_key = k
            break

    raw_data = data.get(ta_key, {}) if ta_key else {}
    points = []
    for date_str, vals in raw_data.items():
        point = {"date": date_str}
        for vk, vv in vals.items():
            point[vk] = float(vv)
        points.append(point)

    result = {
        "symbol": symbol,
        "indicator": indicator,
        "interval": interval,
        "time_period": time_period,
        "data": points,
        "provider": "alpha_vantage",
    }
    cache_set(key, result, ttl_seconds=300)
    return result


# ─── Twelve Data ──────────────────────────────────────────────────────────────

async def twelve_data_quote(symbol: str) -> Dict[str, Any]:
    """Get real-time quote from Twelve Data."""
    key = make_cache_key("td", "quote", symbol)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {"symbol": symbol, "apikey": TWELVE_DATA_KEY}
    session = await get_session()
    async with session.get(f"{TWELVE_DATA_BASE}/quote", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = {
        "symbol": data.get("symbol", symbol),
        "name": data.get("name", ""),
        "exchange": data.get("exchange", ""),
        "price": float(data.get("close", 0)),
        "open": float(data.get("open", 0)),
        "high": float(data.get("high", 0)),
        "low": float(data.get("low", 0)),
        "volume": int(data.get("volume", 0)),
        "previous_close": float(data.get("previous_close", 0)),
        "change": float(data.get("change", 0)),
        "percent_change": float(data.get("percent_change", 0)),
        "datetime": data.get("datetime", ""),
        "provider": "twelve_data",
    }
    cache_set(key, result, ttl_seconds=60)
    return result


async def twelve_data_time_series(
    symbol: str,
    interval: str = "1day",
    outputsize: int = 30
) -> Dict[str, Any]:
    """Get historical time series from Twelve Data."""
    key = make_cache_key("td", "ts", symbol, interval, outputsize)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": TWELVE_DATA_KEY,
    }
    session = await get_session()
    async with session.get(f"{TWELVE_DATA_BASE}/time_series", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    values = data.get("values", [])
    series = []
    for v in values:
        series.append({
            "date": v.get("datetime", ""),
            "open": float(v.get("open", 0)),
            "high": float(v.get("high", 0)),
            "low": float(v.get("low", 0)),
            "close": float(v.get("close", 0)),
            "volume": int(v.get("volume", 0)),
        })

    result = {"symbol": symbol, "interval": interval, "series": series, "provider": "twelve_data"}
    cache_set(key, result, ttl_seconds=300)
    return result


async def twelve_data_forex_pairs() -> List[Dict[str, str]]:
    """Get available forex pairs."""
    key = make_cache_key("td", "forex_pairs")
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {"apikey": TWELVE_DATA_KEY}
    session = await get_session()
    async with session.get(f"{TWELVE_DATA_BASE}/forex_pairs", params=params) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = data.get("data", [])
    cache_set(key, result, ttl_seconds=86400)
    return result


# ─── Polygon.io ───────────────────────────────────────────────────────────────

async def polygon_ticker_details(ticker: str) -> Dict[str, Any]:
    """Get ticker details from Polygon."""
    key = make_cache_key("poly", "ticker", ticker)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers = {"Authorization": f"Bearer {POLYGON_KEY}"}
    session = await get_session()
    async with session.get(
        f"{POLYGON_BASE}/v3/reference/tickers/{ticker}",
        headers=headers
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = data.get("results", {})
    result["provider"] = "polygon"
    cache_set(key, result, ttl_seconds=3600)
    return result


async def polygon_aggregates(
    ticker: str,
    from_date: str,
    to_date: str,
    timespan: str = "day",
    multiplier: int = 1
) -> Dict[str, Any]:
    """Get aggregated bars from Polygon."""
    key = make_cache_key("poly", "aggs", ticker, from_date, to_date, timespan)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers = {"Authorization": f"Bearer {POLYGON_KEY}"}
    url = f"{POLYGON_BASE}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
    session = await get_session()
    async with session.get(url, headers=headers) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    results_raw = data.get("results", [])
    series = []
    for bar in results_raw:
        series.append({
            "timestamp": bar.get("t", 0),
            "open": bar.get("o", 0),
            "high": bar.get("h", 0),
            "low": bar.get("l", 0),
            "close": bar.get("c", 0),
            "volume": bar.get("v", 0),
            "vwap": bar.get("vw", 0),
            "num_transactions": bar.get("n", 0),
        })

    result = {
        "ticker": ticker,
        "results_count": data.get("resultsCount", 0),
        "series": series,
        "provider": "polygon",
    }
    cache_set(key, result, ttl_seconds=300)
    return result


async def polygon_options_chain(
    ticker: str,
    expiration_date: Optional[str] = None,
    strike_price: Optional[float] = None,
    contract_type: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """Get options chain from Polygon."""
    key = make_cache_key("poly", "options", ticker, expiration_date, strike_price, contract_type)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers = {"Authorization": f"Bearer {POLYGON_KEY}"}
    params: Dict[str, Any] = {
        "underlying_ticker": ticker,
        "limit": limit,
    }
    if expiration_date:
        params["expiration_date"] = expiration_date
    if strike_price:
        params["strike_price"] = strike_price
    if contract_type:
        params["contract_type"] = contract_type

    session = await get_session()
    async with session.get(
        f"{POLYGON_BASE}/v3/reference/options/contracts",
        headers=headers,
        params=params
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = {
        "ticker": ticker,
        "contracts": data.get("results", []),
        "provider": "polygon",
    }
    cache_set(key, result, ttl_seconds=300)
    return result


async def polygon_news(
    ticker: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Get ticker news from Polygon."""
    key = make_cache_key("poly", "news", ticker or "all", limit)
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers = {"Authorization": f"Bearer {POLYGON_KEY}"}
    params: Dict[str, Any] = {"limit": limit}
    if ticker:
        params["ticker"] = ticker

    session = await get_session()
    async with session.get(
        f"{POLYGON_BASE}/v2/reference/news",
        headers=headers,
        params=params
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    result = data.get("results", [])
    cache_set(key, result, ttl_seconds=120)
    return result
