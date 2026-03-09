"""
FastAPI приложение для Zeta Terminal Backend.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os

logger = logging.getLogger(__name__)

from src.utils.http_client import close_session
from src.middleware.auth import require_api_key
from src.middleware.rate_limit import limiter
from src.database.client import init_db

# Импортируем все роутеры
from src.api import backtest
from src.api import bond
from src.api import ccmv
from src.api import compute
from src.api import database
from src.api import forward
from src.api import hjb
from src.api import market_data
from src.api import multivariate_hmm
from src.api import portfolio
from src.api import rudata
from src.api import spectral_regime
from src.api import stress
from src.api import swap
from src.api import zcyc
from src.api import market_feeds
from src.api import macro_data
from src.api import crypto_data
from src.api import news_ai
from src.api import calendar_utils
from src.api import security_tools
from src.api import sharpe_stats
from src.api import realized_kernels
from src.api import har
from src.api import factor_analysis
from src.api import eigenportfolio
from src.api import pbo
from src.api import alpha_stacking
from src.api import meta_labeling
from src.api import convex_portfolio
from src.api import black_litterman
from src.api import adversarial_stress
from src.api import moexalgo
from src.api import dadata
from src.api import etf
from src.api import gemini
from src.api import secrets
from src.api import auth
from src.api import repo

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
    yield
    await close_session()


async def _seed_admin() -> None:
    """Create default admin user if no admin exists."""
    from sqlalchemy import select
    from src.database.sa_models import User
    from src.database.client import async_session_factory
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    try:
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.role == "admin")
            )
            if result.scalar_one_or_none():
                return

            admin_password = os.getenv("ADMIN_PASSWORD", "admin")
            admin = User(
                username="admin",
                domain_handle="admin@zetaterminal.dev",
                email="admin@zetaterminal.io",
                password_hash=pwd_context.hash(admin_password),
                role="admin",
                status="active",
                invite_code="ADMIN000",
            )
            session.add(admin)
            await session.commit()
            logger.info("Default admin user seeded")
    except Exception as e:
        logger.warning("Could not seed admin user: %s", e)


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
    allow_headers=["Content-Type", "X-API-Key"],
)

# Подключаем все роутеры (с обязательной аутентификацией по API-ключу)
_auth = [Depends(require_api_key)]

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"], dependencies=_auth)
app.include_router(bond.router, prefix="/api/bond", tags=["Bond"], dependencies=_auth)
app.include_router(swap.router, prefix="/api/swap", tags=["Swap"], dependencies=_auth)
app.include_router(forward.router, prefix="/api/forward", tags=["Forward"], dependencies=_auth)
app.include_router(compute.router, prefix="/api/compute", tags=["Compute"], dependencies=_auth)
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtest"], dependencies=_auth)
app.include_router(stress.router, prefix="/api/stress", tags=["Stress"], dependencies=_auth)
app.include_router(ccmv.router, prefix="/api/ccmv", tags=["CCMV"], dependencies=_auth)
app.include_router(hjb.router, prefix="/api/hjb", tags=["HJB"], dependencies=_auth)
app.include_router(market_data.router, prefix="/api/market-data", tags=["Market Data"], dependencies=_auth)
app.include_router(zcyc.router, prefix="/api/zcyc", tags=["ZCYC"], dependencies=_auth)
app.include_router(rudata.router, prefix="/api/rudata", tags=["RuData"], dependencies=_auth)
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
app.include_router(secrets.router, prefix="/api/secrets", tags=["Secrets"], dependencies=_auth)
app.include_router(repo.router, prefix="/api/repo", tags=["REPO"], dependencies=_auth)

# REMOVED: platform_services router — contains dangerous endpoints:
# open email relay, SSRF vectors, auth token proxy, open storage


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
