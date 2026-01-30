"""
SQLAlchemy mappings for existing EAIMMS tables (read-only).

These models map to existing tables in the EAIMMS database.
They are used for reading sensor data, not for modifications.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.services.database import Base


class MonitoringPlan(Base):
    """Monitoring plan definition."""

    __tablename__ = "monitoring_plans_plans"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    points: Mapped[list["MonitoringPoint"]] = relationship(
        "MonitoringPoint", back_populates="plan"
    )


class MonitoringPoint(Base):
    """Monitoring point (sensor location) in EAIMMS."""

    __tablename__ = "monitoring_plans_points"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("monitoring_plans_plans.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    plan: Mapped["MonitoringPlan"] = relationship(
        "MonitoringPlan", back_populates="points"
    )
    tasks: Mapped[list["MonitoringTask"]] = relationship(
        "MonitoringTask", back_populates="point"
    )


class MonitoringTask(Base):
    """Monitoring task linked to a point."""

    __tablename__ = "monitoring_plans_tasks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    label: Mapped[str] = mapped_column(String(255), nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(100), nullable=True)
    task_attributes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)
    values: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)
    point_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("monitoring_plans_points.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    point: Mapped["MonitoringPoint"] = relationship(
        "MonitoringPoint", back_populates="tasks"
    )
    results: Mapped[list["MonitoringTaskResult"]] = relationship(
        "MonitoringTaskResult", back_populates="task"
    )


class MonitoringTaskResult(Base):
    """Individual sensor reading/measurement result."""

    __tablename__ = "monitoring_plans_task_results"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)
    comments: Mapped[str] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("monitoring_plans_tasks.id"),
        nullable=True
    )
    plan_result_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    task: Mapped["MonitoringTask"] = relationship(
        "MonitoringTask", back_populates="results"
    )

    @property
    def value(self) -> float | None:
        """Extract numeric value from data JSON."""
        if self.data and "value" in self.data:
            try:
                return float(self.data["value"])
            except (TypeError, ValueError):
                return None
        return None


class Equipment(Base):
    """Equipment/asset being monitored."""

    __tablename__ = "equipments_equipment"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=True)
    organisation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    division_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    equipment_type_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    mine_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class User(Base):
    """User reference for acknowledged_by relationships."""

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    # Only map fields we need for references
