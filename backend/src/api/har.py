"""
API endpoints для HAR модели прогнозирования волатильности.
"""
import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.har_service import fit_har_model
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import FinancialBaseModel

router = APIRouter()


class HARRequest(FinancialBaseModel):
    rv: list[float] = Field(..., description="Ряд ежедневных реализованных дисперсий (RV)")
    bv: list[float] | None = Field(None, description="Bipower Variation для HAR-RV-CJ (опционально)")
    log_transform: bool = Field(False, description="Применять log(RV) как зависимую переменную")
    forecast_horizons: list[int] = Field([1, 5, 22], description="Горизонты прогноза в днях")
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
    result: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/fit", response_model=HARResponse)
@limiter.limit("10/minute")
@service_endpoint("Fit Har")
async def fit_har(http_request: Request, request: HARRequest):
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

    result = await asyncio.to_thread(lambda: fit_har_model(
        rv=request.rv,
        bv=request.bv,
        log_transform=request.log_transform,
        forecast_horizons=request.forecast_horizons,
        train_ratio=request.train_ratio,
    ))
    return HARResponse(result=result)
    return {"status": "healthy", "service": "har"}
