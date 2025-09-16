"""Database models used by the scoring services."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.types import Numeric
from sqlmodel import Field, Relationship, SQLModel


class Athlete(SQLModel, table=True):
    """Athlete participating in one or more events."""

    __tablename__ = "athlete"
    __table_args__ = (UniqueConstraint("full_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    given_name: str = Field(max_length=100)
    family_name: str = Field(max_length=150, default="")
    full_name: str = Field(max_length=255, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    results: list["Result"] = Relationship(back_populates="athlete")


class Event(SQLModel, table=True):
    """A competitive event for a particular discipline."""

    __tablename__ = "event"
    __table_args__ = (UniqueConstraint("name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    discipline: str = Field(max_length=50, index=True)
    start_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    results: list["Result"] = Relationship(back_populates="event")


class Result(SQLModel, table=True):
    """Result for a competitor within a specific event."""

    __tablename__ = "result"
    __table_args__ = (UniqueConstraint("event_id", "athlete_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    athlete_id: int = Field(foreign_key="athlete.id", index=True)
    start_number: Optional[int] = Field(default=None, index=True)
    raw_score: Decimal = Field(sa_column=Column(Numeric(12, 3)))
    raw_score_text: str = Field(default="", max_length=50)
    placing: Optional[int] = Field(default=None, index=True)
    points: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 3)))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    athlete: Optional["Athlete"] = Relationship(back_populates="results")
    event: Optional["Event"] = Relationship(back_populates="results")


__all__ = ["Athlete", "Event", "Result"]
