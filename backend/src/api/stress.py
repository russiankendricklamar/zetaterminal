"""
API endpoints для стресс-тестирования портфеля.
"""
import logging

from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional, Dict, Any
from pydantic import Field
from src.services.stress_service import run_stress_test
from src.utils.financial_validation import (
    FinancialBaseModel, MAX_ASSETS, MAX_MONTE_CARLO_PATHS,
    MAX_SCENARIOS, MAX_CAPITAL,
)
from src.middleware.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter()


class StressScenario(FinancialBaseModel):
    """Описание стресс-сценария."""
    name: str = Field(..., max_length=200, description="Название сценария")
    key: str = Field(..., max_length=100, description="Уникальный ключ сценария")
    type: str = Field('return_shock', description="Тип сценария: 'return_shock', 'volatility_shock', 'correlation_shock'")
    return_multiplier: Optional[float] = Field(None, ge=-100, le=100, description="Множитель доходности (для return_shock)")
    volatility_multiplier: Optional[float] = Field(None, ge=0, le=100, description="Множитель волатильности (для volatility_shock)")
    correlation_multiplier: Optional[float] = Field(None, ge=-10, le=10, description="Множитель корреляций (для correlation_shock)")
    seed: Optional[int] = Field(None, description="Seed для воспроизводимости")


class StressTestRequest(FinancialBaseModel):
    """Запрос на стресс-тестирование."""
    mu: List[float] = Field(..., max_length=MAX_ASSETS, description="Ожидаемые доходности активов")
    cov_matrix: List[List[float]] = Field(..., max_length=MAX_ASSETS, description="Ковариационная матрица")
    initial_capital: float = Field(1000000, gt=0, le=MAX_CAPITAL, description="Начальный капитал")
    risk_free_rate: float = Field(..., ge=-1, le=1, description="Безрисковая ставка")
    gamma: float = Field(..., gt=0, le=100, description="Коэффициент риск-аверсии")
    scenarios: List[StressScenario] = Field(..., max_length=MAX_SCENARIOS, description="Список сценариев для тестирования")
    asset_names: Optional[List[str]] = Field(None, max_length=MAX_ASSETS, description="Названия активов")
    n_paths: int = Field(1000, ge=1, le=MAX_MONTE_CARLO_PATHS, description="Количество Монте-Карло траекторий")
    seed: Optional[int] = Field(None, description="Seed для воспроизводимости")


@router.post("/test", response_model=Dict[str, Any])
@limiter.limit("10/minute")
async def run_stress_tests(http_request: Request, request: StressTestRequest):
    """
    Выполняет стресс-тестирование портфеля для списка сценариев.
    """
    try:
        # Конвертируем сценарии в словари
        scenarios_dict = [scenario.dict() for scenario in request.scenarios]
        
        result = run_stress_test(
            mu=request.mu,
            cov_matrix=request.cov_matrix,
            initial_capital=request.initial_capital,
            risk_free_rate=request.risk_free_rate,
            gamma=request.gamma,
            scenarios=scenarios_dict,
            asset_names=request.asset_names,
            n_paths=request.n_paths,
            seed=request.seed
        )
        return result
    except ValueError as e:
        logger.error("Stress test validation error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid input parameters")
    except Exception as e:
        logger.error("Stress test failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
