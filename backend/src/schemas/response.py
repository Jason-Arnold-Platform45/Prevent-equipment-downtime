"""
Pydantic response schemas for API endpoints.
"""

from datetime import datetime
from typing import Any, Generic, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class PredictionResponse(BaseModel):
    """Response schema for a prediction."""

    id: UUID
    point_id: UUID
    point_name: str | None = None
    equipment_id: UUID | None = None
    equipment_name: str | None = None
    risk_level: Literal["HIGH", "MEDIUM", "LOW"]
    confidence_score: float = Field(ge=0, le=100)
    predicted_failure_start: datetime | None = None
    predicted_failure_end: datetime | None = None
    context_start: datetime
    context_end: datetime
    readings_analyzed: int
    model_version: str
    status: Literal["pending", "confirmed", "dismissed"]
    acknowledged_by_id: UUID | None = None
    acknowledged_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionListResponse(PaginatedResponse[PredictionResponse]):
    """Paginated list of predictions."""

    pass


class RunPredictionResult(BaseModel):
    """Result for a single point prediction."""

    point_id: UUID
    success: bool
    prediction: PredictionResponse | None = None
    error: str | None = None


class RunPredictionResponse(BaseModel):
    """Response from running predictions."""

    predictions_created: int
    predictions: list[PredictionResponse]
    errors: list[RunPredictionResult]


class RunAllResponse(BaseModel):
    """Response from running predictions for all eligible points."""

    eligible_points: int
    predictions_created: int
    errors_count: int
    message: str


class LatestReading(BaseModel):
    """Latest sensor reading for a point."""

    value: float
    captured_at: datetime


class PointResponse(BaseModel):
    """Response schema for a monitoring point."""

    id: UUID
    name: str | None
    readings_count: int
    latest_reading: LatestReading | None = None
    latest_prediction: PredictionResponse | None = None

    class Config:
        from_attributes = True


class PointListResponse(PaginatedResponse[PointResponse]):
    """Paginated list of monitoring points."""

    pass


class ReadingResponse(BaseModel):
    """Individual sensor reading."""

    value: float
    captured_at: datetime


class ReadingsResponse(BaseModel):
    """Response with sensor readings for a point."""

    point_id: UUID
    point_name: str | None
    readings: list[ReadingResponse]
    total: int


class RiskCounts(BaseModel):
    """Count of predictions by risk level."""

    high: int = 0
    medium: int = 0
    low: int = 0


class EquipmentAtRisk(BaseModel):
    """Equipment with high-risk sensors."""

    equipment_id: UUID
    equipment_name: str | None
    high_risk_sensors: int
    total_sensors: int


class HighRiskPoint(BaseModel):
    """Summary of a high-risk point."""

    point_id: UUID
    point_name: str | None
    confidence_score: float
    predicted_failure_start: datetime | None


class DashboardSummary(BaseModel):
    """Dashboard summary statistics."""

    total_points: int
    points_with_predictions: int
    sensors_by_risk: RiskCounts
    recent_predictions: list[PredictionResponse]
    high_risk_points: list[HighRiskPoint]


class PredictionExport(BaseModel):
    """Export format for predictions."""

    point_id: str
    point_name: str | None
    equipment_name: str | None
    risk_level: str
    confidence_score: float
    predicted_failure_start: str | None
    predicted_failure_end: str | None
    status: str
    created_at: str


class ErrorDetail(BaseModel):
    """Error detail for responses."""

    error: str
    message: str
    details: dict[str, Any] | None = None
    timestamp: datetime
