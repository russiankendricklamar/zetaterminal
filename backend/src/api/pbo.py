"""
API endpoints для PBO (Probability of Backtest Overfitting) и DSR.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.pbo_service import compute_pbo

router = APIRouter()


class PBORequest(BaseModel):
    strategy_returns: List[List[float]] = Field(
        ..., description="Матрица доходностей T × N (строки=периоды, столбцы=стратегии)"
    )
    n_splits: int = Field(16, ge=4, le=64, description="Число подмножеств S для CSCV (чётное)")
    annualize: int = Field(252, ge=1, description="Периодов в году для аннуализации SR")
    sr_benchmark: float = Field(0.0, description="Пороговый SR для PSR (годовой)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "strategy_returns": [[0.001, 0.002], [-0.001, 0.000], [0.002, 0.001]],
                "n_splits": 16,
                "annualize": 252,
                "sr_benchmark": 0.0,
            }
        }
    }


class PBOResponse(BaseModel):
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/analyze", response_model=PBOResponse)
async def analyze_pbo(request: PBORequest):
    """
    Полный анализ переобучения бэктеста.

    Возвращает:
    - PBO (CSCV): вероятность переобучения через Combinatorially Symmetric Cross-Validation
    - DSR: Deflated Sharpe Ratio с поправкой на число испытаний
    - MinBTL: минимальная длина бэктеста для достоверного SR
    - IS vs OOS scatter: деградация производительности
    - Логит-гистограмма OOS ранга
    - Статистика по каждой стратегии (SR, PSR)
    """
    try:
        result = compute_pbo(
            strategy_returns=request.strategy_returns,
            n_splits=request.n_splits,
            annualize=request.annualize,
            sr_benchmark=request.sr_benchmark,
        )
        return PBOResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "pbo"}
