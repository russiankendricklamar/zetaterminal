"""
API endpoints для Orthogonal Alpha Stacking.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.alpha_stacking_service import compute_alpha_stacking

router = APIRouter()


class AlphaStackingRequest(BaseModel):
    panel_signals: List[List[List[float]]] = Field(
        ...,
        description="Матрица T × N_assets × N_signals — значения сигналов (z-scores, ранки)"
    )
    panel_fwd_returns: List[List[float]] = Field(
        ...,
        description="Матрица T × N_assets — форвардные доходности (горизонт 1 период)"
    )
    signal_names: Optional[List[str]] = Field(None, description="Названия N_signals сигналов")
    ortho_method: str = Field("sequential", description="'sequential' (Gram-Schmidt) или 'pairwise'")
    ic_horizons: Optional[List[int]] = Field(None, description="Горизонты для IC decay [1,5,10,21]")
    shrinkage: float = Field(0.3, ge=0.0, le=1.0, description="Shrinkage к равным весам (0=pure IR², 1=equal)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "panel_signals": [
                    [[0.5, -0.3, 0.1], [0.2, 0.4, -0.1]],
                    [[-0.1, 0.3, 0.2], [0.4, -0.2, 0.3]],
                ],
                "panel_fwd_returns": [
                    [0.01, -0.005],
                    [-0.002, 0.008],
                ],
                "signal_names": ["Momentum", "Reversal", "Quality"],
                "ortho_method": "sequential",
                "shrinkage": 0.3,
            }
        }
    }


class AlphaStackingResponse(BaseModel):
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/analyze", response_model=AlphaStackingResponse)
async def analyze(request: AlphaStackingRequest):
    """
    Orthogonal Alpha Stacking.

    Возвращает:
    - IC/IR до и после ортогонализации для каждого сигнала
    - Cross-IC матрицу (мера redundancy) до и после
    - IR²-proportional веса стэка с shrinkage
    - IC decay по горизонтам
    - IC стэкингового сигнала во времени
    """
    try:
        result = compute_alpha_stacking(
            panel_signals=request.panel_signals,
            panel_fwd_returns=request.panel_fwd_returns,
            signal_names=request.signal_names,
            ortho_method=request.ortho_method,
            ic_horizons=request.ic_horizons or [1, 5, 10, 21],
            shrinkage=request.shrinkage,
        )
        return AlphaStackingResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "alpha_stacking"}
