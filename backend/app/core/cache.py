"""Simple in-memory LRU cache for hot queries."""

import time
from functools import wraps
from threading import Lock

_cache: dict[str, tuple[float, any]] = {}
_lock = Lock()


def cache_get(key: str):
    """Get value from cache. Returns None if not found or expired."""
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        expire_at, value = entry
        if time.time() > expire_at:
            del _cache[key]
            return None
        return value


def cache_set(key: str, value: any, ttl: int = 300) -> None:
    """Set value in cache with TTL in seconds (default 5 min)."""
    with _lock:
        _cache[key] = (time.time() + ttl, value)


def cache_delete(prefix: str) -> None:
    """Delete all cache entries matching a prefix."""
    with _lock:
        keys_to_delete = [k for k in _cache if k.startswith(prefix)]
        for k in keys_to_delete:
            del _cache[k]


def cached(key_prefix: str, ttl: int = 300):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from prefix + stringified args
            cache_key = f"{key_prefix}:{str(args[1:])}"  # skip self
            result = cache_get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
