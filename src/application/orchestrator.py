"""Main generation orchestrator for RepoDoc AI.

Coordinates repo scanning, analysis, and README generation into a
single ``generate`` use case.
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

__all__ = ["GenerationOrchestrator", "GenerationResult"]


@dataclass
class GenerationResult:
    """Result of a README generation run."""

    readme_content: str
    sections: list[str] = field(default_factory=list)
    tech_stack: dict = field(default_factory=dict)
    languages: dict = field(default_factory=dict)
    branch: str = "repodoc/update-readme"


@dataclass
class RepoInfo:
    """Aggregated repository information used to generate the README."""

    owner: str
    repo: str
    tree: list[dict] = field(default_factory=list)
    parsed_configs: dict = field(default_factory=dict)
    tech_stack: dict = field(default_factory=dict)
    languages: dict = field(default_factory=dict)
    commits: list[dict] = field(default_factory=list)
    ci_info: dict = field(default_factory=dict)
    api_endpoints: list[dict] = field(default_factory=list)


class GenerationOrchestrator:
    """Orchestrates the full README generation pipeline.

    Coordinates multiple analysers and detectors to gather repository
    information, then delegates to a README generator to produce the
    final output.
    """

    def __init__(
        self,
        scanner,
        file_parser,
        commit_analyzer,
        tech_detector,
        ci_detector,
        api_detector,
        readme_generator,
        config_loader,
    ) -> None:
        """Initialise the orchestrator.

        Args:
            scanner: Repository tree scanner.
            file_parser: Configuration file parser (package.json, pyproject.toml, etc.).
            commit_analyzer: Commit history analyser.
            tech_detector: Technology stack detector.
            ci_detector: CI/CD configuration detector.
            api_detector: API endpoint detector.
            readme_generator: README content generator.
            config_loader: Per-repo configuration loader.
        """
        self._scanner = scanner
        self._file_parser = file_parser
        self._commit_analyzer = commit_analyzer
        self._tech_detector = tech_detector
        self._ci_detector = ci_detector
        self._api_detector = api_detector
        self._readme_generator = readme_generator
        self._config_loader = config_loader

    async def generate(self, owner: str, repo: str, installation_id: int) -> GenerationResult:
        """Run the full README generation pipeline.

        Args:
            owner: Repository owner.
            repo: Repository name.
            installation_id: GitHub App installation ID.

        Returns:
            A ``GenerationResult`` containing the generated README and metadata.
        """
        logger.info("Starting README generation for %s/%s", owner, repo)

        # 1. Load per-repo config
        config = await self._config_loader.load(owner, repo)
        if not config.enabled:
            logger.info("RepoDoc is disabled for %s/%s", owner, repo)
            return GenerationResult(readme_content="", branch=config.branch)

        # 2. Scan repo tree
        logger.info("Scanning repository tree for %s/%s", owner, repo)
        tree = await self._scanner.scan(owner, repo, config)

        # 3. Parse config files (package.json, pyproject.toml, etc.)
        logger.info("Parsing configuration files for %s/%s", owner, repo)
        parsed_configs = await self._file_parser.parse(owner, repo, tree)

        # 4. Detect tech stack
        logger.info("Detecting tech stack for %s/%s", owner, repo)
        tech_stack = await self._tech_detector.detect(tree, parsed_configs)

        # 5. Analyse commits
        logger.info("Analysing commits for %s/%s", owner, repo)
        commits = await self._commit_analyzer.analyze(owner, repo)

        # 6. Detect CI/CD configuration
        logger.info("Detecting CI/CD for %s/%s", owner, repo)
        ci_info = await self._ci_detector.detect(tree, parsed_configs)

        # 7. Detect API endpoints (optional)
        api_endpoints: list[dict] = []
        if config.sections.api_docs:
            logger.info("Detecting API endpoints for %s/%s", owner, repo)
            api_endpoints = await self._api_detector.detect(owner, repo, tree)

        # 8. Build RepoInfo
        repo_info = RepoInfo(
            owner=owner,
            repo=repo,
            tree=tree,
            parsed_configs=parsed_configs,
            tech_stack=tech_stack,
            languages=tech_stack.get("languages", {}),
            commits=commits,
            ci_info=ci_info,
            api_endpoints=api_endpoints,
        )

        # 9. Generate README
        logger.info("Generating README content for %s/%s", owner, repo)
        readme_content, sections = await self._readme_generator.generate(repo_info, config)

        result = GenerationResult(
            readme_content=readme_content,
            sections=sections,
            tech_stack=tech_stack,
            languages=repo_info.languages,
            branch=config.branch,
        )

        logger.info("README generation complete for %s/%s (%d sections)", owner, repo, len(sections))
        return result
