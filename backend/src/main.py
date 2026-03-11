"""
FastAPI приложение для Zeta Terminal Backend.
"""
import logging
import os
import secrets
from contextlib import asynccontextmanager, suppress

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

# Импортируем все роутеры
from datetime import UTC

from src.api import (
    admin,
    adversarial_stress,
    alpha_stacking,
    auth,
    backtest,
    black_litterman,
    bond,
    calendar_utils,
    ccmv,
    compute,
    convex_portfolio,
    crypto_data,
    dadata,
    database,
    eigenportfolio,
    etf,
    factor_analysis,
    forward,
    garch,
    gemini,
    har,
    hjb,
    macro_data,
    market_data,
    market_feeds,
    meta_labeling,
    moexalgo,
    multivariate_hmm,
    news_ai,
    pbo,
    portfolio,
    realized_kernels,
    repo,
    risk,
    cbonds,
    rudata,
    security_tools,
    sharpe_stats,
    spectral_regime,
    stress,
    swap,
    zcyc,
)
from src.api import secrets as secrets_api
from src.database.client import init_db
from src.middleware.admin import require_admin
from src.middleware.auth import require_api_key
from src.middleware.rate_limit import limiter
from src.utils.http_client import close_session
from src.utils.jwt_utils import validate_jwt_secret


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate JWT secret at startup
    validate_jwt_secret()
    await init_db()
    await _migrate_user_profile_columns()
    # Load API keys from DB into memory cache
    from src.database.client import async_session_factory
    from src.services import secrets_service
    async with async_session_factory() as session:
        try:
            await secrets_service.load_all(session)
        except Exception as e:
            logger.warning("Could not load API keys from DB: %s", e)
    # Seed admin user if none exists
    await _seed_admin()
    from src.middleware.ip_ban import load_banned_ips
    await load_banned_ips()
    # Cleanup expired/revoked refresh tokens
    await _cleanup_expired_tokens()
    yield
    await close_session()


async def _migrate_user_profile_columns() -> None:
    """Add profile columns to users table if they don't exist."""
    from sqlalchemy import text

    from src.database.client import engine

    columns = [
        ("phone", "VARCHAR"),
        ("bio", "TEXT"),
        ("preferences", "JSONB"),
        ("failed_login_count", "INTEGER DEFAULT 0"),
        ("locked_until", "TIMESTAMPTZ"),
    ]
    # user_id columns for data isolation
    user_id_tables = [
        "bond_valuations", "portfolios", "calculation_history", "file_records",
    ]
    # Build migration SQL at startup from hardcoded constants only.
    # Using string formatting here is safe because col_name, col_type, and table
    # are compile-time constants defined above — never user input.
    _user_col_stmts = [
        f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
        for col_name, col_type in columns
    ]
    _uid_stmts = []
    for table in user_id_tables:
        _uid_stmts.append(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS user_id INTEGER")
        _uid_stmts.append(f"CREATE INDEX IF NOT EXISTS ix_{table}_user_id ON {table} (user_id)")

    try:
        async with engine.begin() as conn:
            for stmt in _user_col_stmts:
                await conn.execute(text(stmt))
            for stmt in _uid_stmts:
                with suppress(Exception):
                    await conn.execute(text(stmt))
        logger.info("User profile columns migration complete")
    except Exception as e:
        logger.warning("Could not migrate user profile columns: %s", e)


async def _seed_admin() -> None:
    """Create default admin user if no admin exists. Requires ADMIN_PASSWORD env var."""
    from passlib.context import CryptContext
    from sqlalchemy import select

    from src.database.client import async_session_factory
    from src.database.sa_models import User

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    try:
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.role == "admin")
            )
            if result.scalar_one_or_none():
                return

            admin_password = os.getenv("ADMIN_PASSWORD", "")
            if not admin_password:
                logger.warning("ADMIN_PASSWORD not set — skipping admin seed")
                return
            if len(admin_password) < 12:
                logger.warning("ADMIN_PASSWORD too short (min 12 chars) — skipping admin seed")
                return
            import re
            if not re.search(r'[A-Z]', admin_password) or \
               not re.search(r'[a-z]', admin_password) or \
               not re.search(r'\d', admin_password):
                logger.warning("ADMIN_PASSWORD must contain uppercase, lowercase, and digit — skipping admin seed")
                return

            admin_user = User(
                username="admin",
                domain_handle="admin@zetaterminal.dev",
                email="admin@zetaterminal.io",
                password_hash=pwd_context.hash(admin_password),
                role="admin",
                status="active",
                invite_code=secrets.token_hex(8).upper(),
            )
            session.add(admin_user)
            await session.commit()
            logger.info("Default admin user seeded")
    except Exception as e:
        logger.warning("Could not seed admin user: %s", e)


async def _cleanup_expired_tokens() -> None:
    """Delete expired or revoked refresh tokens on startup."""
    from datetime import datetime

    from sqlalchemy import delete

    from src.database.client import async_session_factory
    from src.database.sa_models import RefreshToken

    try:
        async with async_session_factory() as session:
            result = await session.execute(
                delete(RefreshToken).where(
                    (RefreshToken.revoked)
                    | (RefreshToken.expires_at < datetime.now(UTC))
                )
            )
            await session.commit()
            if result.rowcount:
                logger.info("Cleaned up %d expired/revoked refresh tokens", result.rowcount)
    except Exception as e:
        logger.warning("Could not clean up refresh tokens: %s", e)


# Создаем FastAPI приложение
app = FastAPI(
    title="Zeta Terminal API",
    description="Backend API для Zeta Terminal",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Настройка CORS
cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

if not cors_origins:
    # Production MUST set CORS_ORIGINS. Fallback is dev-only.
    if any(os.getenv(m) for m in ("RENDER", "ORACLE_CLOUD", "OCI_REGION", "PRODUCTION")):
        cors_origins = ["https://russiankendricklamar.github.io"]
        logger.warning("CORS_ORIGINS not set in production — restricting to GitHub Pages only")
    else:
        cors_origins = [
            "http://localhost:5173",
            "https://russiankendricklamar.github.io",
            "tauri://localhost",
            "https://tauri.localhost",
        ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Username"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response

# Request tracking middleware (after CORS so preflight is not tracked)
from src.middleware.request_tracker import RequestTrackerMiddleware

app.add_middleware(RequestTrackerMiddleware)

# IP ban middleware (added after RequestTracker — middleware executes in reverse order,
# so IpBan runs before RequestTracker, blocking banned IPs early)
from src.middleware.ip_ban import IpBanMiddleware

app.add_middleware(IpBanMiddleware)

# Подключаем все роутеры (с обязательной аутентификацией)
_auth = [Depends(require_api_key)]

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"], dependencies=_auth)
app.include_router(bond.router, prefix="/api/bond", tags=["Bond"], dependencies=_auth)
app.include_router(swap.router, prefix="/api/swap", tags=["Swap"], dependencies=_auth)
app.include_router(forward.router, prefix="/api/forward", tags=["Forward"], dependencies=_auth)
app.include_router(compute.router, prefix="/api/compute", tags=["Compute"], dependencies=_auth)
app.include_router(garch.router, prefix="/api/garch", tags=["GARCH"], dependencies=_auth)
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtest"], dependencies=_auth)
app.include_router(stress.router, prefix="/api/stress", tags=["Stress"], dependencies=_auth)
app.include_router(ccmv.router, prefix="/api/ccmv", tags=["CCMV"], dependencies=_auth)
app.include_router(hjb.router, prefix="/api/hjb", tags=["HJB"], dependencies=_auth)
app.include_router(market_data.router, prefix="/api/market-data", tags=["Market Data"], dependencies=_auth)
app.include_router(zcyc.router, prefix="/api/zcyc", tags=["ZCYC"], dependencies=_auth)
app.include_router(rudata.router, prefix="/api/rudata", tags=["RuData"], dependencies=_auth)
app.include_router(cbonds.router, prefix="/api/cbonds", tags=["Cbonds"], dependencies=_auth)
app.include_router(spectral_regime.router, prefix="/api/spectral-regime", tags=["Spectral Regime"], dependencies=_auth)
app.include_router(multivariate_hmm.router, prefix="/api/multivariate-hmm", tags=["Multivariate HMM"], dependencies=_auth)
app.include_router(database.router, prefix="/api/database", tags=["Database"], dependencies=_auth)
app.include_router(market_feeds.router, prefix="/api/market-feeds", tags=["Market Feeds"], dependencies=_auth)
app.include_router(macro_data.router, prefix="/api/macro-data", tags=["Macro Data"], dependencies=_auth)
app.include_router(crypto_data.router, prefix="/api/crypto-data", tags=["Crypto Data"], dependencies=_auth)
app.include_router(news_ai.router, prefix="/api/news-ai", tags=["News & AI"], dependencies=_auth)
app.include_router(calendar_utils.router, prefix="/api/calendar", tags=["Calendar"], dependencies=_auth)
app.include_router(security_tools.router, prefix="/api/security", tags=["Security Tools"], dependencies=_auth)
app.include_router(sharpe_stats.router, prefix="/api/sharpe-stats", tags=["Sharpe Statistics"], dependencies=_auth)
app.include_router(realized_kernels.router, prefix="/api/realized-kernels", tags=["Realized Kernels"], dependencies=_auth)
app.include_router(har.router, prefix="/api/har", tags=["HAR Model"], dependencies=_auth)
app.include_router(factor_analysis.router, prefix="/api/factor-analysis", tags=["Factor Analysis"], dependencies=_auth)
app.include_router(eigenportfolio.router, prefix="/api/eigenportfolio", tags=["Eigenportfolio"], dependencies=_auth)
app.include_router(pbo.router, prefix="/api/pbo", tags=["PBO/DSR"], dependencies=_auth)
app.include_router(alpha_stacking.router, prefix="/api/alpha-stacking", tags=["Alpha Stacking"], dependencies=_auth)
app.include_router(meta_labeling.router, prefix="/api/meta-labeling", tags=["Meta Labeling"], dependencies=_auth)
app.include_router(convex_portfolio.router, prefix="/api/convex-portfolio", tags=["Convex Portfolio"], dependencies=_auth)
app.include_router(black_litterman.router, prefix="/api/black-litterman", tags=["Black-Litterman"], dependencies=_auth)
app.include_router(adversarial_stress.router, prefix="/api/adversarial-stress", tags=["Adversarial Stress"], dependencies=_auth)
app.include_router(moexalgo.router, prefix="/api/moexalgo", tags=["MOEX ISS"], dependencies=_auth)
app.include_router(dadata.router, prefix="/api/dadata", tags=["DaData"], dependencies=_auth)
app.include_router(etf.router, prefix="/api/etf", tags=["ETF"], dependencies=_auth)
app.include_router(gemini.router, prefix="/api/gemini", tags=["Gemini AI"], dependencies=_auth)
app.include_router(secrets_api.router, prefix="/api/secrets", tags=["Secrets"], dependencies=[Depends(require_api_key), Depends(require_admin)])
app.include_router(repo.router, prefix="/api/repo", tags=["REPO"], dependencies=_auth)
app.include_router(risk.router, prefix="/api/risk", tags=["Risk Engine"], dependencies=_auth)
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"], dependencies=[Depends(require_api_key), Depends(require_admin)])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """Корневой endpoint — minimal info for uptime monitors."""
    return {"status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint (unauthenticated for Render probes)."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
