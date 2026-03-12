"""
API endpoints для расчета метрик портфеля.
"""
from datetime import datetime

from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.models.schemas import PortfolioMetricsRequest, PortfolioMetricsResponse
from src.services.portfolio_service import PortfolioService
from src.utils.error_handler import service_endpoint

router = APIRouter()
portfolio_service = PortfolioService()
limiter = Limiter(key_func=get_remote_address)


@router.post("/metrics", response_model=PortfolioMetricsResponse)
@limiter.limit("10/minute")
@service_endpoint("Calculate Portfolio Metrics")
async def calculate_portfolio_metrics(http_request: Request, request: PortfolioMetricsRequest):
    """
    Вычисляет все метрики портфеля на основе позиций.
    
    Args:
        request: Параметры портфеля и позиции
        
    Returns:
        Все метрики портфеля
    """
    # Преобразуем Pydantic модели в словари
    positions_dict = [pos.dict() for pos in request.positions]

    result = portfolio_service.calculate_portfolio_metrics(
        positions=positions_dict,
        risk_free_rate=request.risk_free_rate,
        market_return=request.market_return,
        market_volatility=request.market_volatility
    )

    return PortfolioMetricsResponse(
        **result,
        timestamp=datetime.now().isoformat()
    )
