"""Footer section generator for README documents."""

from __future__ import annotations

from src.domain.entities import RepoInfo, Section
from src.domain.enums import LicenseType
from src.generators.templates import CONTRIBUTING_TEMPLATE

__all__ = ["FooterGenerator"]


class FooterGenerator:
    """Generates the Contributing, License, and footer sections."""

    ORDER = 60

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the footer section.

        Includes a contributing guide, license information, and links
        to the repository's issues and discussions pages.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered footer markdown.
        """
        parts: list[str] = []

        # Contributing
        parts.append(CONTRIBUTING_TEMPLATE)

        # License
        license_section = self._license_section(repo_info)
        parts.append(license_section)

        # Links
        links_section = self._links_section(repo_info)
        parts.append(links_section)

        return Section(
            title="Footer",
            content="\n\n".join(parts),
            order=self.ORDER,
            enabled=True,
        )

    def _license_section(self, repo_info: RepoInfo) -> str:
        """Generate the license section text.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            Markdown string for the license section.
        """
        license_type = repo_info.tech_stack.license_type

        if license_type in (LicenseType.UNKNOWN, LicenseType.PROPRIETARY):
            return "## License\n\nSee the [LICENSE](LICENSE) file for license information."

        return (
            f"## License\n\n"
            f"This project is licensed under the **{license_type.value}** License. "
            f"See the [LICENSE](LICENSE) file for details."
        )

    def _links_section(self, repo_info: RepoInfo) -> str:
        """Generate the links section with issue tracker and discussions.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            Markdown string for the links section.
        """
        base_url = f"https://github.com/{repo_info.owner}/{repo_info.name}"
        lines = [
            "## Links",
            "",
            f"- [Issues]({base_url}/issues)",
            f"- [Discussions]({base_url}/discussions)",
        ]

        if repo_info.homepage:
            lines.append(f"- [Homepage]({repo_info.homepage})")

        return "\n".join(lines)
