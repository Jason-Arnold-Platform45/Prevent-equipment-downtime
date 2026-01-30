"""
Structured logging configuration.
"""

import logging
import sys
from typing import Any

from .config import get_settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured log output."""

    def format(self, record: logging.LogRecord) -> str:
        # Add extra fields if present
        extra = ""
        if hasattr(record, "extra_fields"):
            extra_fields: dict[str, Any] = record.extra_fields
            extra = " ".join(f"{k}={v}" for k, v in extra_fields.items())
            if extra:
                extra = f" | {extra}"

        # Format timestamp
        timestamp = self.formatTime(record, self.datefmt)

        # Build message
        message = f"{timestamp} | {record.levelname:<8} | {record.name} | {record.getMessage()}{extra}"

        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()

    # Create formatter
    formatter = StructuredFormatter(
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(settings.log_level)
    root_logger.addHandler(console_handler)

    # Set levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds extra fields to log records."""

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        extra = kwargs.get("extra", {})
        extra["extra_fields"] = {**self.extra, **extra.get("extra_fields", {})}
        kwargs["extra"] = extra
        return msg, kwargs


def get_context_logger(name: str, **context: Any) -> LoggerAdapter:
    """Get a logger with context fields automatically added."""
    logger = get_logger(name)
    return LoggerAdapter(logger, context)
