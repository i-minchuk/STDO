"""Health check API for monitoring and diagnostics.

Endpoints:
- GET /api/health - Basic health check
- GET /api/health/db - Database connectivity check
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from core.service_locator import get_locator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "DokPotok IRIS",
        "version": "0.3.0",
    }


@router.get("/db")
def database_health():
    """Database connectivity check.
    
    Verifies that database connection is alive and responsive.
    """
    try:
        locator = get_locator()
        user_count = locator.user_repo.count()
        return {
            "status": "healthy",
            "db": "connected",
            "user_count": user_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return {
            "status": "unhealthy",
            "db": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
