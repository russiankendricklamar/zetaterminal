"""
Reference-based tests for Bond Pricing.

References:
- Hull, "Options, Futures, and Other Derivatives", Table 4.3
- Tuckman & Serrat, "Fixed Income Securities", Ch. 3
- Fabozzi, "Fixed Income Mathematics"
"""
import numpy as np
import pandas as pd
import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.bond_pricing import YTMCalculator
from src.services.bond_pricing_cashflows import DayCountCalculator
from src.services.bond_pricing_types import DayCountConvention


# ---------------------------------------------------------------------------
# Helper: compute bond dirty price from YTM using Actual/365F day-count
# ---------------------------------------------------------------------------

def _bond_price_from_ytm(
    face_value: float,
    coupon_rate: float,
    ytm: float,
    n_periods: int,
    coupons_per_year: int,
    valuation_date: pd.Timestamp,
    maturity_date: pd.Timestamp,
    day_count: DayCountConvention = DayCountConvention.ACTUAL_365F,
) -> float:
    """Compute dirty price = sum CF_i / (1+ytm)^t_i using year fractions."""
    cash_flows = _build_cashflows(
        face_value, coupon_rate, n_periods, coupons_per_year, valuation_date, maturity_date
    )
    price = 0.0
    for cf in cash_flows:
        t = DayCountCalculator.calculate_year_fraction(
            valuation_date, cf["date"], day_count
        )
        price += cf["cf"] / (1.0 + ytm) ** t
    return price


def _build_cashflows(
    face_value: float,
    coupon_rate: float,
    n_periods: int,
    coupons_per_year: int,
    valuation_date: pd.Timestamp,
    maturity_date: pd.Timestamp,
) -> list[dict]:
    """Build evenly-spaced coupon cashflows + principal at maturity."""
    coupon = face_value * coupon_rate / coupons_per_year
    months_per_period = 12 // coupons_per_year
    cash_flows = []
    for i in range(1, n_periods + 1):
        cf_date = valuation_date + pd.DateOffset(months=months_per_period * i)
        cf_amount = coupon + (face_value if i == n_periods else 0.0)
        cash_flows.append({"date": pd.Timestamp(cf_date), "cf": cf_amount})
    return cash_flows


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestZeroCouponPrice:
    """P = FV / (1+y)^T for a zero-coupon bond."""

    def test_zero_coupon_price(self):
        """FV=100, y=6%, T=5  =>  P = 100/1.06^5 = 74.7258."""
        face_value = 100.0
        ytm = 0.06
        t_years = 5.0
        expected_price = face_value / (1.0 + ytm) ** t_years  # 74.72582...

        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2030-01-01")

        # Build a single cashflow at maturity (zero-coupon)
        cash_flows = [{"date": maturity_date, "cf": face_value}]

        # Recover YTM from the expected price
        recovered_ytm = YTMCalculator.calculate_ytm(
            dirty_price=expected_price,
            cash_flows=cash_flows,
            valuation_date=valuation_date,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            face_value=face_value,
            maturity_date=maturity_date,
        )

        np.testing.assert_allclose(
            recovered_ytm, ytm, rtol=1e-3,
            err_msg="YTM recovered from zero-coupon price should match original"
        )


class TestCouponBondPriceHull:
    """Hull Table 4.3: 5% semiannual coupon, 10yr, YTM=6% => Price ~ 92.64."""

    def test_coupon_bond_price_hull_table(self):
        """Verify round-trip: price from YTM -> YTM from price matches."""
        face_value = 100.0
        coupon_rate = 0.05
        ytm = 0.06
        n_periods = 20
        coupons_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2035-01-01")

        # Textbook semiannual price: sum of 20 coupons of 2.5 at 3% per period + 100/1.03^20
        # P = 2.5 * [1 - 1.03^-20] / 0.03 + 100 / 1.03^20
        period_rate = 0.03
        annuity = 2.5 * (1 - (1 + period_rate) ** (-n_periods)) / period_rate
        principal_pv = 100.0 / (1 + period_rate) ** n_periods
        expected_textbook = annuity + principal_pv  # ~92.64

        np.testing.assert_allclose(
            expected_textbook, 92.64, atol=0.1,
            err_msg="Textbook semiannual bond price sanity check"
        )

        # Now compute price using our helper (year-fraction based) and recover YTM
        price = _bond_price_from_ytm(
            face_value, coupon_rate, ytm, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        cash_flows = _build_cashflows(
            face_value, coupon_rate, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        recovered_ytm = YTMCalculator.calculate_ytm(
            dirty_price=price,
            cash_flows=cash_flows,
            valuation_date=valuation_date,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            face_value=face_value,
            maturity_date=maturity_date,
        )
        np.testing.assert_allclose(
            recovered_ytm, ytm, rtol=1e-3,
            err_msg="Recovered YTM should match original 6%"
        )


class TestParBondPrice:
    """When coupon_rate == YTM, price should equal face_value."""

    def test_par_bond_price(self):
        face_value = 100.0
        coupon_rate = 0.05
        ytm = 0.05
        n_periods = 10
        coupons_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2030-01-01")

        price = _bond_price_from_ytm(
            face_value, coupon_rate, ytm, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        np.testing.assert_allclose(
            price, face_value, rtol=5e-3,
            err_msg="Par bond (coupon == YTM) should price at face value"
        )


class TestPremiumDiscount:
    """coupon > YTM => premium, coupon < YTM => discount."""

    def test_premium_discount(self):
        face_value = 100.0
        n_periods = 10
        coupons_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2030-01-01")

        # Premium: coupon 8% > YTM 5%
        price_premium = _bond_price_from_ytm(
            face_value, 0.08, 0.05, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        assert price_premium > face_value, "Coupon > YTM should be a premium bond"

        # Discount: coupon 3% < YTM 5%
        price_discount = _bond_price_from_ytm(
            face_value, 0.03, 0.05, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        assert price_discount < face_value, "Coupon < YTM should be a discount bond"


class TestModifiedDurationFiniteDiff:
    """ModDur ~ -(P+ - P-) / (2 * dy * P0) via finite differences."""

    def test_modified_duration_finite_diff(self):
        face_value = 100.0
        coupon_rate = 0.05
        ytm = 0.06
        n_periods = 10
        coupons_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2030-01-01")
        dy = 0.0001  # 1 bp

        p0 = _bond_price_from_ytm(
            face_value, coupon_rate, ytm, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        p_up = _bond_price_from_ytm(
            face_value, coupon_rate, ytm + dy, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        p_down = _bond_price_from_ytm(
            face_value, coupon_rate, ytm - dy, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )

        mod_dur = -(p_up - p_down) / (2 * dy * p0)

        # 5yr semiannual 5% coupon at 6% YTM: ModDur should be ~4.0-4.5
        assert 3.0 < mod_dur < 6.0, (
            f"Modified duration {mod_dur:.4f} outside expected range for a 5yr bond"
        )


class TestMacaulayToModified:
    """ModDur = MacDur / (1 + y/n). Verify via finite differences."""

    def test_macaulay_to_modified(self):
        face_value = 100.0
        coupon_rate = 0.06
        ytm = 0.06
        n_periods = 10
        coupons_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2030-01-01")
        dy = 0.0001

        cash_flows = _build_cashflows(
            face_value, coupon_rate, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )

        # Compute Macaulay duration analytically (weighted average time)
        p0 = 0.0
        mac_dur = 0.0
        for cf in cash_flows:
            t = DayCountCalculator.calculate_year_fraction(
                valuation_date, cf["date"], DayCountConvention.ACTUAL_365F
            )
            pv = cf["cf"] / (1.0 + ytm) ** t
            p0 += pv
            mac_dur += t * pv
        mac_dur /= p0

        # Finite-diff modified duration
        p_up = _bond_price_from_ytm(
            face_value, coupon_rate, ytm + dy, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        p_down = _bond_price_from_ytm(
            face_value, coupon_rate, ytm - dy, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        mod_dur_fd = -(p_up - p_down) / (2 * dy * p0)

        # Relationship: ModDur ~ MacDur / (1 + y)
        # For continuous-compounding-like year fractions, the denominator is (1+y)
        mod_dur_from_mac = mac_dur / (1.0 + ytm)

        np.testing.assert_allclose(
            mod_dur_fd, mod_dur_from_mac, rtol=0.02,
            err_msg="Finite-diff ModDur should match MacDur/(1+y)"
        )


class TestConvexityImprovesEstimate:
    """Duration + convexity should give a more accurate price change estimate."""

    def test_convexity_improves_estimate(self):
        face_value = 100.0
        coupon_rate = 0.05
        ytm = 0.06
        n_periods = 20
        coupons_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2035-01-01")
        dy_large = 0.02  # 200bp shock
        dy_small = 0.0001

        p0 = _bond_price_from_ytm(
            face_value, coupon_rate, ytm, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        p_up = _bond_price_from_ytm(
            face_value, coupon_rate, ytm + dy_small, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )
        p_down = _bond_price_from_ytm(
            face_value, coupon_rate, ytm - dy_small, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )

        mod_dur = -(p_up - p_down) / (2 * dy_small * p0)
        convexity = (p_up + p_down - 2 * p0) / (dy_small ** 2 * p0)

        # Actual price at ytm + 200bp
        p_actual = _bond_price_from_ytm(
            face_value, coupon_rate, ytm + dy_large, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )

        # Duration-only estimate
        dp_dur = -mod_dur * p0 * dy_large
        # Duration + convexity estimate
        dp_dur_conv = dp_dur + 0.5 * convexity * p0 * dy_large ** 2

        actual_dp = p_actual - p0
        err_dur_only = abs(dp_dur - actual_dp)
        err_dur_conv = abs(dp_dur_conv - actual_dp)

        assert err_dur_conv < err_dur_only, (
            f"Convexity adjustment should reduce error: "
            f"dur_only={err_dur_only:.4f}, dur+conv={err_dur_conv:.4f}"
        )


class TestYTMRoundTrip:
    """Price -> YTM -> Price round-trip consistency."""

    def test_ytm_from_price(self):
        face_value = 100.0
        coupon_rate = 0.07
        ytm_original = 0.08
        n_periods = 14
        coupons_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2032-01-01")

        price = _bond_price_from_ytm(
            face_value, coupon_rate, ytm_original, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )

        cash_flows = _build_cashflows(
            face_value, coupon_rate, n_periods, coupons_per_year,
            valuation_date, maturity_date,
        )

        recovered_ytm = YTMCalculator.calculate_ytm(
            dirty_price=price,
            cash_flows=cash_flows,
            valuation_date=valuation_date,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            face_value=face_value,
            maturity_date=maturity_date,
        )

        np.testing.assert_allclose(
            recovered_ytm, ytm_original, rtol=1e-3,
            err_msg="YTM round-trip should recover original yield"
        )


class TestPriceMonotonicity:
    """Higher YTM => lower price (inverse relationship)."""

    def test_bond_price_decreases_with_yield(self):
        face_value = 100.0
        coupon_rate = 0.05
        n_periods = 10
        coupons_per_year = 2
        valuation_date = pd.Timestamp("2025-01-01")
        maturity_date = pd.Timestamp("2030-01-01")

        ytm_values = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
        prices = [
            _bond_price_from_ytm(
                face_value, coupon_rate, y, n_periods, coupons_per_year,
                valuation_date, maturity_date,
            )
            for y in ytm_values
        ]

        for i in range(len(prices) - 1):
            assert prices[i] > prices[i + 1], (
                f"Price should decrease as YTM increases: "
                f"P({ytm_values[i]})={prices[i]:.4f} vs P({ytm_values[i+1]})={prices[i+1]:.4f}"
            )


class TestDurationIncreasesWithMaturity:
    """Longer maturity => higher duration for coupon bonds near par."""

    def test_duration_increases_with_maturity(self):
        face_value = 100.0
        coupon_rate = 0.05
        ytm = 0.05
        coupons_per_year = 2
        dy = 0.0001

        durations = []
        tenors = [2, 5, 10, 20]
        for tenor in tenors:
            n_periods = tenor * coupons_per_year
            valuation_date = pd.Timestamp("2025-01-01")
            maturity_date = valuation_date + pd.DateOffset(years=tenor)

            p0 = _bond_price_from_ytm(
                face_value, coupon_rate, ytm, n_periods, coupons_per_year,
                valuation_date, maturity_date,
            )
            p_up = _bond_price_from_ytm(
                face_value, coupon_rate, ytm + dy, n_periods, coupons_per_year,
                valuation_date, maturity_date,
            )
            p_down = _bond_price_from_ytm(
                face_value, coupon_rate, ytm - dy, n_periods, coupons_per_year,
                valuation_date, maturity_date,
            )
            mod_dur = -(p_up - p_down) / (2 * dy * p0)
            durations.append(mod_dur)

        for i in range(len(durations) - 1):
            assert durations[i] < durations[i + 1], (
                f"Duration should increase with maturity: "
                f"D({tenors[i]}yr)={durations[i]:.4f} vs D({tenors[i+1]}yr)={durations[i+1]:.4f}"
            )
