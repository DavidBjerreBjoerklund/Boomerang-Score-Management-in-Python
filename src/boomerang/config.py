"""Application configuration utilities."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="BOOMERANG_", env_file=".env", extra="ignore")

    database_url: str = f"sqlite:///{Path(__file__).resolve().parents[2] / 'data' / 'boomerang.db'}"
    database_echo: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
