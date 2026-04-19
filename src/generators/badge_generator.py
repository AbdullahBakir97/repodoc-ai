"""Badge generator for shields.io markdown badges."""

from __future__ import annotations

from src.domain.entities import RepoInfo
from src.domain.enums import CIProvider, Framework, LicenseType, ProjectType

__all__ = ["BadgeGenerator"]


class BadgeGenerator:
    """Generates shields.io badge markdown strings."""

    BASE_URL = "https://img.shields.io/badge"

    _LANGUAGE_COLORS: dict[str, str] = {
        "python": "3776AB",
        "javascript": "F7DF1E",
        "typescript": "3178C6",
        "go": "00ADD8",
        "rust": "000000",
        "java": "ED8B00",
        "ruby": "CC342D",
        "csharp": "239120",
        "php": "777BB4",
        "unknown": "gray",
    }

    _FRAMEWORK_COLORS: dict[str, str] = {
        "FastAPI": "009688",
        "Django": "092E20",
        "Flask": "000000",
        "Express": "000000",
        "Next.js": "000000",
        "React": "61DAFB",
        "Vue.js": "4FC08D",
        "Angular": "DD0031",
        "Spring": "6DB33F",
        "Rails": "CC0000",
        "Laravel": "FF2D20",
        "Gin": "00ADD8",
        "Actix": "000000",
    }

    _FRAMEWORK_LOGOS: dict[str, str] = {
        "FastAPI": "fastapi",
        "Django": "django",
        "Flask": "flask",
        "Express": "express",
        "Next.js": "nextdotjs",
        "React": "react",
        "Vue.js": "vuedotjs",
        "Angular": "angular",
        "Spring": "spring",
        "Rails": "rubyonrails",
        "Laravel": "laravel",
        "Gin": "go",
        "Actix": "rust",
    }

    def generate_all(self, repo_info: RepoInfo) -> str:
        """Generate all applicable badges for a repository.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A string of space-separated badge markdown images.
        """
        badges: list[str] = []

        # Language badge
        badges.append(self._language_badge(repo_info.tech_stack.primary_language))

        # Framework badge (if detected)
        if repo_info.tech_stack.framework != Framework.NONE:
            badges.append(self._framework_badge(repo_info.tech_stack.framework))

        # License badge
        badges.append(self._license_badge(repo_info.owner, repo_info.name))

        # CI badge (GitHub Actions)
        if repo_info.tech_stack.ci_provider == CIProvider.GITHUB_ACTIONS:
            badges.append(self._ci_badge(repo_info.owner, repo_info.name))

        # Docker badge
        if repo_info.tech_stack.has_docker:
            badges.append(self._docker_badge())

        # Tests badge
        if repo_info.tech_stack.has_tests:
            badges.append(self._tests_badge())

        return " ".join(badges)

    def _language_badge(self, lang: ProjectType) -> str:
        """Generate a badge for the primary programming language.

        Args:
            lang: The primary language project type.

        Returns:
            Markdown image string for the language badge.
        """
        color = self._LANGUAGE_COLORS.get(lang.value, "gray")
        return (
            f"![{lang.value}]"
            f"(https://img.shields.io/badge/{lang.value}-{color}"
            f"?style=for-the-badge&logo={lang.value}&logoColor=white)"
        )

    def _framework_badge(self, framework: Framework) -> str:
        """Generate a badge for the detected framework.

        Args:
            framework: The detected framework enum value.

        Returns:
            Markdown image string for the framework badge.
        """
        color = self._FRAMEWORK_COLORS.get(framework.value, "gray")
        logo = self._FRAMEWORK_LOGOS.get(framework.value, framework.value.lower())
        label = framework.value.replace(".", "")
        return (
            f"![{framework.value}]"
            f"(https://img.shields.io/badge/{label}-{color}"
            f"?style=for-the-badge&logo={logo}&logoColor=white)"
        )

    def _license_badge(self, owner: str, repo: str) -> str:
        """Generate a license badge linked to the GitHub license endpoint.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Markdown image string for the license badge.
        """
        return (
            f"![License]"
            f"(https://img.shields.io/github/license/{owner}/{repo}"
            f"?style=for-the-badge)"
        )

    def _ci_badge(self, owner: str, repo: str) -> str:
        """Generate a GitHub Actions CI status badge.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Markdown image string for the CI badge.
        """
        return (
            f"![CI]"
            f"(https://img.shields.io/github/actions/workflow/status"
            f"/{owner}/{repo}/ci.yml?style=for-the-badge&logo=githubactions"
            f"&logoColor=white)"
        )

    def _docker_badge(self) -> str:
        """Generate a Docker badge.

        Returns:
            Markdown image string for the Docker badge.
        """
        return (
            "![Docker]"
            "(https://img.shields.io/badge/Docker-2496ED"
            "?style=for-the-badge&logo=docker&logoColor=white)"
        )

    def _tests_badge(self) -> str:
        """Generate a tests badge.

        Returns:
            Markdown image string for the tests badge.
        """
        return (
            "![Tests]"
            "(https://img.shields.io/badge/Tests-passing-brightgreen"
            "?style=for-the-badge)"
        )
