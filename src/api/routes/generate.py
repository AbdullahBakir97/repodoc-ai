"""Manual README generation and preview endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_container
from src.api.schemas import GenerateRequest, GenerateResponse
from src.container import Container

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["generate"])

__all__ = ["router"]


@router.post("/generate", response_model=GenerateResponse)
async def generate_readme(
    request: GenerateRequest,
    container: Container = Depends(get_container),
) -> GenerateResponse:
    """Manually trigger README generation for a repository.

    Args:
        request: Generation request with owner, repo, and optional installation ID.
        container: Application DI container.

    Returns:
        A ``GenerateResponse`` with the generated README content and metadata.

    Raises:
        HTTPException: 400 if installation_id is missing,
                       500 if generation fails.
    """
    if request.installation_id is None:
        raise HTTPException(status_code=400, detail="installation_id is required")

    logger.info("Manual generation requested for %s/%s", request.owner, request.repo)

    try:
        container.github_client.set_installation_id(request.installation_id)
        result = await container.orchestrator.generate(request.owner, request.repo, request.installation_id)

        return GenerateResponse(
            readme_content=result.readme_content,
            sections=result.sections,
            tech_stack=result.tech_stack,
            pr_url=None,
        )
    except Exception as exc:
        logger.exception("Generation failed for %s/%s: %s", request.owner, request.repo, exc)
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc


@router.get("/preview/{owner}/{repo}")
async def preview_readme(
    owner: str,
    repo: str,
    installation_id: int | None = None,
    container: Container = Depends(get_container),
) -> dict:
    """Preview what the generated README would look like for a repository.

    This endpoint runs the generation pipeline but does not create a PR.

    Args:
        owner: Repository owner.
        repo: Repository name.
        installation_id: GitHub App installation ID.
        container: Application DI container.

    Returns:
        A dictionary with the preview README content and metadata.

    Raises:
        HTTPException: 400 if installation_id is missing,
                       500 if generation fails.
    """
    if installation_id is None:
        raise HTTPException(status_code=400, detail="installation_id query parameter is required")

    logger.info("Preview requested for %s/%s", owner, repo)

    try:
        container.github_client.set_installation_id(installation_id)
        result = await container.orchestrator.generate(owner, repo, installation_id)

        return {
            "owner": owner,
            "repo": repo,
            "readme_content": result.readme_content,
            "sections": result.sections,
            "tech_stack": result.tech_stack,
            "languages": result.languages,
        }
    except Exception as exc:
        logger.exception("Preview failed for %s/%s: %s", owner, repo, exc)
        raise HTTPException(status_code=500, detail=f"Preview failed: {exc}") from exc
