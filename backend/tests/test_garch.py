"""
Reference-based tests for GARCH models.

References:
- Bollerslev (1986), "Generalized Autoregressive Conditional Heteroskedasticity"
- Engle (1982), "ARCH"
- RiskMetrics Technical Document (J.P. Morgan, 1996)
- Glosten, Jagannathan, Runkle (1993) for GJR-GARCH
- Nelson (1991) for EGARCH
"""
import numpy as np
import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.garch.univariate import garch_11, gjr_garch, egarch, ewma
from src.services.garch.forecasting import forecast_volatility


# ---------------------------------------------------------------------------
# GARCH(1,1) tests
# ---------------------------------------------------------------------------


class TestGarch11ForwardPass:
    """Bollerslev (1986) forward variance recursion with known parameters."""

    def test_garch11_forward_pass_known_params(self):
        """Verify GARCH(1,1) variance recursion: sigma2_t = omega + alpha*r_{t-1}^2 + beta*sigma2_{t-1}."""
        omega, alpha, beta = 1e-6, 0.08, 0.88
        returns = np.array(
            [0.01, -0.02, 0.005, -0.01, 0.015, -0.008, 0.003, -0.012, 0.007, -0.005]
        )

        # Manual variance computation
        v = [omega / (1 - alpha - beta)]  # v0 = unconditional = 2.5e-5
        for i in range(len(returns)):
            v_next = omega + alpha * returns[i] ** 2 + beta * v[-1]
            v.append(v_next)

        result = garch_11(
            returns, params={"omega": omega, "alpha": alpha, "beta": beta}
        )

        # result["variances"][0] = v0 (initial), result["variances"][1] = first recursion step
        # Manual v[0] = v0, v[1] = first step, etc.
        np.testing.assert_allclose(
            result["variances"][:5], v[:5], rtol=1e-6,
            err_msg="First 5 GARCH(1,1) variances must match manual recursion"
        )


class TestGarch11Stationarity:
    """Stationarity constraint: alpha + beta < 1."""

    def test_garch11_stationarity_check(self):
        """alpha=0.5, beta=0.6 → persistence >= 1.0 → should raise ValueError."""
        returns = np.random.normal(0, 0.01, 100)
        with pytest.raises(ValueError):
            garch_11(returns, params={"omega": 1e-6, "alpha": 0.5, "beta": 0.6})


class TestGarch11LongRunVariance:
    """Long-run variance = omega / (1 - alpha - beta)."""

    def test_garch11_long_run_variance(self):
        omega, alpha, beta = 1e-6, 0.08, 0.88
        expected_lrv = omega / (1 - alpha - beta)  # 2.5e-5

        returns = np.random.normal(0, 0.01, 500)
        result = garch_11(
            returns, params={"omega": omega, "alpha": alpha, "beta": beta}
        )

        np.testing.assert_allclose(
            result["long_run_variance"], expected_lrv, rtol=1e-6,
            err_msg="Long-run variance must equal omega/(1-alpha-beta)"
        )


class TestGarch11Persistence:
    """Persistence = alpha + beta."""

    def test_garch11_persistence(self):
        omega, alpha, beta = 1e-6, 0.08, 0.88
        returns = np.random.normal(0, 0.01, 500)
        result = garch_11(
            returns, params={"omega": omega, "alpha": alpha, "beta": beta}
        )

        np.testing.assert_allclose(
            result["persistence"], alpha + beta, rtol=1e-6,
            err_msg="Persistence must equal alpha + beta"
        )


class TestGarch11MLE:
    """MLE should recover true parameters from synthetic GARCH(1,1) data."""

    def test_garch11_mle_recovery(self):
        """Generate 2000 synthetic GARCH(1,1) returns, fit via MLE, check recovery within 30%."""
        np.random.seed(42)
        true_omega, true_alpha, true_beta = 2e-6, 0.10, 0.85
        n = 2000

        # Simulate GARCH(1,1) returns
        returns = np.zeros(n)
        variances = np.zeros(n)
        variances[0] = true_omega / (1 - true_alpha - true_beta)
        returns[0] = np.random.normal(0, np.sqrt(variances[0]))

        for t in range(1, n):
            variances[t] = true_omega + true_alpha * returns[t - 1] ** 2 + true_beta * variances[t - 1]
            returns[t] = np.random.normal(0, np.sqrt(variances[t]))

        result = garch_11(returns, params=None)

        fitted = result["params"]
        # omega is hardest to recover — MLE variance is high for small values
        # Relax to 80% for omega, 30% for alpha/beta
        assert abs(fitted["omega"] - true_omega) / true_omega < 0.80, (
            f"omega recovery failed: {fitted['omega']:.2e} vs {true_omega:.2e}"
        )
        assert abs(fitted["alpha"] - true_alpha) / true_alpha < 0.30, (
            f"alpha recovery failed: {fitted['alpha']:.4f} vs {true_alpha:.4f}"
        )
        assert abs(fitted["beta"] - true_beta) / true_beta < 0.30, (
            f"beta recovery failed: {fitted['beta']:.4f} vs {true_beta:.4f}"
        )
        # persistence should be close to true (alpha+beta ≈ 0.95)
        assert abs(result["persistence"] - (true_alpha + true_beta)) < 0.05


# ---------------------------------------------------------------------------
# EWMA tests (RiskMetrics)
# ---------------------------------------------------------------------------


class TestEWMARiskMetrics:
    """RiskMetrics Technical Document (J.P. Morgan, 1996): lambda=0.94."""

    def test_ewma_riskmetrics(self):
        """Verify EWMA variance recursion: sigma2_t = lambda*sigma2_{t-1} + (1-lambda)*r_{t-1}^2."""
        lam = 0.94
        returns = np.array(
            [0.01, -0.02, 0.005, -0.01, 0.015, -0.008, 0.003, -0.012, 0.007, -0.005]
        )
        v0 = np.var(returns)

        # Manual recursion
        v = [v0]
        for i in range(len(returns)):
            v_next = lam * v[-1] + (1 - lam) * returns[i] ** 2
            v.append(v_next)

        result = ewma(returns, lam=lam)

        # result["variances"][0] = v0, result["variances"][1] = first step, etc.
        np.testing.assert_allclose(
            result["variances"][:5], v[:5], rtol=1e-6,
            err_msg="First 5 EWMA variances must match manual recursion"
        )


class TestEWMALambdaBounds:
    """Lambda must be in (0, 1) exclusive."""

    def test_ewma_lambda_bounds(self):
        returns = np.random.normal(0, 0.01, 100)

        with pytest.raises(ValueError):
            ewma(returns, lam=0.0)

        with pytest.raises(ValueError):
            ewma(returns, lam=1.0)


# ---------------------------------------------------------------------------
# GJR-GARCH tests
# ---------------------------------------------------------------------------


class TestGJRGARCHLeverage:
    """Glosten, Jagannathan, Runkle (1993): leverage effect."""

    def test_gjr_garch_leverage_effect(self):
        """Negative return should produce higher next-period variance than positive return of same magnitude."""
        base = np.array([0.01, 0.005, -0.005, 0.003, 0.002, 0.001, -0.001, 0.004, 0.002, 0.001])
        positive_returns = base.copy()
        positive_returns[3] = 0.02  # Large positive shock

        negative_returns = base.copy()
        negative_returns[3] = -0.02  # Large negative shock (same magnitude)

        result_pos = gjr_garch(positive_returns)
        result_neg = gjr_garch(negative_returns)

        # After element 3, negative return should yield higher variance (leverage effect)
        assert result_neg["variances"][4] > result_pos["variances"][4], (
            "GJR-GARCH must exhibit leverage: negative shocks → higher variance"
        )


# ---------------------------------------------------------------------------
# EGARCH tests
# ---------------------------------------------------------------------------


class TestEGARCHLogSpace:
    """Nelson (1991): EGARCH operates in log-variance space → variances always positive."""

    def test_egarch_log_space(self):
        """All EGARCH variances must be strictly positive (guaranteed by exp transform)."""
        np.random.seed(123)
        returns = np.random.normal(0, 0.02, 200)
        result = egarch(returns)

        assert np.all(np.array(result["variances"]) > 0), (
            "EGARCH variances must be strictly positive (exp transform guarantee)"
        )


# ---------------------------------------------------------------------------
# Forecasting tests
# ---------------------------------------------------------------------------


class TestForecastMeanReversion:
    """GARCH(1,1) forecasts must mean-revert to the unconditional variance."""

    def test_forecast_garch_mean_reversion(self):
        np.random.seed(99)
        returns = np.random.normal(0, 0.015, 500)
        model = garch_11(returns)
        fc = forecast_volatility(model, n_steps=100)

        long_run_var = model["long_run_variance"]
        last_forecast = fc["forecasts"][-1]

        assert abs(last_forecast - long_run_var) < 0.1 * long_run_var, (
            f"100-step forecast {last_forecast:.2e} must converge to long-run variance {long_run_var:.2e}"
        )


class TestForecastEWMAConstant:
    """EWMA has unit persistence → forecast is constant (no mean reversion)."""

    def test_forecast_ewma_constant(self):
        np.random.seed(77)
        returns = np.random.normal(0, 0.01, 300)
        model = ewma(returns, lam=0.94)
        fc = forecast_volatility(model, n_steps=22)

        forecasts = np.array(fc["forecasts"])
        np.testing.assert_allclose(
            forecasts, forecasts[0], rtol=1e-6,
            err_msg="EWMA forecasts must be constant (no mean reversion)"
        )


class TestForecastStructure:
    """Forecast output must contain all required keys."""

    def test_forecast_returns_correct_structure(self):
        np.random.seed(55)
        returns = np.random.normal(0, 0.01, 200)
        model = garch_11(returns)
        fc = forecast_volatility(model, n_steps=22)

        required_keys = {
            "forecasts",
            "forecast_volatilities",
            "annualized_volatilities",
            "confidence_intervals",
            "term_structure",
            "current_vol",
            "forecast_vol",
            "n_steps",
        }
        missing = required_keys - set(fc.keys())
        assert not missing, f"Missing forecast keys: {missing}"
