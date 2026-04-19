"""Request logging middleware for RepoDoc AI."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

__all__ = ["RequestLoggingMiddleware"]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every incoming request with timing information.

    Logs the HTTP method, path, status code, and response time for
    each request. Useful for debugging and performance monitoring.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process the request and log timing information.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            The HTTP response from the downstream handler.
        """
        start = time.time()
        method = request.method
        path = request.url.path

        logger.info("-> %s %s", method, path)

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start) * 1000
            logger.info(
                "<- %s %s %d (%.1fms)",
                method,
                path,
                response.status_code,
                duration_ms,
            )
            return response
        except Exception as exc:
            duration_ms = (time.time() - start) * 1000
            logger.exception(
                "<- %s %s ERROR (%.1fms): %s",
                method,
                path,
                duration_ms,
                exc,
            )
            raise
