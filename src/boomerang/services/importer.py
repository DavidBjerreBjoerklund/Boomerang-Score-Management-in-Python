"""Data import utilities for events."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from sqlmodel import Session

from ..domain.rules import Discipline, get_discipline
from ..models import Event
from ..repositories import get_or_create_athlete, upsert_result
from .scoring import score_event


@dataclass
class ResultRecord:
    """Structured representation of a row imported for an event."""

    name: str
    start_number: int | None
    score: Decimal
    raw_score_text: str


class ResultImporter:
    """Import structured rows into the database and trigger scoring."""

    def __init__(self, session: Session, event: Event, discipline: Discipline):
        self.session = session
        self.event = event
        self.discipline = discipline

    def import_records(self, records: Sequence[ResultRecord]) -> int:
        """Persist the provided records and recalculate event rankings."""

        processed = 0
        for record in records:
            given_name, family_name = split_full_name(record.name)
            athlete = get_or_create_athlete(self.session, given_name=given_name, family_name=family_name)
            upsert_result(
                self.session,
                event_id=self.event.id,
                athlete_id=athlete.id,
                start_number=record.start_number,
                raw_score=record.score,
                raw_score_text=record.raw_score_text,
            )
            processed += 1
        self.session.flush()
        score_event(self.session, self.event)
        self.session.commit()
        return processed


def split_full_name(full_name: str) -> tuple[str, str]:
    """Split a full name into given and family components."""

    parts = [part for part in full_name.strip().split() if part]
    if not parts:
        return "Unknown", "Competitor"
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def parse_score(value: str) -> Decimal:
    """Convert a textual score into a Decimal value."""

    cleaned = value.strip().replace(",", ".")
    if not cleaned:
        raise ValueError("Score column cannot be empty.")
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Invalid numeric score '{value}'.") from exc


def parse_start_number(value: str | None) -> int | None:
    """Convert a start number column to an integer."""

    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return int(stripped)
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Invalid start number '{value}'.") from exc


def read_csv(path: Path) -> list[ResultRecord]:
    """Read a CSV file in the historical format bundled with the repository."""

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        records: list[ResultRecord] = []
        for row in reader:
            participant = (row.get("Participant") or row.get("Name") or "").strip()
            if not participant:
                continue
            start_number = parse_start_number(row.get("Start-Nbr.") or row.get("Start"))
            score_text = (row.get("Score") or row.get("Result") or "").strip()
            if not score_text:
                raise ValueError(f"CSV is missing a score entry for participant '{participant}'.")
            score = parse_score(score_text)
            records.append(ResultRecord(participant, start_number, score, score_text))
    return records


def import_event_from_csv(
    session: Session,
    *,
    event: Event,
    discipline_slug: str,
    csv_path: Path,
) -> int:
    """Import a CSV file and recalculate the event standings."""

    discipline = get_discipline(discipline_slug)
    importer = ResultImporter(session, event, discipline)
    records = read_csv(csv_path)
    return importer.import_records(records)


__all__ = [
    "ResultImporter",
    "ResultRecord",
    "import_event_from_csv",
    "parse_score",
    "read_csv",
    "split_full_name",
]
