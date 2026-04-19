"""Changelog section generator for README documents."""

from __future__ import annotations

import re

from src.domain.entities import CommitInfo, RepoInfo, Section

__all__ = ["ChangelogGenerator"]

# Conventional commit prefixes and their display categories
_COMMIT_CATEGORIES: dict[str, str] = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "style": "Style",
    "refactor": "Refactoring",
    "perf": "Performance",
    "test": "Tests",
    "build": "Build",
    "ci": "CI/CD",
    "chore": "Chores",
}

_CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore)"
    r"(?:\(.+?\))?:\s*(?P<message>.+)$",
    re.IGNORECASE,
)

_MAX_COMMITS = 20


class ChangelogGenerator:
    """Generates the Recent Changes section from commit history."""

    ORDER = 50

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the recent changes section.

        Groups commits by conventional commit type and formats them
        as categorized lists. Shows up to 20 recent commits.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered changelog markdown,
            or a disabled section if there are no commits.
        """
        commits = repo_info.recent_commits[:_MAX_COMMITS]

        if not commits:
            return Section(
                title="Recent Changes",
                content="",
                order=self.ORDER,
                enabled=False,
            )

        grouped = self._group_commits(commits)
        lines = ["## Recent Changes", ""]

        for category, messages in grouped.items():
            lines.append(f"### {category}")
            for msg in messages:
                lines.append(f"- {msg}")
            lines.append("")

        return Section(
            title="Recent Changes",
            content="\n".join(lines).rstrip(),
            order=self.ORDER,
            enabled=True,
        )

    def _group_commits(
        self, commits: list[CommitInfo]
    ) -> dict[str, list[str]]:
        """Group commits by conventional commit category.

        Commits that don't follow conventional format are placed
        under 'Other Changes'.

        Args:
            commits: The list of commit info objects to group.

        Returns:
            An ordered dict mapping category names to lists of messages.
        """
        groups: dict[str, list[str]] = {}

        for commit in commits:
            first_line = commit.message.split("\n", 1)[0].strip()
            match = _CONVENTIONAL_COMMIT_RE.match(first_line)

            if match:
                commit_type = match.group("type").lower()
                category = _COMMIT_CATEGORIES.get(commit_type, "Other Changes")
                message = match.group("message")
            else:
                category = "Other Changes"
                message = first_line

            if category not in groups:
                groups[category] = []
            groups[category].append(message)

        # Sort categories: Features first, Bug Fixes second, rest alpha
        priority = {"Features": 0, "Bug Fixes": 1}
        sorted_groups: dict[str, list[str]] = {}
        for key in sorted(groups, key=lambda k: (priority.get(k, 99), k)):
            sorted_groups[key] = groups[key]

        return sorted_groups
