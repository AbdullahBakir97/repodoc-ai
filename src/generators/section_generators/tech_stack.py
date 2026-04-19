"""Tech stack section generator for README documents."""

from __future__ import annotations

from src.domain.entities import RepoInfo, Section
from src.domain.enums import CIProvider, Framework, LicenseType

__all__ = ["TechStackGenerator"]


class TechStackGenerator:
    """Generates the Tech Stack section as a markdown table."""

    ORDER = 15

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the tech stack section.

        Renders detected technologies as a two-column markdown table.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered tech stack markdown.
        """
        ts = repo_info.tech_stack
        rows: list[tuple[str, str]] = []

        # Primary language with version if available
        lang_value = ts.primary_language.value.title()
        if ts.python_version:
            lang_value = f"Python {ts.python_version}"
        elif ts.node_version:
            lang_value = f"{lang_value} (Node {ts.node_version})"
        rows.append(("Language", lang_value))

        # Framework
        if ts.framework != Framework.NONE:
            rows.append(("Framework", ts.framework.value))

        # Package manager
        rows.append(("Package Manager", ts.package_manager.value))

        # CI/CD
        if ts.ci_provider != CIProvider.NONE:
            rows.append(("CI/CD", ts.ci_provider.value))

        # Container
        if ts.has_docker:
            rows.append(("Container", "Docker"))

        # License
        if ts.license_type not in (LicenseType.UNKNOWN, LicenseType.PROPRIETARY):
            rows.append(("License", ts.license_type.value))

        # Build table
        lines = [
            "## Tech Stack",
            "",
            "| Category | Technology |",
            "|----------|-----------|",
        ]
        for category, technology in rows:
            lines.append(f"| {category} | {technology} |")

        return Section(
            title="Tech Stack",
            content="\n".join(lines),
            order=self.ORDER,
            enabled=True,
        )
