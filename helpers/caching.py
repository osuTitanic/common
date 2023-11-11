
from datetime import timedelta, datetime
from functools import lru_cache, wraps
from typing import Callable

def ttl_cache(maxsize: int = 128, typed: bool = False, ttl: int = -1):
    ttl = 0x10000 if ttl <= 0 else ttl

    def wrapper(func: Callable) -> Callable:
        func = lru_cache(maxsize=maxsize, typed=typed)(func)
        func.lifetime = timedelta(seconds=ttl)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            # Check func expiration
            if datetime.utcnow() > func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)
        return wrapped_func
    return wrapper
