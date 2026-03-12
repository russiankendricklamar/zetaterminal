"""
Stooq Historical Data Service — CSV-based market data provider.

Stooq provides free historical OHLCV data via direct CSV download.
No API key required. Used as the historical data layer for the backtest engine
and offline quote storage.

Supported assets: Global stocks, ETFs, FX, bonds, crypto, indices.

Ticker format examples:
  - US stocks: AAPL, MSFT, GOOGL
  - UK stocks: BARC.UK, HSBA.UK
  - German stocks: BMW.DE, SAP.DE
  - Polish stocks: PKO, CDR
  - FX: EURUSD, GBPUSD, USDJPY
  - Crypto: BTC.V, ETH.V
  - Indices: ^SPX, ^DJI, ^NDQ, ^DAX
  - ETF: SPY, QQQ, IWM
"""

import io
import logging
import re
from datetime import datetime
from typing import Any

import pandas as pd

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.utils.http_client import get_session

logger = logging.getLogger(__name__)

STOOQ_BASE = "https://stooq.com/q/d/l/"

_TICKER_RE = re.compile(r"^[A-Za-z0-9.\-\^]{1,30}$")

# Mapping of interval codes for Stooq
INTERVAL_MAP = {
    "daily": "d",
    "weekly": "w",
    "monthly": "m",
    "quarterly": "q",
    "yearly": "y",
}


def _validate_ticker(ticker: str) -> str:
    """Validate ticker to prevent URL injection."""
    ticker = ticker.strip()
    if not _TICKER_RE.match(ticker):
        raise ValueError(f"Invalid ticker format: {ticker!r}")
    return ticker


async def stooq_history(
    ticker: str,
    date_from: str | None = None,
    date_to: str | None = None,
    interval: str = "daily",
) -> dict[str, Any]:
    """
    Download historical OHLCV data from Stooq.

    Args:
        ticker: Stooq ticker symbol
        date_from: Start date YYYY-MM-DD (default: 1y ago)
        date_to: End date YYYY-MM-DD (default: today)
        interval: daily, weekly, monthly, quarterly, yearly

    Returns:
        Dict with candles list and metadata
    """
    ticker = _validate_ticker(ticker)
    interval_code = INTERVAL_MAP.get(interval, "d")

    cache_key = make_cache_key("stooq", "hist", ticker, date_from, date_to, interval)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    params: dict[str, str] = {
        "s": ticker.lower(),
        "i": interval_code,
    }
    if date_from:
        params["d1"] = date_from.replace("-", "")
    if date_to:
        params["d2"] = date_to.replace("-", "")

    session = await get_session()
    async with session.get(STOOQ_BASE, params=params) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Stooq returned HTTP {resp.status} for {ticker}")
        text = await resp.text()

    if "No data" in text or len(text.strip()) < 20:
        raise ValueError(f"No data available for ticker {ticker}")

    df = pd.read_csv(io.StringIO(text))

    # Stooq CSV columns: Date, Open, High, Low, Close, Volume
    # Some tickers don't have Volume
    required = {"Date", "Open", "High", "Low", "Close"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"Unexpected CSV format for {ticker}: {list(df.columns)}")

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    candles = []
    for row in df.itertuples(index=False):
        candle: dict[str, Any] = {
            "date": row.Date.strftime("%Y-%m-%d"),
            "open": float(row.Open),
            "high": float(row.High),
            "low": float(row.Low),
            "close": float(row.Close),
        }
        if hasattr(row, "Volume") and pd.notna(row.Volume):
            candle["volume"] = int(row.Volume)
        else:
            candle["volume"] = 0
        candles.append(candle)

    metadata = {
        "ticker": ticker,
        "interval": interval,
        "start_date": candles[0]["date"] if candles else None,
        "end_date": candles[-1]["date"] if candles else None,
        "n_observations": len(candles),
        "provider": "stooq",
    }

    result = {
        "success": True,
        "candles": candles,
        "metadata": metadata,
    }

    # Cache for 1 hour — historical data doesn't change often
    cache_set(cache_key, result, ttl_seconds=3600)
    return result


async def stooq_bulk_download(
    tickers: list[str],
    date_from: str | None = None,
    date_to: str | None = None,
    interval: str = "daily",
) -> dict[str, Any]:
    """
    Download historical data for multiple tickers.

    Returns dict mapping ticker -> history result or error string.
    """
    import asyncio

    if len(tickers) > 50:
        raise ValueError("Maximum 50 tickers per bulk request")

    validated = [_validate_ticker(t) for t in tickers]

    async def _fetch_one(t: str) -> tuple[str, dict[str, Any] | str]:
        try:
            data = await stooq_history(t, date_from, date_to, interval)
            return t, data
        except Exception as e:
            logger.warning("Stooq bulk: failed for %s: %s", t, e)
            return t, str(e)

    results = await asyncio.gather(*[_fetch_one(t) for t in validated])
    return {
        "success": True,
        "results": {t: d for t, d in results},
        "total": len(validated),
        "succeeded": sum(1 for _, d in results if isinstance(d, dict)),
        "failed": sum(1 for _, d in results if isinstance(d, str)),
    }


async def stooq_search_tickers(query: str) -> list[dict[str, str]]:
    """
    Search for available tickers on Stooq.

    Note: Stooq doesn't have a search API, so this returns
    from a curated list of known tickers matching the query.
    """
    query_upper = query.upper()

    known_tickers = [
        # US Indices
        {"ticker": "^SPX", "name": "S&P 500", "category": "index"},
        {"ticker": "^DJI", "name": "Dow Jones Industrial", "category": "index"},
        {"ticker": "^NDQ", "name": "NASDAQ Composite", "category": "index"},
        {"ticker": "^RUT", "name": "Russell 2000", "category": "index"},
        # European Indices
        {"ticker": "^DAX", "name": "DAX 40", "category": "index"},
        {"ticker": "^FTM", "name": "FTSE MIB", "category": "index"},
        {"ticker": "^UKX", "name": "FTSE 100", "category": "index"},
        {"ticker": "^CAC", "name": "CAC 40", "category": "index"},
        # FX
        {"ticker": "EURUSD", "name": "EUR/USD", "category": "fx"},
        {"ticker": "GBPUSD", "name": "GBP/USD", "category": "fx"},
        {"ticker": "USDJPY", "name": "USD/JPY", "category": "fx"},
        {"ticker": "USDCHF", "name": "USD/CHF", "category": "fx"},
        {"ticker": "AUDUSD", "name": "AUD/USD", "category": "fx"},
        {"ticker": "USDCAD", "name": "USD/CAD", "category": "fx"},
        {"ticker": "USDRUB", "name": "USD/RUB", "category": "fx"},
        {"ticker": "EURRUB", "name": "EUR/RUB", "category": "fx"},
        # Crypto
        {"ticker": "BTC.V", "name": "Bitcoin USD", "category": "crypto"},
        {"ticker": "ETH.V", "name": "Ethereum USD", "category": "crypto"},
        {"ticker": "SOL.V", "name": "Solana USD", "category": "crypto"},
        # Commodities
        {"ticker": "GC.F", "name": "Gold Futures", "category": "commodity"},
        {"ticker": "SI.F", "name": "Silver Futures", "category": "commodity"},
        {"ticker": "CL.F", "name": "Crude Oil WTI Futures", "category": "commodity"},
        {"ticker": "NG.F", "name": "Natural Gas Futures", "category": "commodity"},
        # Popular US stocks
        {"ticker": "AAPL.US", "name": "Apple Inc.", "category": "stock"},
        {"ticker": "MSFT.US", "name": "Microsoft Corp.", "category": "stock"},
        {"ticker": "GOOGL.US", "name": "Alphabet Inc.", "category": "stock"},
        {"ticker": "AMZN.US", "name": "Amazon.com Inc.", "category": "stock"},
        {"ticker": "NVDA.US", "name": "NVIDIA Corp.", "category": "stock"},
        {"ticker": "TSLA.US", "name": "Tesla Inc.", "category": "stock"},
        {"ticker": "META.US", "name": "Meta Platforms Inc.", "category": "stock"},
        # Popular ETFs
        {"ticker": "SPY.US", "name": "SPDR S&P 500 ETF", "category": "etf"},
        {"ticker": "QQQ.US", "name": "Invesco QQQ Trust", "category": "etf"},
        {"ticker": "IWM.US", "name": "iShares Russell 2000 ETF", "category": "etf"},
        {"ticker": "TLT.US", "name": "iShares 20+ Year Treasury Bond ETF", "category": "etf"},
        {"ticker": "GLD.US", "name": "SPDR Gold Shares", "category": "etf"},
        # Bonds
        {"ticker": "10USY.B", "name": "US 10Y Treasury Yield", "category": "bond"},
        {"ticker": "2USY.B", "name": "US 2Y Treasury Yield", "category": "bond"},
        {"ticker": "10DEY.B", "name": "Germany 10Y Bund Yield", "category": "bond"},
    ]

    matches = [
        t for t in known_tickers
        if query_upper in t["ticker"].upper() or query_upper in t["name"].upper()
    ]
    return matches[:20]
