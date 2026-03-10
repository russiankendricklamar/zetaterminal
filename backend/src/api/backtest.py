"""
API endpoints для бэктестинга портфеля.
"""
import logging

from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional, Dict, Any
from pydantic import Field
from src.services.backtest_service import run_backtest
from src.utils.financial_validation import FinancialBaseModel, MAX_ASSETS, MAX_CAPITAL
from src.middleware.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter()


class BacktestRequest(FinancialBaseModel):
    """Запрос на бэктестинг портфеля."""
    mu: List[float] = Field(..., max_length=MAX_ASSETS, description="Ожидаемые доходности активов")
    cov_matrix: List[List[float]] = Field(..., max_length=MAX_ASSETS, description="Ковариационная матрица")
    initial_capital: float = Field(1000000, gt=0, le=MAX_CAPITAL, description="Начальный капитал")
    risk_free_rate: float = Field(..., ge=-1, le=1, description="Безрисковая ставка")
    gamma: float = Field(..., gt=0, le=100, description="Коэффициент риск-аверсии")
    horizon_years: float = Field(1.0, gt=0, le=100, description="Горизонт инвестирования (годы)")
    n_steps: int = Field(252, ge=1, le=1000, description="Количество временных шагов")
    asset_names: Optional[List[str]] = Field(None, max_length=MAX_ASSETS, description="Названия активов")
    n_paths: int = Field(1000, ge=1, le=10000, description="Количество Монте-Карло траекторий")
    seed: Optional[int] = Field(None, description="Seed для воспроизводимости")


@router.post("/run", response_model=Dict[str, Any])
@limiter.limit("10/minute")
async def run_portfolio_backtest(http_request: Request, request: BacktestRequest):
    """
    Выполняет бэктест портфеля.
    """
    try:
        result = run_backtest(
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
        return result
    except ValueError as e:
        logger.error("Backtest validation error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid input parameters")
    except Exception as e:
        logger.error("Backtest failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
