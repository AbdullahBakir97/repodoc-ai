"""Webhook endpoint for receiving GitHub events."""

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from src.api.dependencies import get_container
from src.container import Container

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhook"])

__all__ = ["router"]


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_hub_signature_256: str = Header(default="", alias="X-Hub-Signature-256"),
    container: Container = Depends(get_container),
) -> dict:
    """Receive and process a GitHub webhook event.

    Verifies the webhook signature (if a secret is configured), then
    delegates to the ``WebhookHandler`` for event routing.

    Args:
        request: The raw incoming request.
        x_github_event: GitHub event type header.
        x_hub_signature_256: HMAC-SHA256 signature header.
        container: Application DI container.

    Returns:
        A status dictionary from the webhook handler.

    Raises:
        HTTPException: 401 if signature verification fails.
    """
    body = await request.body()

    # Verify signature if webhook secret is configured
    if container.webhook_verifier is not None:
        if not x_hub_signature_256:
            logger.warning("Missing webhook signature header")
            raise HTTPException(status_code=401, detail="Missing signature")

        if not container.webhook_verifier.verify(body, x_hub_signature_256):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    result = await container.webhook_handler.handle_event(x_github_event, payload)

    logger.info("Webhook %s processed: %s", x_github_event, result.get("status", "unknown"))
    return result
