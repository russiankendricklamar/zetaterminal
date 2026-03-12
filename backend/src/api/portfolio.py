"""
API endpoints для расчета метрик портфеля.
"""
from datetime import datetime

from fastapi import APIRouter, Request

from src.middleware.rate_limit import limiter
from src.models.schemas import PortfolioMetricsRequest, PortfolioMetricsResponse
from src.services.portfolio_service import PortfolioService
from src.utils.error_handler import service_endpoint

router = APIRouter()
portfolio_service = PortfolioService()


@router.post("/metrics", response_model=PortfolioMetricsResponse)
@limiter.limit("10/minute")
@service_endpoint("Calculate Portfolio Metrics")
async def calculate_portfolio_metrics(request: Request, body: PortfolioMetricsRequest):
    """
    Вычисляет все метрики портфеля на основе позиций.

    Args:
        body: Параметры портфеля и позиции

    Returns:
        Все метрики портфеля
    """
    # Преобразуем Pydantic модели в словари
    positions_dict = [pos.dict() for pos in body.positions]

    result = portfolio_service.calculate_portfolio_metrics(
        positions=positions_dict,
        risk_free_rate=body.risk_free_rate,
        market_return=body.market_return,
        market_volatility=body.market_volatility
    )

    return PortfolioMetricsResponse(
        **result,
        timestamp=datetime.now().isoformat()
    )
