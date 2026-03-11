"""
Tests for forward pricing service.

References:
- Covered Interest Parity (CIP) for FX forwards
- Cost-of-Carry model for commodity/equity forwards
"""
import numpy as np
import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.forward_service import (
    forward_rate_change,
    currency_pair,
    tenor_for_days,
    fair_value_fx,
)


# ---------------------------------------------------------------------------
# forward_rate_change tests
# ---------------------------------------------------------------------------


class TestForwardRateChange:
    """Test forward rate change: ((1 + r_int/100)^(d/365)) / ((1 + r_ext/100)^(d/365))."""

    def test_forward_rate_change(self):
        """rate_internal=10%, rate_external=5%, days=365 → (1.10/1.05) ≈ 1.04762."""
        result = forward_rate_change(days=365, rate_internal=10.0, rate_external=5.0)
        expected = (1.10 / 1.05)  # 1.047619...

        np.testing.assert_allclose(
            result, expected, rtol=1e-6,
            err_msg="Forward rate change for 1Y with 10% vs 5% rates"
        )

    def test_forward_rate_change_zero_days(self):
        """days=0 → any rates → result = 1.0 (no time elapsed)."""
        result = forward_rate_change(days=0, rate_internal=10.0, rate_external=5.0)

        np.testing.assert_allclose(
            result, 1.0, rtol=1e-12,
            err_msg="Zero-day forward rate change must be 1.0"
        )


# ---------------------------------------------------------------------------
# currency_pair tests
# ---------------------------------------------------------------------------


class TestCurrencyPair:
    """Currency pair ordering by CURRENCY_PRIORITY dict."""

    def test_currency_pair_priority(self):
        """EUR has priority=1, USD has priority=5 → 'EURUSD'."""
        result = currency_pair("USD", "EUR")
        assert result == "EURUSD", f"Expected EURUSD, got {result}"

    def test_currency_pair_same(self):
        """Same currency → 'USDUSD' (lower priority not strictly less)."""
        result = currency_pair("USD", "USD")
        assert result == "USDUSD", f"Expected USDUSD, got {result}"


# ---------------------------------------------------------------------------
# tenor_for_days tests
# ---------------------------------------------------------------------------


class TestTenorForDays:
    """Tenor bucket mapping for various day counts."""

    @pytest.mark.parametrize(
        "days, expected",
        [
            (3, (1, 1)),
            (10, (7, 14)),
            (25, (14, 31)),
            (45, (31, 59)),
            (100, (90, 180)),
            (200, (180, 270)),
            (300, (270, 360)),
            (400, (360, 360)),
        ],
    )
    def test_tenor_for_days(self, days, expected):
        result = tenor_for_days(days)
        assert result == expected, f"tenor_for_days({days}) = {result}, expected {expected}"


# ---------------------------------------------------------------------------
# fair_value_fx tests
# ---------------------------------------------------------------------------


class TestFairValueFX:
    """Test fair_value_fx: FV of FX forward given discount factors and spot."""

    def test_fair_value_fx_buy_rub(self):
        """
        When buy_currency='RUB':
            fv = (buy_amount * disc_internal - sell_amount * spot * disc_external) / 1000

        buy_amount=1_000_000 RUB, sell_amount=10_000 EUR,
        disc_internal=0.95, disc_external=0.99, spot=100.0 (₽/EUR)
        Expected: (1_000_000 * 0.95 - 10_000 * 100.0 * 0.99) / 1000
                = (950_000 - 990_000) / 1000 = -40.0
        """
        result = fair_value_fx(
            buy_currency="RUB",
            buy_amount=1_000_000.0,
            sell_amount=10_000.0,
            disc_internal=0.95,
            disc_external=0.99,
            spot=100.0,
        )
        expected = (1_000_000.0 * 0.95 - 10_000.0 * 100.0 * 0.99) / 1000.0

        np.testing.assert_allclose(
            result, expected, rtol=1e-10,
            err_msg="fair_value_fx (buy RUB) must match manual formula"
        )

    def test_fair_value_fx_buy_eur(self):
        """
        When buy_currency='EUR' (not RUB):
            fv = (buy_amount * spot * disc_external - sell_amount * disc_internal) / 1000

        buy_amount=10_000 EUR, sell_amount=1_000_000 RUB,
        disc_internal=0.95, disc_external=0.99, spot=100.0
        Expected: (10_000 * 100.0 * 0.99 - 1_000_000 * 0.95) / 1000
                = (990_000 - 950_000) / 1000 = 40.0
        """
        result = fair_value_fx(
            buy_currency="EUR",
            buy_amount=10_000.0,
            sell_amount=1_000_000.0,
            disc_internal=0.95,
            disc_external=0.99,
            spot=100.0,
        )
        expected = (10_000.0 * 100.0 * 0.99 - 1_000_000.0 * 0.95) / 1000.0

        np.testing.assert_allclose(
            result, expected, rtol=1e-10,
            err_msg="fair_value_fx (buy EUR) must match manual formula"
        )
