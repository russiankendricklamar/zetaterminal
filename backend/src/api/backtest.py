"""
API endpoints для бэктестинга портфеля.
"""
from typing import Any

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.backtest_service import run_backtest
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import MAX_ASSETS, MAX_CAPITAL, FinancialBaseModel

router = APIRouter()


class BacktestRequest(FinancialBaseModel):
    """Запрос на бэктестинг портфеля."""
    mu: list[float] = Field(..., max_length=MAX_ASSETS, description="Ожидаемые доходности активов")
    cov_matrix: list[list[float]] = Field(..., max_length=MAX_ASSETS, description="Ковариационная матрица")
    initial_capital: float = Field(1000000, gt=0, le=MAX_CAPITAL, description="Начальный капитал")
    risk_free_rate: float = Field(..., ge=-1, le=1, description="Безрисковая ставка")
    gamma: float = Field(..., gt=0, le=100, description="Коэффициент риск-аверсии")
    horizon_years: float = Field(1.0, gt=0, le=100, description="Горизонт инвестирования (годы)")
    n_steps: int = Field(252, ge=1, le=1000, description="Количество временных шагов")
    asset_names: list[str] | None = Field(None, max_length=MAX_ASSETS, description="Названия активов")
    n_paths: int = Field(1000, ge=1, le=10000, description="Количество Монте-Карло траекторий")
    seed: int | None = Field(None, description="Seed для воспроизводимости")


@router.post("/run", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Backtest")
async def run_portfolio_backtest(http_request: Request, request: BacktestRequest):
    """
    Выполняет бэктест портфеля.
    """
    return run_backtest(
        mu=request.mu,
        cov_matrix=request.cov_matrix,
        initial_capital=request.initial_capital,
        risk_free_rate=request.risk_free_rate,
        gamma=request.gamma,
        horizon_years=request.horizon_years,
        n_steps=request.n_steps,
        asset_names=request.asset_names,
        n_paths=request.n_paths,
        seed=request.seed
    )
