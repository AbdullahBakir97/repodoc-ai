"""Configuration loader for per-repository RepoDoc settings."""

import logging

import yaml

from src.infrastructure.github.client import GitHubClient

from .schema import RepodocConfig

logger = logging.getLogger(__name__)

__all__ = ["ConfigLoader"]

CONFIG_PATH = ".github/repodoc.yml"


class ConfigLoader:
    """Loads and merges per-repository RepoDoc configuration.

    Attempts to read ``.github/repodoc.yml`` from the repository. If the
    file is missing or unparseable, returns a default configuration.
    """

    def __init__(self, github_client: GitHubClient) -> None:
        """Initialise the loader.

        Args:
            github_client: GitHub API client used to fetch config files.
        """
        self._client = github_client

    async def load(self, owner: str, repo: str) -> RepodocConfig:
        """Load repository configuration, merging with defaults.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Merged configuration with defaults applied for missing fields.
        """
        content = await self._client.get_file_content(owner, repo, CONFIG_PATH)

        if content is None:
            logger.info("No %s found in %s/%s, using defaults", CONFIG_PATH, owner, repo)
            return RepodocConfig()

        try:
            raw = yaml.safe_load(content)
            if not isinstance(raw, dict):
                logger.warning("Invalid config format in %s/%s, using defaults", owner, repo)
                return RepodocConfig()

            config = RepodocConfig(**raw)
            logger.info("Loaded config from %s/%s", owner, repo)
            return config
        except Exception as exc:
            logger.warning("Failed to parse config in %s/%s: %s — using defaults", owner, repo, exc)
            return RepodocConfig()
