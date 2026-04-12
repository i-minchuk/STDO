"""Health check API for monitoring and diagnostics.

Endpoints:
- GET /api/health - Basic health check
- GET /api/health/db - Database connectivity check
- GET /api/health/cache - Cache (Redis) connectivity check
- GET /api/health/metrics - Application metrics
"""

from __future__ import annotations
import logging
import time
import sys
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter
from core.service_locator import get_locator
from core.cache import get_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


def _get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


@router.get("")
async def health_check():
    """Basic health check endpoint.
    
    Returns application status and uptime.
    Used by load balancers for basic availability checks.
    
    Returns:
        200 OK if application is running
    """
    return {
        "status": "healthy",
        "timestamp": _get_utc_timestamp(),
        "service": "DokPotok IRIS",
        "version": "0.1.0",
    }


@router.get("/db")
async def database_health():
    """Database connectivity check.
    
    Verifies that database connection is alive and responsive.
    Used by Kubernetes liveness/readiness probes.
    
    Returns:
        200 OK if database is responsive
        503 Service Unavailable if database is down
    """
    try:
        locator = get_locator()
        db = locator.db
        
        # Simple query to test connection
        start_time = time.time()
        result = db.fetch_one("SELECT 1 as test")
        query_time = (time.time() - start_time) * 1000  # ms
        
        if result and result.get("test") == 1:
            return {
                "status": "healthy",
                "database": "PostgreSQL",
                "query_time_ms": round(query_time, 2),
                "timestamp": _get_utc_timestamp(),
            }
        else:
            return {
                "status": "degraded",
                "database": "PostgreSQL",
                "error": "Unexpected response from database",
                "timestamp": _get_utc_timestamp(),
            }
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return {
            "status": "unhealthy",
            "database": "PostgreSQL",
            "error": str(e),
            "timestamp": _get_utc_timestamp(),
        }


@router.get("/cache")
async def cache_health():
    """Cache (Redis) connectivity check.
    
    Verifies that Redis cache is available.
    Returns degraded status if cache is unavailable (app still works with fallback).
    
    Returns:
        200 OK if cache is healthy
        503 if cache is down (but app still works)
    """
    try:
        cache = get_cache()
        is_connected = cache.is_connected() if hasattr(cache, "is_connected") else True
        
        if is_connected:
            return {
                "status": "healthy",
                "cache_type": "Redis",
                "connected": True,
                "timestamp": _get_utc_timestamp(),
            }
        else:
            return {
                "status": "degraded",
                "cache_type": "In-Memory (fallback)",
                "connected": False,
                "message": "Redis unavailable, using in-memory cache",
                "timestamp": _get_utc_timestamp(),
            }
    except Exception as e:
        logger.error("Cache health check failed: %s", e)
        return {
            "status": "degraded",
            "cache_type": "Unknown",
            "error": str(e),
            "timestamp": _get_utc_timestamp(),
        }


@router.get("/metrics")
async def application_metrics():
    """Application metrics endpoint.
    
    Returns basic application metrics for monitoring.
    Can be extended with Prometheus integration.
    
    Returns:
        dict with application metrics
    """
    # Try to import psutil, but make it optional
    try:
        import psutil
        has_psutil = True
    except ImportError:
        has_psutil = False
        logger.warning("psutil not installed - some metrics unavailable")
    
    metrics = {
        "timestamp": _get_utc_timestamp(),
        "application": {
            "status": "healthy",
            "version": "0.1.0",
            "uptime_seconds": 0,  # Would need to track startup time
        },
        "python": {
            "version": sys.version,
            "implementation": sys.implementation.name,
        },
    }
    
    if has_psutil:
        process = psutil.Process()
        metrics["process"] = {
            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
        }
        metrics["system"] = {
            "platform": sys.platform,
            "available_memory_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
        }
    else:
        metrics["process"] = {
            "memory_mb": None,
            "cpu_percent": None,
            "threads": None,
            "note": "Install psutil for detailed metrics: pip install psutil"
        }
    
    return metrics


@router.get("/ready")
async def readiness_check():
    """Readiness probe - checks if app is ready to serve traffic.
    
    Verifies all critical dependencies are available.
    Returns 503 if app should not receive traffic.
    
    Returns:
        200 OK if app is ready
        503 if app is not ready
    """
    checks = {
        "database": False,
        "cache": True,  # Cache is optional (has fallback)
    }
    
    # Check database
    try:
        locator = get_locator()
        result = locator.db.fetch_one("SELECT 1")
        checks["database"] = bool(result and result.get("test") == 1)
    except Exception:
        checks["database"] = False
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": _get_utc_timestamp(),
    }
