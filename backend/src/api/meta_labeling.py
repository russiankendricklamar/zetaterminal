"""
API endpoints для Meta-Labeling (Signal Quality Control).
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.meta_labeling_service import compute_meta_labeling

router = APIRouter()


class MetaLabelingRequest(BaseModel):
    prices: List[float] = Field(
        ..., description="Ценовой ряд (T,) — закрытия или mid-цены"
    )
    pt_multiplier: float = Field(1.5, gt=0, description="Profit-take: pt × daily_vol")
    sl_multiplier: float = Field(1.0, gt=0, description="Stop-loss: sl × daily_vol")
    max_holding: int = Field(5, ge=1, le=100, description="Максимальный горизонт удержания (баров)")
    vol_window: int = Field(20, ge=5, le=252, description="Окно rolling vol для нормировки барьеров")
    train_ratio: float = Field(0.7, gt=0.1, lt=0.95, description="Доля обучающей выборки")
    regularization: float = Field(0.01, ge=1e-6, description="L2 λ для мета-модели")
    meta_threshold: float = Field(0.5, ge=0.1, le=0.9, description="Порог вероятности для открытия позиции")

    model_config = {
        "json_schema_extra": {
            "example": {
                "prices": [100.0, 100.5, 101.2, 100.8, 99.9],
                "pt_multiplier": 1.5,
                "sl_multiplier": 1.0,
                "max_holding": 5,
                "meta_threshold": 0.5,
            }
        }
    }


class MetaLabelingResponse(BaseModel):
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/analyze", response_model=MetaLabelingResponse)
async def analyze(request: MetaLabelingRequest):
    """
    Meta-Labeling анализ.

    Возвращает:
    - Triple-barrier метки (+1/-1/0) для ценового ряда
    - Первичную модель (momentum side rule)
    - Meta-модель (логистическая регрессия предсказывает P(profitable))
    - Precision/recall/F1 и финансовые метрики (Sharpe до и после фильтрации)
    - Кривую equity (baseline vs meta-filtered)
    - Precision-recall curve (threshold sweep)
    - Feature importances мета-модели
    """
    try:
        result = compute_meta_labeling(
            prices=request.prices,
            pt_multiplier=request.pt_multiplier,
            sl_multiplier=request.sl_multiplier,
            max_holding=request.max_holding,
            vol_window=request.vol_window,
            train_ratio=request.train_ratio,
            regularization=request.regularization,
            meta_threshold=request.meta_threshold,
        )
        return MetaLabelingResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "meta_labeling"}
