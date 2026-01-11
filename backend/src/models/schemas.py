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


class Position(BaseModel):
    """Схема позиции в портфеле."""
    symbol: str
    name: str
    price: float
    dayChange: float
    notional: float
    allocation: float
    targetAllocation: float
    color: str = ""


class PortfolioMetricsRequest(BaseModel):
    """Схема запроса для расчета метрик портфеля."""
    positions: List[Position]
    risk_free_rate: float = 0.042
    market_return: float = 0.10
    market_volatility: float = 0.15


class PortfolioMetricsResponse(BaseModel):
    """Схема ответа с метриками портфеля."""
    total_pnl: float
    nav: float
    annual_return: float
    daily_return: float
    volatility: float
    var_95: float
    var_95_daily: float
    var_95_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    beta: float
    alpha: float
    skew: float
    max_drawdown: float
    diversification: float
    avg_correlation: float
    risk_free_rate: float
    num_positions: int
    status: str = "success"
    timestamp: Optional[str] = ""
