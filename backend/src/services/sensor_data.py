"""
Service for fetching sensor data from EAIMMS database.
"""

from datetime import datetime
from uuid import UUID

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.lib.logging import get_logger
from src.models.existing import MonitoringPoint, MonitoringTask, MonitoringTaskResult

logger = get_logger(__name__)


async def get_point_readings(
    session: AsyncSession,
    point_id: UUID,
    limit: int | None = None,
) -> pd.DataFrame:
    """
    Fetch sensor readings for a monitoring point.

    Args:
        session: Database session
        point_id: Monitoring point UUID
        limit: Maximum number of readings to return (None for all)

    Returns:
        DataFrame with columns: timestamp, value
    """
    # Join through MonitoringTask to get results for a point
    query = (
        select(
            MonitoringTaskResult.captured_at,
            MonitoringTaskResult.data,
        )
        .join(MonitoringTask, MonitoringTaskResult.task_id == MonitoringTask.id)
        .where(MonitoringTask.point_id == point_id)
        .order_by(MonitoringTaskResult.captured_at.asc())
    )

    if limit:
        query = query.limit(limit)

    result = await session.execute(query)
    rows = result.fetchall()

    if not rows:
        return pd.DataFrame(columns=["timestamp", "value"])

    # Extract values from JSON data field
    data = []
    for captured_at, json_data in rows:
        if json_data and isinstance(json_data, dict):
            # Extract numeric value from JSON - try common field names
            value = None
            for key in ["value", "reading", "measurement", "data"]:
                if key in json_data:
                    try:
                        value = float(json_data[key])
                        break
                    except (TypeError, ValueError):
                        continue

            # If no standard key found, try first numeric value
            if value is None:
                for v in json_data.values():
                    try:
                        value = float(v)
                        break
                    except (TypeError, ValueError):
                        continue

            if value is not None:
                data.append({"timestamp": captured_at, "value": value})

    df = pd.DataFrame(data)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

    return df


async def get_point_readings_count(
    session: AsyncSession,
    point_id: UUID,
) -> int:
    """Get the count of readings for a monitoring point."""
    # Join through MonitoringTask to count results for a point
    query = (
        select(func.count())
        .select_from(MonitoringTaskResult)
        .join(MonitoringTask, MonitoringTaskResult.task_id == MonitoringTask.id)
        .where(MonitoringTask.point_id == point_id)
    )
    result = await session.execute(query)
    return result.scalar() or 0


async def get_point_with_equipment(
    session: AsyncSession,
    point_id: UUID,
) -> MonitoringPoint | None:
    """Get a monitoring point with its equipment relationship."""
    query = (
        select(MonitoringPoint)
        .where(MonitoringPoint.id == point_id)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_points_with_min_readings(
    session: AsyncSession,
    min_readings: int = 5,
) -> list[UUID]:
    """
    Get all monitoring points with at least min_readings.

    Args:
        session: Database session
        min_readings: Minimum number of readings required

    Returns:
        List of point IDs that have sufficient data
    """
    # Join through MonitoringTask to group by point
    query = (
        select(MonitoringTask.point_id)
        .join(MonitoringTaskResult, MonitoringTaskResult.task_id == MonitoringTask.id)
        .group_by(MonitoringTask.point_id)
        .having(func.count() >= min_readings)
    )
    result = await session.execute(query)
    return [row[0] for row in result.fetchall()]


async def get_latest_reading(
    session: AsyncSession,
    point_id: UUID,
) -> tuple[float, datetime] | None:
    """Get the most recent reading for a point."""
    # Join through MonitoringTask to get latest result for a point
    query = (
        select(
            MonitoringTaskResult.data,
            MonitoringTaskResult.captured_at,
        )
        .join(MonitoringTask, MonitoringTaskResult.task_id == MonitoringTask.id)
        .where(MonitoringTask.point_id == point_id)
        .order_by(MonitoringTaskResult.captured_at.desc())
        .limit(1)
    )
    result = await session.execute(query)
    row = result.fetchone()

    if not row:
        return None

    json_data, captured_at = row
    if not json_data or not isinstance(json_data, dict):
        return None

    # Extract value
    value = None
    for key in ["value", "reading", "measurement", "data"]:
        if key in json_data:
            try:
                value = float(json_data[key])
                break
            except (TypeError, ValueError):
                continue

    if value is None:
        for v in json_data.values():
            try:
                value = float(v)
                break
            except (TypeError, ValueError):
                continue

    if value is not None:
        return value, captured_at

    return None


async def list_points_paginated(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    has_prediction: bool | None = None,
) -> tuple[list[MonitoringPoint], int]:
    """
    List monitoring points with pagination.

    Args:
        session: Database session
        page: Page number (1-indexed)
        page_size: Items per page
        has_prediction: Filter by whether point has predictions

    Returns:
        Tuple of (points list, total count)
    """
    from src.models.prediction import MoiraiPrediction

    # Base query
    query = select(MonitoringPoint)

    # Apply filter if specified
    if has_prediction is not None:
        subquery = select(MoiraiPrediction.point_id).distinct()
        if has_prediction:
            query = query.where(MonitoringPoint.id.in_(subquery))
        else:
            query = query.where(MonitoringPoint.id.notin_(subquery))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await session.execute(query)
    points = list(result.scalars().all())

    return points, total
