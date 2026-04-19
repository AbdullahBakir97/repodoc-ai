"""FastAPI application factory for RepoDoc AI."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.middleware.error_handler import register_error_handlers
from src.api.middleware.logging import RequestLoggingMiddleware
from src.api.routes import generate, health, webhook
from src.config.settings import Settings
from src.container import Container

logger = logging.getLogger(__name__)

__all__ = ["create_app"]


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Wires up middleware, error handlers, routers, and the DI container.

    Args:
        settings: Application settings. If ``None``, settings are loaded
                  from the environment.

    Returns:
        A fully configured ``FastAPI`` application instance.
    """
    if settings is None:
        settings = Settings()

    app = FastAPI(
        title="RepoDoc AI",
        description="Auto-generate README.md files by scanning repos via the GitHub API.",
        version="0.1.0",
    )

    # --- DI Container ---
    container = Container(settings)
    app.state.container = container

    # --- CORS Middleware ---
    origins = [o.strip() for o in settings.allowed_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request Logging Middleware ---
    app.add_middleware(RequestLoggingMiddleware)

    # --- Error Handlers ---
    register_error_handlers(app)

    # --- Routers ---
    app.include_router(webhook.router)
    app.include_router(generate.router)
    app.include_router(health.router)

    # --- Static Files (Dashboard) ---
    try:
        app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
        logger.info("Dashboard static files mounted at /dashboard")
    except Exception:
        logger.warning("Dashboard directory not found — skipping static file mount")

    # --- Root Redirect ---
    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        """Redirect the root path to the dashboard."""
        return RedirectResponse(url="/dashboard")

    logger.info("RepoDoc AI application created (env=%s)", settings.env)
    return app
