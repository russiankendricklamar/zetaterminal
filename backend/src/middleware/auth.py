"""
JWT Bearer authentication middleware.

Usage:
    from src.middleware.auth import require_auth, require_api_key
    app.include_router(router, dependencies=[Depends(require_auth)])

Set DISABLE_AUTH=true for local development without auth.
In production (RENDER env var is set), DISABLE_AUTH is ignored.
"""
import logging
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils.jwt_utils import TokenPayload, decode_token

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


def _is_auth_disabled() -> bool:
    """Allow DISABLE_AUTH only when NOT running on Render (production)."""
    if os.getenv("RENDER"):
        return False
    return os.getenv("DISABLE_AUTH", "").lower() == "true"


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> TokenPayload:
    """Validate JWT access token from Authorization: Bearer header."""
    if _is_auth_disabled():
        logger.warning("DISABLE_AUTH is active — returning dev user with 'user' role")
        return TokenPayload(
            sub=0, username="dev", role="user", exp=0, iat=0, type="access"
        )

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# Backward-compatible alias used by ~40 router registrations in main.py
require_api_key = require_auth
