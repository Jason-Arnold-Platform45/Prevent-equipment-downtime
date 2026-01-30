"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.error_handler import setup_error_handlers
from src.api.routes import health
from src.lib.config import get_settings
from src.lib.logging import get_logger, setup_logging
from src.services.database import close_database, init_database

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Model cache (loaded on startup)
_moirai_model = None


def get_moirai_model():
    """Get the cached Moirai model instance."""
    global _moirai_model
    return _moirai_model


async def load_moirai_model() -> None:
    """Load Moirai model into memory."""
    global _moirai_model

    settings = get_settings()
    logger.info(f"Loading Moirai model: {settings.moirai_model}")

    try:
        # Import here to avoid slow startup if model not needed
        from uni2ts.model.moirai import MoiraiForecast, MoiraiModule

        module = MoiraiModule.from_pretrained(settings.moirai_model)
        _moirai_model = MoiraiForecast(
            module=module,
            prediction_length=settings.moirai_prediction_length,
            context_length=settings.moirai_context_length,
            num_samples=settings.moirai_num_samples,
            target_dim=1,
            patch_size="auto",
        )
        logger.info("Moirai model loaded successfully")
    except ImportError as e:
        logger.warning(f"Moirai model not available: {e}")
        _moirai_model = None
    except Exception as e:
        logger.error(f"Failed to load Moirai model: {e}")
        _moirai_model = None


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

    # Future route registrations:
    # app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
    # app.include_router(points.router, prefix="/api/v1", tags=["Points"])
    # app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])

    return app


# Create the app instance
app = create_app()
