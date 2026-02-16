"""
API endpoints для Time-Series vs Cross-Sectional факторного анализа.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.factor_analysis_service import run_factor_analysis

router = APIRouter()


class FactorAnalysisRequest(BaseModel):
    returns: List[List[float]] = Field(
        ..., description="Матрица доходностей T × N (строки=периоды, столбцы=активы)"
    )
    factors: List[List[float]] = Field(
        ..., description="Матрица факторов T × K"
    )
    asset_names: Optional[List[str]] = Field(None, description="Названия N активов")
    factor_names: Optional[List[str]] = Field(None, description="Названия K факторов")

    model_config = {
        "json_schema_extra": {
            "example": {
                "returns": [[0.01, 0.02], [-0.01, 0.00], [0.02, 0.01]],
                "factors": [[0.005], [-0.003], [0.008]],
                "asset_names": ["AAPL", "MSFT"],
                "factor_names": ["MKT"],
            }
        }
    }


class FactorAnalysisResponse(BaseModel):
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/analyze", response_model=FactorAnalysisResponse)
async def analyze_factors(request: FactorAnalysisRequest):
    """
    Двухшаговый Fama-MacBeth факторный анализ.

    Шаг 1 — TS регрессии: оценка факторных нагрузок β, GRS тест (H₀: все αᵢ=0).
    Шаг 2 — CS регрессии: оценка факторных премий λ (Shanken SE).

    Возвращает:
    - Матрицу β (N × K) с t-статистиками
    - GRS F-статистику и p-value
    - Риск-премии λ с FM и Shanken SE
    - Ценовые ошибки per asset
    - R² (TS и CS)
    """
    try:
        result = run_factor_analysis(
            returns=request.returns,
            factors=request.factors,
            asset_names=request.asset_names,
            factor_names=request.factor_names,
        )
        return FactorAnalysisResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "factor-analysis"}
