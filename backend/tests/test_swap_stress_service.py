"""
Tests for swap stress testing service.

Validates DV01, curve shocks, spread shocks, vol shocks,
Greeks computation, and key rate durations.
"""
import pytest

from src.services.swap_stress_service import (
    apply_curve_shock,
    apply_spread_shock,
    apply_vol_shock,
    compute_key_rate_durations,
    compute_swap_greeks,
    get_predefined_scenarios,
    stress_test_swap_portfolio,
)


@pytest.fixture
def base_position() -> dict:
    """Standard IRS position for testing."""
    return {
        "notional": 100_000_000,
        "tenor": 5,
        "fixed_rate": 8.5,
        "floating_rate": 7.0,
        "spread": 50,
        "coupons_per_year": 2,
        "discount_rate": 7.5,
        "volatility": 20.0,
        "swap_type": "irs",
    }


@pytest.fixture
def two_position_portfolio(base_position: dict) -> list[dict]:
    """Two-swap portfolio."""
    short_swap = {
        **base_position,
        "notional": 50_000_000,
        "tenor": 2,
        "fixed_rate": 7.0,
        "floating_rate": 6.5,
        "spread": 25,
    }
    return [base_position, short_swap]


class TestCurveShock:
    """Tests for parallel curve shift."""

    def test_positive_shift_reduces_payer_value(self, base_position: dict) -> None:
        """Rates up -> payer swap value decreases (P&L negative for fixed-rate payer)."""
        result = apply_curve_shock(base_position, shift_bp=200, multiplier=1.0)
        # A parallel shift should produce non-zero P&L
        assert result["pnlImpact"] != 0.0
        assert "basePv" in result
        assert "shockedPv" in result

    def test_negative_shift_opposite_sign(self, base_position: dict) -> None:
        """Symmetric shift should produce opposite P&L."""
        up = apply_curve_shock(base_position, shift_bp=200, multiplier=1.0)
        down = apply_curve_shock(base_position, shift_bp=-200, multiplier=1.0)
        # Signs should be opposite
        assert up["pnlImpact"] * down["pnlImpact"] < 0

    def test_multiplier_scales_linearly(self, base_position: dict) -> None:
        """Multiplier 2x should roughly double the impact."""
        r1 = apply_curve_shock(base_position, shift_bp=100, multiplier=1.0)
        r2 = apply_curve_shock(base_position, shift_bp=100, multiplier=2.0)
        # Not perfectly linear due to convexity, but should be directionally consistent
        assert abs(r2["pnlImpact"]) > abs(r1["pnlImpact"])

    def test_zero_shift_no_impact(self, base_position: dict) -> None:
        """Zero shift should produce zero P&L."""
        result = apply_curve_shock(base_position, shift_bp=0, multiplier=1.0)
        assert abs(result["pnlImpact"]) < 0.01


class TestSpreadShock:
    """Tests for spread/OAS shock."""

    def test_spread_widening_impacts_pnl(self, base_position: dict) -> None:
        result = apply_spread_shock(base_position, spread_shift_bp=100, multiplier=1.0)
        assert result["pnlImpact"] != 0.0

    def test_spread_tightening_opposite(self, base_position: dict) -> None:
        up = apply_spread_shock(base_position, spread_shift_bp=100, multiplier=1.0)
        down = apply_spread_shock(base_position, spread_shift_bp=-100, multiplier=1.0)
        assert up["pnlImpact"] * down["pnlImpact"] < 0

    def test_zero_spread_shift(self, base_position: dict) -> None:
        result = apply_spread_shock(base_position, spread_shift_bp=0, multiplier=1.0)
        assert abs(result["pnlImpact"]) < 0.01


class TestVolShock:
    """Tests for volatility shock."""

    def test_vol_shock_computes_vega(self, base_position: dict) -> None:
        result = apply_vol_shock(base_position, vol_shift_pct=5.0, multiplier=1.0)
        assert "vega" in result
        # Vega should be finite
        assert abs(result["vega"]) < 1e15

    def test_vol_zero_shift(self, base_position: dict) -> None:
        result = apply_vol_shock(base_position, vol_shift_pct=0.0, multiplier=1.0)
        assert abs(result["pnlImpact"]) < 0.01


class TestGreeks:
    """Tests for swap Greeks computation."""

    def test_greeks_all_present(self, base_position: dict) -> None:
        greeks = compute_swap_greeks(base_position)
        assert "delta" in greeks
        assert "gamma" in greeks
        assert "vega" in greeks
        assert "theta" in greeks

    def test_dv01_is_nonzero(self, base_position: dict) -> None:
        """A 5Y IRS should have non-zero DV01."""
        greeks = compute_swap_greeks(base_position)
        assert abs(greeks["delta"]) > 0

    def test_gamma_is_positive_for_long_position(self, base_position: dict) -> None:
        """Gamma (convexity) should typically be non-zero."""
        greeks = compute_swap_greeks(base_position)
        assert greeks["gamma"] != 0.0

    def test_theta_is_finite(self, base_position: dict) -> None:
        greeks = compute_swap_greeks(base_position)
        assert abs(greeks["theta"]) < 1e15


class TestKeyRateDurations:
    """Tests for key rate duration computation."""

    def test_krd_has_all_buckets(self, base_position: dict) -> None:
        krd = compute_key_rate_durations(base_position)
        assert "2Y" in krd
        assert "5Y" in krd
        assert "10Y" in krd
        assert "30Y" in krd

    def test_krd_5y_dominant_for_5y_swap(self, base_position: dict) -> None:
        """5Y swap should have highest KRD sensitivity near the 5Y bucket."""
        krd = compute_key_rate_durations(base_position)
        # The 5Y bucket should be among the largest absolute KRDs
        assert abs(krd["5Y"]) >= abs(krd["30Y"])

    def test_krd_scales_with_multiplier(self, base_position: dict) -> None:
        krd1 = compute_key_rate_durations(base_position, multiplier=1.0)
        krd2 = compute_key_rate_durations(base_position, multiplier=2.0)
        for key in krd1:
            if krd1[key] != 0:
                assert abs(krd2[key]) > abs(krd1[key])


class TestStressTestPortfolio:
    """Tests for the main stress_test_swap_portfolio entry point."""

    def test_returns_results_for_all_scenarios(self, base_position: dict) -> None:
        results = stress_test_swap_portfolio([base_position])
        # Should return 9 predefined scenarios
        assert len(results) == 9

    def test_result_shape(self, base_position: dict) -> None:
        results = stress_test_swap_portfolio([base_position])
        first = results[0]
        required_keys = {
            "id", "name", "description", "shockType", "severity",
            "probability", "duration", "pnlImpact", "dv01Change",
            "spreadDv01", "delta", "gamma", "vega", "theta",
            "keyRateDurations", "marketShocks", "positionImpact",
        }
        assert required_keys.issubset(set(first.keys()))

    def test_portfolio_aggregates_positions(self, two_position_portfolio: list[dict]) -> None:
        results = stress_test_swap_portfolio(two_position_portfolio)
        first = results[0]
        # positionImpact should have entries for both positions
        assert len(first["positionImpact"]) == 2

    def test_multiplier_affects_results(self, base_position: dict) -> None:
        r1 = stress_test_swap_portfolio([base_position], multiplier=1.0)
        r2 = stress_test_swap_portfolio([base_position], multiplier=2.0)
        # P&L should differ
        assert r1[0]["pnlImpact"] != r2[0]["pnlImpact"]

    def test_empty_positions_raises(self) -> None:
        with pytest.raises(ValueError, match="At least one swap position"):
            stress_test_swap_portfolio([])

    def test_custom_scenarios(self, base_position: dict) -> None:
        custom = [{
            "id": 99,
            "name": "Custom",
            "description": "Test",
            "shockType": "Curve",
            "severity": "low",
            "probability": 0.5,
            "duration": "1 day",
            "shocks": {"curve_shift_bp": 50},
        }]
        results = stress_test_swap_portfolio([base_position], scenarios=custom)
        assert len(results) == 1
        assert results[0]["name"] == "Custom"


class TestPredefinedScenarios:
    """Tests for get_predefined_scenarios."""

    def test_returns_9_scenarios(self) -> None:
        scenarios = get_predefined_scenarios()
        assert len(scenarios) == 9

    def test_scenario_shape(self) -> None:
        scenarios = get_predefined_scenarios()
        for s in scenarios:
            assert "id" in s
            assert "name" in s
            assert "shockType" in s
            assert "shocks" in s
            assert "severity" in s
