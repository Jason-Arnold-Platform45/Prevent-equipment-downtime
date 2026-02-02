"""
Risk classification service for Moirai predictions.

Classifies predictions into risk levels based on forecast patterns
and calculates confidence scores.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np

from src.lib.logging import get_logger
from src.models.prediction import RiskLevel

logger = get_logger(__name__)


@dataclass
class RiskClassification:
    """Result of risk classification."""

    risk_level: RiskLevel
    confidence_score: float  # 0-100
    predicted_failure_start: datetime | None
    predicted_failure_end: datetime | None
    anomaly_indices: list[int]


def classify_risk(
    historical_values: np.ndarray,
    forecast_mean: np.ndarray,
    forecast_std: np.ndarray,
    context_end: datetime,
    hours_per_step: float = 1.0,
) -> RiskClassification:
    """
    Classify risk level based on forecast patterns.

    Risk Classification Logic:
    - HIGH: Confidence >= 75% AND predicted failure within 7 days
    - MEDIUM: Confidence >= 50% OR predicted failure within 30 days
    - LOW: All other cases

    Confidence is based on:
    - Deviation from historical mean
    - Forecast uncertainty (std)
    - Trend direction and magnitude

    Args:
        historical_values: Historical sensor readings
        forecast_mean: Mean forecast values from Moirai
        forecast_std: Standard deviation of forecast
        context_end: End timestamp of the context window
        hours_per_step: Hours between each forecast step

    Returns:
        RiskClassification with level, confidence, and failure window
    """
    if len(forecast_mean) == 0:
        return RiskClassification(
            risk_level=RiskLevel.LOW,
            confidence_score=0.0,
            predicted_failure_start=None,
            predicted_failure_end=None,
            anomaly_indices=[],
        )

    # Calculate historical statistics
    hist_mean = np.mean(historical_values)
    hist_std = np.std(historical_values)

    # Avoid division by zero
    if hist_std < 1e-6:
        hist_std = np.abs(hist_mean) * 0.1 if hist_mean != 0 else 1.0

    # Find anomalous forecast points (beyond 2 std from historical mean)
    z_scores = np.abs((forecast_mean - hist_mean) / hist_std)
    anomaly_threshold = 2.0
    anomaly_mask = z_scores > anomaly_threshold
    anomaly_indices = np.where(anomaly_mask)[0].tolist()

    # Calculate trend
    if len(forecast_mean) >= 2:
        trend = (forecast_mean[-1] - forecast_mean[0]) / len(forecast_mean)
        trend_z = abs(trend) / hist_std
    else:
        trend = 0
        trend_z = 0

    # Calculate confidence score components
    # 1. Anomaly severity (how far beyond normal)
    max_z_score = np.max(z_scores) if len(z_scores) > 0 else 0
    anomaly_confidence = min(100, max_z_score * 25)  # Scale: z=4 -> 100%

    # 2. Forecast certainty (inverse of uncertainty)
    mean_relative_std = np.mean(forecast_std) / (hist_std + 1e-6)
    certainty_confidence = max(0, 100 - mean_relative_std * 50)

    # 3. Trend strength
    trend_confidence = min(100, trend_z * 30)

    # Combined confidence (weighted average)
    confidence_score = (
        anomaly_confidence * 0.5 + certainty_confidence * 0.3 + trend_confidence * 0.2
    )
    confidence_score = round(min(100, max(0, confidence_score)), 2)

    # Determine failure window if anomalies detected
    predicted_failure_start = None
    predicted_failure_end = None

    if len(anomaly_indices) > 0:
        first_anomaly_idx = anomaly_indices[0]
        last_anomaly_idx = anomaly_indices[-1]

        predicted_failure_start = context_end + timedelta(
            hours=first_anomaly_idx * hours_per_step
        )
        predicted_failure_end = context_end + timedelta(
            hours=(last_anomaly_idx + 1) * hours_per_step
        )

    # Calculate days to potential failure
    days_to_failure = None
    if predicted_failure_start:
        days_to_failure = (predicted_failure_start - context_end).days

    # Classify risk level
    if confidence_score >= 75 and days_to_failure is not None and days_to_failure <= 7:
        risk_level = RiskLevel.HIGH
    elif (
        confidence_score >= 50
        or (days_to_failure is not None and days_to_failure <= 30)
    ):
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    logger.debug(
        f"Risk classification: {risk_level.value}, confidence: {confidence_score}",
        extra={
            "extra_fields": {
                "max_z_score": float(max_z_score),
                "anomaly_count": len(anomaly_indices),
                "days_to_failure": days_to_failure,
            }
        },
    )

    return RiskClassification(
        risk_level=risk_level,
        confidence_score=confidence_score,
        predicted_failure_start=predicted_failure_start,
        predicted_failure_end=predicted_failure_end,
        anomaly_indices=anomaly_indices,
    )
