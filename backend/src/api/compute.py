"""
API endpoints для вычислительных задач.
"""
import asyncio
from datetime import datetime

from fastapi import APIRouter, Body, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.models.schemas import ComputeResponse
from src.services.compute_service import ComputeService
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import MAX_DATA_POINTS, FinancialBaseModel

router = APIRouter()
compute_service = ComputeService()


class GARCHRequest(FinancialBaseModel):
    """Схема запроса для GARCH моделирования."""
    returns: list[float] = Field(..., max_length=MAX_DATA_POINTS)
    omega: float | None = Field(0.000025, gt=0, le=1.0)
    alpha: float | None = Field(0.082, ge=0, le=1.0)
    beta: float | None = Field(0.893, ge=0, le=1.0)
    initial_variance: float | None = Field(None, gt=0, le=1.0)


@router.post("/statistics", response_model=ComputeResponse)
@limiter.limit("10/minute")
@service_endpoint("Statistics computation")
async def calculate_statistics(request: Request, data: list[float] = Body(..., max_length=MAX_DATA_POINTS)):
    """
    Вычисляет статистику для массива данных.

    Args:
        data: Список числовых значений

    Returns:
        Статистические показатели
    """
    result = await asyncio.to_thread(compute_service.calculate_statistics, data)
    return ComputeResponse(
        result=result,
        status="success",
        timestamp=datetime.now()
    )


@router.post("/garch")
@limiter.limit("10/minute")
@service_endpoint("GARCH computation")
async def calculate_garch(request: Request, body: GARCHRequest):
    """
    Вычисляет GARCH(1,1) модель волатильности.

    Args:
        body: Параметры GARCH модели

    Returns:
        Результаты GARCH моделирования
    """
    result = compute_service.calculate_garch(
        returns=body.returns,
        omega=body.omega,
        alpha=body.alpha,
        beta=body.beta,
        initial_variance=body.initial_variance
    )
    return {
        "result": result,
        "status": "success",
        "timestamp": datetime.now()
    }


@router.get("/health")
async def compute_health():
    """Health check для вычислительного сервиса."""
    return {"status": "healthy", "service": "compute"}
