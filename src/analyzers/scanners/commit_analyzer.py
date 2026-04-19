"""Commit analyzer — analyzes commit history from a GitHub repository."""

from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Any

from src.domain.entities import CommitInfo
from src.domain.exceptions import ScanError
from src.domain.interfaces import ICommitAnalyzer, IGitHubClient

__all__ = ["CommitAnalyzer"]

logger = logging.getLogger(__name__)

# Conventional commit pattern: type(scope): message
_CONVENTIONAL_RE = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\((?P<scope>[^)]+)\))?:\s*(?P<description>.+)$",
    re.IGNORECASE,
)


class CommitAnalyzer(ICommitAnalyzer):
    """Analyzes commit history of a GitHub repository.

    Extracts CommitInfo objects, identifies top contributors, and groups
    commits by type using conventional commit parsing.
    """

    def __init__(self, github_client: IGitHubClient) -> None:
        self._client = github_client

    async def analyze(
        self, owner: str, repo: str, count: int = 20
    ) -> list[CommitInfo]:
        """Analyze recent commits from a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            count: Number of recent commits to analyze.

        Returns:
            A list of CommitInfo objects.

        Raises:
            ScanError: If commit analysis fails.
        """
        try:
            raw_commits = await self._client.get_commits(owner, repo, count=count)
            return [self._parse_commit(c) for c in raw_commits]
        except ScanError:
            raise
        except Exception as exc:
            raise ScanError(
                f"Failed to analyze commits for {owner}/{repo}: {exc}"
            ) from exc

    def get_contributors(self, commits: list[CommitInfo]) -> list[str]:
        """Identify top contributors from commit history.

        Args:
            commits: List of CommitInfo objects.

        Returns:
            A list of contributor names sorted by commit count (descending).
        """
        counter: Counter[str] = Counter()
        for commit in commits:
            counter[commit.author] += 1
        return [author for author, _ in counter.most_common()]

    def group_by_type(
        self, commits: list[CommitInfo]
    ) -> dict[str, list[CommitInfo]]:
        """Group commits by conventional commit type.

        Args:
            commits: List of CommitInfo objects.

        Returns:
            A dict mapping commit type to list of CommitInfo objects.
            Commits that don't follow conventional format go under "other".
        """
        groups: dict[str, list[CommitInfo]] = {}

        for commit in commits:
            commit_type = self._extract_type(commit.message)
            groups.setdefault(commit_type, []).append(commit)

        return groups

    @staticmethod
    def _parse_commit(raw: dict[str, Any]) -> CommitInfo:
        """Parse a raw GitHub API commit into a CommitInfo.

        Args:
            raw: Raw commit dict from the GitHub API.

        Returns:
            A CommitInfo object.
        """
        commit_data = raw.get("commit", {})
        author_data = commit_data.get("author", {})

        return CommitInfo(
            sha=raw.get("sha", "")[:7],
            message=commit_data.get("message", "").split("\n", 1)[0],
            author=author_data.get("name", "Unknown"),
            date=author_data.get("date", ""),
            files_changed=len(raw.get("files", [])),
        )

    @staticmethod
    def _extract_type(message: str) -> str:
        """Extract the conventional commit type from a message.

        Args:
            message: Commit message string.

        Returns:
            The commit type (e.g. "feat", "fix") or "other".
        """
        match = _CONVENTIONAL_RE.match(message)
        if match:
            return match.group("type").lower()
        return "other"
