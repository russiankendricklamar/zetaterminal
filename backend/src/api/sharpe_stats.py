"""
API endpoints для статистического анализа коэффициента Шарпа.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.sharpe_stats_service import compute_sharpe_stats

router = APIRouter()


class SharpeStatsRequest(BaseModel):
    returns: List[float] = Field(..., description="Ряд периодических доходностей (в долях, напр. 0.01 = 1%)")
    risk_free_rate: float = Field(0.0, ge=0.0, description="Безрисковая ставка годовая (в долях)")
    periods_per_year: int = Field(252, ge=1, le=365, description="Периодов в году: 252=дни, 52=недели, 12=месяцы")
    benchmark_sr: float = Field(0.0, description="Пороговое SR для PSR (годовое)")
    n_trials: int = Field(1, ge=1, le=10000, description="Число стратегий для DSR (поправка на data mining)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "returns": [0.001, -0.002, 0.003, 0.0015, -0.001],
                "risk_free_rate": 0.05,
                "periods_per_year": 252,
                "benchmark_sr": 1.0,
                "n_trials": 1,
            }
        }
    }


class SharpeStatsResponse(BaseModel):
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/analyze", response_model=SharpeStatsResponse)
async def analyze_sharpe(request: SharpeStatsRequest):
    """
    Полный статистический анализ коэффициента Шарпа.

    Возвращает:
    - Годовой SR с SE (IID и с поправкой на ненормальность)
    - t-статистику и p-value для H₀: SR = 0
    - Доверительные интервалы 95%/99%
    - Probabilistic Sharpe Ratio (PSR) и Deflated Sharpe Ratio (DSR)
    - Данные для PSR-кривой и распределения SR под H₀
    """
    try:
        result = compute_sharpe_stats(
            returns=request.returns,
            risk_free_rate=request.risk_free_rate,
            periods_per_year=request.periods_per_year,
            benchmark_sr=request.benchmark_sr,
            n_trials=request.n_trials,
        )
        return SharpeStatsResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "sharpe-stats"}
