"""内存缓存工具 — 减少高频接口的数据库查询"""
import time
import asyncio
from functools import wraps
from collections import OrderedDict
from typing import Any, Callable, Optional


class TTLCache:
    """带过期时间的 LRU 内存缓存"""

    def __init__(self, maxsize: int = 128, ttl: float = 30.0):
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，过期返回 None"""
        if key not in self._cache:
            return None
        expire_at, value = self._cache[key]
        if time.monotonic() > expire_at:
            del self._cache[key]
            return None
        # 移到末尾 (LRU)
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """设置缓存"""
        if ttl is None:
            ttl = self.ttl
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.maxsize:
            # 淘汰最久未使用的
            self._cache.popitem(last=False)
        self._cache[key] = (time.monotonic() + ttl, value)

    def clear(self):
        self._cache.clear()

    def __len__(self):
        return len(self._cache)


# 全局缓存实例
# auth/me: 用户信息很少变，缓存 60 秒
user_cache = TTLCache(maxsize=256, ttl=60)
# knowledge/stats: 统计数据，缓存 30 秒
stats_cache = TTLCache(maxsize=16, ttl=30)
# conversations list: 会话列表，缓存 15 秒
conv_cache = TTLCache(maxsize=256, ttl=15)


def cached(cache: TTLCache, key_func: Callable = None):
    """装饰器：对异步函数结果进行缓存

    Usage:
        @cached(user_cache, key_func=lambda user_id: f"user:{user_id}")
        async def get_user(user_id): ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            cached_val = cache.get(key)
            if cached_val is not None:
                return cached_val

            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result

        return wrapper

    return decorator
