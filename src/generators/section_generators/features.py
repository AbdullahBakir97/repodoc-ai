"""Features section generator for README documents.

Strategy: prefer the most specific evidence available.
1. If the repo has explicit topics, render them as-is (Title Case).
2. If the repo has key directories matching known feature areas, list those.
3. Combine signals when both are present (topics first, then a few inferred
   features that aren't already represented by a topic).
"""

from __future__ import annotations

from src.domain.entities import RepoInfo, Section

__all__ = ["FeaturesGenerator"]

# Directories commonly representing feature areas. The description for each
# is what gets rendered as a feature when the directory is present.
_KEY_DIRECTORIES: dict[str, str] = {
    "api": "REST API layer",
    "auth": "Authentication and authorization",
    "cli": "Command-line interface",
    "core": "Core domain logic",
    "db": "Database integration",
    "database": "Database integration",
    "models": "Data models and schemas",
    "routes": "HTTP routing layer",
    "services": "Business logic services",
    "ui": "User interface components",
    "web": "Web frontend",
    "graphql": "GraphQL API layer",
    "grpc": "gRPC service definitions",
    "websocket": "Real-time WebSocket support",
    "cache": "Caching layer",
    "queue": "Background job queue",
    "workers": "Background worker processes",
    "migrations": "Database migrations",
    "fixtures": "Test fixtures and seed data",
    "i18n": "Internationalization support",
    "locale": "Locale-specific resources",
    "plugins": "Plugin architecture",
    "extensions": "Extension system",
    "middleware": "HTTP middleware pipeline",
}

# Topic-to-feature mapping for common topics whose Title Case rendering is
# misleading or ungrammatical (e.g. "github-action" -> "GitHub Action").
_TOPIC_OVERRIDES: dict[str, str] = {
    "github-action": "GitHub Action",
    "github-app": "GitHub App",
    "github-marketplace": "Listed on GitHub Marketplace",
    "cli": "Command-line interface",
    "api": "Public API",
    "rest-api": "REST API",
    "graphql": "GraphQL API",
    "json-resume": "JSON Resume support",
    "cv-generator": "CV / resume generator",
    "personal-branding": "Personal branding tool",
    "developer-portfolio": "Developer portfolio generator",
    "profile-readme": "GitHub profile README support",
    "automation": "Automation",
    "typescript": "Written in TypeScript",
    "python": "Written in Python",
    "rust": "Written in Rust",
    "go": "Written in Go",
    "docker": "Docker support",
    "kubernetes": "Kubernetes support",
    "ai": "AI-powered",
    "machine-learning": "Machine-learning powered",
    "open-source": "Open source",
    "self-hosted": "Self-hostable",
}


class FeaturesGenerator:
    """Generates the Features section from repo metadata and structure."""

    ORDER = 10

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the features section.

        Combines signals from repo topics and directory structure to
        produce a feature list that reflects what the repo actually does.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered features markdown,
            or a disabled section if no features can be inferred.
        """
        features = self._extract_features(repo_info)

        if not features:
            return Section(
                title="Features",
                content="",
                order=self.ORDER,
                enabled=False,
            )

        # Cap the list at 10 to avoid bloated README sections.
        features = features[:10]

        lines = ["## Features", ""]
        lines.extend(f"- {feature}" for feature in features)

        return Section(
            title="Features",
            content="\n".join(lines),
            order=self.ORDER,
            enabled=True,
        )

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #

    def _extract_features(self, repo_info: RepoInfo) -> list[str]:
        """Extract feature list from available repo metadata.

        Strategy:
          1. Map repo topics through _TOPIC_OVERRIDES (or Title Case).
          2. Add directory-based features that aren't already covered.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A deduplicated, ordered list of feature description strings.
        """
        seen: set[str] = set()
        features: list[str] = []

        # 1. Topics first (most specific signal — set by the maintainer).
        for topic in repo_info.topics:
            mapped = _TOPIC_OVERRIDES.get(topic.lower(), topic.replace("-", " ").title())
            if mapped.lower() not in seen:
                features.append(mapped)
                seen.add(mapped.lower())

        # 2. Add directory-based features that don't duplicate topics.
        top_level_names = {node.name.lower() for node in repo_info.tree if node.is_dir}
        for dir_name, description in _KEY_DIRECTORIES.items():
            if dir_name in top_level_names and description.lower() not in seen:
                features.append(description)
                seen.add(description.lower())

        return features
