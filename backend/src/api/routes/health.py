"""
Health check endpoint.
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from src.lib.config import get_settings
from src.services.database import check_connection
from src.services.model_cache import get_moirai_model

router = APIRouter()


class HealthStatus(str, Enum):
    """Health status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    database_connected: bool
    model_loaded: bool
    model_version: str | None
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check API and system health status.

    Returns:
        Health status including database and model availability.
    """
    settings = get_settings()

    # Check database
    db_connected = await check_connection()

    # Check model
    model = get_moirai_model()
    model_loaded = model is not None

    # Determine overall status
    if db_connected and model_loaded:
        status = HealthStatus.HEALTHY
    elif db_connected:
        status = HealthStatus.DEGRADED  # Can still serve some endpoints
    else:
        status = HealthStatus.UNHEALTHY

    return HealthResponse(
        status=status.value,
        database_connected=db_connected,
        model_loaded=model_loaded,
        model_version=settings.moirai_model if model_loaded else None,
        timestamp=datetime.utcnow(),
    )
