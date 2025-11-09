"""
Cache management API endpoints.

Provides:
- Cache statistics
- Cache clearing by namespace
- Cache warming
"""

from fastapi import APIRouter, HTTPException, status
from app.core.cache import cache_service, CacheNamespace
from typing import Dict, Any

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    """
    Get cache statistics.

    Returns:
        Dictionary with hits, misses, hit rate, and mode (redis/fallback)
    """
    stats = await cache_service.get_stats()
    return {
        "status": "success",
        "cache_stats": stats
    }


@router.delete("/clear/{namespace}")
async def clear_cache_namespace(namespace: str):
    """
    Clear all cache entries for a specific namespace.

    Args:
        namespace: One of: jaimini, lal_kitab, ashtakavarga, varshaphal, compatibility

    Returns:
        Number of keys deleted
    """
    valid_namespaces = [
        CacheNamespace.JAIMINI,
        CacheNamespace.LAL_KITAB,
        CacheNamespace.ASHTAKAVARGA,
        CacheNamespace.VARSHAPHAL,
        CacheNamespace.COMPATIBILITY,
        CacheNamespace.CHARTS,
        CacheNamespace.PROFILES,
    ]

    if namespace not in valid_namespaces:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid namespace. Must be one of: {', '.join(valid_namespaces)}"
        )

    deleted_count = await cache_service.clear_namespace(namespace)

    return {
        "status": "success",
        "namespace": namespace,
        "keys_deleted": deleted_count,
        "message": f"Cleared {deleted_count} cache entries from {namespace} namespace"
    }


@router.delete("/clear-all")
async def clear_all_caches():
    """
    Clear ALL cache entries (use with caution).

    Returns:
        Total number of keys deleted across all namespaces
    """
    total_deleted = 0

    namespaces = [
        CacheNamespace.JAIMINI,
        CacheNamespace.LAL_KITAB,
        CacheNamespace.ASHTAKAVARGA,
        CacheNamespace.VARSHAPHAL,
        CacheNamespace.COMPATIBILITY,
        CacheNamespace.CHARTS,
        CacheNamespace.PROFILES,
    ]

    for namespace in namespaces:
        deleted = await cache_service.clear_namespace(namespace)
        total_deleted += deleted

    return {
        "status": "success",
        "total_keys_deleted": total_deleted,
        "namespaces_cleared": namespaces,
        "message": f"Cleared {total_deleted} total cache entries"
    }


@router.get("/health")
async def cache_health():
    """
    Check cache health status.

    Returns:
        Cache mode (redis/fallback) and connection status
    """
    stats = await cache_service.get_stats()

    return {
        "status": "healthy",
        "mode": stats["mode"],
        "redis_available": stats["mode"] == "redis",
        "total_requests": stats["total_requests"],
        "hit_rate": stats["hit_rate"]
    }
