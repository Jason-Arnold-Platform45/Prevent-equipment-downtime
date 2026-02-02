"""
Prediction API endpoints.
"""

import csv
import io
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.model_cache import get_moirai_model
from src.lib.logging import get_logger
from src.models.prediction import PredictionStatus, RiskLevel
from src.schemas.request import RunPredictionRequest, UpdatePredictionRequest
from src.schemas.response import (
    PredictionExport,
    PredictionListResponse,
    PredictionResponse,
    RunAllResponse,
    RunPredictionResponse,
    RunPredictionResult,
)
from src.services.database import get_session
from src.services.prediction import (
    get_prediction_by_id,
    list_predictions,
    run_prediction_for_point,
    update_prediction_status,
)
from src.services.sensor_data import get_point_with_equipment, get_points_with_min_readings

logger = get_logger(__name__)
router = APIRouter()


def _prediction_to_response(
    prediction,
    point_name: str | None = None,
    equipment_name: str | None = None,
) -> PredictionResponse:
    """Convert a MoiraiPrediction model to response schema."""
    return PredictionResponse(
        id=prediction.id,
        point_id=prediction.point_id,
        point_name=point_name,
        equipment_id=prediction.equipment_id,
        equipment_name=equipment_name,
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


@router.post("/predictions/run", response_model=RunPredictionResponse)
async def run_predictions(
    request: RunPredictionRequest,
    session: AsyncSession = Depends(get_session),
) -> RunPredictionResponse:
    """
    Run predictions for specified monitoring points.

    This endpoint fetches sensor data for each point, runs the Moirai model,
    and creates prediction records with risk classifications.
    """
    model = get_moirai_model()
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Moirai model not loaded",
        )

    predictions = []
    errors = []

    for point_id in request.point_ids:
        try:
            prediction = await run_prediction_for_point(session, point_id, model)

            # Get point info for response
            point = await get_point_with_equipment(session, point_id)
            point_name = point.name if point else None
            equipment_name = point.equipment.name if point and point.equipment else None

            predictions.append(
                _prediction_to_response(prediction, point_name, equipment_name)
            )
        except Exception as e:
            logger.error(
                f"Prediction failed for point {point_id}: {e}",
                extra={"extra_fields": {"point_id": str(point_id)}},
            )
            errors.append(
                RunPredictionResult(
                    point_id=point_id,
                    success=False,
                    error=str(e),
                )
            )

    await session.commit()

    return RunPredictionResponse(
        predictions_created=len(predictions),
        predictions=predictions,
        errors=errors,
    )


@router.post("/predictions/run-all", response_model=RunAllResponse)
async def run_all_predictions(
    session: AsyncSession = Depends(get_session),
) -> RunAllResponse:
    """
    Run predictions for all monitoring points with sufficient data.

    Finds all points with at least 5 readings and runs predictions for each.
    """
    model = get_moirai_model()
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Moirai model not loaded",
        )

    # Get all eligible points
    eligible_point_ids = await get_points_with_min_readings(session, min_readings=5)

    predictions_created = 0
    errors_count = 0

    for point_id in eligible_point_ids:
        try:
            await run_prediction_for_point(session, point_id, model)
            predictions_created += 1
        except Exception as e:
            logger.error(
                f"Prediction failed for point {point_id}: {e}",
                extra={"extra_fields": {"point_id": str(point_id)}},
            )
            errors_count += 1

    await session.commit()

    return RunAllResponse(
        eligible_points=len(eligible_point_ids),
        predictions_created=predictions_created,
        errors_count=errors_count,
        message=f"Processed {len(eligible_point_ids)} points: {predictions_created} predictions created, {errors_count} errors",
    )


@router.get("/predictions", response_model=PredictionListResponse)
async def get_predictions(
    risk_level: Literal["HIGH", "MEDIUM", "LOW"] | None = Query(
        default=None, description="Filter by risk level"
    ),
    point_id: UUID | None = Query(default=None, description="Filter by point ID"),
    equipment_id: UUID | None = Query(
        default=None, description="Filter by equipment ID"
    ),
    prediction_status: Literal["pending", "confirmed", "dismissed"] | None = Query(
        default=None, alias="status", description="Filter by status"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_session),
) -> PredictionListResponse:
    """
    List predictions with optional filtering.

    Supports filtering by risk level, point ID, equipment ID, and status.
    Results are paginated and sorted by creation date (newest first).
    """
    # Convert string filters to enums
    risk_level_enum = RiskLevel(risk_level) if risk_level else None
    status_enum = PredictionStatus(prediction_status) if prediction_status else None

    predictions, total = await list_predictions(
        session=session,
        risk_level=risk_level_enum,
        point_id=point_id,
        equipment_id=equipment_id,
        status=status_enum,
        page=page,
        page_size=page_size,
    )

    # Get point/equipment names for each prediction
    items = []
    for pred in predictions:
        point = await get_point_with_equipment(session, pred.point_id)
        point_name = point.name if point else None
        equipment_name = point.equipment.name if point and point.equipment else None
        items.append(_prediction_to_response(pred, point_name, equipment_name))

    total_pages = (total + page_size - 1) // page_size

    return PredictionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> PredictionResponse:
    """Get a specific prediction by ID."""
    prediction = await get_prediction_by_id(session, prediction_id)

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {prediction_id} not found",
        )

    # Get point/equipment names
    point = await get_point_with_equipment(session, prediction.point_id)
    point_name = point.name if point else None
    equipment_name = point.equipment.name if point and point.equipment else None

    return _prediction_to_response(prediction, point_name, equipment_name)


@router.patch("/predictions/{prediction_id}", response_model=PredictionResponse)
async def update_prediction(
    prediction_id: UUID,
    request: UpdatePredictionRequest,
    session: AsyncSession = Depends(get_session),
) -> PredictionResponse:
    """
    Update a prediction's status.

    Used to confirm or dismiss a prediction after review.
    """
    status_enum = PredictionStatus(request.status)

    prediction = await update_prediction_status(
        session=session,
        prediction_id=prediction_id,
        status=status_enum,
        acknowledged_by_id=None,  # TODO: Get from auth context
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {prediction_id} not found",
        )

    await session.commit()

    # Get point/equipment names
    point = await get_point_with_equipment(session, prediction.point_id)
    point_name = point.name if point else None
    equipment_name = point.equipment.name if point and point.equipment else None

    return _prediction_to_response(prediction, point_name, equipment_name)


@router.get("/predictions/export")
async def export_predictions(
    format: Literal["csv", "json"] = Query(default="csv", description="Export format"),
    risk_level: Literal["HIGH", "MEDIUM", "LOW"] | None = Query(
        default=None, description="Filter by risk level"
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Export predictions in CSV or JSON format.

    Supports filtering by risk level. Returns all matching predictions
    (not paginated) for use in maintenance planning systems.
    """
    risk_level_enum = RiskLevel(risk_level) if risk_level else None

    # Get all predictions (no pagination for export)
    predictions, _ = await list_predictions(
        session=session,
        risk_level=risk_level_enum,
        page=1,
        page_size=10000,  # Large limit for export
    )

    # Build export data with point/equipment names
    export_data = []
    for pred in predictions:
        point = await get_point_with_equipment(session, pred.point_id)
        point_name = point.name if point else None
        equipment_name = point.equipment.name if point and point.equipment else None

        export_data.append(
            PredictionExport(
                point_id=str(pred.point_id),
                point_name=point_name,
                equipment_name=equipment_name,
                risk_level=pred.risk_level.value,
                confidence_score=pred.confidence_score,
                predicted_failure_start=(
                    pred.predicted_failure_start.isoformat()
                    if pred.predicted_failure_start
                    else None
                ),
                predicted_failure_end=(
                    pred.predicted_failure_end.isoformat()
                    if pred.predicted_failure_end
                    else None
                ),
                status=pred.status.value,
                created_at=pred.created_at.isoformat(),
            )
        )

    if format == "json":
        return JSONResponse(
            content=[item.model_dump() for item in export_data],
            headers={
                "Content-Disposition": "attachment; filename=predictions.json"
            },
        )

    # CSV format
    output = io.StringIO()
    if export_data:
        fieldnames = list(export_data[0].model_dump().keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for item in export_data:
            writer.writerow(item.model_dump())

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=predictions.csv"
        },
    )
