"""Pydantic request and response models for the RepoDoc AI API."""

from pydantic import BaseModel, Field

__all__ = ["GenerateRequest", "GenerateResponse", "HealthResponse"]


class GenerateRequest(BaseModel):
    """Request body for manual README generation."""

    owner: str = Field(..., description="Repository owner (user or organisation)")
    repo: str = Field(..., description="Repository name")
    installation_id: int | None = Field(
        default=None,
        description="GitHub App installation ID (required for private repos)",
    )


class GenerateResponse(BaseModel):
    """Response body for README generation."""

    readme_content: str = Field(..., description="Generated README markdown content")
    sections: list[str] = Field(default_factory=list, description="Sections included in the README")
    tech_stack: dict = Field(default_factory=dict, description="Detected technology stack")
    pr_url: str | None = Field(default=None, description="URL of the created pull request, if any")


class HealthResponse(BaseModel):
    """Response body for the health check endpoint."""

    status: str = Field(..., description="Application health status")
    uptime: float = Field(..., description="Application uptime in seconds")
    version: str = Field(..., description="Application version string")
