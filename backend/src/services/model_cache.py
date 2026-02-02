"""
Model cache service for storing loaded ML models.
"""

from src.lib.config import get_settings
from src.lib.logging import get_logger

logger = get_logger(__name__)

# Model cache (loaded on startup)
_moirai_model = None


def get_moirai_model():
    """Get the cached Moirai model instance."""
    global _moirai_model
    return _moirai_model


def set_moirai_model(model):
    """Set the cached Moirai model instance."""
    global _moirai_model
    _moirai_model = model


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
