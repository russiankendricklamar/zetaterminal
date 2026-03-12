"""
API endpoints для Convex Portfolio Construction.
"""
import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.convex_portfolio_service import compute_convex_portfolio
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import FinancialBaseModel

router = APIRouter()

VALID_OBJECTIVES = {"min_variance", "max_sharpe", "mean_variance", "cvar", "risk_parity", "kelly"}


class ConvexPortfolioRequest(FinancialBaseModel):
    returns: list[list[float]] = Field(
        ..., description="Матрица T × N доходностей (строки=периоды, столбцы=активы)"
    )
    asset_names: list[str] | None = Field(None, description="Названия N активов")
    objectives: list[str] | None = Field(
        None,
        description="Задачи: min_variance, max_sharpe, cvar, risk_parity, kelly, mean_variance"
    )
    long_only: bool = Field(True, description="Только длинные позиции")
    lb: float = Field(0.0, ge=0.0, description="Нижняя граница весов")
    ub: float = Field(1.0, le=2.0, description="Верхняя граница весов")
    max_weight: float | None = Field(None, ge=0.0, le=1.0, description="Максимальный вес актива")
    target_return: float | None = Field(None, description="Минимальная ожидаемая доходность (дневная)")
    leverage: float = Field(1.0, ge=1.0, le=3.0, description="Максимальное плечо ||w||₁")
    cvar_alpha: float = Field(0.95, ge=0.5, le=0.999, description="Уровень доверия CVaR")
    risk_free: float = Field(0.0, description="Дневная безрисковая ставка")
    kelly_fraction: float = Field(0.5, gt=0.0, le=1.0, description="Дробный Kelly (0.5 = half-Kelly)")
    annualize: int = Field(252, ge=1, description="Периодов в году")
    n_frontier: int = Field(30, ge=5, le=100, description="Точек на эффективной границе")

    model_config = {
        "json_schema_extra": {
            "example": {
                "returns": [[0.001, 0.002, -0.001], [-0.001, 0.000, 0.002], [0.002, 0.001, 0.000]],
                "asset_names": ["SPY", "QQQ", "IEF"],
                "objectives": ["min_variance", "max_sharpe", "cvar", "risk_parity", "kelly"],
                "long_only": True,
                "max_weight": 0.4,
                "cvar_alpha": 0.95,
            }
        }
    }


class ConvexPortfolioResponse(BaseModel):
    result: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/optimize", response_model=ConvexPortfolioResponse)
@limiter.limit("5/minute")
@service_endpoint("Convex portfolio optimization")
async def optimize(request: Request, body: ConvexPortfolioRequest):
    """
    Convex Portfolio Optimization.

    Поддерживаемые задачи:
    - min_variance  : минимальная дисперсия
    - max_sharpe    : максимальный коэффициент Шарпа (Charnes-Cooper QP)
    - mean_variance : mean-variance с risk aversion γ=1
    - cvar          : минимальный CVaR на сценариях (LP)
    - risk_parity   : равный вклад риска (log-barrier, ERC)
    - kelly         : дробный Kelly (max ожидаемого log-роста)

    Плюс always: equal_weight baseline и эффективная граница.
    """
    # Validate objectives
    if body.objectives:
        invalid = set(body.objectives) - VALID_OBJECTIVES
        if invalid:
            raise HTTPException(status_code=400, detail=f"Неизвестные задачи: {invalid}")

    result = await asyncio.to_thread(lambda: compute_convex_portfolio(
        returns=body.returns,
        asset_names=body.asset_names,
        objectives=body.objectives,
        long_only=body.long_only,
        lb=body.lb,
        ub=body.ub,
        max_weight=body.max_weight,
        target_return=body.target_return,
        leverage=body.leverage,
        cvar_alpha=body.cvar_alpha,
        risk_free=body.risk_free,
        kelly_fraction=body.kelly_fraction,
        annualize=body.annualize,
        n_frontier=body.n_frontier,
    ))
    return ConvexPortfolioResponse(result=result)


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "convex_portfolio"}
