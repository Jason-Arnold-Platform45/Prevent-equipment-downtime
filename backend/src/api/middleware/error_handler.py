"""
Global error handling middleware for FastAPI.
"""

from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from src.lib.logging import get_logger

logger = get_logger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    message: str
    details: dict[str, Any] | None = None
    timestamp: datetime


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""

    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    """Validation error response format."""

    error: str = "validation_error"
    message: str
    details: list[ValidationErrorDetail]
    timestamp: datetime


def create_error_response(
    error: str,
    message: str,
    status_code: int,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Create a standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=error,
            message=message,
            details=details,
            timestamp=datetime.utcnow(),
        ).model_dump(mode="json"),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception(
        f"Unhandled exception: {exc}",
        extra={"extra_fields": {"path": request.url.path, "method": request.method}},
    )
    return create_error_response(
        error="internal_error",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(
            ValidationErrorDetail(
                field=field,
                message=error["msg"],
            )
        )

    logger.warning(
        f"Validation error: {len(errors)} errors",
        extra={"extra_fields": {"path": request.url.path, "errors": len(errors)}},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse(
            message="Request validation failed",
            details=errors,
            timestamp=datetime.utcnow(),
        ).model_dump(mode="json"),
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    logger.exception(
        f"Database error: {exc}",
        extra={"extra_fields": {"path": request.url.path}},
    )
    return create_error_response(
        error="database_error",
        message="A database error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class InsufficientDataError(Exception):
    """Raised when there's not enough data for prediction."""

    def __init__(self, point_id: str, readings_count: int, minimum_required: int = 5):
        self.point_id = point_id
        self.readings_count = readings_count
        self.minimum_required = minimum_required
        super().__init__(
            f"Point {point_id} has only {readings_count} readings, "
            f"minimum {minimum_required} required"
        )


async def insufficient_data_handler(
    request: Request, exc: InsufficientDataError
) -> JSONResponse:
    """Handle insufficient data errors."""
    return create_error_response(
        error="insufficient_data",
        message=str(exc),
        status_code=status.HTTP_400_BAD_REQUEST,
        details={
            "point_id": exc.point_id,
            "readings_count": exc.readings_count,
            "minimum_required": exc.minimum_required,
        },
    )


class PredictionError(Exception):
    """Raised when prediction fails."""

    def __init__(self, message: str, point_id: str | None = None):
        self.point_id = point_id
        super().__init__(message)


async def prediction_error_handler(
    request: Request, exc: PredictionError
) -> JSONResponse:
    """Handle prediction errors."""
    logger.error(
        f"Prediction error: {exc}",
        extra={"extra_fields": {"point_id": exc.point_id}},
    )
    return create_error_response(
        error="prediction_error",
        message=str(exc),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"point_id": exc.point_id} if exc.point_id else None,
    )


def setup_error_handlers(app: FastAPI) -> None:
    """Register all error handlers with the FastAPI app."""
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(InsufficientDataError, insufficient_data_handler)
    app.add_exception_handler(PredictionError, prediction_error_handler)
