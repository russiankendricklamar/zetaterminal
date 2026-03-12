"""
API endpoints for Performance Attribution (Brinson-Fachler and Factor-based).
"""
import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.attribution_service import (
    brinson_fachler_attribution,
    factor_attribution,
)
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import (
    MAX_ASSETS,
    MAX_DATA_POINTS,
    FinancialBaseModel,
)

router = APIRouter()


# -- Request / Response Models -------------------------------------------------


class BrinsonRequest(FinancialBaseModel):
    """Brinson-Fachler performance attribution request."""

    portfolio_weights: list[float] = Field(
        ..., max_length=MAX_ASSETS, description="Portfolio weights per sector"
    )
    benchmark_weights: list[float] = Field(
        ..., max_length=MAX_ASSETS, description="Benchmark weights per sector"
    )
    portfolio_returns: list[float] = Field(
        ..., max_length=MAX_ASSETS, description="Portfolio returns per sector"
    )
    benchmark_returns: list[float] = Field(
        ..., max_length=MAX_ASSETS, description="Benchmark returns per sector"
    )
    sector_names: list[str] | None = Field(
        None, max_length=MAX_ASSETS, description="Sector/asset class names"
    )

    model_config = {  # noqa: RUF012
        "json_schema_extra": {
            "example": {
                "portfolio_weights": [0.4, 0.35, 0.25],
                "benchmark_weights": [0.3, 0.4, 0.3],
                "portfolio_returns": [0.12, 0.08, -0.02],
                "benchmark_returns": [0.10, 0.06, 0.01],
                "sector_names": ["Equities", "Bonds", "Commodities"],
            }
        }
    }


class FactorAttributionRequest(FinancialBaseModel):
    """Factor-based P&L attribution request."""

    portfolio_returns: list[float] = Field(
        ..., max_length=MAX_DATA_POINTS, description="Portfolio return time series (T)"
    )
    factor_returns: list[list[float]] = Field(
        ..., max_length=MAX_DATA_POINTS, description="Factor returns matrix (T x K)"
    )
    factor_names: list[str] | None = Field(
        None, max_length=MAX_ASSETS, description="Factor names"
    )
    portfolio_value: float = Field(
        default=1_000_000.0, gt=0, le=1e15, description="Portfolio notional value"
    )

    model_config = {  # noqa: RUF012
        "json_schema_extra": {
            "example": {
                "portfolio_returns": [0.01, -0.005, 0.008, 0.003, -0.002],
                "factor_returns": [
                    [0.012, 0.003],
                    [-0.008, 0.001],
                    [0.010, -0.002],
                    [0.005, 0.004],
                    [-0.003, 0.002],
                ],
                "factor_names": ["Market", "SMB"],
                "portfolio_value": 1000000,
            }
        }
    }


class AttributionResponse(BaseModel):
    result: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


# -- Endpoints -----------------------------------------------------------------


@router.post("/brinson", response_model=AttributionResponse)
@service_endpoint("Brinson-Fachler attribution")
@limiter.limit("20/minute")
async def run_brinson(request: BrinsonRequest, http_request: Request) -> AttributionResponse:
    """
    Brinson-Fachler performance attribution.

    Decomposes excess return vs benchmark into:
    - Allocation effect: sector weight differences
    - Selection effect: security selection within sectors
    - Interaction effect: cross-term

    Reference: Brinson, Hood & Beebower (1986)
    """
    result = await asyncio.to_thread(
        brinson_fachler_attribution,
        portfolio_weights=request.portfolio_weights,
        benchmark_weights=request.benchmark_weights,
        portfolio_returns=request.portfolio_returns,
        benchmark_returns=request.benchmark_returns,
        sector_names=request.sector_names,
    )
    return AttributionResponse(result=result)


@router.post("/factor", response_model=AttributionResponse)
@service_endpoint("Factor attribution")
@limiter.limit("20/minute")
async def run_factor(request: FactorAttributionRequest, http_request: Request) -> AttributionResponse:
    """
    Factor-based P&L attribution via OLS regression.

    R_p = alpha + sum(beta_i * F_i) + epsilon

    Returns per-factor betas, P&L contributions, R-squared, and residual analysis.
    """
    result = await asyncio.to_thread(
        factor_attribution,
        portfolio_returns=request.portfolio_returns,
        factor_returns=request.factor_returns,
        factor_names=request.factor_names,
        portfolio_value=request.portfolio_value,
    )
    return AttributionResponse(result=result)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "attribution"}
