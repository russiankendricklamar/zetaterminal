"""
API endpoints для вычислительных задач.
"""
import logging

from fastapi import APIRouter, Body, HTTPException, Request
from typing import List, Optional
from pydantic import Field
from src.models.schemas import ComputeRequest, ComputeResponse
from src.services.compute_service import ComputeService
from src.utils.financial_validation import FinancialBaseModel, MAX_DATA_POINTS
from src.middleware.rate_limit import limiter
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()
compute_service = ComputeService()


class GARCHRequest(FinancialBaseModel):
    """Схема запроса для GARCH моделирования."""
    returns: List[float] = Field(..., max_length=MAX_DATA_POINTS)
    omega: Optional[float] = Field(0.000025, gt=0, le=1.0)
    alpha: Optional[float] = Field(0.082, ge=0, le=1.0)
    beta: Optional[float] = Field(0.893, ge=0, le=1.0)
    initial_variance: Optional[float] = Field(None, gt=0, le=1.0)


@router.post("/statistics", response_model=ComputeResponse)
async def calculate_statistics(data: List[float] = Body(..., max_length=100000)):
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
        logger.error("Compute operation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid input parameters")


@router.post("/garch")
@limiter.limit("10/minute")
async def calculate_garch(http_request: Request, request: GARCHRequest):
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
        logger.error("Compute operation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid input parameters")


@router.get("/health")
async def compute_health():
    """Health check для вычислительного сервиса."""
    return {"status": "healthy", "service": "compute"}
