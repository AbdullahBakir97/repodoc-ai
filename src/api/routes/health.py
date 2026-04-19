"""Health check endpoint for RepoDoc AI."""

import time

from fastapi import APIRouter

from src.api.schemas import HealthResponse

router = APIRouter(tags=["health"])

__all__ = ["router"]

_start_time = time.time()

VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return the application health status.

    Returns:
        A ``HealthResponse`` with status, uptime, and version.
    """
    return HealthResponse(
        status="healthy",
        uptime=round(time.time() - _start_time, 2),
        version=VERSION,
    )
