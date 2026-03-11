"""
Reusable error handling for API endpoints.

Usage:
    from src.utils.error_handler import service_endpoint

    @router.post("/optimize")
    @service_endpoint("CCMV optimization")
    async def optimize(request: CCMVRequest):
        return optimize_ccmv(...)  # just the happy path
"""
import functools
import logging

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def service_endpoint(operation_name: str):
    """Decorator that wraps endpoint with standardized error handling.

    Catches ValueError/RuntimeError → 400, numpy LinAlgError → 400,
    everything else → 500. Logs with exc_info for debugging.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except ValueError as e:
                logger.error("%s validation error: %s", operation_name, e, exc_info=True)
                raise HTTPException(status_code=400, detail="Invalid input parameters") from e
            except RuntimeError as e:
                logger.error("%s runtime error: %s", operation_name, e, exc_info=True)
                raise HTTPException(status_code=400, detail="Calculation error") from e
            except Exception as e:
                # Check for numpy LinAlgError without importing numpy at module level
                if type(e).__name__ == "LinAlgError":
                    logger.error("%s linear algebra error: %s", operation_name, e, exc_info=True)
                    raise HTTPException(
                        status_code=400, detail="Linear algebra error in computation"
                    ) from e
                logger.error("%s failed: %s", operation_name, e, exc_info=True)
                raise HTTPException(status_code=500, detail="Internal server error") from e

        return wrapper

    return decorator
