"""
API endpoints for swap portfolio stress testing.
"""
import asyncio
from typing import Any

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.swap_stress_service import (
    get_predefined_scenarios,
    stress_test_swap_portfolio,
)
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import (
    MAX_NOTIONAL,
    MAX_RATE_PCT,
    MAX_TENOR_YEARS,
    FinancialBaseModel,
)

router = APIRouter()


class SwapPosition(FinancialBaseModel):
    """A single swap position for stress testing."""
    notional: float = Field(..., gt=0, le=MAX_NOTIONAL, description="Notional amount")
    tenor: float = Field(..., gt=0, le=MAX_TENOR_YEARS, description="Tenor in years")
    fixed_rate: float = Field(..., ge=-MAX_RATE_PCT, le=MAX_RATE_PCT, description="Fixed rate (%)")
    floating_rate: float = Field(..., ge=-MAX_RATE_PCT, le=MAX_RATE_PCT, description="Floating rate (%)")
    spread: float = Field(0.0, ge=-10000, le=10000, description="Spread (bp)")
    coupons_per_year: int = Field(2, ge=1, le=12, description="Coupons per year")
    discount_rate: float = Field(..., ge=-MAX_RATE_PCT, le=MAX_RATE_PCT, description="Discount rate (%)")
    volatility: float | None = Field(None, ge=0, le=500, description="Volatility (%)")
    swap_type: str = Field("irs", max_length=20, description="Swap type (irs, cds, basis, xccy)")


class SwapStressTestRequest(FinancialBaseModel):
    """Request to run swap stress tests."""
    positions: list[SwapPosition] = Field(..., min_length=1, max_length=50, description="Swap positions")
    scenarios: list[dict[str, Any]] | None = Field(None, max_length=20, description="Custom scenarios (uses predefined if null)")
    multiplier: float = Field(1.0, ge=0.1, le=10.0, description="Severity multiplier")


@router.post("/test", response_model=list[dict[str, Any]])
@limiter.limit("5/minute")
@service_endpoint("Swap stress test")
async def run_swap_stress_tests(http_request: Request, request: SwapStressTestRequest) -> list[dict[str, Any]]:
    """
    Run stress tests on a swap portfolio.

    Applies curve shifts, spread bumps, and volatility shocks,
    then computes P&L impact, Greeks, and key rate durations.
    """
    positions_dicts = [pos.model_dump() for pos in request.positions]

    result = await asyncio.to_thread(
        stress_test_swap_portfolio,
        positions=positions_dicts,
        scenarios=request.scenarios,
        multiplier=request.multiplier,
    )
    return result


@router.get("/scenarios", response_model=list[dict[str, Any]])
@limiter.limit("30/minute")
@service_endpoint("Swap stress scenarios")
async def get_swap_stress_scenarios(http_request: Request) -> list[dict[str, Any]]:
    """Return the list of predefined swap stress scenarios."""
    return get_predefined_scenarios()
