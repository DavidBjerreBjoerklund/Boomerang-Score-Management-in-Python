"""FastAPI application factory for the Boomerang scoring service."""

from __future__ import annotations

from fastapi import FastAPI

from ..database import init_db
from .events import router as events_router
from .metadata import router as metadata_router


def create_app() -> FastAPI:
    """Initialise database tables and create a FastAPI application."""

    init_db()
    app = FastAPI(title="Boomerang Score Management API", version="0.1.0")
    app.include_router(metadata_router)
    app.include_router(events_router)
    return app


app = create_app()


__all__ = ["app", "create_app"]
