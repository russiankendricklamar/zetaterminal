---
name: zeta-replicate-model
description: Step-by-step guide to replicate a financial model from QuantLib, Bloomberg, RiskMetrics, Barra, or other industry frameworks into zetaterminal. Use when porting specific models.
---

# Zeta Terminal — Replicate Model

Port a model from an external framework into zetaterminal.

## Step 1: Identify Source

Fill in before coding:

```
Model: _______________
Source framework: QuantLib / Bloomberg / RiskMetrics / Barra / Academic paper
Paper: Author (Year). Title.
Reference implementation: URL (GitHub, QuantLib docs, etc.)
```

## Step 2: Gather Reference Values

Find at least 2 test cases with known outputs:

```
Test Case 1:
  Input: {param1}={val}, {param2}={val}, ...
  Expected Output: {result}={val}
  Source: Hull Ch.15 / QuantLib test suite / Bloomberg FLDS

Test Case 2:
  Input: {param1}={val}, {param2}={val}, ...
  Expected Output: {result}={val}
  Source: _______________
```

**Where to find reference values:**
- QuantLib: `github.com/lballabio/QuantLib/tree/master/test-suite`
- Hull: "Options, Futures, and Other Derivatives" (numbered examples)
- Fabozzi: "Fixed Income Mathematics" (chapter examples)
- Jorion: "Value at Risk" (numerical examples)
- Shreve: "Stochastic Calculus for Finance" (exercises)

## Step 3: Write Math Spec

Document the formula before coding. Plain text or LaTeX:

```
Given: S (spot), K (strike), T (maturity), r (rate), sigma (vol)

d1 = (ln(S/K) + (r + sigma^2/2) * T) / (sigma * sqrt(T))
d2 = d1 - sigma * sqrt(T)
C = S * N(d1) - K * exp(-rT) * N(d2)
```

## Step 4: Create Service

File: `backend/src/services/{model}_service.py`

Follow the `zeta-risk-model` skill template:
- Docstring with paper reference
- `np.float64` precision
- `np.clip()` before `np.exp()`
- Input validation with descriptive errors
- Return `dict` with `result` + `metadata`

## Step 5: Create Pydantic Models

File: add to existing or new file in `backend/src/api/`

```python
from src.utils.financial_validation import FinancialBaseModel, MAX_NOTIONAL

class ModelRequest(FinancialBaseModel):
    """Request for {Model} calculation. Source: {Framework}."""
    param1: float = Field(..., gt=0, le=MAX_NOTIONAL, description="...")
```

## Step 6: Create API Endpoint

Follow the `zeta-api-endpoint` skill:
- Router with `@limiter.limit` on heavy endpoints
- `asyncio.to_thread()` for CPU-bound calculations
- 3-tier error handling

## Step 7: Create Vue Page

Follow the `zeta-vue-page` skill:
- Page subtitle references the source: `"Based on QuantLib HullWhiteProcess"`
- Input panel matches the Pydantic model fields
- Results panel shows computed values in `.font-mono`
- Chart if applicable (follow `zeta-chart` skill)

## Step 8: Write Tests

```python
def test_{model}_reference_ql():
    """Compare against QuantLib reference value."""
    result = calculate_{model}(...)
    assert abs(result["result"] - ql_value) < 1e-4

def test_{model}_reference_textbook():
    """Compare against {Author} example."""
    result = calculate_{model}(...)
    assert abs(result["result"] - textbook_value) < 1e-4

def test_{model}_edge_cases():
    """Test degenerate inputs."""
    # T=0 should return intrinsic value
    # sigma=0 should return deterministic value
    # Extreme values should not crash
```

## Step 9: Verify

Run the `zeta-verify` skill to check linting, types, and security.

## Framework-Specific Notes

### From QuantLib (C++)

- QuantLib uses `Date` objects — convert to float `T` (years) in Python
- QuantLib `Handle<Quote>` pattern — simplify to plain parameters
- QuantLib `PricingEngine` — map to a single service function
- Day count: QuantLib `Actual365Fixed` = our `T = days / 365.0`

### From Bloomberg (PORT/FLDS)

- Bloomberg fields (FLDS) map to API response keys
- PORT risk decomposition: systematic + specific + interaction
- Bloomberg uses settlement dates — we use trade dates

### From RiskMetrics

- EWMA decay factor: lambda = 0.94 (daily), 0.97 (monthly)
- VaR horizons: 1-day, 10-day (sqrt-T scaling for parametric)
- Covariance matrix: ensure positive definiteness

### From Barra/MSCI

- Factor returns: style (value, momentum, size) + industry + country
- Specific risk: idiosyncratic variance per asset
- Factor covariance: estimated from cross-sectional regression

## Validation Tolerances

| Model Type | Tolerance | Reason |
|------------|-----------|--------|
| Closed-form (BSM) | 1e-6 | Exact analytical formula |
| Numerical (FD, tree) | 1e-4 | Grid discretization |
| Monte Carlo | 1e-2 | Stochastic variance |
| Optimization | 1e-4 | Solver convergence |
| Factor models | 1e-3 | Data-dependent |

## Checklist

- [ ] Source paper/framework documented
- [ ] 2+ reference values collected
- [ ] Math spec written
- [ ] Service function with docstring citation
- [ ] Pydantic model with FinancialBaseModel
- [ ] API endpoint with rate limiting
- [ ] Vue page with brutalist UI
- [ ] Reference tests passing
- [ ] Edge case tests
- [ ] `ruff check` + `eslint` clean
