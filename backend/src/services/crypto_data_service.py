"""
Crypto Data Service — CoinGecko, CoinGap

Proxies crypto market data and arbitrage opportunities.
"""

import os
from typing import Optional, Dict, Any, List
import aiohttp

from src.services.cache_service import cache_get, cache_set, make_cache_key

COINGECKO_KEY = os.getenv("COINGECKO_API_KEY", "")
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

COINGAP_KEY = os.getenv("COINGAP_API_KEY", "")
COINGAP_BASE = "https://api.coingap.io"


# ─── CoinGecko ────────────────────────────────────────────────────────────────

async def coingecko_markets(
    vs_currency: str = "usd",
    per_page: int = 100,
    page: int = 1,
    order: str = "market_cap_desc"
) -> List[Dict[str, Any]]:
    """Get top crypto markets from CoinGecko."""
    key = make_cache_key("cg", "markets", vs_currency, per_page, page, order)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params: Dict[str, Any] = {
        "vs_currency": vs_currency,
        "order": order,
        "per_page": per_page,
        "page": page,
        "sparkline": "true",
        "price_change_percentage": "1h,24h,7d",
    }
    headers: Dict[str, str] = {}
    if COINGECKO_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_KEY

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{COINGECKO_BASE}/coins/markets", params=params, headers=headers) as resp:
            if resp.status == 429:
                cached_fallback = cache_get(make_cache_key("cg", "markets", vs_currency, per_page, page, order, "fallback"))
                if cached_fallback is not None:
                    return cached_fallback
                return []
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    cache_set(key, data, ttl_seconds=120)
    cache_set(make_cache_key("cg", "markets", vs_currency, per_page, page, order, "fallback"), data, ttl_seconds=600)
    return data


async def coingecko_coin(coin_id: str) -> Dict[str, Any]:
    """Get detailed coin info from CoinGecko."""
    key = make_cache_key("cg", "coin", coin_id)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
    }
    headers: Dict[str, str] = {}
    if COINGECKO_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_KEY

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{COINGECKO_BASE}/coins/{coin_id}", params=params, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    result = {
        "id": data.get("id", ""),
        "symbol": data.get("symbol", ""),
        "name": data.get("name", ""),
        "description": data.get("description", {}).get("en", ""),
        "image": data.get("image", {}).get("large", ""),
        "market_data": data.get("market_data", {}),
        "market_cap_rank": data.get("market_cap_rank", 0),
        "genesis_date": data.get("genesis_date", ""),
        "provider": "coingecko",
    }
    cache_set(key, result, ttl_seconds=120)
    return result


async def coingecko_market_chart(
    coin_id: str,
    vs_currency: str = "usd",
    days: int = 30
) -> Dict[str, Any]:
    """Get price history chart data from CoinGecko."""
    key = make_cache_key("cg", "chart", coin_id, vs_currency, days)
    cached = cache_get(key)
    if cached is not None:
        return cached

    params = {"vs_currency": vs_currency, "days": days}
    headers: Dict[str, str] = {}
    if COINGECKO_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_KEY

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{COINGECKO_BASE}/coins/{coin_id}/market_chart", params=params, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    result = {
        "coin_id": coin_id,
        "vs_currency": vs_currency,
        "prices": data.get("prices", []),
        "market_caps": data.get("market_caps", []),
        "total_volumes": data.get("total_volumes", []),
        "provider": "coingecko",
    }
    cache_set(key, result, ttl_seconds=120)
    return result


async def coingecko_trending() -> Dict[str, Any]:
    """Get trending coins from CoinGecko."""
    key = make_cache_key("cg", "trending")
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers: Dict[str, str] = {}
    if COINGECKO_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_KEY

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{COINGECKO_BASE}/search/trending", headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    cache_set(key, data, ttl_seconds=300)
    return data


async def coingecko_global() -> Dict[str, Any]:
    """Get global crypto market stats."""
    key = make_cache_key("cg", "global")
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers: Dict[str, str] = {}
    if COINGECKO_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_KEY

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{COINGECKO_BASE}/global", headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    result = data.get("data", {})
    result["provider"] = "coingecko"
    cache_set(key, result, ttl_seconds=120)
    return result


# ─── CoinGap ──────────────────────────────────────────────────────────────────

async def coingap_arbitrage() -> List[Dict[str, Any]]:
    """Get crypto arbitrage opportunities from CoinGap."""
    key = make_cache_key("coingap", "arb")
    cached = cache_get(key)
    if cached is not None:
        return cached

    headers: Dict[str, str] = {}
    if COINGAP_KEY:
        headers["Authorization"] = f"Bearer {COINGAP_KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{COINGAP_BASE}/v1/arbitrage", headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    result = data if isinstance(data, list) else data.get("data", [])
    cache_set(key, result, ttl_seconds=60)
    return result
