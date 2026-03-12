"""
Finnhub Market Data Service — real-time and historical data.

Finnhub provides stock quotes, candles, company profiles, market news,
forex rates, crypto data, and symbol search. Free tier: 30 calls/second.

Used for web-dashboards, near-real-time quotes, and SPA clients.
Load-balanced with Alpaca to avoid overloading either provider.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.services.secrets_service import get_key_sync
from src.utils.http_client import get_session

logger = logging.getLogger(__name__)

FINNHUB_BASE = "https://finnhub.io/api/v1"

_TICKER_RE = re.compile(r"^[A-Za-z0-9.\-\^:]{1,30}$")

# Resolution mapping for candles
RESOLUTION_MAP = {
    "1": "1",
    "5": "5",
    "15": "15",
    "30": "30",
    "60": "60",
    "D": "D",
    "W": "W",
    "M": "M",
}


def _api_key() -> str:
    return get_key_sync("FINNHUB_API_KEY")


def _validate_symbol(symbol: str) -> str:
    """Validate symbol to prevent injection."""
    symbol = symbol.strip()
    if not _TICKER_RE.match(symbol):
        raise ValueError(f"Invalid symbol format: {symbol!r}")
    return symbol


async def _finnhub_get(path: str, params: dict[str, Any]) -> dict[str, Any] | list:
    """Make authenticated GET request to Finnhub API."""
    session = await get_session()
    headers = {"X-Finnhub-Token": _api_key()}
    url = f"{FINNHUB_BASE}{path}"

    async with session.get(url, params=params, headers=headers) as resp:
        if resp.status == 429:
            raise RuntimeError("Finnhub rate limit exceeded")
        if resp.status == 403:
            raise RuntimeError("Finnhub API key invalid or missing")
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"Finnhub API error {resp.status}: {text[:200]}")
        return await resp.json(content_type=None)


async def finnhub_quote(symbol: str) -> dict[str, Any]:
    """
    Get real-time quote for a stock symbol.

    Returns: current price, change, percent change, high, low, open, prev close.
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("finnhub", "quote", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _finnhub_get("/quote", {"symbol": symbol})

    result = {
        "symbol": symbol,
        "price": data.get("c", 0),
        "change": data.get("d", 0),
        "change_percent": data.get("dp", 0),
        "high": data.get("h", 0),
        "low": data.get("l", 0),
        "open": data.get("o", 0),
        "previous_close": data.get("pc", 0),
        "timestamp": data.get("t", 0),
        "provider": "finnhub",
    }

    # Short TTL — this is near-real-time data
    cache_set(cache_key, result, ttl_seconds=15)
    return result


async def finnhub_candles(
    symbol: str,
    resolution: str = "D",
    from_ts: int | None = None,
    to_ts: int | None = None,
) -> dict[str, Any]:
    """
    Get OHLCV candle data for a stock.

    Args:
        symbol: Stock symbol (e.g. AAPL, MSFT)
        resolution: 1, 5, 15, 30, 60, D, W, M
        from_ts: Unix timestamp start (default: 1 year ago)
        to_ts: Unix timestamp end (default: now)
    """
    symbol = _validate_symbol(symbol)
    res = RESOLUTION_MAP.get(resolution, "D")

    now = int(datetime.now().timestamp())
    if to_ts is None:
        to_ts = now
    if from_ts is None:
        from_ts = int((datetime.now() - timedelta(days=365)).timestamp())

    cache_key = make_cache_key("finnhub", "candles", symbol, res, from_ts, to_ts)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _finnhub_get("/stock/candle", {
        "symbol": symbol,
        "resolution": res,
        "from": from_ts,
        "to": to_ts,
    })

    if data.get("s") == "no_data":
        raise ValueError(f"No candle data for {symbol}")

    # Transpose parallel arrays into list of candle objects
    timestamps = data.get("t", [])
    candles = []
    for i, ts in enumerate(timestamps):
        candles.append({
            "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
            "open": data["o"][i],
            "high": data["h"][i],
            "low": data["l"][i],
            "close": data["c"][i],
            "volume": data["v"][i],
        })

    result = {
        "success": True,
        "symbol": symbol,
        "resolution": res,
        "candles": candles,
        "metadata": {
            "n_observations": len(candles),
            "start_date": candles[0]["date"] if candles else None,
            "end_date": candles[-1]["date"] if candles else None,
            "provider": "finnhub",
        },
    }

    # Cache based on resolution: intraday = 1min, daily+ = 5min
    ttl = 60 if res in ("1", "5", "15", "30", "60") else 300
    cache_set(cache_key, result, ttl_seconds=ttl)
    return result


async def finnhub_company_profile(symbol: str) -> dict[str, Any]:
    """Get company profile: name, industry, market cap, logo, etc."""
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("finnhub", "profile", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _finnhub_get("/stock/profile2", {"symbol": symbol})

    if not data:
        raise ValueError(f"No profile data for {symbol}")

    result = {
        "symbol": data.get("ticker", symbol),
        "name": data.get("name", ""),
        "exchange": data.get("exchange", ""),
        "industry": data.get("finnhubIndustry", ""),
        "ipo_date": data.get("ipo", ""),
        "market_cap": data.get("marketCapitalization", 0),
        "logo": data.get("logo", ""),
        "website": data.get("weburl", ""),
        "country": data.get("country", ""),
        "currency": data.get("currency", ""),
        "provider": "finnhub",
    }

    cache_set(cache_key, result, ttl_seconds=3600)
    return result


async def finnhub_market_news(category: str = "general") -> list[dict[str, Any]]:
    """
    Get latest market news.

    Categories: general, forex, crypto, merger
    """
    cache_key = make_cache_key("finnhub", "news", category)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _finnhub_get("/news", {"category": category})

    articles = [
        {
            "id": item.get("id"),
            "headline": item.get("headline", ""),
            "summary": item.get("summary", ""),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "image": item.get("image", ""),
            "datetime": item.get("datetime", 0),
            "related": item.get("related", ""),
            "provider": "finnhub",
        }
        for item in (data if isinstance(data, list) else [])
    ]

    cache_set(cache_key, articles, ttl_seconds=300)
    return articles


async def finnhub_forex_rates(base: str = "USD") -> dict[str, Any]:
    """Get forex exchange rates for a base currency."""
    base = _validate_symbol(base.upper())
    cache_key = make_cache_key("finnhub", "forex", base)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _finnhub_get("/forex/rates", {"base": base})

    result = {
        "base": data.get("base", base),
        "rates": data.get("quote", {}),
        "provider": "finnhub",
    }

    cache_set(cache_key, result, ttl_seconds=300)
    return result


async def finnhub_crypto_candles(
    symbol: str,
    resolution: str = "D",
    from_ts: int | None = None,
    to_ts: int | None = None,
) -> dict[str, Any]:
    """
    Get OHLCV candle data for a crypto pair.

    Symbol format: EXCHANGE:PAIR (e.g. BINANCE:BTCUSDT, COINBASE:ETH-USD)
    """
    symbol = _validate_symbol(symbol)
    res = RESOLUTION_MAP.get(resolution, "D")

    now = int(datetime.now().timestamp())
    if to_ts is None:
        to_ts = now
    if from_ts is None:
        from_ts = int((datetime.now() - timedelta(days=365)).timestamp())

    cache_key = make_cache_key("finnhub", "crypto", symbol, res, from_ts, to_ts)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _finnhub_get("/crypto/candle", {
        "symbol": symbol,
        "resolution": res,
        "from": from_ts,
        "to": to_ts,
    })

    if data.get("s") == "no_data":
        raise ValueError(f"No crypto data for {symbol}")

    timestamps = data.get("t", [])
    candles = [
        {
            "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
            "open": data["o"][i],
            "high": data["h"][i],
            "low": data["l"][i],
            "close": data["c"][i],
            "volume": data["v"][i],
        }
        for i, ts in enumerate(timestamps)
    ]

    result = {
        "success": True,
        "symbol": symbol,
        "resolution": res,
        "candles": candles,
        "metadata": {
            "n_observations": len(candles),
            "start_date": candles[0]["date"] if candles else None,
            "end_date": candles[-1]["date"] if candles else None,
            "provider": "finnhub",
        },
    }

    ttl = 60 if res in ("1", "5", "15", "30", "60") else 300
    cache_set(cache_key, result, ttl_seconds=ttl)
    return result


async def finnhub_search(query: str) -> list[dict[str, Any]]:
    """
    Search for symbols by name or ticker.

    Returns up to 20 matches with symbol, description, and type.
    """
    cache_key = make_cache_key("finnhub", "search", query)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _finnhub_get("/search", {"q": query})

    results = [
        {
            "symbol": item.get("symbol", ""),
            "description": item.get("description", ""),
            "display_symbol": item.get("displaySymbol", ""),
            "type": item.get("type", ""),
            "provider": "finnhub",
        }
        for item in data.get("result", [])[:20]
    ]

    cache_set(cache_key, results, ttl_seconds=3600)
    return results
