"""
Reference-based tests for Floater Bond Report.

References:
- Tuckman & Serrat, "Fixed Income Securities", Ch. 15 (Floating-Rate Notes)
- Fabozzi, "Fixed Income Mathematics", Ch. 14 (FRNs)
- ISDA 2006 Definitions for day count fractions
"""
import numpy as np
import pandas as pd
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.bond_pricing import DiscountMarginCalculator, BondPricer
from src.services.bond_pricing_cashflows import AccruedInterestCalculator, DayCountCalculator
from src.services.bond_pricing_types import DayCountConvention


def _make_bond_data(face_value, coupon_percent, payments_per_year, issue_date, mat_date, coupon_dates, coupon_values):
    return {
        "face_value": face_value,
        "coupon_percent": coupon_percent,
        "payments_per_year": payments_per_year,
        "issue_date": issue_date,
        "mat_date": mat_date,
        "coupon_dates_full": coupon_dates,
        "coupon_values_full": coupon_values,
    }


# ---------------------------------------------------------------------------
# Discount Margin Calculator (4 tests)
# ---------------------------------------------------------------------------

class TestDiscountMarginCalculator:
    """Tests for DiscountMarginCalculator.calculate_discount_margin."""

    def _setup_par_floater(self):
        """2-year semiannual floater, face=1000, all reference rates 8%."""
        face_value = 1000.0
        payments_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2027-01-01")
        coupon_start = pd.Timestamp("2025-01-01")
        coupon_end = pd.Timestamp("2027-01-01")
        day_count_convention = DayCountConvention.ACTUAL_365F

        coupon_dates = [
            pd.Timestamp("2025-07-01"),
            pd.Timestamp("2026-01-01"),
            pd.Timestamp("2026-07-01"),
            pd.Timestamp("2027-01-01"),
        ]
        reference_rates = [8.0, 8.0, 8.0, 8.0]
        # Each coupon = ref_rate% / payments_per_year * face = 8/2/100*1000 = 40
        # cash_flows must be list of dicts with "date" and "cf" keys
        cash_flows = [
            {"date": coupon_dates[0], "cf": 40.0},
            {"date": coupon_dates[1], "cf": 40.0},
            {"date": coupon_dates[2], "cf": 40.0},
            {"date": coupon_dates[3], "cf": 1040.0},
        ]

        return {
            "cash_flows": cash_flows,
            "reference_rates": reference_rates,
            "valuation_date": valuation_date,
            "day_count_convention": day_count_convention,
            "face_value": face_value,
            "maturity_date": maturity_date,
            "payments_per_year": payments_per_year,
            "coupon_period_months": 6,
            "coupon_start": coupon_start,
            "coupon_end": coupon_end,
        }

    def test_dm_par_floater_zero_dm(self):
        """Par floater priced at face value should have DM ~ 0 bp.

        Reference: Tuckman & Serrat Ch. 15 — a floater priced at par with
        coupons equal to the index rate has zero discount margin.
        """
        params = self._setup_par_floater()
        dm = DiscountMarginCalculator.calculate_discount_margin(
            dirty_price=1000.0,
            **params,
        )
        np.testing.assert_allclose(dm, 0.0, atol=5.0)

    def test_dm_discount_floater_positive(self):
        """Floater priced below par should have positive DM.

        Reference: Fabozzi Ch. 14 — below-par price implies market demands
        additional spread over the index rate.
        """
        params = self._setup_par_floater()
        dm = DiscountMarginCalculator.calculate_discount_margin(
            dirty_price=980.0,
            **params,
        )
        assert dm > 0, f"Expected positive DM for discount floater, got {dm}"

    def test_dm_premium_floater_negative(self):
        """Floater priced above par should have negative DM.

        Reference: Fabozzi Ch. 14 — above-par price implies the floater
        pays more than required, so effective spread is negative.
        """
        params = self._setup_par_floater()
        dm = DiscountMarginCalculator.calculate_discount_margin(
            dirty_price=1020.0,
            **params,
        )
        assert dm < 0, f"Expected negative DM for premium floater, got {dm}"

    def test_dm_with_spread(self):
        """Floater with 100bp spread over index, priced at par, should have DM ~ 100bp.

        Reference: Tuckman & Serrat Ch. 15 — if the coupon is index + spread
        and the bond trades at par, DM equals the contractual spread.
        """
        params = self._setup_par_floater()
        # Coupons now include 100bp (1%) spread: (8% + 1%) / 2 * 1000 = 45
        coupon_dates = [
            pd.Timestamp("2025-07-01"),
            pd.Timestamp("2026-01-01"),
            pd.Timestamp("2026-07-01"),
            pd.Timestamp("2027-01-01"),
        ]
        params["cash_flows"] = [
            {"date": coupon_dates[0], "cf": 45.0},
            {"date": coupon_dates[1], "cf": 45.0},
            {"date": coupon_dates[2], "cf": 45.0},
            {"date": coupon_dates[3], "cf": 1045.0},
        ]

        dm = DiscountMarginCalculator.calculate_discount_margin(
            dirty_price=1000.0,
            **params,
        )
        np.testing.assert_allclose(dm, 100.0, atol=10.0)


# ---------------------------------------------------------------------------
# Floating Accrued Interest (3 tests)
# ---------------------------------------------------------------------------

class TestFloatingAccruedInterest:
    """Tests for AccruedInterestCalculator floating-rate methods."""

    def test_floating_nkd_in_advance(self):
        """In-advance floating NKD uses the coupon rate set at period start.

        NKD = coupon_rate * face * year_fraction
            = 0.12 * 1000 * (90/365) = 29.589...

        Reference: ISDA 2006, Section 6.2 — Actual/365 Fixed day count.
        """
        nkd = AccruedInterestCalculator.floating_rate_in_advance(
            coupon_rate_pct=12.0,
            face_value=1000.0,
            last_coupon_date=pd.Timestamp("2025-01-01"),
            valuation_date=pd.Timestamp("2025-04-01"),
            day_count_convention=DayCountConvention.ACTUAL_365F,
        )
        expected = 0.12 * 1000.0 * (90.0 / 365.0)
        np.testing.assert_allclose(nkd, expected, rtol=1e-4)

    def test_floating_nkd_in_arrears_average(self):
        """In-arrears average: NKD = face * (avg_rate + spread) * year_fraction.

        avg_rate = mean(10.0, 10.5, 11.0) = 10.5%
        total_rate = (10.5 + 2.0) / 100 = 0.125
        year_fraction = 4 / 365
        NKD = 1000 * 0.125 * (4/365) = 1.3699...

        Reference: Fabozzi Ch. 14 — averaging reference rates over the accrual
        period for in-arrears FRNs.
        """
        nkd = AccruedInterestCalculator.floating_rate_in_arrears_average(
            reference_rates=[10.0, 10.5, 11.0],
            spread_bps=200,
            face_value=1000.0,
            rate_dates=[
                pd.Timestamp("2025-01-02"),
                pd.Timestamp("2025-01-03"),
                pd.Timestamp("2025-01-04"),
            ],
            last_coupon_date=pd.Timestamp("2025-01-01"),
            valuation_date=pd.Timestamp("2025-01-05"),
            day_count_convention=DayCountConvention.ACTUAL_365F,
            lag_days=0,
        )
        expected = (10.5 / 100.0 + 200.0 / 10000.0) * 1000.0 * (4.0 / 365.0)
        np.testing.assert_allclose(nkd, expected, rtol=0.05)

    def test_floating_nkd_before_coupon_zero(self):
        """If valuation <= last_coupon_date, accrued interest should be 0.

        Reference: Standard bond convention — no accrual before the coupon
        period has started.
        """
        nkd = AccruedInterestCalculator.floating_rate_in_advance(
            coupon_rate_pct=12.0,
            face_value=1000.0,
            last_coupon_date=pd.Timestamp("2025-04-01"),
            valuation_date=pd.Timestamp("2025-04-01"),
            day_count_convention=DayCountConvention.ACTUAL_365F,
        )
        np.testing.assert_allclose(nkd, 0.0, atol=1e-10)


# ---------------------------------------------------------------------------
# Integration with BondPricer (3 tests)
# ---------------------------------------------------------------------------

class TestFloaterBondPricerIntegration:
    """Integration tests for BondPricer.calculate_metrics with floating-rate bonds."""

    def _make_simple_floater(self):
        """Create a simple 2-year semiannual floater for integration tests."""
        coupon_dates = [
            pd.Timestamp("2025-07-01"),
            pd.Timestamp("2026-01-01"),
            pd.Timestamp("2026-07-01"),
            pd.Timestamp("2027-01-01"),
        ]
        coupon_values = [40.0, 40.0, 40.0, 40.0]
        return _make_bond_data(
            face_value=1000.0,
            coupon_percent=8.0,
            payments_per_year=2,
            issue_date=pd.Timestamp("2025-01-01"),
            mat_date=pd.Timestamp("2027-01-01"),
            coupon_dates=coupon_dates,
            coupon_values=coupon_values,
        )

    def test_floater_metrics_has_dm(self):
        """BondPricer.calculate_metrics should return discountMargin when
        reference_rates are provided.

        Note: discount_yield is decimal (0.08), not percent (8.0).
        """
        bond_data = self._make_simple_floater()
        result = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=pd.Timestamp("2025-01-01"),
            discount_yield=0.08,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=6,
            reference_rates=[8.0, 8.0, 8.0, 8.0],
        )
        assert "discountMargin" in result, "Result must contain 'discountMargin' key"
        assert result["discountMargin"] is not None, "discountMargin should not be None when reference_rates provided"

    def test_floater_metrics_without_reference_rates(self):
        """Without reference_rates, discountMargin should be None."""
        bond_data = self._make_simple_floater()
        result = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=pd.Timestamp("2025-01-01"),
            discount_yield=0.08,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=6,
        )
        dm = result.get("discountMargin")
        assert dm is None, f"discountMargin should be None without reference_rates, got {dm}"

    def test_floater_dm_sign_consistency(self):
        """Price < par should give positive DM; price > par should give negative DM.

        Reference: Tuckman & Serrat Ch. 15 — the sign of the discount margin
        reflects the bond's cheapness (positive) or richness (negative)
        relative to the floating index.
        """
        bond_data = self._make_simple_floater()

        result_discount = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=pd.Timestamp("2025-01-01"),
            discount_yield=0.09,  # higher yield → lower price → positive DM
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=6,
            reference_rates=[8.0, 8.0, 8.0, 8.0],
        )

        result_premium = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=pd.Timestamp("2025-01-01"),
            discount_yield=0.07,  # lower yield → higher price → negative DM
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=6,
            reference_rates=[8.0, 8.0, 8.0, 8.0],
        )

        dm_discount = result_discount.get("discountMargin")
        dm_premium = result_premium.get("discountMargin")

        assert dm_discount is not None and dm_discount > 0, (
            f"Discount floater should have positive DM, got {dm_discount}"
        )
        assert dm_premium is not None and dm_premium < 0, (
            f"Premium floater should have negative DM, got {dm_premium}"
        )
