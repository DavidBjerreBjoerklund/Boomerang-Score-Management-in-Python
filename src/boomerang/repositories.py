"""Data-access helpers wrapping SQLModel queries."""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .models import Athlete, Event, Result


def get_or_create_athlete(session: Session, *, given_name: str, family_name: str) -> Athlete:
    """Return an existing athlete by name or create a new one."""

    full_name = " ".join(part for part in [given_name.strip(), family_name.strip()] if part)
    statement = select(Athlete).where(Athlete.full_name == full_name)
    athlete = session.exec(statement).first()
    if athlete:
        return athlete

    athlete = Athlete(given_name=given_name.strip(), family_name=family_name.strip(), full_name=full_name)
    session.add(athlete)
    session.flush()
    session.refresh(athlete)
    return athlete


def find_event_by_name(session: Session, name: str) -> Optional[Event]:
    """Retrieve an event by its unique name."""

    statement = select(Event).where(Event.name == name)
    return session.exec(statement).first()


def create_event(session: Session, *, name: str, discipline: str, start_date: date | None = None) -> Event:
    """Create a new event, raising if the name already exists."""

    existing = find_event_by_name(session, name)
    if existing:
        raise ValueError(f"An event named '{name}' already exists.")

    event = Event(name=name, discipline=discipline, start_date=start_date)
    session.add(event)
    session.flush()
    session.refresh(event)
    return event


def get_event(session: Session, event_id: int) -> Optional[Event]:
    """Return an event by primary key."""

    return session.get(Event, event_id)


def upsert_result(
    session: Session,
    *,
    event_id: int,
    athlete_id: int,
    start_number: int | None,
    raw_score,
    raw_score_text: str,
) -> Result:
    """Insert or update a competitor's result for the given event."""

    statement = select(Result).where(Result.event_id == event_id, Result.athlete_id == athlete_id)
    result = session.exec(statement).first()
    if result:
        result.start_number = start_number
        result.raw_score = raw_score
        result.raw_score_text = raw_score_text
        session.add(result)
        return result

    result = Result(
        event_id=event_id,
        athlete_id=athlete_id,
        start_number=start_number,
        raw_score=raw_score,
        raw_score_text=raw_score_text,
    )
    session.add(result)
    session.flush()
    session.refresh(result)
    return result


def list_event_results(session: Session, event_id: int) -> list[Result]:
    """Return all results for an event sorted by placing then score."""

    statement = (
        select(Result)
        .where(Result.event_id == event_id)
        .options(selectinload(Result.athlete))
    )
    records = list(session.exec(statement))
    return sorted(
        records,
        key=lambda result: (result.placing is None, result.placing or 0, result.points or 0, result.raw_score),
    )


__all__ = [
    "create_event",
    "find_event_by_name",
    "get_event",
    "get_or_create_athlete",
    "list_event_results",
    "upsert_result",
]
