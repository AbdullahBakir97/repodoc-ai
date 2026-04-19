"""CI/CD detector — detects continuous integration setup from file tree."""

from __future__ import annotations

import logging

from src.domain.entities import FileNode
from src.domain.enums import CIProvider

__all__ = ["CIDetector"]

logger = logging.getLogger(__name__)

# Path patterns to CI provider mapping
_CI_INDICATORS: dict[str, CIProvider] = {
    ".github/workflows": CIProvider.GITHUB_ACTIONS,
    ".gitlab-ci.yml": CIProvider.GITLAB_CI,
    ".circleci/config.yml": CIProvider.CIRCLECI,
    ".circleci": CIProvider.CIRCLECI,
    ".travis.yml": CIProvider.TRAVIS,
    "Jenkinsfile": CIProvider.JENKINS,
}


class CIDetector:
    """Detects CI/CD setup from a repository's file tree.

    Checks for known CI configuration files and directories:
    - .github/workflows/*.yml  -> GitHub Actions
    - .gitlab-ci.yml           -> GitLab CI
    - .circleci/config.yml     -> CircleCI
    - .travis.yml              -> Travis CI
    - Jenkinsfile              -> Jenkins
    """

    def detect(self, tree: list[FileNode]) -> CIProvider:
        """Detect the CI provider from the file tree.

        Args:
            tree: The repository file tree.

        Returns:
            The detected CIProvider, or CIProvider.NONE.
        """
        all_paths = self._collect_paths(tree)

        for indicator, provider in _CI_INDICATORS.items():
            for path in all_paths:
                if path == indicator or path.startswith(indicator + "/"):
                    logger.debug("Detected CI provider: %s", provider)
                    return provider

        return CIProvider.NONE

    def _collect_paths(self, tree: list[FileNode]) -> set[str]:
        """Collect all file and directory paths from the tree.

        Args:
            tree: Nested list of FileNode objects.

        Returns:
            A set of all paths.
        """
        paths: set[str] = set()
        for node in tree:
            paths.add(node.path)
            if node.children:
                paths.update(self._collect_paths(node.children))
        return paths
