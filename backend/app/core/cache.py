"""
Redis caching layer for advanced astrological systems.

Provides:
- Result caching for expensive calculations
- TTL-based expiration
- Namespace-based key management
- Fallback to in-memory cache if Redis unavailable

Usage:
    from app.core.cache import cache_service

    # Cache a result
    await cache_service.set("jaimini:profile_123", result_data, ttl=3600)

    # Retrieve from cache
    cached = await cache_service.get("jaimini:profile_123")

    # Invalidate cache
    await cache_service.delete("jaimini:profile_123")
"""

import json
import hashlib
from typing import Any, Optional, Dict
from datetime import timedelta
import redis.asyncio as redis
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Async Redis cache service with fallback to in-memory storage.

    Features:
    - Automatic JSON serialization/deserialization
    - Key namespacing for different systems
    - TTL support
    - In-memory fallback when Redis unavailable
    - Cache hit/miss metrics
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache service.

        Args:
            redis_url: Redis connection URL (optional)
        """
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.redis_client: Optional[redis.Redis] = None
        self.fallback_cache: Dict[str, Any] = {}  # In-memory fallback
        self.use_fallback = False

        # Metrics
        self.hits = 0
        self.misses = 0
        self.errors = 0

    async def connect(self):
        """Connect to Redis (optional, auto-connects on first use)."""
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                await self.redis_client.ping()
                self.use_fallback = False
                logger.info("✅ Connected to Redis cache")
            except Exception as e:
                logger.warning(f"⚠️  Redis unavailable, using in-memory fallback: {e}")
                self.use_fallback = True
                self.redis_client = None

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    def _make_key(self, namespace: str, key: str) -> str:
        """
        Create namespaced cache key.

        Args:
            namespace: System namespace (e.g., 'jaimini', 'lal_kitab')
            key: Unique identifier (e.g., profile_id)

        Returns:
            Fully qualified cache key
        """
        return f"jioastro:{namespace}:{key}"

    def _hash_key(self, data: Dict) -> str:
        """
        Generate hash for dictionary data (for complex keys).

        Args:
            data: Dictionary to hash

        Returns:
            SHA256 hash string
        """
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        await self.connect()

        try:
            if self.use_fallback:
                # Use in-memory cache
                value = self.fallback_cache.get(key)
                if value is not None:
                    self.hits += 1
                    return value
                self.misses += 1
                return None

            # Use Redis
            value = await self.redis_client.get(key)
            if value is not None:
                self.hits += 1
                return json.loads(value)

            self.misses += 1
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.errors += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = 3600
    ) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        await self.connect()

        try:
            serialized = json.dumps(value)

            if self.use_fallback:
                # Use in-memory cache (no TTL support in fallback)
                self.fallback_cache[key] = value
                return True

            # Use Redis
            if ttl:
                await self.redis_client.setex(key, ttl, serialized)
            else:
                await self.redis_client.set(key, serialized)

            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.errors += 1
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        await self.connect()

        try:
            if self.use_fallback:
                if key in self.fallback_cache:
                    del self.fallback_cache[key]
                return True

            await self.redis_client.delete(key)
            return True

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.errors += 1
            return False

    async def clear_namespace(self, namespace: str) -> int:
        """
        Clear all keys in a namespace.

        Args:
            namespace: Namespace to clear (e.g., 'jaimini')

        Returns:
            Number of keys deleted
        """
        await self.connect()

        try:
            pattern = f"jioastro:{namespace}:*"

            if self.use_fallback:
                # Clear from in-memory cache
                keys_to_delete = [k for k in self.fallback_cache.keys() if k.startswith(f"jioastro:{namespace}:")]
                for k in keys_to_delete:
                    del self.fallback_cache[k]
                return len(keys_to_delete)

            # Use Redis SCAN to avoid blocking
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await self.redis_client.delete(*keys)
                if cursor == 0:
                    break

            return deleted

        except Exception as e:
            logger.error(f"Cache clear namespace error: {e}")
            self.errors += 1
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hit/miss/error counts and hit rate
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "mode": "fallback" if self.use_fallback else "redis"
        }


def cached(
    namespace: str,
    ttl: int = 3600,
    key_prefix: Optional[str] = None
):
    """
    Decorator for caching function results.

    Args:
        namespace: Cache namespace (e.g., 'jaimini', 'lal_kitab')
        ttl: Time to live in seconds (default: 1 hour)
        key_prefix: Optional prefix for cache key

    Usage:
        @cached(namespace="jaimini", ttl=3600)
        async def calculate_chara_karakas(profile_id: str):
            # Expensive calculation
            return result
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            key_data = {
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            cache_key_hash = cache_service._hash_key(key_data)

            if key_prefix:
                cache_key = cache_service._make_key(namespace, f"{key_prefix}:{cache_key_hash}")
            else:
                cache_key = cache_service._make_key(namespace, cache_key_hash)

            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_result

            # Cache miss - compute result
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_service.set(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


# Global cache service instance
cache_service = CacheService()


# Namespace constants for different systems
class CacheNamespace:
    """Cache namespace constants for different astrological systems."""
    JAIMINI = "jaimini"
    LAL_KITAB = "lal_kitab"
    ASHTAKAVARGA = "ashtakavarga"
    VARSHAPHAL = "varshaphal"
    COMPATIBILITY = "compatibility"
    CHARTS = "charts"
    PROFILES = "profiles"


# TTL constants (in seconds)
class CacheTTL:
    """Cache TTL constants for different data types."""
    SHORT = 300  # 5 minutes
    MEDIUM = 1800  # 30 minutes
    LONG = 3600  # 1 hour
    DAY = 86400  # 24 hours
    WEEK = 604800  # 7 days
