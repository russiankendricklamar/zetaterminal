"""
API endpoints for GARCH volatility modeling.
"""
from typing import Any

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.garch import GarchService
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import MAX_ASSETS, MAX_DATA_POINTS, FinancialBaseModel

router = APIRouter()


class GarchFitRequest(FinancialBaseModel):
    """Request to fit a univariate GARCH model."""
    returns: list[float] = Field(..., min_length=2, max_length=MAX_DATA_POINTS, description="Return series")
    model: str = Field("garch_11", description="Model: garch_11, gjr_garch, egarch, ewma")
    params: dict[str, float] | None = Field(None, description="Manual params (skip MLE if provided)")
    initial_variance: float | None = Field(None, gt=0, description="Initial variance override")


class GarchForecastRequest(FinancialBaseModel):
    """Request to fit + forecast volatility."""
    returns: list[float] = Field(..., min_length=2, max_length=MAX_DATA_POINTS, description="Return series")
    model: str = Field("garch_11", description="Model: garch_11, gjr_garch, egarch, ewma")
    params: dict[str, float] | None = Field(None, description="Manual params (skip MLE if provided)")
    n_steps: int = Field(22, ge=1, le=504, description="Forecast horizon (trading days)")
    confidence_levels: list[float] | None = Field(None, max_length=10, description="CI levels, e.g. [0.05, 0.95]")


class DCCRequest(FinancialBaseModel):
    """Request to fit DCC-GARCH on multivariate returns."""
    returns_matrix: list[list[float]] = Field(
        ..., min_length=20, max_length=MAX_DATA_POINTS,
        description="T x N returns matrix (rows=time, cols=assets)"
    )
    univariate_model: str = Field("garch_11", description="Univariate model for each asset")
    univariate_params: list[dict[str, float]] | None = Field(
        None, max_length=MAX_ASSETS, description="Pre-fitted params per asset"
    )
    dcc_params: dict[str, float] | None = Field(None, description="DCC params {a, b}")
    n_steps: int = Field(22, ge=1, le=252, description="Forecast horizon")


class DiagnosticsRequest(FinancialBaseModel):
    """Request to run model comparison and diagnostics."""
    returns: list[float] = Field(..., min_length=10, max_length=MAX_DATA_POINTS, description="Return series")


@router.post("/fit", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("GARCH fit")
async def fit_garch(request: Request, body: GarchFitRequest):
    """Fit a univariate GARCH model to a return series."""
    return await GarchService.fit(
        returns=body.returns,
        model=body.model,
        params=body.params,
        initial_variance=body.initial_variance,
    )


@router.post("/forecast", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("GARCH forecast")
async def forecast_garch(request: Request, body: GarchForecastRequest):
    """Fit model and produce h-step ahead volatility forecasts."""
    return await GarchService.forecast(
        returns=body.returns,
        model=body.model,
        params=body.params,
        n_steps=body.n_steps,
        confidence_levels=body.confidence_levels,
    )


@router.post("/dcc", response_model=dict[str, Any])
@limiter.limit("5/minute")
@service_endpoint("DCC-GARCH")
async def fit_dcc(request: Request, body: DCCRequest):
    """Fit DCC-GARCH model on multivariate returns."""
    return await GarchService.fit_dcc(
        returns_matrix=body.returns_matrix,
        univariate_model=body.univariate_model,
        univariate_params=body.univariate_params,
        dcc_params=body.dcc_params,
        n_steps=body.n_steps,
    )


@router.post("/diagnostics", response_model=dict[str, Any])
@limiter.limit("5/minute")
@service_endpoint("GARCH diagnostics")
async def garch_diagnostics(request: Request, body: DiagnosticsRequest):
    """Compare all 4 models and run residual diagnostic tests."""
    return await GarchService.diagnostics(returns=body.returns)
