from __future__ import annotations

from decimal import Decimal

import pytest

from boomerang.domain.rules import ScoreDirection
from boomerang.services.scoring import rank_items


class Dummy:
    def __init__(self, score: str) -> None:
        self.score = Decimal(score)


def test_rank_high_scores_with_ties() -> None:
    results = [Dummy("80"), Dummy("78"), Dummy("76"), Dummy("76"), Dummy("76"), Dummy("75")]
    ranked = rank_items(results, score_getter=lambda item: item.score, direction=ScoreDirection.HIGHER_IS_BETTER)

    placements = [entry.placing for entry in ranked]
    assert placements == [1, 2, 3, 3, 3, 6]

    points = [entry.points for entry in ranked]
    assert points[2] == Decimal("4")  # group average of ranks 3,4,5
    assert points[-1] == Decimal("6")


def test_rank_low_scores_prefers_lower_values() -> None:
    results = [Dummy("32.01"), Dummy("34.14"), Dummy("34.50"), Dummy("34.50"), Dummy("34.91")]
    ranked = rank_items(results, score_getter=lambda item: item.score, direction=ScoreDirection.LOWER_IS_BETTER)

    placements = [entry.placing for entry in ranked]
    assert placements == [1, 2, 3, 3, 5]

    points = [entry.points for entry in ranked]
    assert points[2] == Decimal("3.5")
    assert points[3] == Decimal("3.5")


def test_rank_requires_score() -> None:
    class Broken:
        score = None

    with pytest.raises(ValueError):
        rank_items([Broken()], score_getter=lambda item: item.score, direction=ScoreDirection.HIGHER_IS_BETTER)
