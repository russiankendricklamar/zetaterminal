"""
Alpaca Data API Service — US stocks and options data + paper trading.

Provides market data (SIP/IEX feeds), historical bars, and paper trading
capabilities for US equities. Load-balanced with Finnhub.

Base URL (data): https://data.alpaca.markets/v2
Base URL (paper trading): https://paper-api.alpaca.markets/v2
Auth: headers APCA-API-KEY-ID + APCA-API-SECRET-KEY
"""

import logging
import re
from typing import Any

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.services.secrets_service import get_key_sync
from src.utils.http_client import get_session

logger = logging.getLogger(__name__)

ALPACA_DATA_BASE = "https://data.alpaca.markets/v2"
ALPACA_PAPER_BASE = "https://paper-api.alpaca.markets/v2"

_TICKER_RE = re.compile(r"^[A-Za-z0-9.\-/]{1,20}$")


def _api_key() -> str:
    return get_key_sync("ALPACA_API_KEY")


def _api_secret() -> str:
    return get_key_sync("ALPACA_API_SECRET")


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not _TICKER_RE.match(symbol):
        raise ValueError(f"Invalid symbol: {symbol!r}")
    return symbol


def _auth_headers() -> dict[str, str]:
    return {
        "APCA-API-KEY-ID": _api_key(),
        "APCA-API-SECRET-KEY": _api_secret(),
    }


async def _alpaca_data_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Make authenticated GET request to Alpaca Data API."""
    session = await get_session()
    url = f"{ALPACA_DATA_BASE}{path}"

    async with session.get(url, params=params, headers=_auth_headers()) as resp:
        if resp.status == 403:
            raise RuntimeError("Alpaca API key invalid or insufficient permissions")
        if resp.status == 429:
            raise RuntimeError("Alpaca rate limit exceeded")
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"Alpaca error {resp.status}: {text[:200]}")
        return await resp.json(content_type=None)


async def _alpaca_paper_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Make authenticated GET request to Alpaca Paper Trading API."""
    session = await get_session()
    url = f"{ALPACA_PAPER_BASE}{path}"

    async with session.get(url, params=params, headers=_auth_headers()) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise RuntimeError(f"Alpaca paper error {resp.status}: {text[:200]}")
        return await resp.json(content_type=None)


async def alpaca_bars(
    symbol: str,
    timeframe: str = "1Day",
    start: str | None = None,
    end: str | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    """
    Get historical bars (OHLCV) for a US stock.

    Args:
        symbol: Stock ticker (AAPL, MSFT)
        timeframe: 1Min, 5Min, 15Min, 30Min, 1Hour, 1Day, 1Week, 1Month
        start: ISO 8601 date (2024-01-01)
        end: ISO 8601 date
        limit: Max bars (default 1000, max 10000)
    """
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("alpaca", "bars", symbol, timeframe, start, end, limit)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {
        "timeframe": timeframe,
        "limit": min(limit, 10000),
    }
    if start:
        params["start"] = start
    if end:
        params["end"] = end

    data = await _alpaca_data_get(f"/stocks/{symbol}/bars", params)

    candles = [
        {
            "date": bar.get("t", ""),
            "open": bar.get("o", 0),
            "high": bar.get("h", 0),
            "low": bar.get("l", 0),
            "close": bar.get("c", 0),
            "volume": bar.get("v", 0),
            "vwap": bar.get("vw", 0),
            "trade_count": bar.get("n", 0),
        }
        for bar in data.get("bars", [])
    ]

    result = {
        "success": True,
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": candles,
        "metadata": {
            "n_observations": len(candles),
            "start_date": candles[0]["date"] if candles else None,
            "end_date": candles[-1]["date"] if candles else None,
            "provider": "alpaca",
        },
        "next_page_token": data.get("next_page_token"),
    }

    ttl = 60 if "Min" in timeframe or "Hour" in timeframe else 300
    cache_set(cache_key, result, ttl_seconds=ttl)
    return result


async def alpaca_latest_quote(symbol: str) -> dict[str, Any]:
    """Get latest quote (NBBO) for a US stock."""
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("alpaca", "quote", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _alpaca_data_get(f"/stocks/{symbol}/quotes/latest")

    quote = data.get("quote", {})
    result = {
        "symbol": symbol,
        "ask_price": quote.get("ap", 0),
        "ask_size": quote.get("as", 0),
        "bid_price": quote.get("bp", 0),
        "bid_size": quote.get("bs", 0),
        "timestamp": quote.get("t", ""),
        "provider": "alpaca",
    }

    cache_set(cache_key, result, ttl_seconds=5)
    return result


async def alpaca_latest_trade(symbol: str) -> dict[str, Any]:
    """Get latest trade for a US stock."""
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("alpaca", "trade", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _alpaca_data_get(f"/stocks/{symbol}/trades/latest")

    trade = data.get("trade", {})
    result = {
        "symbol": symbol,
        "price": trade.get("p", 0),
        "size": trade.get("s", 0),
        "timestamp": trade.get("t", ""),
        "exchange": trade.get("x", ""),
        "provider": "alpaca",
    }

    cache_set(cache_key, result, ttl_seconds=5)
    return result


async def alpaca_snapshot(symbol: str) -> dict[str, Any]:
    """Get full snapshot (quote + trade + bar) for a US stock."""
    symbol = _validate_symbol(symbol)
    cache_key = make_cache_key("alpaca", "snap", symbol)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _alpaca_data_get(f"/stocks/{symbol}/snapshot")

    result = {
        "symbol": symbol,
        "latest_trade": data.get("latestTrade", {}),
        "latest_quote": data.get("latestQuote", {}),
        "minute_bar": data.get("minuteBar", {}),
        "daily_bar": data.get("dailyBar", {}),
        "prev_daily_bar": data.get("prevDailyBar", {}),
        "provider": "alpaca",
    }

    cache_set(cache_key, result, ttl_seconds=10)
    return result


async def alpaca_multi_bars(
    symbols: list[str],
    timeframe: str = "1Day",
    start: str | None = None,
    end: str | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    """Get bars for multiple stocks in one request."""
    validated = [_validate_symbol(s) for s in symbols]
    if len(validated) > 50:
        raise ValueError("Maximum 50 symbols per multi-bar request")

    symbols_str = ",".join(validated)
    cache_key = make_cache_key("alpaca", "mbars", symbols_str, timeframe, start, end)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {
        "symbols": symbols_str,
        "timeframe": timeframe,
        "limit": min(limit, 10000),
    }
    if start:
        params["start"] = start
    if end:
        params["end"] = end

    data = await _alpaca_data_get("/stocks/bars", params)

    result = {
        "success": True,
        "bars": data.get("bars", {}),
        "symbols_requested": len(validated),
        "provider": "alpaca",
        "next_page_token": data.get("next_page_token"),
    }

    cache_set(cache_key, result, ttl_seconds=300)
    return result


async def alpaca_account() -> dict[str, Any]:
    """Get paper trading account info."""
    cache_key = make_cache_key("alpaca", "account")
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _alpaca_paper_get("/account")

    result = {
        "account_number": data.get("account_number", ""),
        "status": data.get("status", ""),
        "buying_power": float(data.get("buying_power", 0)),
        "cash": float(data.get("cash", 0)),
        "portfolio_value": float(data.get("portfolio_value", 0)),
        "equity": float(data.get("equity", 0)),
        "last_equity": float(data.get("last_equity", 0)),
        "long_market_value": float(data.get("long_market_value", 0)),
        "short_market_value": float(data.get("short_market_value", 0)),
        "provider": "alpaca",
    }

    cache_set(cache_key, result, ttl_seconds=30)
    return result
