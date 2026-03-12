"""
Shared rate limiter instance for use across routers.

Usage in router files:
    from src.middleware.rate_limit import limiter

    @router.post("/heavy-endpoint")
    @limiter.limit("10/minute")
    async def heavy_endpoint(request: Request, ...):
        ...
"""
from slowapi import Limiter
from starlette.requests import Request


def _trusted_client_ip(request: Request) -> str:
    """Extract client IP from the rightmost X-Forwarded-For entry.

    Consistent with ip_ban.py's _client_ip — the rightmost entry is the one
    appended by the nearest trusted proxy (Render). A client can prepend
    arbitrary values, but cannot control the rightmost entry.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        parts = [p.strip() for p in forwarded.split(",")]
        return parts[-1]
    if request.client:
        return request.client.host
    return "unknown"


limiter = Limiter(key_func=_trusted_client_ip, default_limits=["60/minute"])
