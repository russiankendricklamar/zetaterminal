"""
Marketstack Service — lightweight EOD market data.

Provides global equities and indices end-of-day data.
Used as a lightweight REST API for EOD quotes in small services.

Base URL: https://api.marketstack.com/v1 (free: HTTP only)
Auth: query parameter `access_key`
Free tier: 100 requests/month, EOD only
"""

import logging
import re
from typing import Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.services.secrets_service import get_key_sync
from src.utils.http_client import get_session

logger = logging.getLogger(__name__)

# Free tier uses HTTP, paid uses HTTPS
MARKETSTACK_BASE = "http://api.marketstack.com/v1"

_TICKER_RE = re.compile(r"^[A-Za-z0-9.\-]{1,20}$")


def _api_key() -> str:
    return get_key_sync("MARKETSTACK_API_KEY")


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not _TICKER_RE.match(symbol):
        raise ValueError(f"Invalid symbol: {symbol!r}")
    return symbol


async def _ms_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Make authenticated GET request to Marketstack."""
    session = await get_session()
    url = f"{MARKETSTACK_BASE}{path}"
    req_params = {"access_key": _api_key()}
    if params:
        req_params.update(params)

    async with session.get(url, params=req_params) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"Marketstack error {resp.status}: {text[:200]}")
        return await resp.json(content_type=None)


async def marketstack_eod(
    symbol: str,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """
    Get end-of-day data for a symbol.

    Args:
        symbol: Ticker (AAPL, MSFT, TSLA)
        date_from: YYYY-MM-DD
        date_to: YYYY-MM-DD
        limit: Max results (default 100, max 1000)
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("ms", "eod", symbol, date_from, date_to, limit)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {"symbols": symbol, "limit": min(limit, 1000)}
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to

    data = await _ms_get("/eod", params)

    candles = [
        {
            "date": item.get("date", "")[:10],
            "open": item.get("open", 0),
            "high": item.get("high", 0),
            "low": item.get("low", 0),
            "close": item.get("close", 0),
            "volume": item.get("volume", 0),
            "adj_close": item.get("adj_close", 0),
            "exchange": item.get("exchange", ""),
        }
        for item in data.get("data", [])
    ]

    result = {
        "success": True,
        "symbol": symbol,
        "candles": candles,
        "metadata": {
            "n_observations": len(candles),
            "start_date": candles[-1]["date"] if candles else None,
            "end_date": candles[0]["date"] if candles else None,
            "provider": "marketstack",
        },
        "pagination": data.get("pagination", {}),
    }

    cache_set(cache_key, result, ttl_seconds=3600)
    return result


async def marketstack_eod_latest(symbols: list[str]) -> dict[str, Any]:
    """Get latest EOD data for multiple symbols."""
    validated = [_validate_symbol(s) for s in symbols]
    if len(validated) > 50:
        raise ValueError("Maximum 50 symbols per request")

    symbols_str = ",".join(validated)
    cache_key = make_cache_key("ms", "latest", symbols_str)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _ms_get("/eod/latest", {"symbols": symbols_str})

    quotes = [
        {
            "symbol": item.get("symbol", ""),
            "date": item.get("date", "")[:10],
            "open": item.get("open", 0),
            "high": item.get("high", 0),
            "low": item.get("low", 0),
            "close": item.get("close", 0),
            "volume": item.get("volume", 0),
            "exchange": item.get("exchange", ""),
        }
        for item in data.get("data", [])
    ]

    result = {
        "success": True,
        "quotes": quotes,
        "total": len(quotes),
        "provider": "marketstack",
    }

    cache_set(cache_key, result, ttl_seconds=300)
    return result


async def marketstack_tickers(search: str | None = None, limit: int = 50) -> dict[str, Any]:
    """Search or list available tickers on Marketstack."""
    cache_key = make_cache_key("ms", "tickers", search, limit)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {"limit": min(limit, 1000)}
    if search:
        params["search"] = search

    data = await _ms_get("/tickers", params)

    tickers = [
        {
            "symbol": item.get("symbol", ""),
            "name": item.get("name", ""),
            "exchange": item.get("stock_exchange", {}).get("acronym", ""),
            "country": item.get("stock_exchange", {}).get("country", ""),
        }
        for item in data.get("data", [])
    ]

    result = {"success": True, "tickers": tickers, "total": len(tickers)}
    cache_set(cache_key, result, ttl_seconds=3600)
    return result
