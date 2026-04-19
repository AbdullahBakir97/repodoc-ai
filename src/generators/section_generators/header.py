"""Header section generator for README documents."""

from __future__ import annotations

from src.domain.entities import RepoInfo, Section
from src.generators.badge_generator import BadgeGenerator

__all__ = ["HeaderGenerator"]


class HeaderGenerator:
    """Generates the title, description, and badges header section."""

    ORDER = 0

    def __init__(self) -> None:
        self._badge_generator = BadgeGenerator()

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the header section with title, badges, and description.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered header markdown.
        """
        badges = self._badge_generator.generate_all(repo_info)
        description = repo_info.description or "N/A"

        content = f"# {repo_info.name}\n\n{badges}\n\n{description}"

        return Section(
            title="Header",
            content=content,
            order=self.ORDER,
            enabled=True,
        )
