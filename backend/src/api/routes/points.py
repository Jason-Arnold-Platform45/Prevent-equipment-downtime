"""
Monitoring points API endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.logging import get_logger
from src.schemas.response import (
    LatestReading,
    PointListResponse,
    PointResponse,
    PredictionResponse,
    ReadingResponse,
    ReadingsResponse,
)
from src.services.database import get_session
from src.services.prediction import get_latest_prediction_for_point
from src.services.sensor_data import (
    get_latest_reading,
    get_point_readings,
    get_point_readings_count,
    get_point_with_equipment,
    list_points_paginated,
)

logger = get_logger(__name__)
router = APIRouter()


def _prediction_to_response(prediction) -> PredictionResponse | None:
    """Convert a MoiraiPrediction model to response schema."""
    if not prediction:
        return None

    return PredictionResponse(
        id=prediction.id,
        point_id=prediction.point_id,
        point_name=None,
        equipment_id=prediction.equipment_id,
        equipment_name=None,
        risk_level=prediction.risk_level.value,
        confidence_score=prediction.confidence_score,
        predicted_failure_start=prediction.predicted_failure_start,
        predicted_failure_end=prediction.predicted_failure_end,
        context_start=prediction.context_start,
        context_end=prediction.context_end,
        readings_analyzed=prediction.readings_analyzed,
        model_version=prediction.model_version,
        status=prediction.status.value,
        acknowledged_by_id=prediction.acknowledged_by_id,
        acknowledged_at=prediction.acknowledged_at,
        created_at=prediction.created_at,
    )


@router.get("/points", response_model=PointListResponse)
async def list_points(
    has_prediction: bool | None = Query(
        default=None, description="Filter to points with/without predictions"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_session),
) -> PointListResponse:
    """
    List monitoring points with pagination.

    Includes latest reading and prediction for each point.
    Can filter to show only points with or without predictions.
    """
    points, total = await list_points_paginated(
        session=session,
        page=page,
        page_size=page_size,
        has_prediction=has_prediction,
    )

    items = []
    for point in points:
        # Get readings count
        readings_count = await get_point_readings_count(session, point.id)

        # Get latest reading
        latest = await get_latest_reading(session, point.id)
        latest_reading = None
        if latest:
            value, captured_at = latest
            latest_reading = LatestReading(value=value, captured_at=captured_at)

        # Get latest prediction
        prediction = await get_latest_prediction_for_point(session, point.id)

        items.append(
            PointResponse(
                id=point.id,
                name=point.name,
                readings_count=readings_count,
                latest_reading=latest_reading,
                latest_prediction=_prediction_to_response(prediction),
            )
        )

    total_pages = (total + page_size - 1) // page_size

    return PointListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/points/{point_id}", response_model=PointResponse)
async def get_point(
    point_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> PointResponse:
    """Get a specific monitoring point by ID."""
    point = await get_point_with_equipment(session, point_id)

    if not point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Point {point_id} not found",
        )

    # Get readings count
    readings_count = await get_point_readings_count(session, point_id)

    # Get latest reading
    latest = await get_latest_reading(session, point_id)
    latest_reading = None
    if latest:
        value, captured_at = latest
        latest_reading = LatestReading(value=value, captured_at=captured_at)

    # Get latest prediction
    prediction = await get_latest_prediction_for_point(session, point_id)

    return PointResponse(
        id=point.id,
        name=point.name,
        readings_count=readings_count,
        latest_reading=latest_reading,
        latest_prediction=_prediction_to_response(prediction),
    )


@router.get("/points/{point_id}/readings", response_model=ReadingsResponse)
async def get_point_readings_endpoint(
    point_id: UUID,
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum readings"),
    session: AsyncSession = Depends(get_session),
) -> ReadingsResponse:
    """
    Get time-series readings for a monitoring point.

    Returns sensor readings ordered by timestamp (oldest first).
    Use the limit parameter to control how many readings are returned.
    """
    point = await get_point_with_equipment(session, point_id)

    if not point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Point {point_id} not found",
        )

    df = await get_point_readings(session, point_id, limit=limit)

    readings = [
        ReadingResponse(
            value=row["value"],
            captured_at=row["timestamp"],
        )
        for _, row in df.iterrows()
    ]

    return ReadingsResponse(
        point_id=point_id,
        point_name=point.name,
        readings=readings,
        total=len(readings),
    )
