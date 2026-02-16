"""
API endpoints для анализа Eigenportfolios (PCA).
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.services.eigenportfolio_service import compute_eigenportfolios

router = APIRouter()


class EigenportfolioRequest(BaseModel):
    returns: List[List[float]] = Field(
        ..., description="Матрица доходностей T × N (строки=периоды, столбцы=активы)"
    )
    asset_names: Optional[List[str]] = Field(None, description="Названия активов")
    use_shrinkage: bool = Field(True, description="Применять Ledoit-Wolf shrinkage")
    n_components: Optional[int] = Field(None, ge=1, description="Число PC для реконструкции")
    portfolio_weights: Optional[List[float]] = Field(None, description="Веса портфеля для декомпозиции риска")

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
    result: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/decompose", response_model=EigenportfolioResponse)
async def decompose(request: EigenportfolioRequest):
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
    if request.portfolio_weights is not None:
        ret_matrix = request.returns
        n_assets = len(ret_matrix[0]) if ret_matrix else 0
        if len(request.portfolio_weights) != n_assets:
            raise HTTPException(
                status_code=400,
                detail=f"portfolio_weights длина {len(request.portfolio_weights)} != N активов {n_assets}"
            )

    try:
        result = compute_eigenportfolios(
            returns=request.returns,
            asset_names=request.asset_names,
            use_shrinkage=request.use_shrinkage,
            n_components=request.n_components,
            portfolio_weights=request.portfolio_weights,
        )
        return EigenportfolioResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "eigenportfolio"}
