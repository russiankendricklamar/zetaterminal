"""
SQLAlchemy async database connection (Neon PostgreSQL).
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from .sa_models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/zetaterminal")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes."""
    async with async_session_factory() as session:
        yield session
