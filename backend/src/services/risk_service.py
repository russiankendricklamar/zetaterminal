"""
GARCH-Conditional VaR/CVaR Risk Engine.

Three VaR methods (parametric, historical, Monte Carlo) with optional
GARCH-conditional volatility, plus Euler component VaR decomposition.

All CPU-bound work is wrapped in asyncio.to_thread via the RiskService facade.
"""
import asyncio
from typing import Any

import numpy as np
from scipy.stats import norm

from src.services.garch import GarchService

# ---------------------------------------------------------------------------
# 1. Parametric VaR / CVaR
# ---------------------------------------------------------------------------

def parametric_var(
    returns: np.ndarray,
    confidence: float = 0.95,
    horizon: int = 1,
    portfolio_value: float = 1.0,
    garch_forecast_vol: float | None = None,
) -> dict[str, float]:
    """Parametric (Gaussian) VaR and analytical CVaR.

    If *garch_forecast_vol* is provided it replaces the historical-std estimate.
    Multi-day scaling:
      - Without GARCH: sigma * sqrt(horizon)
      - With GARCH: garch_forecast_vol already accounts for horizon structure.
    """
    alpha = 1 - confidence
    z = norm.ppf(confidence)  # positive, e.g. 1.645 for 95%

    if garch_forecast_vol is not None and garch_forecast_vol > 0:
        sigma = garch_forecast_vol
    else:
        sigma = float(np.std(returns, ddof=1)) * np.sqrt(horizon)

    var_abs = z * sigma * portfolio_value

    # Analytical CVaR for normal distribution: sigma * phi(z) / (1 - alpha)
    phi_z = float(norm.pdf(z))
    cvar_abs = sigma * phi_z / alpha * portfolio_value

    return {
        "var": round(float(var_abs), 6),
        "cvar": round(float(cvar_abs), 6),
        "volatility": round(float(sigma), 8),
        "z_score": round(float(z), 4),
    }


# ---------------------------------------------------------------------------
# 2. Historical VaR / CVaR
# ---------------------------------------------------------------------------

def historical_var(
    returns: np.ndarray,
    confidence: float = 0.95,
    horizon: int = 1,
    portfolio_value: float = 1.0,
) -> dict[str, float]:
    """Non-parametric historical simulation VaR/CVaR.

    Sorts returns and picks the (1-alpha) quantile.  Multi-day uses sqrt(h)
    scaling on the daily quantile (Danielsson's square-root-of-time rule).
    """
    alpha = 1 - confidence
    sorted_returns = np.sort(returns)

    # VaR quantile (negative tail)
    var_quantile = float(np.percentile(returns, alpha * 100))
    # CVaR = mean of returns below the VaR quantile
    tail = sorted_returns[sorted_returns <= var_quantile]
    cvar_quantile = float(np.mean(tail)) if len(tail) > 0 else var_quantile

    scale = np.sqrt(horizon)
    var_abs = abs(var_quantile) * scale * portfolio_value
    cvar_abs = abs(cvar_quantile) * scale * portfolio_value

    return {
        "var": round(float(var_abs), 6),
        "cvar": round(float(cvar_abs), 6),
        "var_quantile": round(float(var_quantile), 8),
        "cvar_quantile": round(float(cvar_quantile), 8),
        "n_tail_obs": len(tail),
    }


# ---------------------------------------------------------------------------
# 3. Monte Carlo VaR / CVaR
# ---------------------------------------------------------------------------

def monte_carlo_var(
    returns: np.ndarray,
    confidence: float = 0.95,
    horizon: int = 1,
    portfolio_value: float = 1.0,
    n_simulations: int = 10_000,
    garch_variances: list[float] | None = None,
    seed: int | None = None,
) -> dict[str, float]:
    """Monte Carlo VaR with optional GARCH-conditional variance paths.

    Without GARCH: GBM with constant historical vol.
    With GARCH: each step uses sigma_t from the GARCH forecast variance schedule.
    """
    rng = np.random.default_rng(seed)
    mu = float(np.mean(returns))

    if garch_variances is not None and len(garch_variances) >= horizon:
        # GARCH-conditional: sigma changes each step
        vols = np.sqrt(np.array(garch_variances[:horizon]))
    else:
        daily_vol = float(np.std(returns, ddof=1))
        vols = np.full(horizon, daily_vol)

    # Simulate paths: (n_simulations, horizon)
    eps = rng.standard_normal((n_simulations, horizon))
    daily_returns = mu + vols[np.newaxis, :] * eps  # broadcast

    # Terminal portfolio value (cumulative returns)
    cumulative = np.prod(1 + daily_returns, axis=1)
    terminal_pnl = (cumulative - 1) * portfolio_value

    alpha = 1 - confidence
    var_value = float(-np.percentile(terminal_pnl, alpha * 100))
    tail = terminal_pnl[terminal_pnl <= -var_value]
    cvar_value = float(-np.mean(tail)) if len(tail) > 0 else var_value

    return {
        "var": round(var_value, 6),
        "cvar": round(cvar_value, 6),
        "mean_pnl": round(float(np.mean(terminal_pnl)), 6),
        "std_pnl": round(float(np.std(terminal_pnl)), 6),
        "n_simulations": n_simulations,
        "percentile_5": round(float(np.percentile(terminal_pnl, 5)), 6),
        "percentile_95": round(float(np.percentile(terminal_pnl, 95)), 6),
    }


# ---------------------------------------------------------------------------
# 4. Component VaR (Euler decomposition)
# ---------------------------------------------------------------------------

def component_var(
    returns_matrix: np.ndarray,
    weights: np.ndarray,
    confidence: float = 0.95,
    portfolio_value: float = 1.0,
) -> dict[str, Any]:
    """Marginal and component VaR via Euler decomposition.

    Component VaR_i = w_i * (Cov @ w)_i / sigma_p * VaR_total
    Sum of component VaRs = total VaR (Euler's theorem for homogeneous functions).
    """
    cov = np.cov(returns_matrix, rowvar=False)
    z = norm.ppf(confidence)
    sigma_p = float(np.sqrt(weights @ cov @ weights))

    if sigma_p < 1e-12:
        n = len(weights)
        return {
            "total_var": 0.0,
            "marginal_var": [0.0] * n,
            "component_var": [0.0] * n,
            "pct_contribution": [0.0] * n,
            "portfolio_volatility": 0.0,
        }

    total_var = z * sigma_p * portfolio_value

    # Marginal VaR = z * (Cov @ w)_i / sigma_p
    cov_w = cov @ weights
    marginal_var = z * cov_w / sigma_p

    # Component VaR = w_i * marginal_var_i * portfolio_value
    comp_var = weights * marginal_var * portfolio_value

    # Percentage contribution
    pct_contribution = comp_var / total_var if total_var > 0 else np.zeros_like(comp_var)

    return {
        "total_var": round(float(total_var), 6),
        "marginal_var": [round(float(v), 8) for v in marginal_var],
        "component_var": [round(float(v), 6) for v in comp_var],
        "pct_contribution": [round(float(v), 6) for v in pct_contribution],
        "portfolio_volatility": round(sigma_p, 8),
    }


# ---------------------------------------------------------------------------
# 5. RiskService facade (async)
# ---------------------------------------------------------------------------

class RiskService:
    """Unified async entry point for all risk calculations."""

    @staticmethod
    async def calculate_var(
        method: str,
        returns: list[float],
        confidence: float = 0.95,
        horizon: int = 1,
        portfolio_value: float = 1.0,
        n_simulations: int = 10_000,
        use_garch: bool = False,
        garch_model: str = "garch_11",
    ) -> dict[str, Any]:
        """Calculate VaR/CVaR using the specified method."""
        arr = np.array(returns, dtype=np.float64)

        garch_forecast_vol = None
        garch_variances = None

        if use_garch:
            fc_result = await GarchService.forecast(
                returns=returns,
                model=garch_model,
                n_steps=horizon,
            )
            forecast_data = fc_result["forecast"]
            # Multi-step vol: sqrt of SUM of forecasted variances over horizon
            # σ²_horizon = Σ_{h=1}^{H} E[σ²_{t+h}], NOT average
            forecasted_vars = forecast_data["forecasts"]
            garch_forecast_vol = float(np.sqrt(np.sum(forecasted_vars)))
            garch_variances = forecasted_vars

        if method == "parametric":
            result = await asyncio.to_thread(
                parametric_var, arr, confidence, horizon,
                portfolio_value, garch_forecast_vol,
            )
        elif method == "historical":
            result = await asyncio.to_thread(
                historical_var, arr, confidence, horizon, portfolio_value,
            )
        elif method == "monte_carlo":
            result = await asyncio.to_thread(
                monte_carlo_var, arr, confidence, horizon,
                portfolio_value, n_simulations, garch_variances,
            )
        else:
            raise ValueError(f"Unknown method: {method}. Use: parametric, historical, monte_carlo")

        return {
            "method": method,
            "confidence": confidence,
            "horizon": horizon,
            "portfolio_value": portfolio_value,
            "use_garch": use_garch,
            "garch_model": garch_model if use_garch else None,
            **result,
        }

    @staticmethod
    async def calculate_component_var(
        returns_matrix: list[list[float]],
        weights: list[float],
        confidence: float = 0.95,
        portfolio_value: float = 1.0,
    ) -> dict[str, Any]:
        """Calculate component VaR via Euler decomposition."""
        arr = np.array(returns_matrix, dtype=np.float64)
        w = np.array(weights, dtype=np.float64)
        return await asyncio.to_thread(component_var, arr, w, confidence, portfolio_value)

    @staticmethod
    async def full_risk_report(
        returns: list[float],
        confidence: float = 0.95,
        horizon: int = 1,
        portfolio_value: float = 1.0,
        n_simulations: int = 10_000,
        use_garch: bool = False,
        garch_model: str = "garch_11",
        returns_matrix: list[list[float]] | None = None,
        weights: list[float] | None = None,
    ) -> dict[str, Any]:
        """Run all 3 VaR methods + optional component VaR."""
        methods = ["parametric", "historical", "monte_carlo"]
        tasks = [
            RiskService.calculate_var(
                method=m,
                returns=returns,
                confidence=confidence,
                horizon=horizon,
                portfolio_value=portfolio_value,
                n_simulations=n_simulations,
                use_garch=use_garch,
                garch_model=garch_model,
            )
            for m in methods
        ]

        if returns_matrix is not None and weights is not None:
            tasks.append(
                RiskService.calculate_component_var(
                    returns_matrix=returns_matrix,
                    weights=weights,
                    confidence=confidence,
                    portfolio_value=portfolio_value,
                )
            )

        results = await asyncio.gather(*tasks)

        report: dict[str, Any] = {
            "confidence": confidence,
            "horizon": horizon,
            "portfolio_value": portfolio_value,
            "use_garch": use_garch,
        }

        for i, m in enumerate(methods):
            report[m] = results[i]

        if returns_matrix is not None and weights is not None:
            report["component_var"] = results[-1]

        return report
