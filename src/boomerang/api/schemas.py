"""Pydantic models used by the public HTTP API."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from ..domain.rules import Discipline, ScoreDirection


class DisciplineRead(BaseModel):
    """Representation of an IFBA discipline."""

    slug: str
    name: str
    score_direction: ScoreDirection
    description: str | None = None
    rule_reference: str | None = None

    @classmethod
    def from_domain(cls, discipline: Discipline) -> "DisciplineRead":
        return cls(**discipline.__dict__)


class EventCreate(BaseModel):
    """Payload for creating a new event."""

    name: str
    discipline: str = Field(description="Discipline slug, e.g. 'accuracy'.")
    start_date: date | None = None


class EventRead(BaseModel):
    """Event representation returned to clients."""

    id: int
    name: str
    discipline: str
    start_date: date | None
    created_at: datetime

    discipline_name: str
    score_direction: ScoreDirection


class ResultCreate(BaseModel):
    """Payload representing a competitor's raw result."""

    athlete_name: str
    start_number: int | None = None
    score: Decimal


class ResultRead(BaseModel):
    """Result representation returned to API clients."""

    id: int
    athlete_name: str
    start_number: int | None
    score: Decimal
    placing: int | None
    points: Decimal | None


__all__ = [
    "DisciplineRead",
    "EventCreate",
    "EventRead",
    "ResultCreate",
    "ResultRead",
]
