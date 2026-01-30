"""
MoiraiPrediction model for storing failure predictions.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.services.database import Base


class RiskLevel(str, Enum):
    """Risk level classification for predictions."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PredictionStatus(str, Enum):
    """Status of a prediction."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"


class MoiraiPrediction(Base):
    """Moirai model failure prediction."""

    __tablename__ = "moirai_predictions"
    __table_args__ = (
        Index("idx_moirai_predictions_point_created", "point_id", "created_at"),
        Index("idx_moirai_predictions_risk_created", "risk_level", "created_at"),
        Index("idx_moirai_predictions_equipment_risk", "equipment_id", "risk_level"),
        Index("idx_moirai_predictions_status_created", "status", "created_at"),
        {"extend_existing": True},
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    point_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("monitoring_plans_points.id"),
        nullable=False,
        index=True
    )
    equipment_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("equipments_equipment.id"),
        nullable=True
    )

    # Prediction results
    risk_level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )
    confidence_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    predicted_failure_start: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    predicted_failure_end: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Analysis context
    context_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    context_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    readings_analyzed: Mapped[int] = mapped_column(Integer, nullable=False)

    # Model output
    forecast_values: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Review status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=PredictionStatus.PENDING.value
    )
    acknowledged_by_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    point: Mapped["MonitoringPoint"] = relationship(  # noqa: F821
        "MonitoringPoint",
        foreign_keys=[point_id],
        lazy="joined"
    )
    equipment: Mapped["Equipment | None"] = relationship(  # noqa: F821
        "Equipment",
        foreign_keys=[equipment_id],
        lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<MoiraiPrediction(id={self.id}, point_id={self.point_id}, "
            f"risk_level={self.risk_level}, confidence={self.confidence_score})>"
        )

    @property
    def is_high_risk(self) -> bool:
        """Check if prediction is high risk."""
        return self.risk_level == RiskLevel.HIGH.value

    @property
    def is_pending(self) -> bool:
        """Check if prediction is pending review."""
        return self.status == PredictionStatus.PENDING.value


# Import for relationship resolution
from src.models.existing import Equipment, MonitoringPoint  # noqa: E402, F401
