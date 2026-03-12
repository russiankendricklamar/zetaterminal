"""
API endpoints для анализа Eigenportfolios (PCA).
"""
import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.eigenportfolio_service import compute_eigenportfolios
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import FinancialBaseModel

router = APIRouter()


class EigenportfolioRequest(FinancialBaseModel):
    returns: list[list[float]] = Field(
        ..., description="Матрица доходностей T × N (строки=периоды, столбцы=активы)"
    )
    asset_names: list[str] | None = Field(None, description="Названия активов")
    use_shrinkage: bool = Field(True, description="Применять Ledoit-Wolf shrinkage")
    n_components: int | None = Field(None, ge=1, description="Число PC для реконструкции")
    portfolio_weights: list[float] | None = Field(None, description="Веса портфеля для декомпозиции риска")

    model_config = {
        "json_schema_extra": {
            "example": {
                "returns": [[0.01, 0.02, -0.01], [-0.01, 0.00, 0.02], [0.02, 0.01, 0.00]],
                "asset_names": ["AAPL", "MSFT", "GOOG"],
                "use_shrinkage": True,
            }
        }
    }


class EigenportfolioResponse(BaseModel):
    result: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/decompose", response_model=EigenportfolioResponse)
@limiter.limit("10/minute")
@service_endpoint("Eigenportfolio decomposition")
async def decompose(request: Request, body: EigenportfolioRequest):
    """
    PCA декомпозиция ковариационной матрицы.

    Возвращает:
    - Собственные значения и векторы (eigenportfolio weights)
    - Explained variance (scree plot)
    - Marchenko-Pastur bounds для отделения сигнала от шума
    - Ledoit-Wolf shrinkage коэффициент
    - Тепловую карту нагрузок (loadings)
    - Декомпозицию риска портфеля по PC
    - Ошибку реконструкции Σ с K компонентами
    """
    if body.portfolio_weights is not None:
        ret_matrix = body.returns
        n_assets = len(ret_matrix[0]) if ret_matrix else 0
        if len(body.portfolio_weights) != n_assets:
            raise HTTPException(
                status_code=400,
                detail=f"portfolio_weights длина {len(body.portfolio_weights)} != N активов {n_assets}"
            )

    result = await asyncio.to_thread(lambda: compute_eigenportfolios(
        returns=body.returns,
        asset_names=body.asset_names,
        use_shrinkage=body.use_shrinkage,
        n_components=body.n_components,
        portfolio_weights=body.portfolio_weights,
    ))
    return EigenportfolioResponse(result=result)


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "eigenportfolio"}
