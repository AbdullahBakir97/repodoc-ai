"""Features section generator for README documents."""

from __future__ import annotations

from src.domain.entities import RepoInfo, Section

__all__ = ["FeaturesGenerator"]

# Directories commonly representing feature areas
_KEY_DIRECTORIES: dict[str, str] = {
    "api": "API layer",
    "auth": "Authentication",
    "cli": "Command-line interface",
    "core": "Core functionality",
    "db": "Database layer",
    "docs": "Documentation",
    "models": "Data models",
    "routes": "Routing",
    "services": "Business logic services",
    "tests": "Test suite",
    "ui": "User interface",
    "utils": "Utility functions",
    "web": "Web interface",
}


class FeaturesGenerator:
    """Generates the Features section from repo metadata and structure."""

    ORDER = 10

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the features section.

        Extracts features from topics/keywords or falls back to listing
        key directories as feature areas.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered features markdown.
        """
        features = self._extract_features(repo_info)

        if not features:
            return Section(
                title="Features",
                content="",
                order=self.ORDER,
                enabled=False,
            )

        lines = ["## Features", ""]
        for feature in features:
            lines.append(f"- {feature}")

        return Section(
            title="Features",
            content="\n".join(lines),
            order=self.ORDER,
            enabled=True,
        )

    def _extract_features(self, repo_info: RepoInfo) -> list[str]:
        """Extract feature list from available repo metadata.

        Priority order:
        1. Repository topics/tags
        2. Key directories in the file tree

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A list of feature description strings.
        """
        # Use topics if available
        if repo_info.topics:
            return [topic.replace("-", " ").title() for topic in repo_info.topics]

        # Fall back to key directories
        features: list[str] = []
        top_level_names = {node.name for node in repo_info.tree if node.is_dir}

        for dir_name, description in _KEY_DIRECTORIES.items():
            if dir_name in top_level_names:
                features.append(description)

        return features
