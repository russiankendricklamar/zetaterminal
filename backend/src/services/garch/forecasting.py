"""
Volatility forecasting from fitted GARCH/EWMA model results.

Recursive h-step ahead forecasts with mean-reversion to long-run variance
and confidence intervals from chi-squared distribution.
"""
from typing import Any

import numpy as np
from scipy.stats import chi2


def forecast_volatility(
    model_result: dict[str, Any],
    n_steps: int = 22,
    confidence_levels: list[float] | None = None,
) -> dict[str, Any]:
    """
    Produce h-step ahead variance/volatility forecasts from a fitted univariate model.

    For GARCH-type models: E[sigma^2_{t+h}] = long_run_var + (persistence^h) * (sigma^2_t - long_run_var)
    For EWMA: simple recursive with lambda.
    """
    if confidence_levels is None:
        confidence_levels = [0.05, 0.95]
    if n_steps < 1 or n_steps > 504:
        raise ValueError(f"n_steps must be in [1, 504], got {n_steps}")

    model = model_result["model"]
    variances = model_result["variances"]
    params = model_result["params"]
    n_obs = model_result["n_obs"]

    last_var = variances[-1]

    forecasts = np.zeros(n_steps)

    if model == "ewma":
        # EWMA has no mean-reversion; under E[r^2] = sigma^2, forecast is constant
        for h in range(n_steps):
            forecasts[h] = last_var
    elif model == "egarch":
        # EGARCH operates in LOG-variance space: ln(σ²)
        beta = params["beta"]
        long_run_var = model_result.get("long_run_variance")
        if long_run_var is None or long_run_var <= 0:
            long_run_var = np.mean(variances)
        long_run_logvar = np.log(max(long_run_var, 1e-12))
        last_logvar = np.log(max(last_var, 1e-12))
        for h in range(n_steps):
            logvar_h = long_run_logvar + (abs(beta) ** (h + 1)) * (last_logvar - long_run_logvar)
            forecasts[h] = max(np.exp(logvar_h), 1e-12)
    else:
        # GARCH(1,1) and GJR-GARCH
        persistence = model_result.get("persistence", 0.95)
        long_run_var = model_result.get("long_run_variance")
        if long_run_var is None or long_run_var <= 0:
            long_run_var = np.mean(variances)
        for h in range(n_steps):
            forecasts[h] = long_run_var + (persistence ** (h + 1)) * (last_var - long_run_var)
            forecasts[h] = max(forecasts[h], 1e-12)

    forecast_vols = np.sqrt(forecasts)
    annualized_vols = forecast_vols * np.sqrt(252)

    # Confidence intervals via chi-squared distribution
    # sigma^2 * (n-1) / chi2 gives CI for variance
    ci = {}
    for level in confidence_levels:
        chi2_val = chi2.ppf(level, df=max(n_obs - 1, 1))
        ci_variances = forecasts * (n_obs - 1) / chi2_val
        ci[str(level)] = np.sqrt(np.maximum(ci_variances, 1e-12)).tolist()

    # Term structure: annualized vol at each horizon
    term_structure = []
    for h in range(n_steps):
        avg_var = np.mean(forecasts[: h + 1])
        term_structure.append(float(np.sqrt(avg_var * 252)))

    return {
        "forecasts": forecasts.tolist(),
        "forecast_volatilities": forecast_vols.tolist(),
        "annualized_volatilities": annualized_vols.tolist(),
        "confidence_intervals": ci,
        "term_structure": term_structure,
        "current_vol": float(np.sqrt(last_var)),
        "forecast_vol": float(forecast_vols[-1]),
        "long_run_vol": float(np.sqrt(long_run_var)) if model != "ewma" else None,
        "n_steps": n_steps,
    }


def forecast_dcc(
    dcc_result: dict[str, Any],
    n_steps: int = 22,
) -> dict[str, Any]:
    """Forecast DCC covariance matrices for h steps ahead."""
    if n_steps < 1 or n_steps > 252:
        raise ValueError(f"n_steps must be in [1, 252], got {n_steps}")

    univariate_results = dcc_result["univariate_results"]
    last_R = np.array(dcc_result["last_R"])
    n_assets = len(univariate_results)

    # Forecast individual volatilities
    vol_forecasts = []
    for res in univariate_results:
        fc = forecast_volatility(res, n_steps=n_steps)
        vol_forecasts.append(fc["forecast_volatilities"])

    vol_matrix = np.array(vol_forecasts)  # shape: (n_assets, n_steps)

    # DCC mean-reverts to Q_bar; approximate by keeping last R constant
    cov_matrices = []
    for h in range(n_steps):
        D_h = np.diag(vol_matrix[:, h])
        cov_h = D_h @ last_R @ D_h
        cov_matrices.append(cov_h.tolist())

    return {
        "covariance_matrices": cov_matrices,
        "correlation_matrix": last_R.tolist(),
        "volatility_forecasts": vol_matrix.tolist(),
        "n_steps": n_steps,
        "n_assets": n_assets,
    }
