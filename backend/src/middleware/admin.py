"""
Admin-only dependency: JWT auth + role check from database.
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.client import get_session
from src.database.sa_models import User
from src.middleware.auth import require_auth
from src.utils.jwt_utils import TokenPayload


async def require_admin(
    payload: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Verify that the caller is an authenticated admin via JWT claims + DB check."""
    result = await session.execute(
        select(User).where(User.id == payload.sub)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if user.status == "blocked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is blocked",
        )
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
