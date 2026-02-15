"""
Shared aiohttp ClientSession singleton.

Instead of creating a new session per request, reuse a single session
with connection pooling. Call close_session() on app shutdown.

Usage:
    from src.utils.http_client import get_session

    session = await get_session()
    async with session.get(url) as resp:
        data = await resp.json()
"""

import aiohttp
from typing import Optional

_session: Optional[aiohttp.ClientSession] = None


async def get_session() -> aiohttp.ClientSession:
    """Return the shared aiohttp session, creating it if needed."""
    global _session
    if _session is None or _session.closed:
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
        )
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        _session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
        )
    return _session


async def close_session() -> None:
    """Close the shared session. Call on app shutdown."""
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        _session = None
