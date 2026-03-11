"""
SQLAlchemy async database connection (Neon PostgreSQL).
"""
import logging
import os
import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .sa_models import Base

logger = logging.getLogger(__name__)


def _normalize_database_url(url: str) -> str:
    """Ensure the URL uses the asyncpg driver.

    Neon/Render provide URLs like ``postgresql://...`` which default to
    the sync ``psycopg2`` driver.  This helper rewrites the scheme so
    SQLAlchemy uses ``asyncpg`` instead.

    Also strips ``channel_binding`` which asyncpg does not support.
    """
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]

    # asyncpg does not support sslmode or channel_binding as URL params —
    # strip them and handle SSL via connect_args instead
    from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params.pop("channel_binding", None)
    params.pop("sslmode", None)
    cleaned_query = urlencode(params, doseq=True)
    url = urlunparse(parsed._replace(query=cleaned_query))

    return url


_raw_url = os.getenv("DATABASE_URL", "")
if not _raw_url:
    logger.warning("DATABASE_URL is not set — using local fallback")
    _raw_url = "postgresql+asyncpg://localhost/zetaterminal"

DATABASE_URL = _normalize_database_url(_raw_url)

# Neon requires SSL — use default SSL context (validates certs via system CA)
_ssl_context = ssl.create_default_context()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    connect_args={"ssl": _ssl_context},
)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create tables if they don't exist."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes."""
    async with async_session_factory() as session:
        yield session
