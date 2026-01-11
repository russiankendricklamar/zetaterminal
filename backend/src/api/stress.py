"""
API endpoints для стресс-тестирования портфеля.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.services.stress_service import run_stress_test
from datetime import datetime
import numpy as np

router = APIRouter()


class StressScenario(BaseModel):
    """Описание стресс-сценария."""
    name: str = Field(..., description="Название сценария")
    key: str = Field(..., description="Уникальный ключ сценария")
    type: str = Field('return_shock', description="Тип сценария: 'return_shock', 'volatility_shock', 'correlation_shock'")
    return_multiplier: Optional[float] = Field(None, description="Множитель доходности (для return_shock)")
    volatility_multiplier: Optional[float] = Field(None, description="Множитель волатильности (для volatility_shock)")
    correlation_multiplier: Optional[float] = Field(None, description="Множитель корреляций (для correlation_shock)")
    seed: Optional[int] = Field(None, description="Seed для воспроизводимости")


class StressTestRequest(BaseModel):
    """Запрос на стресс-тестирование."""
    mu: List[float] = Field(..., description="Ожидаемые доходности активов")
    cov_matrix: List[List[float]] = Field(..., description="Ковариационная матрица")
    initial_capital: float = Field(1000000, description="Начальный капитал")
    risk_free_rate: float = Field(..., description="Безрисковая ставка")
    gamma: float = Field(..., description="Коэффициент риск-аверсии")
    scenarios: List[StressScenario] = Field(..., description="Список сценариев для тестирования")
    asset_names: Optional[List[str]] = Field(None, description="Названия активов")
    n_paths: int = Field(1000, description="Количество Монте-Карло траекторий")
    seed: Optional[int] = Field(None, description="Seed для воспроизводимости")


@router.post("/test", response_model=Dict[str, Any])
async def run_stress_tests(request: StressTestRequest):
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
