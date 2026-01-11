"""
API endpoints для вычислительных задач.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from src.models.schemas import ComputeRequest, ComputeResponse
from src.services.compute_service import ComputeService
from datetime import datetime

router = APIRouter()
compute_service = ComputeService()


class GARCHRequest(BaseModel):
    """Схема запроса для GARCH моделирования."""
    returns: List[float]
    omega: Optional[float] = 0.000025
    alpha: Optional[float] = 0.082
    beta: Optional[float] = 0.893
    initial_variance: Optional[float] = None


@router.post("/statistics", response_model=ComputeResponse)
async def calculate_statistics(data: List[float]):
    """
    Вычисляет статистику для массива данных.
    
    Args:
        data: Список числовых значений
        
    Returns:
        Статистические показатели
    """
    try:
        result = compute_service.calculate_statistics(data)
        return ComputeResponse(
            result=result,
            status="success",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/garch")
async def calculate_garch(request: GARCHRequest):
    """
    Вычисляет GARCH(1,1) модель волатильности.
    
    Args:
        request: Параметры GARCH модели
        
    Returns:
        Результаты GARCH моделирования
    """
    try:
        result = compute_service.calculate_garch(
            returns=request.returns,
            omega=request.omega,
            alpha=request.alpha,
            beta=request.beta,
            initial_variance=request.initial_variance
        )
        return {
            "result": result,
            "status": "success",
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def compute_health():
    """Health check для вычислительного сервиса."""
    return {"status": "healthy", "service": "compute"}
