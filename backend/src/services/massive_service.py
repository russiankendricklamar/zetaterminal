"""
Massive (Stock Market API) Service — global tick + historical data.

Provides global stock data at tick level with WebSocket support.
Used for experiments with tick-level data, low-code/LLM agents.

Base URL: https://api.stockmarketapi.com/v1
Auth: query parameter `api_token`
"""

import logging
import re
from typing import Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.services.secrets_service import get_key_sync
from src.utils.http_client import get_session

logger = logging.getLogger(__name__)

MASSIVE_BASE = "https://api.stockmarketapi.com/v1"

_TICKER_RE = re.compile(r"^[A-Za-z0-9.\-]{1,20}$")


def _api_key() -> str:
    return get_key_sync("MASSIVE_API_KEY")


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not _TICKER_RE.match(symbol):
        raise ValueError(f"Invalid symbol: {symbol!r}")
    return symbol


async def _massive_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Make authenticated GET request to Massive API."""
    session = await get_session()
    url = f"{MASSIVE_BASE}{path}"
    req_params = {"api_token": _api_key()}
    if params:
        req_params.update(params)

    async with session.get(url, params=req_params) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"Massive API error {resp.status}: {text[:200]}")
        return await resp.json(content_type=None)


async def massive_quote(symbol: str) -> dict[str, Any]:
    """Get real-time quote for a global stock."""
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("massive", "quote", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _massive_get("/quote", {"symbol": symbol})

    quote_data = data.get("data", data)
    result = {
        "symbol": symbol,
        "price": float(quote_data.get("price", quote_data.get("last", 0))),
        "open": float(quote_data.get("open", 0)),
        "high": float(quote_data.get("high", 0)),
        "low": float(quote_data.get("low", 0)),
        "close": float(quote_data.get("close", quote_data.get("previous_close", 0))),
        "volume": int(quote_data.get("volume", 0)),
        "change": float(quote_data.get("change", 0)),
        "change_percent": float(quote_data.get("change_percent", quote_data.get("percent_change", 0))),
        "provider": "massive",
    }

    cache_set(cache_key, result, ttl_seconds=15)
    return result


async def massive_history(
    symbol: str,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, Any]:
    """
    Get historical OHLCV data for a global stock.

    Args:
        symbol: Stock ticker
        date_from: YYYY-MM-DD
        date_to: YYYY-MM-DD
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("massive", "hist", symbol, date_from, date_to)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {"symbol": symbol}
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to

    data = await _massive_get("/history", params)

    history_data = data.get("data", data)
    candles = []
    if isinstance(history_data, list):
        candles = [
            {
                "date": item.get("date", ""),
                "open": float(item.get("open", 0)),
                "high": float(item.get("high", 0)),
                "low": float(item.get("low", 0)),
                "close": float(item.get("close", 0)),
                "volume": int(item.get("volume", 0)),
            }
            for item in history_data
        ]

    result = {
        "success": True,
        "symbol": symbol,
        "candles": candles,
        "metadata": {
            "n_observations": len(candles),
            "start_date": candles[0]["date"] if candles else None,
            "end_date": candles[-1]["date"] if candles else None,
            "provider": "massive",
        },
    }

    cache_set(cache_key, result, ttl_seconds=300)
    return result


async def massive_search(query: str) -> list[dict[str, Any]]:
    """Search for stock symbols."""
    cache_key = make_cache_key("massive", "search", query)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _massive_get("/search", {"query": query})

    results = [
        {
            "symbol": item.get("symbol", ""),
            "name": item.get("name", ""),
            "exchange": item.get("exchange", ""),
            "type": item.get("type", ""),
            "provider": "massive",
        }
        for item in data.get("data", data) if isinstance(data.get("data", data), list)
    ]

    cache_set(cache_key, results, ttl_seconds=3600)
    return results
