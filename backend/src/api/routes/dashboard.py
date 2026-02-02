"""
Dashboard API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.lib.logging import get_logger
from src.models.existing import MonitoringPoint
from src.models.prediction import MoiraiPrediction, PredictionStatus, RiskLevel
from src.schemas.response import (
    DashboardSummary,
    HighRiskPoint,
    PredictionResponse,
    RiskCounts,
)
from src.services.database import get_session
from src.services.prediction import (
    get_high_risk_points,
    get_recent_predictions,
    get_risk_counts,
)
from src.services.sensor_data import get_point_with_equipment

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


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    session: AsyncSession = Depends(get_session),
) -> DashboardSummary:
    """
    Get dashboard summary statistics.

    Returns:
    - Total monitoring points count
    - Points with predictions count
    - Risk counts (high/medium/low)
    - Recent predictions
    - High-risk points requiring attention
    """
    # Total points count
    total_points_query = select(func.count()).select_from(MonitoringPoint)
    total_points = (await session.execute(total_points_query)).scalar() or 0

    # Points with predictions count
    points_with_predictions_query = (
        select(func.count(func.distinct(MoiraiPrediction.point_id)))
    )
    points_with_predictions = (
        await session.execute(points_with_predictions_query)
    ).scalar() or 0

    # Get risk counts
    risk_counts_dict = await get_risk_counts(session)
    sensors_by_risk = RiskCounts(
        high=risk_counts_dict["high"],
        medium=risk_counts_dict["medium"],
        low=risk_counts_dict["low"],
    )

    # Get recent predictions with point/equipment names
    recent = await get_recent_predictions(session, limit=10)
    recent_predictions = []
    for pred in recent:
        point = await get_point_with_equipment(session, pred.point_id)
        point_name = point.name if point else None
        equipment_name = point.equipment.name if point and point.equipment else None
        recent_predictions.append(
            _prediction_to_response(pred, point_name, equipment_name)
        )

    # Get high-risk points
    high_risk = await get_high_risk_points(session, limit=10)
    high_risk_points = []
    for pred in high_risk:
        point = await get_point_with_equipment(session, pred.point_id)
        point_name = point.name if point else None
        high_risk_points.append(
            HighRiskPoint(
                point_id=pred.point_id,
                point_name=point_name,
                confidence_score=pred.confidence_score,
                predicted_failure_start=pred.predicted_failure_start,
            )
        )

    return DashboardSummary(
        total_points=total_points,
        points_with_predictions=points_with_predictions,
        sensors_by_risk=sensors_by_risk,
        recent_predictions=recent_predictions,
        high_risk_points=high_risk_points,
    )
