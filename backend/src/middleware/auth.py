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
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils.jwt_utils import TokenPayload, decode_token

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)

# ── Lightweight user-status cache (M1 fix) ─────────────────────────────
# Avoids a DB query on every single request while still catching blocked
# users within _STATUS_CACHE_TTL seconds.
_STATUS_CACHE_TTL = 60  # seconds
_user_status_cache: dict[int, tuple[str, float]] = {}  # user_id -> (status, cached_at)


async def _is_user_active(user_id: int) -> bool:
    """Check user status in DB with a short-lived in-memory cache."""
    now = time.time()
    cached = _user_status_cache.get(user_id)
    if cached and (now - cached[1]) < _STATUS_CACHE_TTL:
        return cached[0] == "active"

    from sqlalchemy import select
    from src.database.client import async_session_factory
    from src.database.sa_models import User

    try:
        async with async_session_factory() as session:
            result = await session.execute(
                select(User.status).where(User.id == user_id)
            )
            row = result.scalar_one_or_none()
            user_status = row if row else "deleted"
            _user_status_cache[user_id] = (user_status, now)
            return user_status == "active"
    except Exception:
        # If DB is unreachable, allow the request (fail-open for availability).
        # The JWT is still cryptographically valid.
        logger.warning("Could not verify user status for user_id=%s", user_id)
        return True


def invalidate_user_status_cache(user_id: int) -> None:
    """Call after admin blocks/deletes a user to immediately evict the cache."""
    _user_status_cache.pop(user_id, None)


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

    # M1: verify user is still active (cached, ~60s TTL)
    if payload.sub and not await _is_user_active(payload.sub):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is blocked or deleted",
        )

    return payload


# Backward-compatible alias used by ~40 router registrations in main.py
require_api_key = require_auth
