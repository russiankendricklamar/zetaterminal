"""
API endpoints для CCMV оптимизации портфеля.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.services.ccmv_service import optimize_ccmv
from datetime import datetime
import numpy as np

router = APIRouter()


class CCMVRequest(BaseModel):
    """Запрос на CCMV оптимизацию."""
    R: List[List[float]] = Field(..., description="Матрица доходностей (time_steps x num_assets)")
    mu: List[float] = Field(..., description="Ожидаемые доходности активов")
    cov_matrix: List[List[float]] = Field(..., description="Ковариационная матрица")
    Delta: int = Field(..., gt=0, description="Максимальное количество активов в портфеле")
    bar_w: float = Field(..., gt=0, le=1, description="Максимальный вес на актив")
    gamma: float = Field(..., gt=0, description="Коэффициент неприятия риска (γ > 0)")
    method: str = Field(default='delta', description="Метод оптимизации: 'delta' или 'alpha'")
    asset_names: Optional[List[str]] = Field(None, description="Названия активов")
    
    class Config:
        schema_extra = {
            "example": {
                "R": [[0.01, 0.02, 0.015], [0.02, 0.01, 0.02], [0.015, 0.02, 0.01]],
                "mu": [0.10, 0.12, 0.08],
                "cov_matrix": [
                    [0.04, 0.02, 0.01],
                    [0.02, 0.05, 0.015],
                    [0.01, 0.015, 0.03]
                ],
                "Delta": 3,
                "bar_w": 0.25,
                "gamma": 2.0,
                "method": "delta",
                "asset_names": ["Asset1", "Asset2", "Asset3"]
            }
        }


class CCMVResponse(BaseModel):
    """Ответ с результатами CCMV оптимизации."""
    optimal_weights: List[float]
    clusters: List[Dict[str, Any]]
    portfolio_stats: Dict[str, float]
    method: str
    Delta: int
    gamma: float
    bar_w: float
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/optimize", response_model=CCMVResponse)
async def optimize_ccmv_portfolio(request: CCMVRequest):
    """
    Выполняет CCMV оптимизацию портфеля.
    
    Args:
        request: Параметры оптимизации
        
    Returns:
        Результаты оптимизации
    """
    try:
        # Валидация входных данных
        R = np.array(request.R)
        mu = np.array(request.mu)
        Sigma = np.array(request.cov_matrix)
        
        if len(mu) == 0:
            raise ValueError("Вектор доходностей не может быть пустым")
        
        if R.shape[1] != len(mu):
            raise ValueError(
                f"Размерность матрицы доходностей R {R.shape} "
                f"не соответствует количеству активов {len(mu)}"
            )
        
        if Sigma.shape != (len(mu), len(mu)):
            raise ValueError(
                f"Размерность ковариационной матрицы {Sigma.shape} "
                f"не соответствует количеству активов {len(mu)}"
            )
        
        if request.method not in ['delta', 'alpha']:
            raise ValueError(f"Метод должен быть 'delta' или 'alpha', получено: {request.method}")
        
        # Выполняем оптимизацию
        result = optimize_ccmv(
            R=R,
            mu=mu,
            Sigma=Sigma,
            Delta=request.Delta,
            bar_w=request.bar_w,
            gamma=request.gamma,
            method=request.method,
            asset_names=request.asset_names
        )
        
        return CCMVResponse(
            optimal_weights=result['optimal_weights'],
            clusters=result['clusters'],
            portfolio_stats=result['portfolio_stats'],
            method=result['method'],
            Delta=result['Delta'],
            gamma=result['gamma'],
            bar_w=result['bar_w']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при оптимизации: {str(e)}")


@router.get("/health")
async def ccmv_health():
    """Health check для CCMV сервиса."""
    return {"status": "healthy", "service": "ccmv"}
