"""
VitalSigns API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import regions, risks, alerts, signals, health

api_router = APIRouter()

# Health check endpoint
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

# Region endpoints
api_router.include_router(
    regions.router,
    prefix="/regions",
    tags=["regions"]
)

# Risk endpoints
api_router.include_router(
    risks.router,
    prefix="/risks",
    tags=["risks"]
)

# Alert endpoints
api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["alerts"]
)

# Signal endpoints
api_router.include_router(
    signals.router,
    prefix="/signals",
    tags=["signals"]
)
