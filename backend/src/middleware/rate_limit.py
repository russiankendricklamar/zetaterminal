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
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
