"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.error_handler import setup_error_handlers
from src.api.routes import dashboard, health, points, predictions
from src.lib.config import get_settings
from src.lib.logging import get_logger, setup_logging
from src.services.database import close_database, init_database
from src.services.model_cache import get_moirai_model, load_moirai_model

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()

    # Startup
    logger.info(
        f"Starting Moirai Sensor Prediction API",
        extra={"extra_fields": {"environment": settings.environment}},
    )

    # Initialize database
    await init_database()

    # Load Moirai model (async-safe but may take time)
    await load_moirai_model()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_database()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Moirai Sensor Failure Prediction API",
        description="API for predicting sensor failures using the Moirai time-series model",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Error handlers
    setup_error_handlers(app)

    # Routes
    app.include_router(health.router, prefix="/api/v1", tags=["System"])
    app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
    app.include_router(points.router, prefix="/api/v1", tags=["Points"])
    app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])

    return app


# Create the app instance
app = create_app()
