"""
API endpoints для Adversarial Stress Testing.
"""
from typing import Any

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.adversarial_stress_service import run_adversarial_stress
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import FinancialBaseModel

router = APIRouter()


class AdversarialStressRequest(FinancialBaseModel):
    """Запрос на adversarial stress test."""
    cov_matrix: list[list[float]] = Field(..., description="Ковариационная матрица (N x N)")
    mu: list[float] = Field(..., description="Ожидаемые доходности активов (N)")
    weights: list[float] = Field(..., description="Веса портфеля (N)")
    kappa: float = Field(default=1.0, gt=0, le=5.0, description="Радиус неопределённости для μ")
    epsilon: float = Field(default=0.1, gt=0, le=1.0, description="Радиус Фробениуса для Σ")
    n_paths: int = Field(default=2000, ge=100, le=10000, description="Число MC траекторий")
    risk_free_rate: float = Field(default=0.0, description="Безрисковая ставка")
    initial_capital: float = Field(default=1_000_000, gt=0, description="Начальный капитал")
    gamma: float = Field(default=3.0, gt=0, description="Коэффициент риск-аверсии")
    asset_names: list[str] | None = Field(None, description="Названия активов")
    seed: int | None = Field(default=42, description="Seed для воспроизводимости")


@router.post("/generate", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Generate Adversarial Stress")
async def generate_adversarial_stress(http_request: Request, request: AdversarialStressRequest):
    """
    Генерирует adversarial worst-case сценарии для портфеля.

    Использует Distributionally Robust Optimization:
    - Worst-case μ* (эллипсоидальная неопределённость, Mahalanobis)
    - Worst-case Σ* (шар Фробениуса)
    - Monte-Carlo с adversarial параметрами
    - EVT (GPD) для хвоста потерь
    """
    n = len(request.mu)

    if len(request.weights) != n:
        raise ValueError(
            f"Длина weights ({len(request.weights)}) ≠ длине mu ({n})"
        )
    if len(request.cov_matrix) != n or any(len(row) != n for row in request.cov_matrix):
        raise ValueError(
            f"Ковариационная матрица должна быть {n}×{n}"
        )

    result = run_adversarial_stress(
        cov_matrix=request.cov_matrix,
        mu=request.mu,
        weights=request.weights,
        kappa=request.kappa,
        epsilon=request.epsilon,
        n_paths=request.n_paths,
        risk_free_rate=request.risk_free_rate,
        initial_capital=request.initial_capital,
        gamma=request.gamma,
        asset_names=request.asset_names,
        seed=request.seed,
    )
    return result

    """Health check."""
    return {"status": "healthy", "service": "adversarial-stress"}
