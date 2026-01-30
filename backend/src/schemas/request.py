"""
Pydantic request schemas for API endpoints.
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RunPredictionRequest(BaseModel):
    """Request to run predictions for specific monitoring points."""

    point_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of monitoring point IDs to run predictions for",
    )


class UpdatePredictionRequest(BaseModel):
    """Request to update a prediction's status."""

    status: Literal["confirmed", "dismissed"] = Field(
        ...,
        description="New status for the prediction",
    )


class PredictionListParams(BaseModel):
    """Query parameters for listing predictions."""

    risk_level: Literal["HIGH", "MEDIUM", "LOW"] | None = Field(
        default=None,
        description="Filter by risk level",
    )
    point_id: UUID | None = Field(
        default=None,
        description="Filter by monitoring point ID",
    )
    equipment_id: UUID | None = Field(
        default=None,
        description="Filter by equipment ID",
    )
    status: Literal["pending", "confirmed", "dismissed"] | None = Field(
        default=None,
        description="Filter by prediction status",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page",
    )


class PointListParams(BaseModel):
    """Query parameters for listing monitoring points."""

    has_prediction: bool | None = Field(
        default=None,
        description="Filter to points with/without predictions",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page",
    )


class ExportParams(BaseModel):
    """Query parameters for exporting predictions."""

    format: Literal["csv", "json"] = Field(
        default="csv",
        description="Export format",
    )
    risk_level: Literal["HIGH", "MEDIUM", "LOW"] | None = Field(
        default=None,
        description="Filter by risk level",
    )
