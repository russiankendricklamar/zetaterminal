"""
Facade for all GARCH operations.

Provides async-safe methods that wrap CPU-bound MLE fitting in asyncio.to_thread().
"""
import asyncio
from typing import Any

import numpy as np

from src.services.garch.forecasting import forecast_dcc, forecast_volatility
from src.services.garch.model_selection import arch_lm_test, compare_models, ljung_box_test
from src.services.garch.multivariate import dcc_garch
from src.services.garch.univariate import egarch, ewma, garch_11, gjr_garch

MODEL_MAP = {
    "garch_11": garch_11,
    "gjr_garch": gjr_garch,
    "egarch": egarch,
}


class GarchService:
    """Unified entry point for GARCH volatility modeling."""

    @staticmethod
    async def fit(
        returns: list[float],
        model: str = "garch_11",
        params: dict[str, float] | None = None,
        initial_variance: float | None = None,
    ) -> dict[str, Any]:
        """Fit a univariate GARCH model. Runs MLE in a thread to avoid blocking."""
        arr = np.array(returns, dtype=np.float64)

        if model == "ewma":
            lam = (params or {}).get("lambda", 0.94)
            return await asyncio.to_thread(ewma, arr, lam, initial_variance)

        model_fn = MODEL_MAP.get(model)
        if model_fn is None:
            raise ValueError(f"Unknown model: {model}. Use: {[*MODEL_MAP.keys(), 'ewma']}")

        return await asyncio.to_thread(model_fn, arr, params, initial_variance)

    @staticmethod
    async def forecast(
        returns: list[float],
        model: str = "garch_11",
        params: dict[str, float] | None = None,
        n_steps: int = 22,
        confidence_levels: list[float] | None = None,
    ) -> dict[str, Any]:
        """Fit model + produce h-step forecasts."""
        arr = np.array(returns, dtype=np.float64)

        if model == "ewma":
            lam = (params or {}).get("lambda", 0.94)
            fit_result = await asyncio.to_thread(ewma, arr, lam)
        else:
            model_fn = MODEL_MAP.get(model)
            if model_fn is None:
                raise ValueError(f"Unknown model: {model}")
            fit_result = await asyncio.to_thread(model_fn, arr, params)

        fc = forecast_volatility(fit_result, n_steps=n_steps, confidence_levels=confidence_levels)

        return {
            "fit": fit_result,
            "forecast": fc,
        }

    @staticmethod
    async def fit_dcc(
        returns_matrix: list[list[float]],
        univariate_model: str = "garch_11",
        univariate_params: list[dict[str, float]] | None = None,
        dcc_params: dict[str, float] | None = None,
        n_steps: int = 22,
    ) -> dict[str, Any]:
        """Fit DCC-GARCH and produce multivariate forecasts."""
        arr = np.array(returns_matrix, dtype=np.float64)

        dcc_result = await asyncio.to_thread(
            dcc_garch, arr, univariate_model, univariate_params, dcc_params
        )

        fc = forecast_dcc(dcc_result, n_steps=n_steps)

        return {
            "dcc": dcc_result,
            "forecast": fc,
        }

    @staticmethod
    async def diagnostics(returns: list[float]) -> dict[str, Any]:
        """Fit all 4 models, compare AIC/BIC, run residual tests on best model."""
        arr = np.array(returns, dtype=np.float64)

        results = []
        for _name, fn in MODEL_MAP.items():
            try:
                result = await asyncio.to_thread(fn, arr, None)
                results.append(result)
            except (ValueError, RuntimeError):
                pass

        try:
            ewma_result = await asyncio.to_thread(ewma, arr)
            results.append(ewma_result)
        except (ValueError, RuntimeError):
            pass

        if not results:
            raise RuntimeError("All models failed to fit")

        comparison = compare_models(results)

        # Run diagnostic tests on best AIC model
        best_model = next(r for r in results if r["model"] == comparison["best_aic"])
        lb_test = ljung_box_test(best_model["residuals"])
        arch_test = arch_lm_test(best_model["residuals"])

        return {
            "comparison": comparison,
            "diagnostics": {
                "ljung_box": lb_test,
                "arch_lm": arch_test,
            },
            "best_model": best_model,
        }
