"""
IEX Cloud Market Data Service — US equities focused.

IEX Cloud provides stock quotes, historical prices, company info,
key stats, and batch requests for US equities (partial FX/crypto).

Used for US-centric dashboard and portfolio tracker.

Base URL: https://cloud.iexapis.com/stable
Auth: query parameter `token=API_KEY`
"""

import logging
import re
from typing import Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.services.secrets_service import get_key_sync
from src.utils.http_client import get_session

logger = logging.getLogger(__name__)

IEX_BASE = "https://cloud.iexapis.com/stable"

_TICKER_RE = re.compile(r"^[A-Za-z0-9.\-]{1,20}$")


def _api_key() -> str:
    return get_key_sync("IEX_CLOUD_API_KEY")


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not _TICKER_RE.match(symbol):
        raise ValueError(f"Invalid symbol format: {symbol!r}")
    return symbol


async def _iex_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Make authenticated GET request to IEX Cloud API."""
    session = await get_session()
    url = f"{IEX_BASE}{path}"
    req_params = {"token": _api_key()}
    if params:
        req_params.update(params)

    async with session.get(url, params=req_params) as resp:
        if resp.status == 402:
            raise RuntimeError("IEX Cloud: insufficient credits or invalid plan")
        if resp.status == 403:
            raise RuntimeError("IEX Cloud API key invalid")
        if resp.status == 404:
            raise ValueError("Symbol not found on IEX Cloud")
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"IEX Cloud error {resp.status}: {text[:200]}")
        return await resp.json(content_type=None)


async def iex_quote(symbol: str) -> dict[str, Any]:
    """
    Get real-time quote for a US stock.

    Returns: price, change, changePercent, volume, marketCap, etc.
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("iex", "quote", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _iex_get(f"/stock/{symbol}/quote")

    result = {
        "symbol": data.get("symbol", symbol),
        "name": data.get("companyName", ""),
        "price": data.get("latestPrice", 0),
        "change": data.get("change", 0),
        "change_percent": data.get("changePercent", 0),
        "volume": data.get("volume", 0),
        "market_cap": data.get("marketCap", 0),
        "pe_ratio": data.get("peRatio"),
        "52_week_high": data.get("week52High"),
        "52_week_low": data.get("week52Low"),
        "avg_volume": data.get("avgTotalVolume", 0),
        "open": data.get("open", 0),
        "high": data.get("high", 0),
        "low": data.get("low", 0),
        "previous_close": data.get("previousClose", 0),
        "latest_time": data.get("latestTime", ""),
        "provider": "iex_cloud",
    }

    cache_set(cache_key, result, ttl_seconds=15)
    return result


async def iex_historical(
    symbol: str,
    range_period: str = "1m",
) -> dict[str, Any]:
    """
    Get historical daily prices for a US stock.

    range_period: 5d, 1m, 3m, 6m, ytd, 1y, 2y, 5y, max
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("iex", "hist", symbol, range_period)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _iex_get(f"/stock/{symbol}/chart/{range_period}")

    if not isinstance(data, list):
        raise ValueError(f"Unexpected response format for {symbol}")

    candles = [
        {
            "date": item.get("date", ""),
            "open": item.get("open", 0),
            "high": item.get("high", 0),
            "low": item.get("low", 0),
            "close": item.get("close", 0),
            "volume": item.get("volume", 0),
        }
        for item in data
        if item.get("close") is not None
    ]

    result = {
        "success": True,
        "symbol": symbol,
        "range": range_period,
        "candles": candles,
        "metadata": {
            "n_observations": len(candles),
            "start_date": candles[0]["date"] if candles else None,
            "end_date": candles[-1]["date"] if candles else None,
            "provider": "iex_cloud",
        },
    }

    cache_set(cache_key, result, ttl_seconds=300)
    return result


async def iex_company(symbol: str) -> dict[str, Any]:
    """Get company information for a US stock."""
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("iex", "company", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _iex_get(f"/stock/{symbol}/company")

    result = {
        "symbol": data.get("symbol", symbol),
        "name": data.get("companyName", ""),
        "exchange": data.get("exchange", ""),
        "industry": data.get("industry", ""),
        "sector": data.get("sector", ""),
        "description": data.get("description", ""),
        "ceo": data.get("CEO", ""),
        "employees": data.get("employees", 0),
        "website": data.get("website", ""),
        "country": data.get("country", ""),
        "provider": "iex_cloud",
    }

    cache_set(cache_key, result, ttl_seconds=3600)
    return result


async def iex_key_stats(symbol: str) -> dict[str, Any]:
    """Get key financial statistics for a US stock."""
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("iex", "stats", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _iex_get(f"/stock/{symbol}/stats")

    result = {
        "symbol": symbol,
        "market_cap": data.get("marketcap", 0),
        "pe_ratio": data.get("peRatio"),
        "beta": data.get("beta"),
        "52_week_high": data.get("week52high"),
        "52_week_low": data.get("week52low"),
        "dividend_yield": data.get("dividendYield"),
        "eps_ttm": data.get("ttmEPS"),
        "revenue_ttm": data.get("revenue"),
        "profit_margin": data.get("profitMargin"),
        "avg_volume_30d": data.get("avg30Volume"),
        "shares_outstanding": data.get("sharesOutstanding"),
        "provider": "iex_cloud",
    }

    cache_set(cache_key, result, ttl_seconds=300)
    return result


async def iex_batch(symbols: list[str], types: str = "quote") -> dict[str, Any]:
    """
    Batch request for multiple symbols.

    types: comma-separated — quote, chart, company, stats
    """
    validated = [_validate_symbol(s) for s in symbols]
    if len(validated) > 100:
        raise ValueError("Maximum 100 symbols per batch request")

    symbols_str = ",".join(validated)
    cache_key = make_cache_key("iex", "batch", symbols_str, types)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _iex_get("/stock/market/batch", {
        "symbols": symbols_str,
        "types": types,
    })

    result = {
        "success": True,
        "data": data,
        "symbols_requested": len(validated),
        "provider": "iex_cloud",
    }

    cache_set(cache_key, result, ttl_seconds=30)
    return result
