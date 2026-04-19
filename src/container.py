"""Dependency injection container for RepoDoc AI.

Wires together all infrastructure, analyser, generator, and application
components into a single container that is attached to the FastAPI app state.
"""

import logging

from src.application.orchestrator import GenerationOrchestrator
from src.application.pr_workflow import PRWorkflow
from src.application.webhook_handler import WebhookHandler
from src.config.settings import Settings
from src.infrastructure.config.loader import ConfigLoader
from src.infrastructure.github.auth import GitHubAuthenticator
from src.infrastructure.github.client import GitHubClient
from src.infrastructure.github.webhook import WebhookVerifier

logger = logging.getLogger(__name__)

__all__ = ["Container"]


# ---------------------------------------------------------------------------
# Lightweight stub analysers / detectors / generator
# These will be replaced by real implementations in future modules.
# ---------------------------------------------------------------------------


class _RepoScanner:
    """Scans the repository tree, filtering by config exclusions."""

    def __init__(self, github_client: GitHubClient) -> None:
        self._client = github_client

    async def scan(self, owner: str, repo: str, config) -> list[dict]:
        """Return the filtered file tree for the repository."""
        tree = await self._client.get_tree(owner, repo)
        exclude = set(config.exclude_dirs)
        return [entry for entry in tree if not any(part in exclude for part in entry.get("path", "").split("/"))]


class _FileParser:
    """Parses configuration files (package.json, pyproject.toml, etc.)."""

    def __init__(self, github_client: GitHubClient) -> None:
        self._client = github_client

    async def parse(self, owner: str, repo: str, tree: list[dict]) -> dict:
        """Parse known config files and return their contents."""
        config_files = {
            "package.json",
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
        }
        result: dict = {}
        for entry in tree:
            name = entry.get("path", "").split("/")[-1]
            if name in config_files:
                content = await self._client.get_file_content(owner, repo, entry["path"])
                if content:
                    result[entry["path"]] = content
        return result


class _CommitAnalyzer:
    """Analyses recent commit history."""

    def __init__(self, github_client: GitHubClient) -> None:
        self._client = github_client

    async def analyze(self, owner: str, repo: str) -> list[dict]:
        """Return recent commits."""
        return await self._client.get_commits(owner, repo)


class _TechDetector:
    """Detects the technology stack from file tree and config files."""

    async def detect(self, tree: list[dict], parsed_configs: dict) -> dict:
        """Return detected technologies."""
        extensions: dict[str, int] = {}
        for entry in tree:
            path = entry.get("path", "")
            if "." in path:
                ext = path.rsplit(".", 1)[-1].lower()
                extensions[ext] = extensions.get(ext, 0) + 1
        return {"extensions": extensions, "config_files": list(parsed_configs.keys())}


class _CIDetector:
    """Detects CI/CD configuration."""

    async def detect(self, tree: list[dict], parsed_configs: dict) -> dict:
        """Return detected CI/CD info."""
        ci_files = {
            ".github/workflows": "GitHub Actions",
            ".gitlab-ci.yml": "GitLab CI",
            "Jenkinsfile": "Jenkins",
            ".circleci": "CircleCI",
            ".travis.yml": "Travis CI",
        }
        detected: list[str] = []
        for entry in tree:
            path = entry.get("path", "")
            for ci_path, ci_name in ci_files.items():
                if path.startswith(ci_path):
                    if ci_name not in detected:
                        detected.append(ci_name)
        return {"providers": detected}


class _APIDetector:
    """Detects API endpoints from source files."""

    def __init__(self, github_client: GitHubClient) -> None:
        self._client = github_client

    async def detect(self, owner: str, repo: str, tree: list[dict]) -> list[dict]:
        """Return detected API endpoints (stub)."""
        return []


class _ReadmeGenerator:
    """Generates README markdown content from repository information."""

    async def generate(self, repo_info, config) -> tuple[str, list[str]]:
        """Generate README content and return (content, sections_list)."""
        sections: list[str] = []
        lines: list[str] = []

        if config.sections.header:
            sections.append("header")
            lines.append(f"# {repo_info.repo}\n")
            lines.append("")

        if config.sections.tech_stack:
            sections.append("tech_stack")
            lines.append("## Tech Stack\n")
            exts = repo_info.tech_stack.get("extensions", {})
            if exts:
                for ext, count in sorted(exts.items(), key=lambda x: -x[1])[:10]:
                    lines.append(f"- `.{ext}` ({count} files)")
            lines.append("")

        if config.sections.structure:
            sections.append("structure")
            lines.append("## Project Structure\n")
            lines.append("```")
            dirs: set[str] = set()
            for entry in repo_info.tree[:50]:
                path = entry.get("path", "")
                parts = path.split("/")
                if len(parts) <= config.max_depth:
                    lines.append(path)
                    if len(parts) > 1:
                        dirs.add("/".join(parts[:-1]))
            lines.append("```")
            lines.append("")

        if config.sections.installation:
            sections.append("installation")
            lines.append("## Installation\n")
            lines.append("```bash")
            lines.append(f"git clone https://github.com/{repo_info.owner}/{repo_info.repo}.git")
            lines.append(f"cd {repo_info.repo}")
            lines.append("```")
            lines.append("")

        if config.sections.contributing:
            sections.append("contributing")
            lines.append("## Contributing\n")
            lines.append("Contributions are welcome! Please open an issue or submit a pull request.")
            lines.append("")

        if config.sections.license:
            sections.append("license")
            lines.append("## License\n")
            lines.append("See [LICENSE](LICENSE) for details.")
            lines.append("")

        content = "\n".join(lines)
        return content, sections


class Container:
    """Dependency injection container wiring all components together.

    Instantiates infrastructure, analyser, generator, and application
    layer objects and exposes them as public attributes.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialise the container and wire all dependencies.

        Args:
            settings: Application settings.
        """
        logger.info("Initialising DI container")

        # Infrastructure
        self.github_auth = GitHubAuthenticator(settings.app_id, settings.get_private_key() if settings.app_id else "")
        self.github_client = GitHubClient(self.github_auth)
        self.webhook_verifier: WebhookVerifier | None = (
            WebhookVerifier(settings.webhook_secret) if settings.webhook_secret else None
        )
        self.config_loader = ConfigLoader(self.github_client)

        # Analysers
        self.repo_scanner = _RepoScanner(self.github_client)
        self.file_parser = _FileParser(self.github_client)
        self.commit_analyzer = _CommitAnalyzer(self.github_client)
        self.tech_detector = _TechDetector()
        self.ci_detector = _CIDetector()
        self.api_detector = _APIDetector(self.github_client)

        # Generators
        self.readme_generator = _ReadmeGenerator()

        # Application
        self.orchestrator = GenerationOrchestrator(
            self.repo_scanner,
            self.file_parser,
            self.commit_analyzer,
            self.tech_detector,
            self.ci_detector,
            self.api_detector,
            self.readme_generator,
            self.config_loader,
        )
        self.pr_workflow = PRWorkflow(self.github_client)
        self.webhook_handler = WebhookHandler(self.orchestrator, self.pr_workflow, self.github_client)

        logger.info("DI container initialised successfully")
