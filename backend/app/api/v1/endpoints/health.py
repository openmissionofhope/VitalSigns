"""
Health check endpoints for VitalSigns API.
"""
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        Health status of the API
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check endpoint - verifies database connectivity.

    Returns:
        Readiness status including database connection
    """
    db_status = "healthy"
    db_message = None

    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        db_message = str(e)

    overall_status = "ready" if db_status == "healthy" else "not_ready"

    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": {
                "status": db_status,
                "message": db_message,
            }
        }
    }


@router.get("/live", response_model=Dict[str, Any])
async def liveness_check():
    """
    Liveness check endpoint.

    Returns:
        Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
