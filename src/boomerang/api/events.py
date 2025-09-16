"""API router that exposes event and result management endpoints."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..domain.rules import DisciplineNotFoundError, get_discipline
from ..models import Event, Result
from ..repositories import create_event, get_event, list_event_results
from ..services.importer import ResultImporter, ResultRecord
from . import schemas

router = APIRouter(prefix="/events", tags=["events"])


def _serialize_event(event: Event) -> schemas.EventRead:
    discipline = get_discipline(event.discipline)
    return schemas.EventRead(
        id=event.id,
        name=event.name,
        discipline=event.discipline,
        start_date=event.start_date,
        created_at=event.created_at,
        discipline_name=discipline.name,
        score_direction=discipline.score_direction,
    )


def _serialize_result(result: Result) -> schemas.ResultRead:
    athlete_name = result.athlete.full_name if result.athlete else "Unknown athlete"
    return schemas.ResultRead(
        id=result.id,
        athlete_name=athlete_name,
        start_number=result.start_number,
        score=result.raw_score,
        placing=result.placing,
        points=result.points,
    )


@router.post("", response_model=schemas.EventRead, status_code=status.HTTP_201_CREATED)
def create_event_endpoint(
    payload: schemas.EventCreate,
    session: Session = Depends(get_session),
) -> schemas.EventRead:
    """Create a new event in the database."""

    try:
        discipline = get_discipline(payload.discipline)
    except DisciplineNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    try:
        event = create_event(session, name=payload.name, discipline=discipline.slug, start_date=payload.start_date)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    session.commit()
    session.refresh(event)
    return _serialize_event(event)


@router.get("", response_model=list[schemas.EventRead])
def list_events_endpoint(session: Session = Depends(get_session)) -> list[schemas.EventRead]:
    """Return all events in creation order."""

    events = session.exec(select(Event).order_by(Event.created_at)).all()
    return [_serialize_event(event) for event in events]


@router.get("/{event_id}", response_model=schemas.EventRead)
def get_event_endpoint(event_id: int, session: Session = Depends(get_session)) -> schemas.EventRead:
    """Return information about a single event."""

    event = get_event(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")
    return _serialize_event(event)


@router.get("/{event_id}/results", response_model=list[schemas.ResultRead])
def get_event_results_endpoint(event_id: int, session: Session = Depends(get_session)) -> list[schemas.ResultRead]:
    """Return ranked results for the specified event."""

    event = get_event(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    results = list_event_results(session, event_id)
    return [_serialize_result(result) for result in results]


@router.post("/{event_id}/results", response_model=list[schemas.ResultRead], status_code=status.HTTP_201_CREATED)
def import_results_endpoint(
    event_id: int,
    payload: list[schemas.ResultCreate],
    session: Session = Depends(get_session),
) -> list[schemas.ResultRead]:
    """Import a batch of results, overwriting existing scores when necessary."""

    event = get_event(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    discipline = get_discipline(event.discipline)
    importer = ResultImporter(session, event, discipline)
    records = [
        ResultRecord(
            name=item.athlete_name,
            start_number=item.start_number,
            score=Decimal(item.score),
            raw_score_text=str(item.score),
        )
        for item in payload
    ]
    importer.import_records(records)

    results = list_event_results(session, event_id)
    return [_serialize_result(result) for result in results]


__all__ = ["router"]
