"""
Simple in-memory TTL cache for external API responses.

Usage:
    from src.services.cache_service import cache_get, cache_set, make_cache_key

    key = make_cache_key("alpha_vantage", "quote", symbol)
    cached = cache_get(key)
    if cached is not None:
        return cached
    result = await fetch_data(...)
    cache_set(key, result, ttl_seconds=60)
    return result
"""

import time
from typing import Any, Optional, Dict, Tuple


_cache: Dict[str, Tuple[Any, float]] = {}


def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache if it exists and hasn't expired."""
    if key in _cache:
        value, expires_at = _cache[key]
        if time.time() < expires_at:
            return value
        del _cache[key]
    return None


def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """Store a value in cache with a TTL in seconds."""
    _cache[key] = (value, time.time() + ttl_seconds)


def cache_clear() -> None:
    """Clear the entire cache."""
    _cache.clear()


def cache_delete(key: str) -> None:
    """Delete a specific key from cache."""
    _cache.pop(key, None)


def make_cache_key(*args) -> str:
    """Build a cache key from multiple arguments."""
    return ":".join(str(a) for a in args)
