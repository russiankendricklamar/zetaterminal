"""
API endpoints для вычислительных задач.
"""
from fastapi import APIRouter, HTTPException
from typing import List
from src.models.schemas import ComputeRequest, ComputeResponse
from src.services.compute_service import ComputeService
from datetime import datetime

router = APIRouter()
compute_service = ComputeService()


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


@router.get("/health")
async def compute_health():
    """Health check для вычислительного сервиса."""
    return {"status": "healthy", "service": "compute"}
