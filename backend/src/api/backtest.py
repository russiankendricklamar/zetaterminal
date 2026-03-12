"""
API endpoints для бэктестинга портфеля.
"""
import asyncio
from typing import Any, Literal

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.backtest_service import (
    run_backtest,
    run_historical_backtest,
    walk_forward_optimization,
)
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import MAX_ASSETS, MAX_CAPITAL, MAX_DATA_POINTS, FinancialBaseModel

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


class HistoricalBacktestRequest(FinancialBaseModel):
    """Запрос на исторический бэктест."""
    historical_prices: list[list[float]] = Field(
        ..., max_length=MAX_DATA_POINTS, description="T x N матрица дневных цен"
    )
    asset_names: list[str] | None = Field(None, max_length=MAX_ASSETS, description="Названия активов")
    rebalance_frequency: Literal["daily", "weekly", "monthly", "quarterly"] = Field(
        "monthly", description="Частота ребалансировки"
    )
    strategy_type: Literal["equal_weight", "min_variance", "risk_parity", "max_sharpe", "custom"] = Field(
        "equal_weight", description="Тип стратегии"
    )
    initial_weights: list[float] | None = Field(None, max_length=MAX_ASSETS, description="Начальные веса")
    lookback_window: int = Field(60, ge=10, le=504, description="Окно для оптимизации (дней)")
    transaction_cost_bps: float = Field(10.0, ge=0, le=100, description="Транзакционные издержки (bps)")
    risk_free_rate: float = Field(0.05, ge=-1, le=1, description="Безрисковая ставка (годовая)")
    initial_capital: float = Field(1_000_000, gt=0, le=MAX_CAPITAL, description="Начальный капитал")


class WalkForwardRequest(FinancialBaseModel):
    """Запрос на walk-forward оптимизацию."""
    historical_prices: list[list[float]] = Field(
        ..., max_length=MAX_DATA_POINTS, description="T x N матрица дневных цен"
    )
    asset_names: list[str] | None = Field(None, max_length=MAX_ASSETS, description="Названия активов")
    in_sample_window: int = Field(252, ge=30, le=1260, description="IS окно (дней)")
    out_of_sample_window: int = Field(63, ge=5, le=252, description="OOS окно (дней)")
    optimization_method: Literal["min_variance", "risk_parity", "max_sharpe"] = Field(
        "max_sharpe", description="Метод оптимизации"
    )
    step_size: int | None = Field(None, ge=1, le=252, description="Шаг сдвига (дней)")
    transaction_cost_bps: float = Field(10.0, ge=0, le=100, description="Транзакционные издержки (bps)")
    risk_free_rate: float = Field(0.05, ge=-1, le=1, description="Безрисковая ставка")
    initial_capital: float = Field(1_000_000, gt=0, le=MAX_CAPITAL, description="Начальный капитал")


@router.post("/run", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Backtest")
async def run_portfolio_backtest(http_request: Request, request: BacktestRequest):
    """
    Выполняет бэктест портфеля (Монте-Карло).
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


@router.post("/historical", response_model=dict[str, Any])
@limiter.limit("5/minute")
@service_endpoint("Historical Backtest")
async def run_historical_backtest_endpoint(http_request: Request, request: HistoricalBacktestRequest):
    """Выполняет исторический бэктест на реальных ценах."""
    return await asyncio.to_thread(
        run_historical_backtest,
        historical_prices=request.historical_prices,
        asset_names=request.asset_names,
        rebalance_frequency=request.rebalance_frequency,
        strategy_type=request.strategy_type,
        initial_weights=request.initial_weights,
        lookback_window=request.lookback_window,
        transaction_cost_bps=request.transaction_cost_bps,
        risk_free_rate=request.risk_free_rate,
        initial_capital=request.initial_capital,
    )


@router.post("/walk-forward", response_model=dict[str, Any])
@limiter.limit("3/minute")
@service_endpoint("Walk-Forward Optimization")
async def run_walk_forward_endpoint(http_request: Request, request: WalkForwardRequest):
    """Выполняет walk-forward оптимизацию."""
    return await asyncio.to_thread(
        walk_forward_optimization,
        historical_prices=request.historical_prices,
        asset_names=request.asset_names,
        in_sample_window=request.in_sample_window,
        out_of_sample_window=request.out_of_sample_window,
        optimization_method=request.optimization_method,
        step_size=request.step_size,
        transaction_cost_bps=request.transaction_cost_bps,
        risk_free_rate=request.risk_free_rate,
        initial_capital=request.initial_capital,
    )
