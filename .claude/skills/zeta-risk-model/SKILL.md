---
name: zeta-risk-model
description: Implement a new financial/risk model with reference tests and proper validation. Use when adding quantitative models, pricing engines, risk metrics, or financial calculations.
---

# Zeta Terminal — New Financial Model

## Aladdin-Grade Standards

Every financial model in Zeta Terminal follows BlackRock Aladdin's principle: **risk analytics as foundation, not afterthought**. Models must have mathematical rigor and reference-value tests.

## Implementation Steps

### 1. Research & Reference Values

Before writing ANY code:
- Find the canonical paper/textbook for the model
- Identify 2-3 reference test cases with known outputs
- Document the mathematical formulation

Example for BSM:
```
S=100, K=105, T=1, r=0.05, σ=0.2
Expected call price: 8.0214 (Hull, 10th ed.)
```

### 2. Create Service

`backend/src/services/{model}_service.py`:

```python
"""
{Model Name} implementation.

References
----------
- Author (Year). Title. Publisher. Chapter X.
- doi:10.xxxx/xxxxx
"""
import logging
import numpy as np
from scipy import stats  # or optimize, linalg, etc.

logger = logging.getLogger(__name__)


def calculate_{model}(
    param1: float,
    param2: float,
    *,
    optional_param: float = 0.0,
) -> dict[str, Any]:
    """
    Calculate {model} result.

    Parameters
    ----------
    param1 : float
        Description with units (e.g., annualized, decimal, bps).
    param2 : float
        Description.
    optional_param : float, default 0.0
        Description.

    Returns
    -------
    dict
        Keys: result, greeks (if applicable), metadata.

    Raises
    ------
    ValueError
        If inputs violate mathematical constraints.
    """
    # Input validation beyond Pydantic
    if param1 <= 0:
        raise ValueError(f"param1 must be positive, got {param1}")

    # Core calculation
    result = ...

    return {
        "result": float(result),
        "metadata": {
            "model": "{model_name}",
            "parameters": {"param1": param1, "param2": param2},
        }
    }
```

### 3. Naming Conventions for Financial Math

Use standard mathematical notation in variable names:
```python
S = spot_price       # Spot price
K = strike           # Strike price
T = time_to_maturity # Time to expiry (years)
r = risk_free_rate   # Risk-free rate (decimal)
sigma = volatility   # Volatility (decimal, annualized)
N = notional         # Notional amount
DV01 = dv01          # Dollar value of 1bp
```

These are ALLOWED despite PEP 8 naming (N806/N803 suppressed in ruff.toml).

### 4. Numerical Stability

```python
# BAD: Overflow risk
result = np.exp(800)

# GOOD: Clamped
result = np.exp(np.clip(x, -500, 500))

# BAD: Division by zero
greeks = value / time_to_maturity

# GOOD: Safe division
greeks = value / max(time_to_maturity, 1e-10)

# Always use np.float64 for financial calculations
prices = np.array(data, dtype=np.float64)
```

### 5. Create API Endpoint

Follow `/zeta-api-endpoint` skill for Router → Service → Repository pattern.

### 6. Create Vue Page

Follow `/zeta-vue-page` skill for brutalist UI with results display.

### 7. Write Reference Test

```python
# backend/tests/test_{model}.py
import pytest
from src.services.{model}_service import calculate_{model}


def test_{model}_reference_value():
    """Test against known reference from [Author, Year]."""
    result = calculate_{model}(param1=100, param2=0.05)
    assert abs(result["result"] - 8.0214) < 1e-4, (
        f"Expected 8.0214, got {result['result']}"
    )


def test_{model}_edge_cases():
    """Test boundary conditions."""
    # Zero time
    with pytest.raises(ValueError):
        calculate_{model}(param1=0, param2=0.05)

    # Extreme values
    result = calculate_{model}(param1=1e6, param2=0.001)
    assert np.isfinite(result["result"])


def test_{model}_symmetry():
    """Test mathematical properties (put-call parity, etc.)."""
    call = calculate_{model}(param1=100, option_type="call")
    put = calculate_{model}(param1=100, option_type="put")
    # Put-call parity: C - P = S - K*exp(-rT)
    assert abs(call["result"] - put["result"] - expected_diff) < 1e-4
```

## Model Categories (Aladdin mapping)

| Category | Existing in Zeta | To Add |
|----------|-----------------|--------|
| **Options** | BSM, Heston, VG, CGMY, FFT | Local Vol, SABR MC |
| **Fixed Income** | Bond DCF, IRS, CDS, Forwards, ZCYC | OAS, key rate durations |
| **Volatility** | SABR, SVI | Variance swaps, vol-of-vol |
| **Risk** | GARCH, VaR/CVaR, CCMV, HJB | Monte Carlo VaR, factor risk, correlation stress |
| **Regimes** | HMM, Spectral (Prony) | Jump-diffusion regime |
| **Portfolio** | Markowitz | Black-Litterman, risk parity, min-CVaR |

## Checklist Before Done

- [ ] Reference paper/textbook cited in docstring
- [ ] At least 2 reference-value tests with known outputs
- [ ] Edge case tests (zero, negative, extreme values)
- [ ] `np.float64` for all financial calculations
- [ ] Numerical stability (no overflow/underflow/division-by-zero)
- [ ] Input validation with descriptive ValueError messages
- [ ] Return dict with `result` + `metadata` keys
- [ ] `ruff check` passes
- [ ] Service has no HTTP/FastAPI imports (pure Python)
