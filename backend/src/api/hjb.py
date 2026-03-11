"""
API endpoints для HJB оптимизации портфеля.
"""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.hjb_service import optimize_hjb
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import (
    MAX_ASSETS,
    MAX_CAPITAL,
    MAX_MONTE_CARLO_PATHS,
    MAX_MONTE_CARLO_STEPS,
    FinancialBaseModel,
)

router = APIRouter()


class MonteCarloParams(FinancialBaseModel):
    """Bounded Monte Carlo simulation parameters."""
    initial_capital: float = Field(1_000_000, gt=0, le=MAX_CAPITAL)
    horizon_years: float = Field(1.0, gt=0, le=100)
    n_paths: int = Field(5000, ge=1, le=MAX_MONTE_CARLO_PATHS)
    n_steps: int = Field(252, ge=1, le=MAX_MONTE_CARLO_STEPS)
    random_seed: int | None = Field(42)


class HJBRequest(FinancialBaseModel):
    """Запрос на HJB оптимизацию."""
    mu: list[float] = Field(..., max_length=MAX_ASSETS, description="Ожидаемые доходности активов")
    cov_matrix: list[list[float]] = Field(..., max_length=MAX_ASSETS, description="Ковариационная матрица")
    risk_free_rate: float = Field(..., ge=-1, le=1, description="Безрисковая ставка (в долях)")
    gamma: float = Field(..., gt=0, le=100, description="Коэффициент риск-аверсии (γ > 0)")
    asset_names: list[str] | None = Field(None, max_length=MAX_ASSETS, description="Названия активов")
    monte_carlo: MonteCarloParams | None = Field(None, description="Параметры Монте-Карло симуляции")

    class Config:
        schema_extra = {
            "example": {
                "mu": [0.10, 0.12, 0.08],
                "cov_matrix": [[0.04, 0.02, 0.01], [0.02, 0.05, 0.015], [0.01, 0.015, 0.03]],
                "risk_free_rate": 0.045, "gamma": 2.0,
                "asset_names": ["Asset1", "Asset2", "Asset3"],
                "monte_carlo": {"initial_capital": 1000000, "horizon_years": 1.0, "n_paths": 5000, "n_steps": 252, "random_seed": 42}
            }
        }


class HJBResponse(BaseModel):
    """Ответ с результатами HJB оптимизации."""
    portfolio_stats: dict[str, Any]
    monte_carlo: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/optimize", response_model=HJBResponse)
@limiter.limit("10/minute")
@service_endpoint("HJB optimization")
async def optimize_hjb_portfolio(http_request: Request, request: HJBRequest):
    """Выполняет HJB оптимизацию портфеля."""
    mu = request.mu
    cov_matrix = request.cov_matrix

    if len(mu) == 0:
        raise ValueError("Вектор доходностей не может быть пустым")
    if len(cov_matrix) != len(mu):
        raise ValueError(f"Размерность ковариационной матрицы {len(cov_matrix)} не соответствует количеству активов {len(mu)}")
    for row in cov_matrix:
        if len(row) != len(mu):
            raise ValueError("Ковариационная матрица должна быть квадратной")

    mc_params = request.monte_carlo.model_dump() if request.monte_carlo else None
    result = optimize_hjb(
        mu=mu, cov_matrix=cov_matrix, risk_free_rate=request.risk_free_rate,
        gamma=request.gamma, asset_names=request.asset_names, monte_carlo_params=mc_params
    )

    return HJBResponse(portfolio_stats=result['portfolio_stats'], monte_carlo=result.get('monte_carlo'))


@router.get("/health")
async def hjb_health():
    """Health check для HJB сервиса."""
    return {"status": "healthy", "service": "hjb"}
