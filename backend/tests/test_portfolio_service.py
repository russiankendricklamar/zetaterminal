"""
Reference-based tests for Portfolio Service.

References:
- Sharpe (1966), "Mutual Fund Performance"
- Sortino & van der Meer (1991)
- Hull, "Options, Futures, and Other Derivatives", Ch. 22
"""
import numpy as np
import pytest
from scipy.stats import norm

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.portfolio_service import PortfolioService


# ---------------------------------------------------------------------------
# Sharpe Ratio
# ---------------------------------------------------------------------------

def test_sharpe_ratio_reference():
    """Sharpe = (R - Rf) / sigma = (0.12 - 0.04) / 0.15 = 0.5333..."""
    result = PortfolioService._calculate_sharpe_ratio(
        return_=0.12, volatility=0.15, risk_free_rate=0.04
    )
    expected = (0.12 - 0.04) / 0.15
    np.testing.assert_allclose(result, expected, rtol=1e-10)


def test_sharpe_ratio_zero_vol():
    """Zero volatility must return Sharpe = 0."""
    result = PortfolioService._calculate_sharpe_ratio(
        return_=0.12, volatility=0.0, risk_free_rate=0.04
    )
    assert result == 0.0


# ---------------------------------------------------------------------------
# Sortino Ratio
# ---------------------------------------------------------------------------

def test_sortino_ratio_reference():
    """Sortino with mixed daily returns, manually computed downside deviation."""
    annual_return = 0.10
    daily_returns = [0.01, -0.02, 0.005, -0.015, 0.008, -0.01, 0.003, -0.005]
    rf = 0.04

    rf_daily = rf / 252
    downside_sq = [(min(r - rf_daily, 0)) ** 2 for r in daily_returns]
    downside_var = sum(downside_sq) / len(daily_returns)
    downside_std = np.sqrt(downside_var) * np.sqrt(252)
    expected = (annual_return - rf) / downside_std

    result = PortfolioService._calculate_sortino_ratio(annual_return, daily_returns, rf)
    np.testing.assert_allclose(result, expected, rtol=1e-10)


def test_sortino_all_positive():
    """All returns above risk-free daily rate => zero downside deviation => Sortino = 0."""
    daily_returns = [0.05, 0.03, 0.04, 0.02, 0.06]
    result = PortfolioService._calculate_sortino_ratio(
        annual_return=0.10, daily_returns=daily_returns, risk_free_rate=0.04
    )
    assert result == 0.0


# ---------------------------------------------------------------------------
# Value at Risk
# ---------------------------------------------------------------------------

def test_var_95_reference():
    """VaR(95%) = |Z_0.05| * sigma * PV = 1.6449 * 0.20 * 1_000_000."""
    vol = 0.20
    pv = 1_000_000.0
    z = norm.ppf(0.95)  # 1.6449...
    expected = z * vol * pv

    result = PortfolioService._calculate_var(vol, pv, confidence_level=0.95)
    np.testing.assert_allclose(result, expected, rtol=1e-10)


def test_var_99():
    """VaR(99%) = |Z_0.01| * sigma * PV = 2.3263 * 0.20 * 1_000_000."""
    vol = 0.20
    pv = 1_000_000.0
    z = norm.ppf(0.99)  # 2.3263...
    expected = z * vol * pv

    result = PortfolioService._calculate_var(vol, pv, confidence_level=0.99)
    np.testing.assert_allclose(result, expected, rtol=1e-10)


# ---------------------------------------------------------------------------
# Beta
# ---------------------------------------------------------------------------

def test_beta_exact_cov():
    """Beta from known market and portfolio return series (>= 20 obs)."""
    rng = np.random.default_rng(42)
    market_returns = rng.normal(0.0005, 0.01, 50).tolist()
    # portfolio = 1.3 * market + noise
    portfolio_returns = [1.3 * m + rng.normal(0, 0.002) for m in market_returns]

    m = np.array(market_returns)
    p = np.array(portfolio_returns)
    cov_pm = float(np.cov(p, m, ddof=1)[0, 1])
    var_m = float(np.var(m, ddof=1))
    expected_beta = cov_pm / var_m

    # positions and volatilities are unused when returns are provided
    result = PortfolioService._calculate_beta(
        positions=[],
        volatilities=[],
        market_volatility=0.15,
        market_returns=market_returns,
        portfolio_returns=portfolio_returns,
    )
    np.testing.assert_allclose(result, expected_beta, rtol=1e-10)


def test_beta_proxy_fallback():
    """Without historical returns, beta = (weighted_vol / market_vol) * 0.7."""
    positions = [
        {"allocation": 60},
        {"allocation": 40},
    ]
    volatilities = [0.20, 0.30]
    market_vol = 0.15

    weighted_vol = (0.60 * 0.20) + (0.40 * 0.30)  # 0.24
    expected = (weighted_vol / market_vol) * 0.7

    result = PortfolioService._calculate_beta(
        positions=positions,
        volatilities=volatilities,
        market_volatility=market_vol,
    )
    np.testing.assert_allclose(result, expected, rtol=1e-10)


# ---------------------------------------------------------------------------
# Diversification (1 - HHI)
# ---------------------------------------------------------------------------

def test_diversification_equal_weight():
    """5 positions at 20% each: HHI = 5 * 0.04 = 0.20, diversification = 0.80."""
    positions = [{"allocation": 20} for _ in range(5)]
    result = PortfolioService._calculate_diversification(positions)
    np.testing.assert_allclose(result, 0.80, rtol=1e-10)


def test_diversification_concentrated():
    """Single position at 100%: HHI = 1.0, diversification = 0.0."""
    positions = [{"allocation": 100}]
    result = PortfolioService._calculate_diversification(positions)
    assert result == 0.0


# ---------------------------------------------------------------------------
# Max Drawdown
# ---------------------------------------------------------------------------

def test_max_drawdown_known():
    """Manually computed max drawdown from a known return series."""
    returns = [0.10, -0.05, -0.10, 0.03, -0.02]

    # Cumulative product: [1.10, 1.045, 0.9405, 0.968715, 0.94934070]
    cumulative = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    expected = abs(np.min(drawdown))

    result = PortfolioService._calculate_max_drawdown(returns)
    np.testing.assert_allclose(result, expected, rtol=1e-10)


# ---------------------------------------------------------------------------
# Default Metrics
# ---------------------------------------------------------------------------

def test_default_metrics():
    """_get_default_metrics returns zeros except beta=1.0 and risk_free_rate=0.042."""
    metrics = PortfolioService._get_default_metrics()

    assert metrics["beta"] == 1.0
    assert metrics["risk_free_rate"] == 0.042
    assert metrics["num_positions"] == 0

    zero_keys = [
        "total_pnl", "nav", "annual_return", "daily_return", "volatility",
        "var_95", "var_95_daily", "var_95_percent", "sharpe_ratio",
        "sortino_ratio", "alpha", "skew", "max_drawdown",
        "diversification", "avg_correlation",
    ]
    for key in zero_keys:
        assert metrics[key] == 0.0, f"{key} should be 0.0, got {metrics[key]}"
