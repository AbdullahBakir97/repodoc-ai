"""Header section generator for README documents."""

from __future__ import annotations

from src.domain.entities import RepoInfo, Section
from src.domain.enums import Framework, ProjectType
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
        description = self._description_or_fallback(repo_info)

        content = f"# {repo_info.name}\n\n{badges}\n\n{description}"

        return Section(
            title="Header",
            content=content,
            order=self.ORDER,
            enabled=True,
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    @staticmethod
    def _description_or_fallback(repo_info: RepoInfo) -> str:
        """Return the repo description, or a sensible fallback derived from
        the detected stack when no description is set.

        Real repos with no description shouldn't get "N/A" — that signals
        the README is dead. Instead we synthesise a one-line description
        from the language and framework so the README still reads naturally.
        """
        if repo_info.description and repo_info.description.strip():
            return repo_info.description.strip()

        lang = repo_info.tech_stack.primary_language
        framework = repo_info.tech_stack.framework

        if framework != Framework.NONE and lang != ProjectType.UNKNOWN:
            return f"A {lang.value.title()} project built with {framework.value}."
        if lang != ProjectType.UNKNOWN:
            return f"A {lang.value.title()} project."
        return f"The `{repo_info.name}` project."
