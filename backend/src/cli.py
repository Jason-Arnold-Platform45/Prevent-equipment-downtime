"""
CLI for Moirai Sensor Failure Prediction.

Usage:
    python -m src.cli predict --point-id <uuid>
    python -m src.cli predict-all [--min-readings 5]
    python -m src.cli list-points [--with-predictions]
"""

import asyncio
from uuid import UUID

import typer
from rich.console import Console
from rich.table import Table

from src.lib.config import get_settings
from src.lib.logging import get_logger
from src.services.database import init_database, close_database, get_session
from src.services.model_cache import load_moirai_model, get_moirai_model
from src.services.prediction import run_prediction_for_point
from src.services.sensor_data import (
    get_points_with_min_readings,
    list_points_paginated,
    get_point_readings_count,
)

logger = get_logger(__name__)
console = Console()
app = typer.Typer(
    name="moirai",
    help="Moirai Sensor Failure Prediction CLI",
    add_completion=False,
)


async def _init() -> None:
    """Initialize database and model."""
    await init_database()
    await load_moirai_model()


async def _cleanup() -> None:
    """Cleanup resources."""
    await close_database()


@app.command()
def predict(
    point_id: str = typer.Argument(..., help="UUID of the monitoring point"),
) -> None:
    """Run prediction for a single monitoring point."""

    async def _run():
        await _init()
        model = get_moirai_model()

        try:
            point_uuid = UUID(point_id)
        except ValueError:
            console.print(f"[red]Invalid UUID: {point_id}[/red]")
            raise typer.Exit(1)

        async for session in get_session():
            try:
                console.print(f"Running prediction for point [cyan]{point_id}[/cyan]...")
                prediction = await run_prediction_for_point(session, point_uuid, model)
                await session.commit()

                console.print(f"\n[green]Prediction created successfully![/green]")
                console.print(f"  ID: {prediction.id}")
                console.print(f"  Risk Level: [bold]{prediction.risk_level}[/bold]")
                console.print(f"  Confidence: {prediction.confidence_score}%")
                if prediction.predicted_failure_start:
                    console.print(f"  Predicted Failure: {prediction.predicted_failure_start}")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)
            break

        await _cleanup()

    asyncio.run(_run())


@app.command("predict-all")
def predict_all(
    min_readings: int = typer.Option(5, help="Minimum readings required for prediction"),
    dry_run: bool = typer.Option(False, help="Show eligible points without running predictions"),
) -> None:
    """Run predictions for all eligible monitoring points."""

    async def _run():
        await _init()
        model = get_moirai_model()

        async for session in get_session():
            # Get eligible points
            eligible_points = await get_points_with_min_readings(session, min_readings)
            console.print(f"Found [cyan]{len(eligible_points)}[/cyan] points with >= {min_readings} readings")

            if dry_run:
                for point_id in eligible_points:
                    console.print(f"  - {point_id}")
                return

            if not eligible_points:
                console.print("[yellow]No eligible points found.[/yellow]")
                return

            # Run predictions
            success_count = 0
            error_count = 0

            with console.status("[bold green]Running predictions...") as status:
                for i, point_id in enumerate(eligible_points, 1):
                    status.update(f"Processing {i}/{len(eligible_points)}: {point_id}")
                    try:
                        prediction = await run_prediction_for_point(session, point_id, model)
                        success_count += 1
                        console.print(f"  [green]OK[/green] {point_id}: {prediction.risk_level}")
                    except Exception as e:
                        error_count += 1
                        console.print(f"  [red]FAIL[/red] {point_id}: {e}")

            await session.commit()
            console.print(f"\n[bold]Complete![/bold] Success: {success_count}, Errors: {error_count}")
            break

        await _cleanup()

    asyncio.run(_run())


@app.command("list-points")
def list_points(
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(20, help="Items per page"),
    with_predictions: bool = typer.Option(False, help="Only show points with predictions"),
) -> None:
    """List monitoring points."""

    async def _run():
        await _init()

        async for session in get_session():
            has_prediction = True if with_predictions else None
            points, total = await list_points_paginated(
                session, page=page, page_size=page_size, has_prediction=has_prediction
            )

            table = Table(title=f"Monitoring Points (Page {page}, Total: {total})")
            table.add_column("ID", style="cyan")
            table.add_column("Name")
            table.add_column("Readings", justify="right")

            for point in points:
                readings_count = await get_point_readings_count(session, point.id)
                table.add_row(
                    str(point.id),
                    point.name or "(unnamed)",
                    str(readings_count),
                )

            console.print(table)
            break

        await _cleanup()

    asyncio.run(_run())


@app.command()
def health() -> None:
    """Check system health."""

    async def _run():
        settings = get_settings()
        console.print(f"[bold]Moirai Sensor Prediction CLI[/bold]")
        console.print(f"Environment: {settings.environment}")
        console.print(f"Model: {settings.moirai_model}")

        try:
            await init_database()
            console.print("[green]OK[/green] Database: Connected")
        except Exception as e:
            console.print(f"[red]FAIL[/red] Database: {e}")

        try:
            await load_moirai_model()
            model = get_moirai_model()
            if model:
                console.print("[green]OK[/green] Moirai Model: Loaded")
            else:
                console.print("[yellow]WARN[/yellow] Moirai Model: Not loaded (mock inference enabled)")
        except Exception as e:
            console.print(f"[red]FAIL[/red] Moirai Model: {e}")

        await _cleanup()

    asyncio.run(_run())


if __name__ == "__main__":
    app()
