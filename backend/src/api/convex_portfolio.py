"""
API endpoints для Convex Portfolio Construction.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.convex_portfolio_service import compute_convex_portfolio

router = APIRouter()

VALID_OBJECTIVES = {"min_variance", "max_sharpe", "mean_variance", "cvar", "risk_parity", "kelly"}


class ConvexPortfolioRequest(BaseModel):
    returns: List[List[float]] = Field(
        ..., description="Матрица T × N доходностей (строки=периоды, столбцы=активы)"
    )
    asset_names: Optional[List[str]] = Field(None, description="Названия N активов")
    objectives: Optional[List[str]] = Field(
        None,
        description="Задачи: min_variance, max_sharpe, cvar, risk_parity, kelly, mean_variance"
    )
    long_only: bool = Field(True, description="Только длинные позиции")
    lb: float = Field(0.0, ge=0.0, description="Нижняя граница весов")
    ub: float = Field(1.0, le=2.0, description="Верхняя граница весов")
    max_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Максимальный вес актива")
    target_return: Optional[float] = Field(None, description="Минимальная ожидаемая доходность (дневная)")
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
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/optimize", response_model=ConvexPortfolioResponse)
async def optimize(request: ConvexPortfolioRequest):
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
    if request.objectives:
        invalid = set(request.objectives) - VALID_OBJECTIVES
        if invalid:
            raise HTTPException(status_code=400, detail=f"Неизвестные задачи: {invalid}")

    try:
        result = compute_convex_portfolio(
            returns=request.returns,
            asset_names=request.asset_names,
            objectives=request.objectives,
            long_only=request.long_only,
            lb=request.lb,
            ub=request.ub,
            max_weight=request.max_weight,
            target_return=request.target_return,
            leverage=request.leverage,
            cvar_alpha=request.cvar_alpha,
            risk_free=request.risk_free,
            kelly_fraction=request.kelly_fraction,
            annualize=request.annualize,
            n_frontier=request.n_frontier,
        )
        return ConvexPortfolioResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка оптимизации: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "convex_portfolio"}
