"""
Admin-only dependency: API key + X-Username header with role check.
"""
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.client import get_session
from src.database.sa_models import User
from src.middleware.auth import require_api_key


async def require_admin(
    _: None = Depends(require_api_key),
    x_username: str = Header(..., alias="X-Username"),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Verify that the caller is an authenticated admin."""
    result = await session.execute(
        select(User).where(User.username == x_username.lower())
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
