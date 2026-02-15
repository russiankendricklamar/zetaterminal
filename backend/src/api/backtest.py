"""
API endpoints для бэктестинга портфеля.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.services.backtest_service import run_backtest

router = APIRouter()


class BacktestRequest(BaseModel):
    """Запрос на бэктестинг портфеля."""
    mu: List[float] = Field(..., description="Ожидаемые доходности активов")
    cov_matrix: List[List[float]] = Field(..., description="Ковариационная матрица")
    initial_capital: float = Field(1000000, description="Начальный капитал")
    risk_free_rate: float = Field(..., description="Безрисковая ставка")
    gamma: float = Field(..., description="Коэффициент риск-аверсии")
    horizon_years: float = Field(1.0, description="Горизонт инвестирования (годы)")
    n_steps: int = Field(252, description="Количество временных шагов")
    asset_names: Optional[List[str]] = Field(None, description="Названия активов")
    n_paths: int = Field(1000, description="Количество Монте-Карло траекторий")
    seed: Optional[int] = Field(None, description="Seed для воспроизводимости")


@router.post("/run", response_model=Dict[str, Any])
async def run_portfolio_backtest(request: BacktestRequest):
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
