"""
Reference-based tests for Swap Service.

References:
- Hull, "Options, Futures, and Other Derivatives", Ch. 7
- Tuckman & Serrat, "Fixed Income Securities"
"""
import numpy as np
import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.swap_service import calculate_swap_valuation


class TestParSwap:
    """When fixed_rate == floating_rate + spread, swap should be at par (value ~ 0)."""

    def test_par_swap_value_zero(self):
        """At par, the swap value should be approximately zero.

        Setup: fixed_rate = 5.0%, floating_rate = 4.5%, spread = 50bp (0.50%),
        so effective floating = 4.5 + 0.50 = 5.0% = fixed_rate.
        Discount at 5.0% so both legs are at par.
        """
        result = calculate_swap_valuation(
            notional=1_000_000,
            tenor=5,
            fixed_rate=5.0,
            floating_rate=4.5,
            spread=50.0,
            coupons_per_year=2,
            discount_rate=5.0,
        )
        np.testing.assert_allclose(
            result["swapValue"], 0.0, atol=1.0,
            err_msg="Par swap should have value ~0"
        )


class TestFixedVsFloating:
    """When fixed coupon exceeds floating, PV of fixed leg should dominate."""

    def test_swap_fixed_vs_floating_pv(self):
        """fixed_rate > floating_rate + spread  =>  swap_value > 0."""
        result = calculate_swap_valuation(
            notional=1_000_000,
            tenor=5,
            fixed_rate=6.0,
            floating_rate=4.0,
            spread=50.0,
            coupons_per_year=2,
            discount_rate=5.0,
        )
        assert result["swapValue"] > 0, (
            "Fixed leg PV should exceed floating leg PV when fixed_rate > floating_rate + spread"
        )
        assert result["pvFixedLeg"] > result["pvFloatingLeg"]


class TestDV01:
    """DV01 must be positive and increase with tenor."""

    def test_dv01_positive(self):
        """DV01 should always be positive for a standard IRS."""
        result = calculate_swap_valuation(
            notional=10_000_000,
            tenor=10,
            fixed_rate=5.0,
            floating_rate=4.5,
            spread=50.0,
            coupons_per_year=2,
            discount_rate=5.0,
        )
        assert result["dv01"] > 0, "DV01 must be positive"

    def test_dv01_increases_with_tenor(self):
        """DV01 for a 10-year swap should exceed DV01 for a 5-year swap."""
        common = dict(
            notional=1_000_000,
            fixed_rate=5.0,
            floating_rate=4.5,
            spread=50.0,
            coupons_per_year=2,
            discount_rate=5.0,
        )
        result_5y = calculate_swap_valuation(tenor=5, **common)
        result_10y = calculate_swap_valuation(tenor=10, **common)

        assert result_10y["dv01"] > result_5y["dv01"], (
            "Longer tenor should produce higher DV01"
        )


class TestFixedLegPVManual:
    """Manually compute the PV of the fixed leg and verify against the service."""

    def test_swap_pv_fixed_leg_manual(self):
        """
        Notional = 1,000,000, fixed_rate = 5%, tenor = 2yr, cpn/yr = 2,
        discount_rate = 4%.

        coupon = 1,000,000 * 0.05 / 2 = 25,000
        period_rate = 0.04 / 2 = 0.02
        periods = 4

        PV = 25000/1.02 + 25000/1.02^2 + 25000/1.02^3 + 25000/1.02^4 + 1000000/1.02^4
           = 24509.80 + 24029.22 + 23558.06 + 23096.13 + 923845.43
           = 1,019,038.64
        """
        result = calculate_swap_valuation(
            notional=1_000_000,
            tenor=2,
            fixed_rate=5.0,
            floating_rate=4.0,
            spread=0.0,
            coupons_per_year=2,
            discount_rate=4.0,
        )
        expected_pv_fixed = 1_019_038.64
        np.testing.assert_allclose(
            result["pvFixedLeg"],
            expected_pv_fixed,
            rtol=1e-3,
            err_msg="Fixed leg PV should match manual calculation"
        )


class TestSpreadDV01:
    """Spread DV01 should be comparable in magnitude to DV01."""

    def test_spread_dv01_vs_dv01(self):
        """Both measure sensitivity to a 1bp move; they should be same order of magnitude."""
        result = calculate_swap_valuation(
            notional=1_000_000,
            tenor=5,
            fixed_rate=5.0,
            floating_rate=4.5,
            spread=50.0,
            coupons_per_year=2,
            discount_rate=5.0,
        )
        dv01 = result["dv01"]
        spread_dv01 = result["spreadDv01"]

        assert spread_dv01 > 0, "Spread DV01 must be positive"
        # Both should be within 2 orders of magnitude of each other
        ratio = spread_dv01 / dv01 if dv01 > 0 else float("inf")
        assert 0.01 < ratio < 100, (
            f"spread_dv01 ({spread_dv01:.2f}) and dv01 ({dv01:.2f}) "
            f"should be comparable in magnitude, ratio={ratio:.4f}"
        )
