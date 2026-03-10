"""
Shared validation utilities for financial API request models.

Provides FinancialBaseModel that rejects NaN/Infinity values in all float fields,
preventing silent corruption in NumPy/SciPy computations.
"""
import math
from typing import Any

from pydantic import BaseModel, model_validator


def _check_finite(obj: Any, path: str = "") -> None:
    """Recursively check that all float values are finite (not NaN or Infinity)."""
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise ValueError(
                f"NaN and Infinity values are not allowed{f' at {path}' if path else ''}"
            )
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _check_finite(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _check_finite(v, f"{path}[{i}]")


class FinancialBaseModel(BaseModel):
    """Base model for financial API requests that rejects NaN/Infinity values."""

    @model_validator(mode="before")
    @classmethod
    def reject_nan_inf(cls, data: Any) -> Any:
        if isinstance(data, dict):
            _check_finite(data)
        return data


# Shared bounds constants
MAX_ASSETS = 200
MAX_MONTE_CARLO_PATHS = 10_000
MAX_MONTE_CARLO_STEPS = 1_000
MAX_SCENARIOS = 20
MAX_NOTIONAL = 1e15
MAX_TENOR_YEARS = 100
MAX_CAPITAL = 1e15
MAX_RATE_PCT = 1000.0
MAX_DATA_POINTS = 50_000
