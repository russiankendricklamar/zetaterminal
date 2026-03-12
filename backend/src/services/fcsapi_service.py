"""
FCS API Service — unified FX, crypto, and stock data.

Provides a unified layer for forex, crypto, and stock quotes.
Used for simple widgets and lightweight dashboards.

Base URL: https://fcsapi.com/api-v3
Auth: query parameter `access_key`
"""

import logging
import re
from typing import Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.services.secrets_service import get_key_sync
from src.utils.http_client import get_session

logger = logging.getLogger(__name__)

FCS_BASE = "https://fcsapi.com/api-v3"

_SYMBOL_RE = re.compile(r"^[A-Za-z0-9/.\-]{1,20}$")


def _api_key() -> str:
    return get_key_sync("FCS_API_KEY")


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not _SYMBOL_RE.match(symbol):
        raise ValueError(f"Invalid symbol: {symbol!r}")
    return symbol


async def _fcs_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Make authenticated GET request to FCS API."""
    session = await get_session()
    url = f"{FCS_BASE}{path}"
    req_params = {"access_key": _api_key()}
    if params:
        req_params.update(params)

    async with session.get(url, params=req_params) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"FCS API error {resp.status}: {text[:200]}")
        return await resp.json(content_type=None)


async def fcs_forex_latest(symbol: str) -> dict[str, Any]:
    """
    Get latest forex quote.

    Symbol format: EUR/USD, GBP/JPY, USD/RUB
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("fcs", "fx", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _fcs_get("/forex/latest", {"symbol": symbol})

    response = data.get("response", [])
    if not response:
        raise ValueError(f"No forex data for {symbol}")

    item = response[0] if isinstance(response, list) else response
    result = {
        "symbol": item.get("s", symbol),
        "price": float(item.get("c", 0)),
        "high": float(item.get("h", 0)),
        "low": float(item.get("l", 0)),
        "open": float(item.get("o", 0)),
        "change": float(item.get("ch", 0)),
        "change_percent": float(item.get("cp", 0)),
        "timestamp": item.get("t", ""),
        "provider": "fcs_api",
    }

    cache_set(cache_key, result, ttl_seconds=60)
    return result


async def fcs_crypto_latest(symbol: str) -> dict[str, Any]:
    """
    Get latest crypto quote.

    Symbol format: BTC/USD, ETH/USD, SOL/USD
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("fcs", "crypto", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _fcs_get("/crypto/latest", {"symbol": symbol})

    response = data.get("response", [])
    if not response:
        raise ValueError(f"No crypto data for {symbol}")

    item = response[0] if isinstance(response, list) else response
    result = {
        "symbol": item.get("s", symbol),
        "price": float(item.get("c", 0)),
        "high": float(item.get("h", 0)),
        "low": float(item.get("l", 0)),
        "open": float(item.get("o", 0)),
        "change": float(item.get("ch", 0)),
        "change_percent": float(item.get("cp", 0)),
        "timestamp": item.get("t", ""),
        "provider": "fcs_api",
    }

    cache_set(cache_key, result, ttl_seconds=30)
    return result


async def fcs_stock_latest(symbol: str) -> dict[str, Any]:
    """
    Get latest stock quote.

    Symbol format: AAPL, MSFT, GOOGL
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("fcs", "stock", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _fcs_get("/stock/latest", {"symbol": symbol})

    response = data.get("response", [])
    if not response:
        raise ValueError(f"No stock data for {symbol}")

    item = response[0] if isinstance(response, list) else response
    result = {
        "symbol": item.get("s", symbol),
        "price": float(item.get("c", 0)),
        "high": float(item.get("h", 0)),
        "low": float(item.get("l", 0)),
        "open": float(item.get("o", 0)),
        "change": float(item.get("ch", 0)),
        "change_percent": float(item.get("cp", 0)),
        "timestamp": item.get("t", ""),
        "provider": "fcs_api",
    }

    cache_set(cache_key, result, ttl_seconds=60)
    return result


async def fcs_forex_list() -> list[dict[str, str]]:
    """Get list of available forex pairs."""
    cache_key = make_cache_key("fcs", "fx_list")
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _fcs_get("/forex/list", {"type": "forex"})
    pairs = [
        {"symbol": item.get("s", ""), "name": item.get("n", "")}
        for item in data.get("response", [])
    ]

    cache_set(cache_key, pairs, ttl_seconds=86400)
    return pairs
