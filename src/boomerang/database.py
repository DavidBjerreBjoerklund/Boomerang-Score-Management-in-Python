"""Database configuration and session helpers."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings

settings = get_settings()
url = make_url(settings.database_url)
connect_args: dict[str, object] = {}

if url.get_backend_name() == "sqlite":
    database = url.database
    if database and database != ":memory:":
        db_path = Path(database).expanduser()
        db_path.parent.mkdir(parents=True, exist_ok=True)
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, echo=settings.database_echo, connect_args=connect_args)


def init_db() -> None:
    """Create database tables if they do not yet exist."""

    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope for database interactions."""

    with Session(engine) as session:
        yield session


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a database session."""

    with Session(engine) as session:
        yield session


__all__ = ["engine", "get_session", "init_db", "session_scope"]
