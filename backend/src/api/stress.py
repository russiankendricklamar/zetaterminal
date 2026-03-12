"""
API endpoints для стресс-тестирования портфеля.
"""
from typing import Any

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.historical_scenarios import get_all_scenarios
from src.services.stress_service import run_stress_test
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import (
    MAX_ASSETS,
    MAX_CAPITAL,
    MAX_MONTE_CARLO_PATHS,
    MAX_SCENARIOS,
    FinancialBaseModel,
)

router = APIRouter()


class StressScenario(FinancialBaseModel):
    """Описание стресс-сценария."""
    name: str = Field(..., max_length=200, description="Название сценария")
    key: str = Field(..., max_length=100, description="Уникальный ключ сценария")
    type: str = Field('return_shock', description="Тип сценария: 'return_shock', 'volatility_shock', 'correlation_shock', 'historical'")
    return_multiplier: float | None = Field(None, ge=-100, le=100, description="Множитель доходности (для return_shock)")
    volatility_multiplier: float | None = Field(None, ge=0, le=100, description="Множитель волатильности (для volatility_shock)")
    correlation_multiplier: float | None = Field(None, ge=-10, le=10, description="Множитель корреляций (для correlation_shock)")
    scenario_key: str | None = Field(None, max_length=100, description="Ключ исторического сценария (для type='historical')")
    seed: int | None = Field(None, description="Seed для воспроизводимости")


class StressTestRequest(FinancialBaseModel):
    """Запрос на стресс-тестирование."""
    mu: list[float] = Field(..., max_length=MAX_ASSETS, description="Ожидаемые доходности активов")
    cov_matrix: list[list[float]] = Field(..., max_length=MAX_ASSETS, description="Ковариационная матрица")
    initial_capital: float = Field(1000000, gt=0, le=MAX_CAPITAL, description="Начальный капитал")
    risk_free_rate: float = Field(..., ge=-1, le=1, description="Безрисковая ставка")
    gamma: float = Field(..., gt=0, le=100, description="Коэффициент риск-аверсии")
    scenarios: list[StressScenario] = Field(..., max_length=MAX_SCENARIOS, description="Список сценариев для тестирования")
    asset_names: list[str] | None = Field(None, max_length=MAX_ASSETS, description="Названия активов")
    n_paths: int = Field(1000, ge=1, le=MAX_MONTE_CARLO_PATHS, description="Количество Монте-Карло траекторий")
    seed: int | None = Field(None, description="Seed для воспроизводимости")


@router.get("/historical-scenarios")
@limiter.limit("30/minute")
@service_endpoint("List historical scenarios")
async def list_historical_scenarios(request: Request):
    """Return all available historical crisis scenarios."""
    return {"scenarios": get_all_scenarios()}


@router.post("/test", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Stress test")
async def run_stress_tests(request: Request, body: StressTestRequest):
    """
    Выполняет стресс-тестирование портфеля для списка сценариев.
    """
    # Конвертируем сценарии в словари
    scenarios_dict = [scenario.dict() for scenario in body.scenarios]

    return run_stress_test(
        mu=body.mu,
        cov_matrix=body.cov_matrix,
        initial_capital=body.initial_capital,
        risk_free_rate=body.risk_free_rate,
        gamma=body.gamma,
        scenarios=scenarios_dict,
        asset_names=body.asset_names,
        n_paths=body.n_paths,
        seed=body.seed
    )
