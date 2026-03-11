---
name: zeta-api-endpoint
description: Create a new FastAPI endpoint following zetaterminal Router → Service → Repository pattern. Use when adding API endpoints, routes, or backend functionality.
---

# Zeta Terminal — New API Endpoint

## Architecture (MANDATORY)

Every endpoint follows a 3-layer pattern:

```
backend/src/api/{domain}.py        ← Router (validation, I/O, error handling)
backend/src/services/{domain}_service.py  ← Service (business logic, calculations)
backend/src/database/repositories.py      ← Repository (DB access, if needed)
backend/src/database/models.py            ← Pydantic schemas (request/response)
```

## Step-by-Step

### 1. Define Pydantic Models

Add request/response schemas in `backend/src/database/models.py` or a dedicated file:

```python
from src.utils.financial_validation import FinancialBaseModel

class NewFeatureRequest(FinancialBaseModel):
    """Inherit FinancialBaseModel to auto-reject NaN/Inf values."""
    param: float = Field(..., ge=0, le=MAX_RATE_PCT, description="Description")

class NewFeatureResponse(BaseModel):
    result: float
    metadata: dict[str, Any] = {}
```

**Rules:**
- Always inherit `FinancialBaseModel` for financial inputs (rejects NaN/Inf automatically)
- Use `Field()` with bounds (`ge`, `le`, `gt`, `lt`) for all numeric parameters
- Reference constants from `financial_validation.py`: `MAX_ASSETS`, `MAX_NOTIONAL`, `MAX_TENOR_YEARS`, `MAX_RATE_PCT`, `MAX_DATA_POINTS`

### 2. Create Service

Create `backend/src/services/{domain}_service.py`:

```python
import logging
import numpy as np

logger = logging.getLogger(__name__)

def calculate_something(param: float) -> dict[str, Any]:
    """
    Pure business logic. No FastAPI imports, no HTTP concepts.

    Parameters
    ----------
    param : float
        Description with units.

    Returns
    -------
    dict with keys: result, metadata
    """
    # Implementation
    return {"result": value, "metadata": {}}
```

**Rules:**
- No FastAPI/HTTP imports in services — pure Python
- Type hints on ALL parameters and return values
- Docstring with Parameters/Returns sections
- Use `logger.error()` not `print()`
- CPU-heavy calculations will be wrapped in `asyncio.to_thread()` by the router

### 3. Create Router

Create `backend/src/api/{domain}.py`:

```python
"""
API endpoints для {domain description}.
"""
import asyncio
import logging
from fastapi import APIRouter, HTTPException, Request
from src.services.{domain}_service import calculate_something

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/api/{domain}/calculate")
async def calculate_endpoint(request: NewFeatureRequest):
    try:
        result = await asyncio.to_thread(
            calculate_something,
            request.param,
        )
        return result
    except ValueError as e:
        logger.error("{Domain} validation error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid input parameters") from e
    except Exception as e:
        logger.error("{Domain} calculation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
```

**Rules:**
- `asyncio.to_thread()` for ALL CPU-heavy sync operations
- Three-tier error handling: ValueError (400) → RuntimeError (400) → Exception (500)
- Always `from e` on raise (B904)
- Never expose internal errors in HTTPException detail
- Add `@limiter.limit("X/minute")` for heavy endpoints

### 4. Register Router

Add to `backend/src/main.py`:

```python
from src.api.{domain} import router as {domain}_router
app.include_router({domain}_router)
```

### 5. Add Rate Limiting (if heavy computation)

```python
from src.middleware.rate_limit import limiter

@router.post("/api/{domain}/calculate")
@limiter.limit("10/minute")
async def calculate_endpoint(http_request: Request, request: NewFeatureRequest):
    # Note: http_request param required by slowapi
```

## Checklist Before Done

- [ ] Pydantic model with FinancialBaseModel + Field bounds
- [ ] Service with pure logic, no HTTP concepts
- [ ] Router with 3-tier error handling + `from e`
- [ ] `asyncio.to_thread()` for CPU-heavy operations
- [ ] Router registered in main.py
- [ ] Rate limiting on heavy endpoints
- [ ] `ruff check` passes on new files
- [ ] Endpoint tested via curl or httpie

## Reference Files

- Router example: `backend/src/api/bond.py`
- Service example: `backend/src/services/bond_service.py`
- Validation base: `backend/src/utils/financial_validation.py`
- Rate limiting: `backend/src/middleware/rate_limit.py`
- Main app: `backend/src/main.py`
