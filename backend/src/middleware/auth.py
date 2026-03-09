"""
API Key authentication middleware.

Usage:
    from src.middleware.auth import require_api_key
    app.include_router(router, dependencies=[Depends(require_api_key)])

If API_KEY env var is not set, returns 503 (service not configured).
Set DISABLE_AUTH=true for local development without auth.
"""
import os

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

API_KEY = os.getenv("API_KEY")


async def require_api_key(
    api_key: str = Security(API_KEY_HEADER),
) -> None:
    if os.getenv("DISABLE_AUTH", "").lower() == "true":
        return
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not configured",
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
