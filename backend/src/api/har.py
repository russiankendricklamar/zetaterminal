"""
API endpoints для HAR модели прогнозирования волатильности.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.har_service import fit_har_model

router = APIRouter()


class HARRequest(BaseModel):
    rv: List[float] = Field(..., description="Ряд ежедневных реализованных дисперсий (RV)")
    bv: Optional[List[float]] = Field(None, description="Bipower Variation для HAR-RV-CJ (опционально)")
    log_transform: bool = Field(False, description="Применять log(RV) как зависимую переменную")
    forecast_horizons: List[int] = Field([1, 5, 22], description="Горизонты прогноза в днях")
    train_ratio: float = Field(0.8, ge=0.5, le=0.95, description="Доля обучающей выборки")

    model_config = {
        "json_schema_extra": {
            "example": {
                "rv": [0.0001, 0.00015, 0.00012, 0.0002, 0.00018],
                "log_transform": False,
                "forecast_horizons": [1, 5, 22],
                "train_ratio": 0.8,
            }
        }
    }


class HARResponse(BaseModel):
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/fit", response_model=HARResponse)
async def fit_har(request: HARRequest):
    """
    Оценивает HAR-RV и (опционально) HAR-RV-CJ модели прогнозирования волатильности.

    Возвращает:
    - Коэффициенты β с HAC SE (Newey-West) и t-статистиками
    - R² и скорректированный R²
    - IS/OOS метрики: RMSE, MAE, QLIKE
    - Прогнозы на h = 1, 5, 22 дня
    - Данные для графика: фактическая vs подогнанная волатильность
    """
    if request.bv is not None and len(request.bv) != len(request.rv):
        raise HTTPException(status_code=400, detail="rv и bv должны быть одинаковой длины")

    for h in request.forecast_horizons:
        if h < 1 or h > 252:
            raise HTTPException(status_code=400, detail="Горизонт прогноза должен быть от 1 до 252 дней")

    try:
        result = fit_har_model(
            rv=request.rv,
            bv=request.bv,
            log_transform=request.log_transform,
            forecast_horizons=request.forecast_horizons,
            train_ratio=request.train_ratio,
        )
        return HARResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка оценки: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "har"}
