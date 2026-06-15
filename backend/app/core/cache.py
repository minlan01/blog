import time
from functools import wraps
from threading import Lock

_cache: dict[str, tuple[float, any]] = {}
_lock = Lock()
_MAX_CACHE_SIZE = 1000


def cache_get(key: str):
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
    with _lock:
        if len(_cache) >= _MAX_CACHE_SIZE:
            _evict_expired()
        if len(_cache) >= _MAX_CACHE_SIZE:
            sorted_keys = sorted(_cache.keys(), key=lambda k: _cache[k][0])
            for k in sorted_keys[: len(_cache) // 4]:
                del _cache[k]
        _cache[key] = (time.time() + ttl, value)


def cache_delete(prefix: str) -> None:
    with _lock:
        keys_to_delete = [k for k in _cache if k.startswith(prefix)]
        for k in keys_to_delete:
            del _cache[k]


def _evict_expired() -> None:
    now = time.time()
    expired = [k for k, (expire_at, _) in _cache.items() if now > expire_at]
    for k in expired:
        del _cache[k]


def cached(key_prefix: str, ttl: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{str(args[1:])}"
            result = cache_get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
