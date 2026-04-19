"""Webhook event handler for RepoDoc AI."""

import logging

from src.application.orchestrator import GenerationOrchestrator
from src.application.pr_workflow import PRWorkflow
from src.infrastructure.github.client import GitHubClient

logger = logging.getLogger(__name__)

__all__ = ["WebhookHandler"]


class WebhookHandler:
    """Routes incoming GitHub webhook events to the appropriate handlers.

    Supports ``push`` events on the default branch (triggers README
    generation) and ``installation`` events (logged for monitoring).
    """

    def __init__(
        self,
        orchestrator: GenerationOrchestrator,
        pr_workflow: PRWorkflow,
        github_client: GitHubClient,
    ) -> None:
        """Initialise the handler.

        Args:
            orchestrator: README generation orchestrator.
            pr_workflow: Pull request creation workflow.
            github_client: GitHub API client.
        """
        self.orchestrator = orchestrator
        self.pr_workflow = pr_workflow
        self.github_client = github_client

    async def handle_event(self, event_type: str, payload: dict) -> dict:
        """Route a webhook event to the correct handler.

        Args:
            event_type: The GitHub event type (e.g. ``push``, ``installation``).
            payload: The full webhook payload.

        Returns:
            A status dictionary describing what action was taken.
        """
        logger.info("Received webhook event: %s", event_type)

        match event_type:
            case "push":
                ref = payload.get("ref", "")
                default_branch = payload.get("repository", {}).get("default_branch", "main")
                if ref == f"refs/heads/{default_branch}":
                    return await self._handle_push(payload)
                else:
                    logger.debug("Ignoring push to non-default branch: %s", ref)
                    return {"status": "ignored", "reason": "non-default branch push"}
            case "installation":
                action = payload.get("action", "unknown")
                logger.info(
                    "Installation event: %s for account %s",
                    action,
                    payload.get("installation", {}).get("account", {}).get("login", "unknown"),
                )
                return {"status": "acknowledged", "event": "installation", "action": action}
            case _:
                logger.debug("Unhandled event type: %s", event_type)
                return {"status": "ignored", "reason": f"unhandled event type: {event_type}"}

    async def _handle_push(self, payload: dict) -> dict:
        """Handle a push event to the default branch.

        Args:
            payload: The push event payload.

        Returns:
            A status dictionary with the PR URL on success.
        """
        owner = payload["repository"]["owner"]["login"]
        repo = payload["repository"]["name"]
        installation_id = payload["installation"]["id"]

        logger.info("Processing push event for %s/%s (installation %d)", owner, repo, installation_id)

        self.github_client.set_installation_id(installation_id)

        try:
            result = await self.orchestrator.generate(owner, repo, installation_id)

            if not result.readme_content:
                logger.info("No README content generated for %s/%s (possibly disabled)", owner, repo)
                return {"status": "skipped", "reason": "generation disabled or empty"}

            pr_url = await self.pr_workflow.create_readme_pr(owner, repo, result)
            logger.info("Created README PR: %s", pr_url)
            return {"status": "success", "pr_url": pr_url}

        except Exception as exc:
            logger.exception("Failed to process push event for %s/%s: %s", owner, repo, exc)
            return {"status": "error", "error": str(exc)}
