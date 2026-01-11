"""
Pydantic schemas for request/response models.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ComputeRequest(BaseModel):
    """Базовая схема для вычислительных запросов."""
    pass


class ComputeResponse(BaseModel):
    """Базовая схема для ответов вычислений."""
    result: Dict[str, Any]
    status: str = "success"
    timestamp: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Схема для health check."""
    status: str
