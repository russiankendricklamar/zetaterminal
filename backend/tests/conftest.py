import numpy as np
import pytest


@pytest.fixture
def sample_returns():
    """252 daily returns ~ N(0.0004, 0.01) — ~10% annual return, 16% vol."""
    rng = np.random.default_rng(42)
    return rng.normal(0.0004, 0.01, 252)


@pytest.fixture
def sample_positions():
    """5 positions for portfolio tests."""
    return [
        {"symbol": "AAPL", "price": 150.0, "dayChange": 1.5, "notional": 300000, "allocation": 30, "targetAllocation": 25},
        {"symbol": "MSFT", "price": 280.0, "dayChange": -0.8, "notional": 250000, "allocation": 25, "targetAllocation": 25},
        {"symbol": "GOOGL", "price": 120.0, "dayChange": 2.1, "notional": 200000, "allocation": 20, "targetAllocation": 20},
        {"symbol": "AMZN", "price": 130.0, "dayChange": -1.2, "notional": 150000, "allocation": 15, "targetAllocation": 15},
        {"symbol": "TSLA", "price": 200.0, "dayChange": 3.5, "notional": 100000, "allocation": 10, "targetAllocation": 15},
    ]


@pytest.fixture
def two_asset_returns():
    """Correlated 2-asset returns for component VaR tests."""
    rng = np.random.default_rng(123)
    n = 500
    # Asset 1: mu=0.0005, sigma=0.015
    # Asset 2: mu=0.0003, sigma=0.020
    # Correlation: ~0.5
    z1 = rng.standard_normal(n)
    z2 = 0.5 * z1 + np.sqrt(1 - 0.25) * rng.standard_normal(n)
    r1 = 0.0005 + 0.015 * z1
    r2 = 0.0003 + 0.020 * z2
    return np.column_stack([r1, r2])
