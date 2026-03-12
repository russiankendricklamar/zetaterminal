"""
API endpoints for the GARCH-Conditional VaR/CVaR Risk Engine.

POST /api/risk/var     — single-method VaR calculation
POST /api/risk/report  — full risk report (all 3 methods + component VaR)
"""
from typing import Any, Literal

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.risk_service import RiskService
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import (
    MAX_ASSETS,
    MAX_DATA_POINTS,
    MAX_MONTE_CARLO_PATHS,
    FinancialBaseModel,
)

router = APIRouter()


class VaRRequest(FinancialBaseModel):
    """Request for single-method VaR calculation."""
    returns: list[float] = Field(
        ..., min_length=10, max_length=MAX_DATA_POINTS,
        description="Daily return series",
    )
    method: Literal["parametric", "historical", "monte_carlo"] = Field(
        "parametric", description="VaR method",
    )
    confidence: float = Field(0.95, gt=0.5, lt=1.0, description="Confidence level")
    horizon: int = Field(1, ge=1, le=252, description="Horizon in trading days")
    portfolio_value: float = Field(1.0, gt=0, le=1e15, description="Portfolio NAV")
    n_simulations: int = Field(
        10_000, ge=1000, le=MAX_MONTE_CARLO_PATHS,
        description="Monte Carlo simulations",
    )
    use_garch: bool = Field(False, description="Use GARCH-conditional volatility")
    garch_model: str = Field("garch_11", description="GARCH model variant")


class RiskReportRequest(FinancialBaseModel):
    """Request for full risk report (all methods + component VaR)."""
    returns: list[float] = Field(
        ..., min_length=10, max_length=MAX_DATA_POINTS,
        description="Daily return series",
    )
    confidence: float = Field(0.95, gt=0.5, lt=1.0, description="Confidence level")
    horizon: int = Field(1, ge=1, le=252, description="Horizon in trading days")
    portfolio_value: float = Field(1.0, gt=0, le=1e15, description="Portfolio NAV")
    n_simulations: int = Field(
        10_000, ge=1000, le=MAX_MONTE_CARLO_PATHS,
        description="Monte Carlo simulations",
    )
    use_garch: bool = Field(False, description="Use GARCH-conditional volatility")
    garch_model: str = Field("garch_11", description="GARCH model variant")
    returns_matrix: list[list[float]] | None = Field(
        None, max_length=MAX_DATA_POINTS,
        description="T x N returns matrix for component VaR",
    )
    weights: list[float] | None = Field(
        None, max_length=MAX_ASSETS,
        description="Portfolio weights for component VaR",
    )


@router.post("/var", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("VaR calculation")
async def calculate_var(request: Request, body: VaRRequest):
    """Calculate VaR/CVaR using a single method."""
    return await RiskService.calculate_var(
        method=body.method,
        returns=body.returns,
        confidence=body.confidence,
        horizon=body.horizon,
        portfolio_value=body.portfolio_value,
        n_simulations=body.n_simulations,
        use_garch=body.use_garch,
        garch_model=body.garch_model,
    )


@router.post("/report", response_model=dict[str, Any])
@limiter.limit("5/minute")
@service_endpoint("Risk report")
async def risk_report(request: Request, body: RiskReportRequest):
    """Generate full risk report with all 3 VaR methods + optional component VaR."""
    return await RiskService.full_risk_report(
        returns=body.returns,
        confidence=body.confidence,
        horizon=body.horizon,
        portfolio_value=body.portfolio_value,
        n_simulations=body.n_simulations,
        use_garch=body.use_garch,
        garch_model=body.garch_model,
        returns_matrix=body.returns_matrix,
        weights=body.weights,
    )
