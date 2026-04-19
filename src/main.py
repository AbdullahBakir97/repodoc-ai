"""Entry point for the RepoDoc AI application."""

import uvicorn

from src.api.app import create_app
from src.config.logging import setup_logging
from src.config.settings import Settings


def main() -> None:
    """Start the RepoDoc AI server.

    Loads settings, configures logging, creates the FastAPI app, and
    runs it with uvicorn.
    """
    settings = Settings()
    setup_logging(level=settings.log_level, json_format=not settings.is_development)

    app = create_app(settings)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
