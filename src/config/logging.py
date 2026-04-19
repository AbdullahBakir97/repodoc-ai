"""Structured logging configuration for RepoDoc AI."""

import logging
import sys
from typing import Optional

__all__ = ["setup_logging"]


def setup_logging(level: str = "INFO", json_format: bool = False) -> None:
    """Configure structured logging for the application.

    Sets up a consistent log format with timestamps, level, logger name,
    and message. Optionally uses JSON-structured output for production
    environments.

    Args:
        level: Log level string (e.g. ``DEBUG``, ``INFO``, ``WARNING``).
        json_format: If ``True``, output logs in JSON format for
                     structured log aggregation systems.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if json_format:
        fmt = (
            '{"timestamp":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%dT%H:%M:%S"))

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)

    # Quieten noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logging.info("Logging configured: level=%s, json=%s", level, json_format)
