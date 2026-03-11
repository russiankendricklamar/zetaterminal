---
name: zeta-pydantic
description: Create Pydantic v2 models with financial validation for zetaterminal backend. Use when defining request/response schemas, adding validation, or creating data models.
---

# Zeta Terminal — Pydantic Models

## Base Class

ALL financial request models inherit `FinancialBaseModel` from `src/utils/financial_validation.py`:

```python
from src.utils.financial_validation import (
    FinancialBaseModel,
    MAX_ASSETS, MAX_MONTE_CARLO_PATHS, MAX_SCENARIOS,
    MAX_NOTIONAL, MAX_TENOR_YEARS, MAX_RATE_PCT, MAX_DATA_POINTS,
)
```

`FinancialBaseModel` auto-rejects NaN and Inf values via `@model_validator`.

## Request Model Template

```python
class FeatureRequest(FinancialBaseModel):
    """Request for feature calculation."""

    # Required fields with bounds
    spot_price: float = Field(..., gt=0, le=MAX_NOTIONAL, description="Spot price")
    strike: float = Field(..., gt=0, le=MAX_NOTIONAL, description="Strike price")
    maturity: float = Field(..., gt=0, le=MAX_TENOR_YEARS, description="Time to maturity (years)")
    risk_free_rate: float = Field(..., ge=-0.1, le=MAX_RATE_PCT / 100, description="Risk-free rate (decimal)")
    volatility: float = Field(..., gt=0, le=5.0, description="Annualized volatility (decimal)")

    # Optional with defaults
    option_type: str = Field("call", pattern="^(call|put)$", description="Option type")
    num_simulations: int = Field(10000, ge=100, le=MAX_MONTE_CARLO_PATHS, description="Monte Carlo paths")

    # Lists with size limits
    weights: list[float] = Field(default=[], max_length=MAX_ASSETS, description="Portfolio weights")
    scenarios: list[dict[str, float]] = Field(default=[], max_length=MAX_SCENARIOS)
```

## Response Model Template

```python
class FeatureResponse(BaseModel):
    """Response — no FinancialBaseModel needed, just BaseModel."""

    result: float
    greeks: dict[str, float] = {}
    metadata: dict[str, Any] = {}

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "result": 8.0214,
                "greeks": {"delta": 0.54, "gamma": 0.019},
                "metadata": {"model": "bsm", "computation_time_ms": 12},
            }
        }
    )
```

## Validation Constants

| Constant | Value | Use For |
|----------|-------|---------|
| `MAX_ASSETS` | 200 | Portfolio size |
| `MAX_MONTE_CARLO_PATHS` | 10,000 | MC simulations |
| `MAX_SCENARIOS` | 20 | Stress scenarios |
| `MAX_NOTIONAL` | 1e15 | Monetary amounts |
| `MAX_TENOR_YEARS` | 100 | Time horizons |
| `MAX_RATE_PCT` | 1000.0 | Interest rates (%) |
| `MAX_DATA_POINTS` | 50,000 | Time series length |

## Common Patterns

**Enum-like validation:**
```python
day_count: str = Field(..., pattern="^(ACT365F|ACT360|30360)$")
```

**Nested models:**
```python
class Position(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    weight: float = Field(..., ge=0, le=1)

class PortfolioRequest(FinancialBaseModel):
    positions: list[Position] = Field(..., min_length=1, max_length=MAX_ASSETS)
```

**Custom validator:**
```python
@field_validator("weights")
@classmethod
def weights_must_sum_to_one(cls, v: list[float]) -> list[float]:
    if v and abs(sum(v) - 1.0) > 1e-6:
        raise ValueError(f"Weights must sum to 1.0, got {sum(v)}")
    return v
```

## Checklist

- [ ] Inherits `FinancialBaseModel` (requests) or `BaseModel` (responses)
- [ ] `Field()` with `gt/ge/lt/le` bounds on ALL numeric params
- [ ] `max_length` on all list fields
- [ ] `description` on every field
- [ ] `pattern` for string enums
- [ ] No `Any` type on required fields
- [ ] Example in `model_config` for responses
