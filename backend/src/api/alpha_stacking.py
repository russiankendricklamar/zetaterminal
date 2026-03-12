"""
API endpoints для Orthogonal Alpha Stacking.
"""
import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.alpha_stacking_service import compute_alpha_stacking
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import FinancialBaseModel

router = APIRouter()


class AlphaStackingRequest(FinancialBaseModel):
    panel_signals: list[list[list[float]]] = Field(
        ...,
        description="Матрица T × N_assets × N_signals — значения сигналов (z-scores, ранки)"
    )
    panel_fwd_returns: list[list[float]] = Field(
        ...,
        description="Матрица T × N_assets — форвардные доходности (горизонт 1 период)"
    )
    signal_names: list[str] | None = Field(None, description="Названия N_signals сигналов")
    ortho_method: str = Field("sequential", description="'sequential' (Gram-Schmidt) или 'pairwise'")
    ic_horizons: list[int] | None = Field(None, description="Горизонты для IC decay [1,5,10,21]")
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
    result: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/analyze", response_model=AlphaStackingResponse)
@limiter.limit("10/minute")
@service_endpoint("Alpha stacking")
async def analyze(request: Request, body: AlphaStackingRequest):
    """
    Orthogonal Alpha Stacking.

    Возвращает:
    - IC/IR до и после ортогонализации для каждого сигнала
    - Cross-IC матрицу (мера redundancy) до и после
    - IR²-proportional веса стэка с shrinkage
    - IC decay по горизонтам
    - IC стэкингового сигнала во времени
    """
    result = await asyncio.to_thread(lambda: compute_alpha_stacking(
        panel_signals=body.panel_signals,
        panel_fwd_returns=body.panel_fwd_returns,
        signal_names=body.signal_names,
        ortho_method=body.ortho_method,
        ic_horizons=body.ic_horizons or [1, 5, 10, 21],
        shrinkage=body.shrinkage,
    ))
    return AlphaStackingResponse(result=result)


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "alpha_stacking"}
