"""Command-line interface for tournament administrators."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from .config import get_settings
from .database import init_db, session_scope
from .domain.rules import DisciplineNotFoundError, get_discipline, list_disciplines
from .repositories import create_event, get_event
from .services.importer import import_event_from_csv

app = typer.Typer(help="Manage IFBA boomerang tournament data.")


@app.command("init-db")
def init_db_command() -> None:
    """Create database tables if they do not already exist."""

    init_db()
    typer.echo(f"Database initialised at {get_settings().database_url}")


@app.command("disciplines")
def disciplines_command() -> None:
    """List supported disciplines and their scoring direction."""

    for discipline in list_disciplines():
        typer.echo(f"{discipline.slug:12} -> {discipline.name} ({discipline.score_direction.value})")


@app.command("create-event")
def create_event_command(
    name: str = typer.Argument(..., help="Display name of the event."),
    discipline: str = typer.Argument(..., help="Discipline slug, e.g. 'accuracy'."),
    start_date: Optional[date] = typer.Option(None, help="Event start date (YYYY-MM-DD)."),
) -> None:
    """Create a new event record."""

    init_db()
    try:
        discipline_meta = get_discipline(discipline)
    except DisciplineNotFoundError as exc:  # pragma: no cover - user input validation
        raise typer.BadParameter(str(exc)) from exc

    with session_scope() as session:
        try:
            event = create_event(session, name=name, discipline=discipline_meta.slug, start_date=start_date)
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc
        session.commit()
        typer.echo(f"Created event #{event.id}: {event.name} ({discipline_meta.name})")


@app.command("import-csv")
def import_csv_command(
    csv_path: Path = typer.Argument(..., exists=True, readable=True, help="CSV file to import."),
    discipline: str = typer.Option(..., "--discipline", "-d", help="Discipline slug."),
    event_id: Optional[int] = typer.Option(None, "--event-id", help="Existing event identifier."),
    event_name: Optional[str] = typer.Option(None, "--name", help="Create a new event with this name."),
    start_date: Optional[date] = typer.Option(None, help="Optional start date when creating a new event."),
) -> None:
    """Import scores from a CSV file into an event."""

    if not event_id and not event_name:
        raise typer.BadParameter("Provide either --event-id or --name to determine the target event.")

    init_db()
    try:
        discipline_meta = get_discipline(discipline)
    except DisciplineNotFoundError as exc:  # pragma: no cover - user input validation
        raise typer.BadParameter(str(exc)) from exc

    with session_scope() as session:
        if event_id is not None:
            event = get_event(session, event_id)
            if not event:
                raise typer.BadParameter(f"Event with id {event_id} does not exist.")
        else:
            try:
                event = create_event(session, name=event_name, discipline=discipline_meta.slug, start_date=start_date)
            except ValueError as exc:
                raise typer.BadParameter(str(exc)) from exc
            session.commit()

        processed = import_event_from_csv(session, event=event, discipline_slug=discipline_meta.slug, csv_path=csv_path)
        session.commit()
        typer.echo(f"Imported {processed} results into event #{event.id} ({event.name}).")


if __name__ == "__main__":
    app()
