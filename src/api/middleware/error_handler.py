"""Global error handling middleware for RepoDoc AI."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

__all__ = ["register_error_handlers"]


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions as 400 Bad Request.

        Args:
            request: The incoming request.
            exc: The raised ValueError.

        Returns:
            A JSON response with error details.
        """
        logger.warning("ValueError on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=400,
            content={"error": "bad_request", "detail": str(exc)},
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError) -> JSONResponse:
        """Handle PermissionError exceptions as 403 Forbidden.

        Args:
            request: The incoming request.
            exc: The raised PermissionError.

        Returns:
            A JSON response with error details.
        """
        logger.warning("PermissionError on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=403,
            content={"error": "forbidden", "detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle uncaught exceptions as 500 Internal Server Error.

        Args:
            request: The incoming request.
            exc: The uncaught exception.

        Returns:
            A JSON response with a generic error message.
        """
        logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "detail": "An unexpected error occurred"},
        )
