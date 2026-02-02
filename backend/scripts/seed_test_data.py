"""
Seed test data for local development.

This script creates sample monitoring points and readings in the database
for testing the prediction API without relying on real EAIMMS data.

Usage:
    python -m scripts.seed_test_data [--points 5] [--readings-per-point 50]
"""

import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4

import typer
from rich.console import Console

# Add parent directory to path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.database import init_database, close_database, async_session_factory
from src.models.existing import MonitoringPoint, MonitoringTask, MonitoringTaskResult, MonitoringPlan

console = Console()
app = typer.Typer()


def generate_sensor_readings(
    num_readings: int,
    base_value: float = 100.0,
    noise_std: float = 5.0,
    trend: float = 0.0,
    anomaly_probability: float = 0.05,
) -> list[tuple[datetime, float]]:
    """Generate synthetic sensor readings with optional anomalies."""
    readings = []
    start_time = datetime.utcnow() - timedelta(hours=num_readings)

    for i in range(num_readings):
        timestamp = start_time + timedelta(hours=i)

        # Base value with trend and noise
        value = base_value + (trend * i) + random.gauss(0, noise_std)

        # Occasionally add anomalies
        if random.random() < anomaly_probability:
            value *= random.uniform(1.5, 2.0)  # Spike

        readings.append((timestamp, round(value, 2)))

    return readings


@app.command()
def seed(
    num_points: int = typer.Option(5, "--points", "-p", help="Number of monitoring points to create"),
    readings_per_point: int = typer.Option(50, "--readings", "-r", help="Readings per point"),
    clear_existing: bool = typer.Option(False, "--clear", "-c", help="Clear existing test data first"),
) -> None:
    """Seed test data for local development."""

    async def _run():
        await init_database()

        async with async_session_factory() as session:
            if clear_existing:
                console.print("[yellow]Clearing existing test data...[/yellow]")
                # Note: In a real scenario, you'd want to be more careful about
                # what data you delete. This is just for local testing.

            # Create a test monitoring plan
            plan = MonitoringPlan(
                id=uuid4(),
                created_at=datetime.utcnow(),
            )
            session.add(plan)

            console.print(f"Creating [cyan]{num_points}[/cyan] monitoring points...")

            for i in range(num_points):
                # Create monitoring point
                point = MonitoringPoint(
                    id=uuid4(),
                    name=f"Test Sensor {i + 1}",
                    plan_id=plan.id,
                    created_at=datetime.utcnow(),
                )
                session.add(point)

                # Create a task for this point
                task = MonitoringTask(
                    id=uuid4(),
                    label=f"Temperature Reading",
                    instructions="Record temperature sensor value",
                    type="numeric",
                    point_id=point.id,
                    created_at=datetime.utcnow(),
                )
                session.add(task)

                # Generate readings with different patterns
                patterns = [
                    {"base_value": 100, "noise_std": 5, "trend": 0, "anomaly_probability": 0.02},
                    {"base_value": 50, "noise_std": 10, "trend": 0.1, "anomaly_probability": 0.05},
                    {"base_value": 200, "noise_std": 20, "trend": -0.05, "anomaly_probability": 0.03},
                    {"base_value": 75, "noise_std": 8, "trend": 0.2, "anomaly_probability": 0.08},
                    {"base_value": 150, "noise_std": 15, "trend": 0, "anomaly_probability": 0.01},
                ]
                pattern = patterns[i % len(patterns)]

                readings = generate_sensor_readings(readings_per_point, **pattern)

                for timestamp, value in readings:
                    result = MonitoringTaskResult(
                        id=uuid4(),
                        data={"value": value},
                        captured_at=timestamp,
                        task_id=task.id,
                        created_at=timestamp,
                    )
                    session.add(result)

                console.print(f"  [green]✓[/green] {point.name}: {len(readings)} readings")

            await session.commit()
            console.print(f"\n[bold green]Successfully seeded {num_points} points with {readings_per_point} readings each![/bold green]")

        await close_database()

    asyncio.run(_run())


@app.command()
def stats() -> None:
    """Show statistics about existing data."""

    async def _run():
        await init_database()

        async with async_session_factory() as session:
            from sqlalchemy import func, select
            from src.models.existing import MonitoringPoint, MonitoringTaskResult
            from src.models.prediction import MoiraiPrediction

            # Count points
            points_count = (await session.execute(select(func.count(MonitoringPoint.id)))).scalar()

            # Count readings
            readings_count = (await session.execute(select(func.count(MonitoringTaskResult.id)))).scalar()

            # Count predictions
            predictions_count = (await session.execute(select(func.count(MoiraiPrediction.id)))).scalar()

            console.print("[bold]Database Statistics[/bold]")
            console.print(f"  Monitoring Points: {points_count}")
            console.print(f"  Task Results (Readings): {readings_count}")
            console.print(f"  Predictions: {predictions_count}")

        await close_database()

    asyncio.run(_run())


if __name__ == "__main__":
    app()
