"""
Prediction service for running Moirai forecasts and saving results.
"""

from datetime import datetime
from uuid import UUID

import numpy as np
import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.error_handler import InsufficientDataError, PredictionError
from src.lib.config import get_settings
from src.lib.logging import get_logger
from src.models.prediction import MoiraiPrediction, PredictionStatus, RiskLevel
from src.services.risk_classifier import classify_risk
from src.services.sensor_data import (
    get_point_readings,
    get_point_readings_count,
    get_point_with_equipment,
)

logger = get_logger(__name__)

# Minimum readings required for prediction
MIN_READINGS = 5


async def run_prediction_for_point(
    session: AsyncSession,
    point_id: UUID,
    model: object,  # MoiraiForecast instance
) -> MoiraiPrediction:
    """
    Run Moirai prediction for a single monitoring point.

    Args:
        session: Database session
        point_id: Monitoring point UUID
        model: Loaded Moirai model instance

    Returns:
        Created MoiraiPrediction record

    Raises:
        InsufficientDataError: If point has fewer than MIN_READINGS
        PredictionError: If model inference fails
    """
    settings = get_settings()

    # Check readings count first
    readings_count = await get_point_readings_count(session, point_id)
    if readings_count < MIN_READINGS:
        raise InsufficientDataError(
            point_id=str(point_id),
            readings_count=readings_count,
            minimum_required=MIN_READINGS,
        )

    # Fetch sensor readings
    df = await get_point_readings(
        session,
        point_id,
        limit=settings.moirai_context_length,
    )

    if len(df) < MIN_READINGS:
        raise InsufficientDataError(
            point_id=str(point_id),
            readings_count=len(df),
            minimum_required=MIN_READINGS,
        )

    logger.info(
        f"Running prediction for point {point_id}",
        extra={"extra_fields": {"readings_count": len(df)}},
    )

    # Get point info (equipment_id not yet mapped in schema)
    point = await get_point_with_equipment(session, point_id)
    equipment_id = None  # TODO: Map equipment relationship when available

    # Context window timestamps
    context_start = df["timestamp"].min()
    context_end = df["timestamp"].max()

    # Run Moirai inference
    try:
        forecast_mean, forecast_std = await run_moirai_inference(
            model=model,
            values=df["value"].values,
            timestamps=df["timestamp"].values,
        )
    except Exception as e:
        logger.error(
            f"Moirai inference failed for point {point_id}: {e}",
            extra={"extra_fields": {"point_id": str(point_id)}},
        )
        raise PredictionError(
            message=f"Model inference failed: {str(e)}",
            point_id=str(point_id),
        )

    # Classify risk
    classification = classify_risk(
        historical_values=df["value"].values,
        forecast_mean=forecast_mean,
        forecast_std=forecast_std,
        context_end=context_end.to_pydatetime(),
        hours_per_step=1.0,  # Assume hourly readings
    )

    # Create prediction record (convert enums to string values for DB storage)
    prediction = MoiraiPrediction(
        point_id=point_id,
        equipment_id=equipment_id,
        risk_level=classification.risk_level.value,
        confidence_score=classification.confidence_score,
        predicted_failure_start=classification.predicted_failure_start,
        predicted_failure_end=classification.predicted_failure_end,
        context_start=context_start.to_pydatetime(),
        context_end=context_end.to_pydatetime(),
        readings_analyzed=len(df),
        forecast_values={
            "mean": forecast_mean.tolist(),
            "std": forecast_std.tolist(),
            "anomaly_indices": classification.anomaly_indices,
        },
        model_version=settings.moirai_model,
        status=PredictionStatus.PENDING.value,
    )

    session.add(prediction)
    await session.flush()
    await session.refresh(prediction)

    logger.info(
        f"Prediction created for point {point_id}",
        extra={
            "extra_fields": {
                "prediction_id": str(prediction.id),
                "risk_level": classification.risk_level.value,
                "confidence_score": classification.confidence_score,
            }
        },
    )

    return prediction


async def run_moirai_inference(
    model: object | None,
    values: np.ndarray,
    timestamps: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run Moirai model inference on time series data.

    Args:
        model: MoiraiForecast instance (or None for mock inference)
        values: Array of sensor values
        timestamps: Array of timestamps

    Returns:
        Tuple of (forecast_mean, forecast_std) arrays
    """
    settings = get_settings()

    # Use mock inference if model is not loaded
    if model is None:
        logger.warning("Using mock inference (Moirai model not loaded)")
        return _mock_inference(values, settings.moirai_prediction_length)

    try:
        # Import GluonTS for data format
        from gluonts.dataset.pandas import PandasDataset

        # Create DataFrame for GluonTS
        df = pd.DataFrame({"target": values}, index=pd.DatetimeIndex(timestamps))
        df.index.name = None
        df.index.freq = pd.infer_freq(df.index) or "h"  # Default to hourly

        # Create GluonTS dataset
        dataset = PandasDataset({"target": df}, target="target")

        # Run prediction
        predictor = model.create_predictor(batch_size=1)
        forecasts = list(predictor.predict(dataset))

        if not forecasts:
            raise ValueError("No forecasts generated")

        forecast = forecasts[0]

        # Get mean and quantiles to calculate std
        forecast_mean = forecast.mean
        # Approximate std from quantiles if available
        if hasattr(forecast, "quantile"):
            q_75 = forecast.quantile(0.75)
            q_25 = forecast.quantile(0.25)
            forecast_std = (q_75 - q_25) / 1.35  # IQR to std approximation
        else:
            forecast_std = np.zeros_like(forecast_mean)

        return np.array(forecast_mean), np.array(forecast_std)

    except ImportError as e:
        logger.warning(f"GluonTS not available, using mock inference: {e}")
        # Mock inference for testing without model
        return _mock_inference(values, settings.moirai_prediction_length)


def _mock_inference(
    values: np.ndarray,
    prediction_length: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Mock inference for testing when Moirai model is not available.

    Generates synthetic forecasts based on historical patterns.
    """
    mean = np.mean(values)
    std = np.std(values)

    # Generate forecast with slight trend and noise
    last_value = values[-1]
    trend = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0

    forecast_mean = np.array(
        [
            last_value + trend * (i + 1) + np.random.normal(0, std * 0.1)
            for i in range(prediction_length)
        ]
    )

    # Add some anomalies for testing (10% chance per point)
    for i in range(prediction_length):
        if np.random.random() < 0.1:
            forecast_mean[i] += np.random.choice([-1, 1]) * std * 3

    forecast_std = np.full(prediction_length, std * 0.5)

    return forecast_mean, forecast_std


async def get_prediction_by_id(
    session: AsyncSession,
    prediction_id: UUID,
) -> MoiraiPrediction | None:
    """Get a prediction by ID."""
    query = select(MoiraiPrediction).where(MoiraiPrediction.id == prediction_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def list_predictions(
    session: AsyncSession,
    risk_level: RiskLevel | None = None,
    point_id: UUID | None = None,
    equipment_id: UUID | None = None,
    status: PredictionStatus | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[MoiraiPrediction], int]:
    """
    List predictions with filtering and pagination.

    Returns:
        Tuple of (predictions list, total count)
    """
    query = select(MoiraiPrediction)

    # Apply filters
    if risk_level:
        query = query.where(MoiraiPrediction.risk_level == risk_level)
    if point_id:
        query = query.where(MoiraiPrediction.point_id == point_id)
    if equipment_id:
        query = query.where(MoiraiPrediction.equipment_id == equipment_id)
    if status:
        query = query.where(MoiraiPrediction.status == status)

    # Order by newest first
    query = query.order_by(MoiraiPrediction.created_at.desc())

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await session.execute(query)
    predictions = list(result.scalars().all())

    return predictions, total


async def update_prediction_status(
    session: AsyncSession,
    prediction_id: UUID,
    status: PredictionStatus,
    acknowledged_by_id: UUID | None = None,
) -> MoiraiPrediction | None:
    """Update a prediction's status."""
    prediction = await get_prediction_by_id(session, prediction_id)
    if not prediction:
        return None

    # Store the string value
    status_value = status.value if hasattr(status, 'value') else status
    prediction.status = status_value
    if status_value in (PredictionStatus.CONFIRMED.value, PredictionStatus.DISMISSED.value):
        prediction.acknowledged_at = datetime.utcnow()
        prediction.acknowledged_by_id = acknowledged_by_id

    await session.flush()
    await session.refresh(prediction)

    return prediction


async def get_latest_prediction_for_point(
    session: AsyncSession,
    point_id: UUID,
) -> MoiraiPrediction | None:
    """Get the most recent prediction for a point."""
    query = (
        select(MoiraiPrediction)
        .where(MoiraiPrediction.point_id == point_id)
        .order_by(MoiraiPrediction.created_at.desc())
        .limit(1)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_risk_counts(
    session: AsyncSession,
) -> dict[str, int]:
    """Get count of predictions by risk level (pending status only)."""
    query = (
        select(MoiraiPrediction.risk_level, func.count())
        .where(MoiraiPrediction.status == PredictionStatus.PENDING.value)
        .group_by(MoiraiPrediction.risk_level)
    )
    result = await session.execute(query)
    # risk_level is stored as string in DB
    counts = {row[0].lower(): row[1] for row in result.fetchall()}

    return {
        "high": counts.get("high", 0),
        "medium": counts.get("medium", 0),
        "low": counts.get("low", 0),
    }


async def get_recent_predictions(
    session: AsyncSession,
    limit: int = 10,
) -> list[MoiraiPrediction]:
    """Get most recent predictions."""
    query = (
        select(MoiraiPrediction)
        .order_by(MoiraiPrediction.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_high_risk_points(
    session: AsyncSession,
    limit: int = 10,
) -> list[MoiraiPrediction]:
    """Get high-risk predictions with pending status."""
    query = (
        select(MoiraiPrediction)
        .where(MoiraiPrediction.risk_level == RiskLevel.HIGH.value)
        .where(MoiraiPrediction.status == PredictionStatus.PENDING.value)
        .order_by(MoiraiPrediction.confidence_score.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    return list(result.scalars().all())
