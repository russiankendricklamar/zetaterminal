"""
FastAPI приложение для Stochastic Dashboard Backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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
from src.api import spectral_regime
from src.api import stress
from src.api import swap
from src.api import zcyc

# Создаем FastAPI приложение
app = FastAPI(
    title="Stochastic Dashboard API",
    description="Backend API для Stochastic Dashboard",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(bond.router, prefix="/api/bond", tags=["Bond"])
app.include_router(swap.router, prefix="/api/swap", tags=["Swap"])
app.include_router(forward.router, prefix="/api/forward", tags=["Forward"])
app.include_router(compute.router, prefix="/api/compute", tags=["Compute"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtest"])
app.include_router(stress.router, prefix="/api/stress", tags=["Stress"])
app.include_router(ccmv.router, prefix="/api/ccmv", tags=["CCMV"])
app.include_router(hjb.router, prefix="/api/hjb", tags=["HJB"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["Market Data"])
app.include_router(zcyc.router, prefix="/api/zcyc", tags=["ZCYC"])
app.include_router(spectral_regime.router, prefix="/api/spectral-regime", tags=["Spectral Regime"])
app.include_router(multivariate_hmm.router, prefix="/api/multivariate-hmm", tags=["Multivariate HMM"])
app.include_router(database.router, prefix="/api/database", tags=["Database"])


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Stochastic Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
