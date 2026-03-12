"""
FreeCryptoAPI Service — free crypto market data.

Specialized crypto data for dashboards and bots.
No API key required.

Base URL: https://api.freecryptoapi.com/v1
"""

import logging
import re
from typing import Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.utils.http_client import get_session

logger = logging.getLogger(__name__)

FREECRYPTO_BASE = "https://api.freecryptoapi.com/v1"

_SYMBOL_RE = re.compile(r"^[A-Za-z0-9]{1,10}$")


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not _SYMBOL_RE.match(symbol):
        raise ValueError(f"Invalid crypto symbol: {symbol!r}")
    return symbol


async def _fc_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Make GET request to FreeCryptoAPI."""
    session = await get_session()
    url = f"{FREECRYPTO_BASE}{path}"

    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"FreeCryptoAPI error {resp.status}: {text[:200]}")
        return await resp.json(content_type=None)


async def freecrypto_price(symbol: str) -> dict[str, Any]:
    """
    Get current price for a cryptocurrency.

    Symbol: BTC, ETH, SOL, etc.
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("fc", "price", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _fc_get(f"/getData/{symbol}")

    coin_data = data.get("data", data)

    result = {
        "symbol": symbol,
        "price": float(coin_data.get("price", coin_data.get("current_price", 0))),
        "change_24h": float(coin_data.get("change_24h", coin_data.get("price_change_24h", 0))),
        "change_percent_24h": float(coin_data.get("change_percent_24h", coin_data.get("price_change_percentage_24h", 0))),
        "volume_24h": float(coin_data.get("volume_24h", coin_data.get("total_volume", 0))),
        "market_cap": float(coin_data.get("market_cap", 0)),
        "provider": "freecryptoapi",
    }

    cache_set(cache_key, result, ttl_seconds=30)
    return result


async def freecrypto_prices(symbols: list[str]) -> dict[str, Any]:
    """Get prices for multiple cryptocurrencies."""
    validated = [_validate_symbol(s) for s in symbols]
    if len(validated) > 50:
        raise ValueError("Maximum 50 symbols per request")

    symbols_str = ",".join(validated)
    cache_key = make_cache_key("fc", "prices", symbols_str)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _fc_get(f"/getData/{symbols_str}")

    coins_data = data.get("data", data)
    if isinstance(coins_data, dict):
        prices = {
            k: {
                "symbol": k,
                "price": float(v.get("price", v.get("current_price", 0))),
                "change_24h": float(v.get("change_24h", v.get("price_change_24h", 0))),
                "provider": "freecryptoapi",
            }
            for k, v in coins_data.items()
            if isinstance(v, dict)
        }
    else:
        prices = {}

    result = {
        "success": True,
        "prices": prices,
        "total": len(prices),
        "provider": "freecryptoapi",
    }

    cache_set(cache_key, result, ttl_seconds=30)
    return result
