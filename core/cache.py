"""Redis caching layer for DokPotok IRIS.

Provides in-memory fallback when Redis is not available.
Use for:
- Dashboard metrics (TTL 5 min)
- User gamification score (TTL 10 min)
- Portfolio overview (TTL 5 min)
- Unread notification count (TTL 1 min)
- Leaderboard (TTL 5 min)
"""

import json
import logging
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
import hashlib
from datetime import timedelta

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - using in-memory cache fallback")


T = TypeVar('T')


class CacheBackend:
    """Abstract cache backend interface."""
    
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        raise NotImplementedError
    
    def delete(self, key: str) -> None:
        raise NotImplementedError
    
    def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        raise NotImplementedError


class RedisCache(CacheBackend):
    """Redis cache backend with JSON serialization."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", default_ttl: int = 300):
        self._client: Optional[redis.Redis] = None
        self._default_ttl = default_ttl
        self._url = redis_url
        self._connected = False
        self._connect()
    
    def _connect(self) -> None:
        """Lazy connection to Redis."""
        if not REDIS_AVAILABLE:
            self._connected = False
            return
        
        try:
            self._client = redis.from_url(
                self._url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self._client.ping()
            self._connected = True
            logger.info("Redis cache connected: %s", self._url)
        except Exception as e:
            logger.warning("Redis connection failed: %s - using in-memory fallback", e)
            self._connected = False
            self._client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._connected or self._client is None:
            return None
        
        try:
            value = self._client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.warning("Redis GET error for key %s: %s", key, e)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        if not self._connected or self._client is None:
            return
        
        if ttl is None:
            ttl = self._default_ttl
        
        try:
            serialized = json.dumps(value, default=str)
            self._client.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning("Redis SET error for key %s: %s", key, e)
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if not self._connected or self._client is None:
            return
        
        try:
            self._client.delete(key)
        except Exception as e:
            logger.warning("Redis DELETE error for key %s: %s", key, e)
    
    def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        if not self._connected or self._client is None:
            return
        
        try:
            cursor = 0
            while True:
                cursor, keys = self._client.scan(cursor, match=pattern, count=100)
                if keys:
                    self._client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            logger.warning("Redis DELETE_PATTERN error for pattern %s: %s", pattern, e)
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected


class InMemoryCache(CacheBackend):
    """Simple in-memory cache with TTL support.
    
    Use as fallback when Redis is not available.
    NOT suitable for multi-instance deployments.
    """
    
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._default_ttl = default_ttl
        self._cleanup_interval = 60  # seconds
        self._last_cleanup = 0
    
    def _cleanup(self) -> None:
        """Remove expired entries."""
        import time
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        expired = [k for k, (_, expires) in self._cache.items() if expires < now]
        for key in expired:
            del self._cache[key]
        self._last_cleanup = now
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        self._cleanup()
        value = self._cache.get(key)
        if value is None:
            return None
        
        data, expires = value
        if expires < 0:  # Permanent
            return data
        if expires < __import__('time').time():  # Expired
            del self._cache[key]
            return None
        return data
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        import time
        if ttl is None:
            ttl = self._default_ttl
        
        expires = -1 if ttl == 0 else time.time() + ttl
        self._cache[key] = (value, expires)
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        self._cache.pop(key, None)
    
    def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern (simple glob)."""
        import fnmatch
        keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del self._cache[key]


# Global cache instance
_cache: Optional[CacheBackend] = None


def init_cache(redis_url: Optional[str] = None) -> CacheBackend:
    """Initialize cache backend.
    
    Args:
        redis_url: Redis connection string. If None, uses in-memory cache.
    
    Returns:
        CacheBackend instance
    """
    global _cache
    
    if redis_url and REDIS_AVAILABLE:
        _cache = RedisCache(redis_url)
    else:
        _cache = InMemoryCache()
    
    return _cache


def get_cache() -> CacheBackend:
    """Get cache backend instance."""
    global _cache
    if _cache is None:
        _cache = InMemoryCache()
        logger.warning("Cache not initialized - using in-memory fallback")
    return _cache


def cache_get(key: str) -> Optional[Any]:
    """Convenience function to get from cache."""
    return get_cache().get(key)


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Convenience function to set in cache."""
    get_cache().set(key, value, ttl)


def cache_delete(key: str) -> None:
    """Convenience function to delete from cache."""
    get_cache().delete(key)


def cache_delete_pattern(pattern: str) -> None:
    """Convenience function to delete pattern from cache."""
    get_cache().delete_pattern(pattern)


def cached(ttl: int = 300, key_prefix: str = "cache"):
    """Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    
    Example:
        @cached(ttl=300, key_prefix="portfolio")
        def get_portfolio_today(target_date: date):
            return {...}
        
        # Cache key: "cache:portfolio:2026-01-15"
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Check if caching is disabled (for testing)
            import os
            if os.getenv("DISABLE_CACHE", "false").lower() == "true":
                return func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            
            # Add args to key (skip self/cls)
            for arg in args[1:] if args else []:
                key_parts.append(str(arg))
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(key_parts)
            
            # Try cache first
            cached_value = cache_get(cache_key)
            if cached_value is not None:
                logger.debug("Cache HIT: %s", cache_key)
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_set(cache_key, result, ttl)
            logger.debug("Cache SET: %s (TTL: %ds)", cache_key, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> None:
    """Invalidate cache entries matching pattern.
    
    Args:
        pattern: Pattern to match (e.g., "cache:portfolio:*", "cache:user:123:*")
    """
    cache_delete_pattern(pattern)
    logger.info("Cache invalidated: %s", pattern)
