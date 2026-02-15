"""
API Key authentication middleware.

Usage:
    from src.middleware.auth import require_api_key
    app.include_router(router, dependencies=[Depends(require_api_key)])

If API_KEY env var is not set, authentication is disabled (dev mode).
"""
import os

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(
    api_key: str = Security(API_KEY_HEADER),
) -> None:
    expected = os.getenv("API_KEY")
    if not expected:
        return
    if api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
