"""Scoring logic mirroring IFBA ranking rules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Generic, Sequence, TypeVar

from sqlmodel import Session, select

from ..domain import rules
from ..domain.rules import ScoreDirection
from ..models import Event, Result

T = TypeVar("T")


@dataclass
class RankedItem(Generic[T]):
    """Container representing a ranked result and associated metadata."""

    item: T
    placing: int
    points: Decimal


ScoreGetter = Callable[[T], Decimal]


def rank_items(
    items: Sequence[T],
    *,
    score_getter: ScoreGetter,
    direction: ScoreDirection,
) -> list[RankedItem[T]]:
    """Rank items according to the specified score direction."""

    if not items:
        return []

    reverse = direction is ScoreDirection.HIGHER_IS_BETTER
    sorted_items = sorted(items, key=score_getter, reverse=reverse)

    ranked: list[RankedItem[T]] = []
    index = 0
    while index < len(sorted_items):
        current_score = score_getter(sorted_items[index])
        if current_score is None:  # type: ignore[unreachable]
            raise ValueError("Results cannot be ranked without a numeric score.")
        group: list[T] = [sorted_items[index]]
        lookahead = index + 1
        while lookahead < len(sorted_items) and score_getter(sorted_items[lookahead]) == current_score:
            group.append(sorted_items[lookahead])
            lookahead += 1

        start_rank = index + 1
        group_size = lookahead - index
        end_rank = start_rank + group_size - 1
        points = (Decimal(start_rank + end_rank) / Decimal(2)).quantize(Decimal("0.001"))

        for entry in group:
            ranked.append(RankedItem(entry, placing=start_rank, points=points.normalize()))

        index = lookahead

    return ranked


def score_event(session: Session, event: Event) -> list[Result]:
    """Recalculate placing and points for all results in an event."""

    discipline = rules.get_discipline(event.discipline)
    statement = select(Result).where(Result.event_id == event.id)
    results = list(session.exec(statement))

    ranked = rank_items(results, score_getter=lambda result: result.raw_score, direction=discipline.score_direction)
    for entry in ranked:
        result = entry.item
        result.placing = entry.placing
        result.points = entry.points
        session.add(result)

    return [entry.item for entry in ranked]


__all__ = ["RankedItem", "rank_items", "score_event"]
