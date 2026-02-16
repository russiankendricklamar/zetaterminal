"""
API endpoints для оценщиков реализованной волатильности.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.realized_kernels_service import compute_realized_kernels

router = APIRouter()


class RealizedKernelsRequest(BaseModel):
    prices: List[float] = Field(..., description="Ряд цен высокочастотных наблюдений (хронологический порядок)")
    kernel: str = Field("parzen", description="Ядро для RK: 'parzen', 'tukey-hanning', 'bartlett'")
    bandwidth: Optional[int] = Field(None, ge=1, description="Bandwidth H для RK (None = n^(3/5))")
    tsrv_scales: int = Field(5, ge=2, le=50, description="Количество масштабов K для TSRV")
    annualize: bool = Field(True, description="Приводить к годовой волатильности")
    periods_per_day: int = Field(390, ge=1, le=1440, description="Наблюдений в торговом дне (390 = минуты NYSE, 1 = дни)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "prices": [100.0, 100.02, 99.98, 100.05, 99.95, 100.10],
                "kernel": "parzen",
                "annualize": True,
                "periods_per_day": 390,
            }
        }
    }


class RealizedKernelsResponse(BaseModel):
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/estimate", response_model=RealizedKernelsResponse)
async def estimate_realized_kernels(request: RealizedKernelsRequest):
    """
    Вычисляет оценщики реализованной волатильности с поправкой на микроструктурный шум.

    Возвращает:
    - RV (наивный), BV (jump-robust), TSRV, MSRV, RK (ядерный)
    - Годовые волатильности для каждого оценщика
    - Тест на наличие скачков (BN-Shephard)
    - Сигнатурный график RV(Δ)
    - Оценку дисперсии шума ω²
    """
    if request.kernel not in ("parzen", "tukey-hanning", "bartlett"):
        raise HTTPException(status_code=400, detail="kernel должен быть 'parzen', 'tukey-hanning' или 'bartlett'")

    try:
        result = compute_realized_kernels(
            prices=request.prices,
            kernel=request.kernel,
            bandwidth=request.bandwidth,
            tsrv_scales=request.tsrv_scales,
            annualize=request.annualize,
            periods_per_day=request.periods_per_day,
        )
        return RealizedKernelsResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "realized-kernels"}
