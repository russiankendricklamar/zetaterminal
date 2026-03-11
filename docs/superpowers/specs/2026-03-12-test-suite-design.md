# Test Suite Design — Reference-Based Full Coverage

## Scope
Full pytest coverage for all backend financial services with reference values from Hull, QuantLib, Wilmott, RiskMetrics.

## Structure
```
backend/tests/
├── conftest.py                # Shared fixtures
├── test_risk_service.py       # 15 tests — VaR/CVaR parametric/historical/MC
├── test_portfolio_service.py  # 12 tests — Sharpe/Sortino/Beta/variance/HHI
├── test_bond_pricing.py       # 10 tests — DCF/duration/convexity/zero-coupon
├── test_garch.py              # 12 tests — GARCH(1,1)/GJR/EGARCH/EWMA/MLE
├── test_forward_service.py    # 6 tests  — forward price/value/delta
├── test_swap_service.py       # 6 tests  — par rate/DV01/spread
```
Total: ~61 reference-based tests.

## Reference Sources
- Hull "Options, Futures, and Other Derivatives" 10th ed.
- QuantLib Python for cross-validation
- Wilmott "Paul Wilmott on Quantitative Finance"
- RiskMetrics Technical Document (J.P. Morgan 1996)
- Acerbi & Tasche (2002) for CVaR

## Tolerance Policy
- Analytical formulas: ±0.01% (1e-4 relative)
- Monte Carlo: ±5% (statistical tolerance)
- MLE fitting: ±20% on recovered params
- Numerical integration: ±0.5%
