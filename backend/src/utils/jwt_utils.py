"""
JWT token utilities for Zeta Terminal authentication.

Provides access token (30 min) and refresh token (30 day) creation/validation.
"""
import hashlib
import logging
import os
from datetime import UTC, datetime, timedelta

import jwt
from pydantic import BaseModel

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET") or ""
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def _require_secret() -> str:
    """Return JWT_SECRET or raise if empty. Guards every sign/verify call."""
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not configured — cannot sign or verify tokens")
    return JWT_SECRET


class TokenPayload(BaseModel):
    sub: int
    username: str
    role: str
    exp: int
    iat: int
    type: str


def validate_jwt_secret() -> None:
    """Check that JWT_SECRET is set and sufficiently long. Fatal on failure."""
    if not JWT_SECRET:
        raise RuntimeError("FATAL: JWT_SECRET is not set. Cannot start without a signing key.")
    if len(JWT_SECRET) < 32:
        raise RuntimeError("FATAL: JWT_SECRET is too short (min 32 chars required)")


def create_access_token(user_id: int, username: str, role: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, _require_secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int, username: str, role: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
    }
    return jwt.encode(payload, _require_secret(), algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token. Raises jwt.InvalidTokenError on failure."""
    data = jwt.decode(token, _require_secret(), algorithms=[JWT_ALGORITHM])
    return TokenPayload(**data)


def hash_token(token: str) -> str:
    """SHA-256 hash of a token for safe DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()
