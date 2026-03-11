"""
Reference-based tests for Risk Service.

References:
- Hull, "Options, Futures, and Other Derivatives", Ch. 22
- Acerbi & Tasche (2002), "On the coherence of Expected Shortfall"
- RiskMetrics Technical Document (J.P. Morgan, 1996)
"""
import numpy as np
import pytest
from scipy.stats import norm

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.risk_service import (
    parametric_var,
    historical_var,
    monte_carlo_var,
    component_var,
)


PV = 1_000_000


# ---------------------------------------------------------------------------
# Parametric VaR
# ---------------------------------------------------------------------------

class TestParametricVaR:
    """Hull Ch.22 — delta-normal VaR = z_alpha * sigma * PV."""

    def test_parametric_var_95_known_vol(self, sample_returns):
        """VaR_95 = z_95 * sample_std * PV — exact match with sample σ."""
        result = parametric_var(sample_returns, confidence=0.95, horizon=1, portfolio_value=PV)
        sample_sigma = float(np.std(sample_returns, ddof=1))
        expected_var = norm.ppf(0.95) * sample_sigma * PV
        np.testing.assert_allclose(result["var"], expected_var, rtol=1e-4)

    def test_parametric_var_99(self, sample_returns):
        """VaR_99 = z_99 * sample_std * PV."""
        result = parametric_var(sample_returns, confidence=0.99, horizon=1, portfolio_value=PV)
        sample_sigma = float(np.std(sample_returns, ddof=1))
        expected_var = norm.ppf(0.99) * sample_sigma * PV
        np.testing.assert_allclose(result["var"], expected_var, rtol=1e-4)

    def test_parametric_cvar_analytical(self, sample_returns):
        """CVaR_95 = σ * φ(z_95) / α * PV (Acerbi & Tasche 2002)."""
        result = parametric_var(sample_returns, confidence=0.95, horizon=1, portfolio_value=PV)
        sample_sigma = float(np.std(sample_returns, ddof=1))
        z95 = norm.ppf(0.95)
        expected_cvar = sample_sigma * norm.pdf(z95) / 0.05 * PV
        np.testing.assert_allclose(result["cvar"], expected_cvar, rtol=1e-4)

    def test_parametric_cvar_exceeds_var(self, sample_returns):
        """Coherence: CVaR >= VaR (Acerbi & Tasche, 2002)."""
        result = parametric_var(sample_returns, confidence=0.95, horizon=1, portfolio_value=PV)
        assert result["cvar"] >= result["var"], "CVaR must be >= VaR"

    def test_parametric_var_with_garch_vol(self, sample_returns):
        """When GARCH vol is provided, VaR uses it instead of historical σ."""
        result = parametric_var(
            sample_returns, confidence=0.95, horizon=1,
            portfolio_value=PV, garch_forecast_vol=0.02,
        )
        expected_var = norm.ppf(0.95) * 0.02 * PV  # 32,900
        np.testing.assert_allclose(result["var"], expected_var, rtol=0.001)

    def test_parametric_var_horizon_scaling(self, sample_returns):
        """RiskMetrics: VaR(h) = VaR(1) * √h."""
        result_1d = parametric_var(sample_returns, confidence=0.95, horizon=1, portfolio_value=PV)
        result_10d = parametric_var(sample_returns, confidence=0.95, horizon=10, portfolio_value=PV)
        np.testing.assert_allclose(
            result_10d["var"],
            result_1d["var"] * np.sqrt(10),
            rtol=0.001,
        )


# ---------------------------------------------------------------------------
# Historical VaR
# ---------------------------------------------------------------------------

class TestHistoricalVaR:
    """Non-parametric VaR from empirical return distribution."""

    def test_historical_var_95(self, sample_returns):
        """VaR = |5th percentile of returns| * PV."""
        result = historical_var(sample_returns, confidence=0.95, horizon=1, portfolio_value=PV)
        quantile_5 = np.percentile(sample_returns, 5)
        expected_var = abs(quantile_5) * PV
        np.testing.assert_allclose(result["var"], expected_var, rtol=0.05)

    def test_historical_cvar_95(self, sample_returns):
        """CVaR = mean of returns below the VaR quantile (tail mean)."""
        result = historical_var(sample_returns, confidence=0.95, horizon=1, portfolio_value=PV)
        quantile_5 = np.percentile(sample_returns, 5)
        tail = sample_returns[sample_returns <= quantile_5]
        expected_cvar = abs(tail.mean()) * PV
        np.testing.assert_allclose(result["cvar"], expected_cvar, rtol=0.05)

    def test_historical_cvar_exceeds_var(self, sample_returns):
        """Coherence: CVaR >= VaR."""
        result = historical_var(sample_returns, confidence=0.95, horizon=1, portfolio_value=PV)
        assert result["cvar"] >= result["var"], "CVaR must be >= VaR"


# ---------------------------------------------------------------------------
# Monte Carlo VaR
# ---------------------------------------------------------------------------

class TestMonteCarloVaR:
    """MC simulation-based VaR with convergence and reproducibility checks."""

    def test_monte_carlo_var_convergence(self, sample_returns):
        """With 100K sims on normal returns, MC VaR converges to parametric VaR within 10%."""
        mc_result = monte_carlo_var(
            sample_returns, confidence=0.95, horizon=1,
            portfolio_value=PV, n_simulations=100_000, seed=42,
        )
        param_result = parametric_var(
            sample_returns, confidence=0.95, horizon=1,
            portfolio_value=PV,
        )
        np.testing.assert_allclose(mc_result["var"], param_result["var"], rtol=0.10)

    def test_monte_carlo_var_seed_reproducibility(self, sample_returns):
        """Same seed produces identical results."""
        kwargs = dict(
            returns=sample_returns, confidence=0.95, horizon=1,
            portfolio_value=PV, n_simulations=10_000, seed=42,
        )
        result_a = monte_carlo_var(**kwargs)
        result_b = monte_carlo_var(**kwargs)
        np.testing.assert_allclose(result_a["var"], result_b["var"], atol=0)


# ---------------------------------------------------------------------------
# Component VaR
# ---------------------------------------------------------------------------

class TestComponentVaR:
    """Euler decomposition of portfolio VaR."""

    def test_component_var_euler_sum(self, two_asset_returns):
        """Sum of component VaRs ≈ total VaR (Euler's theorem)."""
        weights = np.array([0.6, 0.4])
        result = component_var(two_asset_returns, weights, confidence=0.95, portfolio_value=PV)
        np.testing.assert_allclose(
            sum(result["component_var"]),
            result["total_var"],
            rtol=0.0001,
        )

    def test_component_var_pct_sum_to_one(self, two_asset_returns):
        """Percentage contributions sum to 1.0."""
        weights = np.array([0.6, 0.4])
        result = component_var(two_asset_returns, weights, confidence=0.95, portfolio_value=PV)
        np.testing.assert_allclose(sum(result["pct_contribution"]), 1.0, atol=1e-10)

    def test_component_var_single_asset(self):
        """For a single asset, component VaR = total VaR.
        Use 2 identical assets with [0.5, 0.5] weights to avoid np.cov scalar issue."""
        rng = np.random.default_rng(99)
        r = rng.normal(0, 0.01, 500)
        two_asset_returns = np.column_stack([r, r])  # perfectly correlated
        weights = np.array([0.5, 0.5])
        result = component_var(two_asset_returns, weights, confidence=0.95, portfolio_value=PV)
        # Both components should contribute equally
        np.testing.assert_allclose(
            result["component_var"][0], result["component_var"][1], rtol=1e-10
        )
        # Sum = total
        np.testing.assert_allclose(
            sum(result["component_var"]), result["total_var"], rtol=1e-6
        )

    def test_component_var_zero_returns(self):
        """All-zero returns → all VaRs = 0."""
        zero_returns = np.zeros((100, 2))
        weights = np.array([0.5, 0.5])
        result = component_var(zero_returns, weights, confidence=0.95, portfolio_value=PV)
        np.testing.assert_allclose(result["total_var"], 0.0, atol=1e-10)
        np.testing.assert_allclose(result["component_var"], [0.0, 0.0], atol=1e-10)
