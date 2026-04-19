"""FastAPI dependency injection helpers for RepoDoc AI."""

from functools import lru_cache

from fastapi import Request

from src.config.settings import Settings
from src.container import Container

__all__ = ["get_settings", "get_container"]


@lru_cache
def get_settings() -> Settings:
    """Get the cached application settings singleton.

    Returns:
        The application ``Settings`` instance.
    """
    return Settings()


def get_container(request: Request) -> Container:
    """Get the DI container from the application state.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The ``Container`` instance stored on the app.

    Raises:
        AttributeError: If the container has not been wired to the app.
    """
    return request.app.state.container
