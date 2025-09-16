"""Definitions for IFBA disciplines and scoring behaviour."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class ScoreDirection(str, Enum):
    """Possible score orderings for competitions."""

    HIGHER_IS_BETTER = "higher"
    LOWER_IS_BETTER = "lower"


@dataclass(frozen=True)
class Discipline:
    """Metadata describing an IFBA discipline."""

    slug: str
    name: str
    score_direction: ScoreDirection
    description: str | None = None
    rule_reference: str | None = None


class DisciplineNotFoundError(LookupError):
    """Raised when an unknown discipline slug is requested."""


_DISCIPLINES: Dict[str, Discipline] = {
    "accuracy": Discipline(
        slug="accuracy",
        name="Accuracy",
        score_direction=ScoreDirection.HIGHER_IS_BETTER,
        description="Athletes throw from fixed stations aiming for the bullseye.",
        rule_reference="https://www.ifba-online.org/ifba-rules/accuracy/",
    ),
    "fast-catch": Discipline(
        slug="fast-catch",
        name="Fast Catch",
        score_direction=ScoreDirection.LOWER_IS_BETTER,
        description="Six throws and catches recorded as a cumulative time.",
        rule_reference="https://www.ifba-online.org/ifba-rules/fast-catch/",
    ),
}

_ALIASES = {
    "fastcatch": "fast-catch",
    "fast catch": "fast-catch",
    "fast_catch": "fast-catch",
    "accuracy": "accuracy",
}


def list_disciplines() -> list[Discipline]:
    """Return all supported disciplines."""

    return list(_DISCIPLINES.values())


def normalise_slug(value: str) -> str:
    """Normalise human-entered discipline names to canonical slugs."""

    key = value.strip().lower()
    key = key.replace("_", " ")
    key = " ".join(part for part in key.split())
    return _ALIASES.get(key, key.replace(" ", "-"))


def get_discipline(slug: str) -> Discipline:
    """Look up a discipline by slug, raising if it is unknown."""

    normalised = normalise_slug(slug)
    try:
        return _DISCIPLINES[normalised]
    except KeyError as exc:  # pragma: no cover - explicit error path
        raise DisciplineNotFoundError(f"Unknown discipline '{slug}'.") from exc


__all__ = [
    "Discipline",
    "DisciplineNotFoundError",
    "ScoreDirection",
    "get_discipline",
    "list_disciplines",
    "normalise_slug",
]
