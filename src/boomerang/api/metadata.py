"""Endpoints exposing static metadata for clients."""

from __future__ import annotations

from fastapi import APIRouter

from ..domain.rules import list_disciplines
from . import schemas

router = APIRouter(prefix="/disciplines", tags=["disciplines"])


@router.get("", response_model=list[schemas.DisciplineRead])
def list_disciplines_endpoint() -> list[schemas.DisciplineRead]:
    """Return metadata about supported IFBA disciplines."""

    return [schemas.DisciplineRead.from_domain(item) for item in list_disciplines()]


__all__ = ["router"]
