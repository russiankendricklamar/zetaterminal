"""
Reference-based tests for Vanilla Bond Report.

References:
- Hull, "Options, Futures, and Other Derivatives", Ch. 4
- Tuckman & Serrat, "Fixed Income Securities", Ch. 3-4
- ISDA Day Count Fraction definitions (2006)
- Fabozzi, "Fixed Income Mathematics", 4th ed.
"""
import numpy as np
import pandas as pd
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.bond_pricing import YTMCalculator, BondPricer
from src.services.bond_pricing_cashflows import DayCountCalculator, AccruedInterestCalculator
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
# Day Count Conventions (6 tests)
# ---------------------------------------------------------------------------

class TestDayCountConventions:
    """ISDA 2006 day count fraction definitions."""

    def test_actual_365f(self):
        """Jan 1 to Jul 1 = 182 days (2024 is leap year). ACT/365F = 182/365."""
        start = pd.Timestamp("2024-01-01")
        end = pd.Timestamp("2024-07-01")
        result = DayCountCalculator.actual_365f(start, end)
        np.testing.assert_allclose(result, 182 / 365, atol=1e-5)

    def test_actual_360(self):
        """Jan 1 to Jul 1 = 182 days (2024 is leap year). ACT/360 = 182/360."""
        start = pd.Timestamp("2024-01-01")
        end = pd.Timestamp("2024-07-01")
        result = DayCountCalculator.actual_360(start, end)
        np.testing.assert_allclose(result, 182 / 360, atol=1e-5)

    def test_30_360_us(self):
        """Jan 31 to Mar 31. d1=31->30, d2=31->30. days=60. 60/360=0.16667."""
        start = pd.Timestamp("2024-01-31")
        end = pd.Timestamp("2024-03-31")
        maturity = pd.Timestamp("2025-12-31")
        result = DayCountCalculator.thirty_360_us(start, end, maturity)
        np.testing.assert_allclose(result, 60 / 360, atol=1e-4)

    def test_30e_360_eurobond(self):
        """Jan 31 to Mar 31. d1=31->30, d2=31->30. days=60. 60/360=0.16667."""
        start = pd.Timestamp("2024-01-31")
        end = pd.Timestamp("2024-03-31")
        result = DayCountCalculator.thirty_e_360(start, end)
        np.testing.assert_allclose(result, 60 / 360, atol=1e-4)

    def test_actual_actual_isda_full_leap_year(self):
        """Jan 1 2024 to Jan 1 2025 (leap year). 366/366 = 1.0."""
        start = pd.Timestamp("2024-01-01")
        end = pd.Timestamp("2025-01-01")
        result = DayCountCalculator.actual_actual_isda(start, end)
        np.testing.assert_allclose(result, 1.0, atol=1e-5)

    def test_actual_actual_isda_cross_year(self):
        """Jul 1 2023 to Jul 1 2024. 184/365 + 182/366 ≈ 1.0016."""
        start = pd.Timestamp("2023-07-01")
        end = pd.Timestamp("2024-07-01")
        expected = 184 / 365 + 182 / 366
        result = DayCountCalculator.actual_actual_isda(start, end)
        np.testing.assert_allclose(result, expected, atol=1e-4)


# ---------------------------------------------------------------------------
# Accrued Interest (3 tests)
# ---------------------------------------------------------------------------

class TestAccruedInterest:
    """Accrued interest calculations per Fabozzi conventions."""

    def test_accrued_interest_from_rate(self):
        """10% coupon, face=1000, 91 days ACT/365F (Jan 1 → Apr 1 2024, leap year).
        A = 0.10 * 1000 * 91/365 = 24.9315."""
        result = AccruedInterestCalculator.from_coupon_rate(
            coupon_rate_pct=10.0,
            face_value=1000,
            last_coupon_date=pd.Timestamp("2024-01-01"),
            valuation_date=pd.Timestamp("2024-04-01"),
            day_count_convention=DayCountConvention.ACTUAL_365F,
        )
        expected = 0.10 * 1000 * (91.0 / 365.0)
        np.testing.assert_allclose(result, expected, atol=0.01)

    def test_accrued_interest_from_amount(self):
        """coupon=50, 91/182 days fraction (2024 leap year).
        A = 50 * (91/365)/(182/365) = 50*91/182 = 25.0."""
        result = AccruedInterestCalculator.from_coupon_amount(
            coupon_amount=50,
            last_coupon_date=pd.Timestamp("2024-01-01"),
            next_coupon_date=pd.Timestamp("2024-07-01"),
            valuation_date=pd.Timestamp("2024-04-01"),
            day_count_convention=DayCountConvention.ACTUAL_365F,
        )
        expected = 50.0 * (91.0 / 365.0) / (182.0 / 365.0)
        np.testing.assert_allclose(result, expected, atol=0.01)

    def test_accrued_interest_before_last_coupon(self):
        """Valuation on or before last coupon date => accrued = 0."""
        result = AccruedInterestCalculator.from_coupon_rate(
            coupon_rate_pct=10.0,
            face_value=1000,
            last_coupon_date=pd.Timestamp("2024-04-01"),
            valuation_date=pd.Timestamp("2024-01-01"),
            day_count_convention=DayCountConvention.ACTUAL_365F,
        )
        assert result == 0.0


# ---------------------------------------------------------------------------
# YTM Calculator (4 tests)
# ---------------------------------------------------------------------------

class TestYTMCalculator:
    """YTM calculations per Hull Ch. 4 and Tuckman Ch. 3."""

    def test_ytm_zcb_round_trip(self):
        """ZCB: face=100, price=74.73, T=5yr. YTM = (100/74.73)^(1/5) - 1 ≈ 6%."""
        maturity_date = pd.Timestamp("2029-01-01")
        valuation_date = pd.Timestamp("2024-01-01")
        cash_flows = [{"date": maturity_date, "cf": 100}]
        ytm = YTMCalculator.calculate_ytm(
            dirty_price=74.73,
            cash_flows=cash_flows,
            valuation_date=valuation_date,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            face_value=100,
            maturity_date=maturity_date,
            coupon_period_months=0,
        )
        np.testing.assert_allclose(ytm, 0.06, atol=0.005)

    def test_ytm_coupon_bond_newton(self):
        """5% semiannual, 3yr, face=1000, price=1000 (par). YTM ≈ 5%."""
        valuation_date = pd.Timestamp("2024-01-01")
        coupon_dates = [
            pd.Timestamp("2024-07-01"),
            pd.Timestamp("2025-01-01"),
            pd.Timestamp("2025-07-01"),
            pd.Timestamp("2026-01-01"),
            pd.Timestamp("2026-07-01"),
            pd.Timestamp("2027-01-01"),
        ]
        cash_flows = [
            {"date": d, "cf": 25 if i < 5 else 1025}
            for i, d in enumerate(coupon_dates)
        ]
        ytm = YTMCalculator.calculate_ytm(
            dirty_price=1000,
            cash_flows=cash_flows,
            valuation_date=valuation_date,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            face_value=1000,
            maturity_date=coupon_dates[-1],
            coupon_period_months=6,
        )
        np.testing.assert_allclose(ytm, 0.05, atol=0.005)

    def test_ytm_to_nominal_round_trip(self):
        """ytm=0.10, n=2. NY = 2*[(1.10)^0.5 - 1]*100 = 9.762%. Round-trip check."""
        ny = YTMCalculator.ytm_to_nominal_yield(0.10, 2)
        expected_ny = 2 * ((1.10 ** 0.5) - 1) * 100
        np.testing.assert_allclose(ny, expected_ny, atol=0.01)
        ytm_back = YTMCalculator.nominal_yield_to_ytm(ny, 2)
        np.testing.assert_allclose(ytm_back, 0.10, atol=1e-6)

    def test_nominal_yield_to_ytm(self):
        """NY=10%, n=4. YTM = (1 + 0.10/4)^4 - 1 = (1.025)^4 - 1 = 0.10381."""
        ytm = YTMCalculator.nominal_yield_to_ytm(10.0, 4)
        expected = (1.025) ** 4 - 1
        np.testing.assert_allclose(ytm, expected, atol=1e-4)


# ---------------------------------------------------------------------------
# BondPricer.calculate_metrics (5 tests)
# ---------------------------------------------------------------------------

class TestBondPricerMetrics:
    """Full bond metrics per Tuckman Ch. 4 and Fabozzi."""

    @pytest.fixture()
    def annual_8pct_bond(self):
        """8% annual coupon, face=1000, 5yr bond. Valued at issue date."""
        issue_date = pd.Timestamp("2024-01-01")
        mat_date = pd.Timestamp("2029-01-01")
        coupon_dates = [
            pd.Timestamp("2025-01-01"),
            pd.Timestamp("2026-01-01"),
            pd.Timestamp("2027-01-01"),
            pd.Timestamp("2028-01-01"),
            pd.Timestamp("2029-01-01"),
        ]
        coupon_values = [80.0, 80.0, 80.0, 80.0, 80.0]
        bond_data = _make_bond_data(
            face_value=1000,
            coupon_percent=8.0,
            payments_per_year=1,
            issue_date=issue_date,
            mat_date=mat_date,
            coupon_dates=coupon_dates,
            coupon_values=coupon_values,
        )
        return bond_data, issue_date

    def test_metrics_dirty_price(self, annual_8pct_bond):
        """Dirty price at 6% YTM: P = Σ CF/(1.06)^i = 1084.247.

        Note: calculate_metrics expects discount_yield as decimal (0.06), not percent (6.0).
        """
        bond_data, valuation_date = annual_8pct_bond
        expected = (
            80 / 1.06
            + 80 / 1.06**2
            + 80 / 1.06**3
            + 80 / 1.06**4
            + 1080 / 1.06**5
        )
        metrics = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=valuation_date,
            discount_yield=0.06,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=12,
        )
        np.testing.assert_allclose(
            metrics["dirtyPrice"], expected, rtol=0.01,
            err_msg=f"Expected dirty price ~{expected:.2f}",
        )

    def test_metrics_clean_price(self, annual_8pct_bond):
        """Clean = dirty - accrued. At issue date accrued=0, so clean=dirty."""
        bond_data, valuation_date = annual_8pct_bond
        metrics = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=valuation_date,
            discount_yield=0.06,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=12,
        )
        np.testing.assert_allclose(
            metrics["cleanPrice"],
            metrics["dirtyPrice"] - metrics["accruedInterest"],
            atol=0.01,
        )

    def test_metrics_modified_duration(self, annual_8pct_bond):
        """ModDur = MacDur / (1 + YTM). Always ModDur < MacDur."""
        bond_data, valuation_date = annual_8pct_bond
        metrics = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=valuation_date,
            discount_yield=0.06,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=12,
        )
        assert metrics["modifiedDuration"] < metrics["duration"], (
            "Modified duration must be less than Macaulay duration"
        )
        assert metrics["modifiedDuration"] > 0

    def test_metrics_convexity_positive(self, annual_8pct_bond):
        """Convexity is always positive for vanilla (non-callable) bonds."""
        bond_data, valuation_date = annual_8pct_bond
        metrics = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=valuation_date,
            discount_yield=0.06,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=12,
        )
        assert metrics["convexity"] > 0, "Convexity must be positive for vanilla bonds"

    def test_metrics_sensitivity_scenarios(self, annual_8pct_bond):
        """Sensitivity table: 9 entries, price rises when yield falls."""
        bond_data, valuation_date = annual_8pct_bond
        metrics = BondPricer.calculate_metrics(
            bond_data=bond_data,
            valuation_date=valuation_date,
            discount_yield=0.06,
            day_count_convention=DayCountConvention.ACTUAL_365F,
            coupon_period_months=12,
        )
        scenarios = metrics["sensitivityScenarios"]
        assert len(scenarios) == 9, f"Expected 9 scenarios, got {len(scenarios)}"

        # Find the scenario with the most negative shift and the most positive
        sorted_scenarios = sorted(scenarios, key=lambda s: s.get("yieldChangeBps", s.get("shift", 0)))
        lowest_yield_price = sorted_scenarios[0].get("newDirtyPrice", sorted_scenarios[0].get("price", 0))
        highest_yield_price = sorted_scenarios[-1].get("newDirtyPrice", sorted_scenarios[-1].get("price", 0))
        assert lowest_yield_price > highest_yield_price, (
            "Price must increase when yield decreases (inverse relationship)"
        )
