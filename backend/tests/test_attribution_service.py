"""
Tests for attribution_service.py — Brinson-Fachler and Factor Attribution.

Reference: Brinson, Hood & Beebower (1986) for allocation/selection/interaction.
"""

import math

import numpy as np
import pytest

from src.services.attribution_service import (
    brinson_fachler_attribution,
    factor_attribution,
)

# ==============================================================================
# Brinson-Fachler Attribution Tests
# ==============================================================================


class TestBrinsonFachlerAttribution:
    """Tests for Brinson-Fachler performance attribution."""

    def test_two_sector_basic(self) -> None:
        """2-sector portfolio: allocation + selection + interaction = excess return."""
        result = brinson_fachler_attribution(
            portfolio_weights=[0.6, 0.4],
            benchmark_weights=[0.5, 0.5],
            portfolio_returns=[0.10, 0.05],
            benchmark_returns=[0.08, 0.03],
            sector_names=["Equities", "Bonds"],
        )
        totals = result["totals"]
        excess = totals["excess_return"]
        decomp = totals["allocation"] + totals["selection"] + totals["interaction"]
        assert abs(decomp - excess) < 1e-12, (
            f"Decomposition {decomp} != excess return {excess}"
        )
        assert result["n_sectors"] == 2
        assert len(result["sectors"]) == 2

    def test_three_sector_decomposition(self) -> None:
        """3-sector portfolio: verify decomposition identity."""
        w_p = [0.4, 0.35, 0.25]
        w_b = [0.3, 0.4, 0.3]
        r_p = [0.12, 0.08, -0.02]
        r_b = [0.10, 0.06, 0.01]

        result = brinson_fachler_attribution(w_p, w_b, r_p, r_b)

        port_ret = sum(wp * rp for wp, rp in zip(w_p, r_p, strict=True))
        bench_ret = sum(wb * rb for wb, rb in zip(w_b, r_b, strict=True))
        expected_excess = port_ret - bench_ret

        totals = result["totals"]
        assert abs(totals["excess_return"] - expected_excess) < 1e-12
        assert totals["verification_error"] < 1e-12

    def test_allocation_effect_sign(self) -> None:
        """Overweighting a sector that outperforms benchmark -> positive allocation."""
        result = brinson_fachler_attribution(
            portfolio_weights=[0.7, 0.3],
            benchmark_weights=[0.5, 0.5],
            portfolio_returns=[0.10, 0.02],  # irrelevant for allocation
            benchmark_returns=[0.12, 0.04],  # equities outperform benchmark total
        )
        # Benchmark total = 0.5*0.12 + 0.5*0.04 = 0.08
        # Equities: (0.7-0.5)*(0.12-0.08) = 0.2*0.04 = 0.008 > 0
        equities = result["sectors"][0]
        assert equities["allocation_effect"] > 0

    def test_selection_effect(self) -> None:
        """Better stock picking within a sector -> positive selection."""
        result = brinson_fachler_attribution(
            portfolio_weights=[0.5, 0.5],
            benchmark_weights=[0.5, 0.5],
            portfolio_returns=[0.15, 0.05],  # equities: 15% vs benchmark 10%
            benchmark_returns=[0.10, 0.05],
        )
        # Selection for equities: w_b * (r_p - r_b) = 0.5 * (0.15 - 0.10) = 0.025
        equities = result["sectors"][0]
        assert abs(equities["selection_effect"] - 0.025) < 1e-12

    def test_equal_weights_no_allocation(self) -> None:
        """Equal weights -> zero allocation effect."""
        result = brinson_fachler_attribution(
            portfolio_weights=[0.5, 0.5],
            benchmark_weights=[0.5, 0.5],
            portfolio_returns=[0.10, 0.05],
            benchmark_returns=[0.08, 0.03],
        )
        assert abs(result["totals"]["allocation"]) < 1e-12

    def test_single_sector(self) -> None:
        """Single sector: all effect comes from selection."""
        result = brinson_fachler_attribution(
            portfolio_weights=[1.0],
            benchmark_weights=[1.0],
            portfolio_returns=[0.12],
            benchmark_returns=[0.08],
            sector_names=["All"],
        )
        totals = result["totals"]
        assert abs(totals["excess_return"] - 0.04) < 1e-12
        assert abs(totals["allocation"]) < 1e-12  # same weight
        assert abs(totals["selection"] - 0.04) < 1e-12

    def test_short_positions(self) -> None:
        """Short positions: negative weights allowed."""
        result = brinson_fachler_attribution(
            portfolio_weights=[1.3, -0.3],
            benchmark_weights=[0.8, 0.2],
            portfolio_returns=[0.10, -0.05],
            benchmark_returns=[0.08, 0.02],
        )
        totals = result["totals"]
        decomp = totals["allocation"] + totals["selection"] + totals["interaction"]
        assert abs(decomp - totals["excess_return"]) < 1e-12

    def test_zero_excess_return(self) -> None:
        """Identical portfolios -> zero excess return."""
        result = brinson_fachler_attribution(
            portfolio_weights=[0.5, 0.5],
            benchmark_weights=[0.5, 0.5],
            portfolio_returns=[0.10, 0.05],
            benchmark_returns=[0.10, 0.05],
        )
        assert abs(result["totals"]["excess_return"]) < 1e-12

    def test_default_sector_names(self) -> None:
        """Auto-generated sector names when not provided."""
        result = brinson_fachler_attribution(
            portfolio_weights=[0.5, 0.5],
            benchmark_weights=[0.5, 0.5],
            portfolio_returns=[0.10, 0.05],
            benchmark_returns=[0.08, 0.03],
        )
        assert result["sectors"][0]["name"] == "Sector_1"
        assert result["sectors"][1]["name"] == "Sector_2"

    def test_mismatched_lengths_raises(self) -> None:
        """Mismatched input lengths raise ValueError."""
        with pytest.raises(ValueError, match="same length"):
            brinson_fachler_attribution(
                portfolio_weights=[0.5, 0.5],
                benchmark_weights=[0.3, 0.3, 0.4],
                portfolio_returns=[0.10, 0.05],
                benchmark_returns=[0.08, 0.03],
            )

    def test_empty_input_raises(self) -> None:
        """Empty inputs raise ValueError."""
        with pytest.raises(ValueError, match="At least one sector"):
            brinson_fachler_attribution([], [], [], [])

    def test_bad_weight_sum_raises(self) -> None:
        """Weights far from 1.0 raise ValueError."""
        with pytest.raises(ValueError, match="weights sum"):
            brinson_fachler_attribution(
                portfolio_weights=[0.3, 0.3],
                benchmark_weights=[0.5, 0.5],
                portfolio_returns=[0.10, 0.05],
                benchmark_returns=[0.08, 0.03],
            )

    def test_wrong_sector_names_count_raises(self) -> None:
        """Wrong number of sector names raises ValueError."""
        with pytest.raises(ValueError, match="sector names"):
            brinson_fachler_attribution(
                portfolio_weights=[0.5, 0.5],
                benchmark_weights=[0.5, 0.5],
                portfolio_returns=[0.10, 0.05],
                benchmark_returns=[0.08, 0.03],
                sector_names=["Only One"],
            )


# ==============================================================================
# Factor Attribution Tests
# ==============================================================================


class TestFactorAttribution:
    """Tests for OLS factor-based P&L attribution."""

    def test_single_factor_beta_recovery(self) -> None:
        """Synthetic single-factor data: recovered beta should be close to true value."""
        np.random.seed(42)
        t_obs = 100
        true_alpha = 0.0005
        true_beta = 1.2
        factor = np.random.randn(t_obs) * 0.02
        noise = np.random.randn(t_obs) * 0.003
        portfolio = true_alpha + true_beta * factor + noise

        result = factor_attribution(
            portfolio_returns=portfolio.tolist(),
            factor_returns=[[f] for f in factor.tolist()],
            factor_names=["Market"],
            portfolio_value=1_000_000,
        )

        assert abs(result["betas"][0] - true_beta) < 0.15
        assert abs(result["alpha"] - true_alpha) < 0.001
        assert result["r_squared"] > 0.8
        assert result["n_factors"] == 1
        assert result["n_observations"] == t_obs

    def test_three_factor_decomposition(self) -> None:
        """3-factor synthetic data: verify betas approximately recovered."""
        np.random.seed(123)
        t_obs = 200
        true_betas = [1.0, 0.5, -0.3]

        factors = np.random.randn(t_obs, 3) * 0.02
        noise = np.random.randn(t_obs) * 0.002
        portfolio = 0.0002 + factors @ np.array(true_betas) + noise

        result = factor_attribution(
            portfolio_returns=portfolio.tolist(),
            factor_returns=factors.tolist(),
            factor_names=["MKT", "SMB", "HML"],
            portfolio_value=5_000_000,
        )

        for i, true_b in enumerate(true_betas):
            assert abs(result["betas"][i] - true_b) < 0.2, (
                f"Factor {i}: estimated {result['betas'][i]:.4f} vs true {true_b}"
            )
        assert result["r_squared"] > 0.85
        assert result["n_factors"] == 3

    def test_pnl_decomposition_sums(self) -> None:
        """Total P&L should approximately equal factor PnL + alpha PnL + residual PnL."""
        np.random.seed(99)
        t_obs = 50
        factors = np.random.randn(t_obs, 2) * 0.01
        portfolio = 0.001 + factors @ [0.8, 0.4] + np.random.randn(t_obs) * 0.001

        result = factor_attribution(
            portfolio_returns=portfolio.tolist(),
            factor_returns=factors.tolist(),
            portfolio_value=2_000_000,
        )

        explained = result["total_factor_pnl"] + result["alpha_pnl"]
        total = result["total_pnl"]
        residual = result["residual_pnl"]

        # explained + residual should = total
        assert abs((explained + residual) - total) < 1.0, (
            f"PnL decomposition mismatch: {explained} + {residual} != {total}"
        )

    def test_zero_alpha_when_no_intercept(self) -> None:
        """When data is pure factor with no intercept, alpha should be near zero."""
        np.random.seed(7)
        t_obs = 100
        factor = np.random.randn(t_obs) * 0.02
        portfolio = 0.9 * factor  # no alpha, no noise

        result = factor_attribution(
            portfolio_returns=portfolio.tolist(),
            factor_returns=[[f] for f in factor.tolist()],
        )

        assert abs(result["alpha"]) < 0.001
        assert result["r_squared"] > 0.99

    def test_high_r_squared_for_exact_fit(self) -> None:
        """When portfolio = exact linear combination of factors, R2 ~ 1."""
        t_obs = 50
        factors = np.arange(t_obs * 2, dtype=float).reshape(t_obs, 2) * 0.001
        portfolio = factors @ [0.5, -0.3]

        result = factor_attribution(
            portfolio_returns=portfolio.tolist(),
            factor_returns=factors.tolist(),
        )

        assert result["r_squared"] > 0.999

    def test_single_asset_single_factor(self) -> None:
        """Minimal case: 1 factor, few observations."""
        result = factor_attribution(
            portfolio_returns=[0.01, -0.005, 0.008, 0.003, -0.002],
            factor_returns=[[0.012], [-0.008], [0.010], [0.005], [-0.003]],
            factor_names=["Market"],
            portfolio_value=100_000,
        )

        assert len(result["betas"]) == 1
        assert result["n_observations"] == 5
        assert not math.isnan(result["r_squared"])

    def test_default_names(self) -> None:
        """Factor names auto-generated when not provided."""
        result = factor_attribution(
            portfolio_returns=[0.01, -0.01, 0.02, 0.0, 0.01],
            factor_returns=[[0.02, 0.01], [-0.01, 0.0], [0.015, -0.005], [0.005, 0.002], [-0.01, 0.003]],
        )

        assert result["factor_names"] == ["Factor_1", "Factor_2"]

    def test_insufficient_observations_raises(self) -> None:
        """Too few observations for number of factors raises ValueError."""
        with pytest.raises(ValueError, match="Insufficient"):
            factor_attribution(
                portfolio_returns=[0.01, 0.02],
                factor_returns=[[0.01, 0.02, 0.03], [0.02, 0.01, 0.04]],
            )

    def test_mismatched_lengths_raises(self) -> None:
        """Mismatched T between portfolio and factors raises ValueError."""
        with pytest.raises(ValueError, match="observations"):
            factor_attribution(
                portfolio_returns=[0.01, 0.02, 0.03],
                factor_returns=[[0.01], [0.02]],
            )

    def test_negative_portfolio_value_raises(self) -> None:
        """Negative portfolio value raises ValueError."""
        with pytest.raises(ValueError, match="positive"):
            factor_attribution(
                portfolio_returns=[0.01, 0.02, 0.03, 0.04, 0.05],
                factor_returns=[[0.01], [0.02], [0.03], [0.04], [0.05]],
                portfolio_value=-100,
            )

    def test_wrong_factor_names_count_raises(self) -> None:
        """Wrong number of factor names raises ValueError."""
        with pytest.raises(ValueError, match="factor names"):
            factor_attribution(
                portfolio_returns=[0.01, 0.02, 0.03, 0.04, 0.05],
                factor_returns=[[0.01, 0.02], [0.02, 0.01], [0.03, 0.0], [0.04, -0.01], [0.05, 0.01]],
                factor_names=["Only One"],
            )
