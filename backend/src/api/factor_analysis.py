"""
API endpoints для Time-Series vs Cross-Sectional факторного анализа.
"""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.factor_analysis_service import run_factor_analysis
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import FinancialBaseModel

router = APIRouter()


class FactorAnalysisRequest(FinancialBaseModel):
    returns: list[list[float]] = Field(
        ..., description="Матрица доходностей T × N (строки=периоды, столбцы=активы)"
    )
    factors: list[list[float]] = Field(
        ..., description="Матрица факторов T × K"
    )
    asset_names: list[str] | None = Field(None, description="Названия N активов")
    factor_names: list[str] | None = Field(None, description="Названия K факторов")

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
    result: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/analyze", response_model=FactorAnalysisResponse)
@limiter.limit("10/minute")
@service_endpoint("Factor analysis")
async def analyze_factors(http_request: Request, request: FactorAnalysisRequest):
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
    result = run_factor_analysis(
        returns=request.returns,
        factors=request.factors,
        asset_names=request.asset_names,
        factor_names=request.factor_names,
    )
    return FactorAnalysisResponse(result=result)


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "factor-analysis"}
