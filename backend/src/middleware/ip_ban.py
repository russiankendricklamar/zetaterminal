"""
IP Ban middleware: blocks requests from banned IP addresses.
Maintains an in-memory cache, loaded from DB at startup.
"""
import logging
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

_banned_ips: set[str] = set()


def _client_ip(request: Request) -> str:
    """Extract client IP from the rightmost (trusted) X-Forwarded-For entry.

    Render sits behind a single proxy that appends the real client IP.
    Taking the *rightmost* entry is safer: a client can prepend arbitrary
    values to X-Forwarded-For, but only the trusted proxy appends the last one.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        parts = [p.strip() for p in forwarded.split(",")]
        # Rightmost entry = set by the nearest trusted proxy (Render)
        return parts[-1]
    if request.client:
        return request.client.host
    return "unknown"


class IpBanMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any):
        ip = _client_ip(request)
        if ip in _banned_ips:
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"},
            )
        return await call_next(request)


async def load_banned_ips() -> None:
    """Load banned IPs from database into memory cache."""
    from sqlalchemy import select
    from src.database.client import async_session_factory
    from src.database.sa_models import IpBan

    try:
        async with async_session_factory() as session:
            result = await session.execute(select(IpBan.ip_address))
            ips = {row[0] for row in result.fetchall()}
            _banned_ips.clear()
            _banned_ips.update(ips)
            logger.info("Loaded %d banned IPs", len(_banned_ips))
    except Exception as e:
        logger.warning("Could not load banned IPs: %s", e)


def add_banned_ip(ip: str) -> None:
    _banned_ips.add(ip)


def remove_banned_ip(ip: str) -> None:
    _banned_ips.discard(ip)


def get_banned_ips() -> set[str]:
    return set(_banned_ips)
