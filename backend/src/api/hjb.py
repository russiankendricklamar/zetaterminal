"""
API endpoints для HJB оптимизации портфеля.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.services.hjb_service import optimize_hjb
from datetime import datetime

router = APIRouter()


class HJBRequest(BaseModel):
    """Запрос на HJB оптимизацию."""
    mu: List[float] = Field(..., description="Ожидаемые доходности активов")
    cov_matrix: List[List[float]] = Field(..., description="Ковариационная матрица")
    risk_free_rate: float = Field(..., description="Безрисковая ставка (в долях)")
    gamma: float = Field(..., gt=0, description="Коэффициент риск-аверсии (γ > 0)")
    asset_names: Optional[List[str]] = Field(None, description="Названия активов")
    monte_carlo: Optional[Dict[str, Any]] = Field(None, description="Параметры Монте-Карло симуляции")
    
    class Config:
        schema_extra = {
            "example": {
                "mu": [0.10, 0.12, 0.08],
                "cov_matrix": [
                    [0.04, 0.02, 0.01],
                    [0.02, 0.05, 0.015],
                    [0.01, 0.015, 0.03]
                ],
                "risk_free_rate": 0.045,
                "gamma": 2.0,
                "asset_names": ["Asset1", "Asset2", "Asset3"],
                "monte_carlo": {
                    "initial_capital": 1000000,
                    "horizon_years": 1.0,
                    "n_paths": 5000,
                    "n_steps": 252,
                    "random_seed": 42
                }
            }
        }


class HJBResponse(BaseModel):
    """Ответ с результатами HJB оптимизации."""
    portfolio_stats: Dict[str, Any]
    monte_carlo: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


@router.post("/optimize", response_model=HJBResponse)
async def optimize_hjb_portfolio(request: HJBRequest):
    """
    Выполняет HJB оптимизацию портфеля.
    
    Args:
        request: Параметры оптимизации
        
    Returns:
        Результаты оптимизации и Монте-Карло симуляции
    """
    try:
        # Валидация входных данных
        mu = request.mu
        cov_matrix = request.cov_matrix
        
        if len(mu) == 0:
            raise ValueError("Вектор доходностей не может быть пустым")
        
        if len(cov_matrix) != len(mu):
            raise ValueError(
                f"Размерность ковариационной матрицы {len(cov_matrix)} "
                f"не соответствует количеству активов {len(mu)}"
            )
        
        for row in cov_matrix:
            if len(row) != len(mu):
                raise ValueError("Ковариационная матрица должна быть квадратной")
        
        # Выполняем оптимизацию
        result = optimize_hjb(
            mu=mu,
            cov_matrix=cov_matrix,
            risk_free_rate=request.risk_free_rate,
            gamma=request.gamma,
            asset_names=request.asset_names,
            monte_carlo_params=request.monte_carlo
        )
        
        return HJBResponse(
            portfolio_stats=result['portfolio_stats'],
            monte_carlo=result.get('monte_carlo')
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при оптимизации: {str(e)}")


@router.get("/health")
async def hjb_health():
    """Health check для HJB сервиса."""
    return {"status": "healthy", "service": "hjb"}
