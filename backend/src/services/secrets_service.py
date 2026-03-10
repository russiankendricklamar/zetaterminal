"""
Secrets service — loads API keys from the api_keys DB table.

Keys are cached in memory and refreshed on demand.
Falls back to env vars if the DB key is not set.
"""
import logging
import os
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.sa_models import ApiKey
from src.utils.crypto import encrypt_value, decrypt_value

logger = logging.getLogger(__name__)

# In-memory cache: service_name -> decrypted key_value
_cache: dict[str, str] = {}
_loaded = False


async def load_all(session: AsyncSession) -> None:
    """Load all API keys from DB into memory cache (decrypted)."""
    global _loaded
    result = await session.execute(select(ApiKey))
    rows = result.scalars().all()
    _cache.clear()
    for row in rows:
        _cache[row.service] = decrypt_value(row.key_value)
    _loaded = True
    logger.info("Loaded %d API keys from database", len(_cache))


async def _ensure_loaded(session: AsyncSession) -> None:
    if not _loaded:
        await load_all(session)


async def get_key(service: str, session: AsyncSession) -> str:
    """Get API key by service name. Falls back to env var."""
    await _ensure_loaded(session)
    value = _cache.get(service, "")
    if not value:
        # Fallback to env var for backward compatibility
        env_name = service.upper().replace("-", "_").replace(".", "_")
        value = os.getenv(env_name, "")
    return value


def get_key_sync(service: str) -> str:
    """Get cached key synchronously (for use after load_all)."""
    value = _cache.get(service, "")
    if not value:
        env_name = service.upper().replace("-", "_").replace(".", "_")
        value = os.getenv(env_name, "")
    return value


async def set_key(service: str, key_value: str, description: str,
                  session: AsyncSession) -> None:
    """Insert or update an API key (encrypted at rest)."""
    encrypted = encrypt_value(key_value)
    result = await session.execute(
        select(ApiKey).where(ApiKey.service == service)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.key_value = encrypted
        if description:
            existing.description = description
    else:
        session.add(ApiKey(
            service=service,
            key_value=encrypted,
            description=description,
        ))
    await session.commit()
    _cache[service] = key_value  # Cache stores decrypted value
    logger.info("API key updated for service: %s", service)


async def delete_key(service: str, session: AsyncSession) -> bool:
    """Delete an API key."""
    result = await session.execute(
        select(ApiKey).where(ApiKey.service == service)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        return False
    await session.delete(existing)
    await session.commit()
    _cache.pop(service, None)
    return True


async def list_keys(session: AsyncSession) -> list[dict]:
    """List all stored keys (masked values)."""
    await _ensure_loaded(session)
    result = await session.execute(select(ApiKey))
    rows = result.scalars().all()
    return [
        {
            "service": row.service,
            "has_value": bool(row.key_value),
            "description": row.description or "",
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
        for row in rows
    ]


# All known services and their env var names
KNOWN_SERVICES: dict[str, str] = {
    "ALPHA_VANTAGE_API_KEY": "Alpha Vantage — quotes, FX, technicals",
    "TWELVE_DATA_API_KEY": "Twelve Data — quotes, time series",
    "POLYGON_API_KEY": "Polygon.io — tickers, OHLCV, options, news",
    "FRED_API_KEY": "FRED (St. Louis Fed) — economic indicators",
    "OPENFIGI_API_KEY": "OpenFIGI — ticker-to-FIGI mapping",
    "COINGECKO_API_KEY": "CoinGecko — crypto markets, charts",
    "COINGAP_API_KEY": "CoinGap — arbitrage opportunities",
    "NEWSAPI_KEY": "NewsAPI — headlines, article search",
    "CURRENTS_API_KEY": "Currents API — news search",
    "HUGGINGFACE_TOKEN": "Hugging Face — inference (sentiment, summarize)",
    "GEMINI_API_KEY": "Google Gemini — AI market analysis",
    "DADATA_API_TOKEN": "DaData — Russian company lookup",
    "DADATA_SECRET_KEY": "DaData — secret key",
    "VIRUSTOTAL_API_KEY": "VirusTotal — URL scan",
    "ABUSEIPDB_API_KEY": "AbuseIPDB — IP check",
    "URLSCAN_API_KEY": "URLScan.io — URL scan",
    "IP2WHOIS_API_KEY": "IP2WHOIS — WHOIS lookup",
    "IPINFO_TOKEN": "ipinfo.io — IP geolocation",
    "IP2LOCATION_API_KEY": "IP2Location — IP geolocation",
}
