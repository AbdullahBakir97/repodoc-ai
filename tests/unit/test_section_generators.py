"""Tests for the README section generators.

These tests verify each section generator produces specific, useful content
across realistic scenarios (missing description, multiple frameworks, monorepo,
empty topics, etc.). The goal mirrors the comment-builder philosophy: every
generated line should be specific, actionable, and informative — not a
boilerplate placeholder.
"""

from __future__ import annotations

import pytest

from src.domain.entities import FileNode, RepoInfo, TechStack
from src.domain.enums import (
    CIProvider,
    Framework,
    LicenseType,
    PackageManager,
    ProjectType,
)
from src.generators.section_generators.features import FeaturesGenerator
from src.generators.section_generators.header import HeaderGenerator
from src.generators.section_generators.installation import InstallationGenerator

# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


def _stack(
    *,
    language: ProjectType = ProjectType.PYTHON,
    framework: Framework = Framework.NONE,
    package_manager: PackageManager = PackageManager.PIP,
    ci: CIProvider = CIProvider.GITHUB_ACTIONS,
    license_type: LicenseType = LicenseType.MIT,
    has_docker: bool = False,
    has_tests: bool = True,
    python_version: str | None = None,
    node_version: str | None = None,
) -> TechStack:
    return TechStack(
        primary_language=language,
        languages=[f"{language.value.title()} 100%"],
        framework=framework,
        package_manager=package_manager,
        ci_provider=ci,
        license_type=license_type,
        has_docker=has_docker,
        has_tests=has_tests,
        has_docs=False,
        python_version=python_version,
        node_version=node_version,
    )


def _repo(
    *,
    name: str = "demo",
    description: str = "A demo project.",
    topics: list[str] | None = None,
    tree: list[FileNode] | None = None,
    stack: TechStack | None = None,
) -> RepoInfo:
    return RepoInfo(
        owner="testorg",
        name=name,
        description=description,
        default_branch="main",
        tech_stack=stack or _stack(),
        tree=tree or [],
        recent_commits=[],
        contributors=[],
        topics=topics or [],
    )


# ------------------------------------------------------------------ #
# HeaderGenerator
# ------------------------------------------------------------------ #


class TestHeader:
    def test_renders_title_and_description(self):
        section = HeaderGenerator().generate(_repo(name="my-cli", description="Useful command-line tool."))
        assert "# my-cli" in section.content
        assert "Useful command-line tool." in section.content

    def test_missing_description_uses_stack_aware_fallback(self):
        repo = _repo(
            description="",
            stack=_stack(language=ProjectType.PYTHON, framework=Framework.FASTAPI),
        )
        section = HeaderGenerator().generate(repo)

        # No "N/A" — synthesised description from stack
        assert "N/A" not in section.content
        assert "Python" in section.content
        assert "FastAPI" in section.content

    def test_missing_description_and_unknown_stack_uses_repo_name(self):
        repo = _repo(
            description="",
            stack=_stack(language=ProjectType.UNKNOWN, framework=Framework.NONE),
        )
        section = HeaderGenerator().generate(repo)

        assert "demo" in section.content  # the repo name
        assert "N/A" not in section.content


# ------------------------------------------------------------------ #
# FeaturesGenerator
# ------------------------------------------------------------------ #


class TestFeatures:
    def test_no_topics_no_dirs_disables_section(self):
        repo = _repo(topics=[], tree=[])
        section = FeaturesGenerator().generate(repo)

        assert section.enabled is False

    def test_topics_get_titlecase_or_override(self):
        repo = _repo(topics=["github-action", "automation", "json-resume"])
        section = FeaturesGenerator().generate(repo)

        # Override applied for github-action
        assert "GitHub Action" in section.content
        # Override applied for json-resume
        assert "JSON Resume support" in section.content
        # Generic Title Case for unmapped topics
        assert "Automation" in section.content

    def test_directory_features_added_when_no_overlap_with_topics(self):
        tree = [
            FileNode(path="auth", name="auth", is_dir=True),
            FileNode(path="api", name="api", is_dir=True),
            FileNode(path="src", name="src", is_dir=True),  # not a key dir
        ]
        repo = _repo(topics=["python"], tree=tree)
        section = FeaturesGenerator().generate(repo)

        assert "Authentication and authorization" in section.content
        assert "REST API layer" in section.content
        assert "Written in Python" in section.content

    def test_features_list_is_capped_at_ten(self):
        # Build 15 unique topics to trigger the cap.
        topics = [f"topic-{i}" for i in range(15)]
        repo = _repo(topics=topics)
        section = FeaturesGenerator().generate(repo)

        bullet_count = sum(1 for line in section.content.split("\n") if line.startswith("- "))
        assert bullet_count <= 10

    def test_no_duplicates_across_topic_and_directory(self):
        tree = [FileNode(path="cli", name="cli", is_dir=True)]
        # Topic also maps to "Command-line interface"
        repo = _repo(topics=["cli"], tree=tree)
        section = FeaturesGenerator().generate(repo)

        cli_count = section.content.lower().count("command-line interface")
        assert cli_count == 1


# ------------------------------------------------------------------ #
# InstallationGenerator
# ------------------------------------------------------------------ #


class TestInstallation:
    def test_python_pip_with_pyproject_uses_editable_install(self):
        tree = [FileNode(path="pyproject.toml", name="pyproject.toml", is_dir=False)]
        repo = _repo(stack=_stack(language=ProjectType.PYTHON, package_manager=PackageManager.PIP), tree=tree)
        section = InstallationGenerator().generate(repo)

        assert "pip install -e ." in section.content

    def test_python_pip_without_pyproject_uses_requirements(self):
        repo = _repo(stack=_stack(language=ProjectType.PYTHON, package_manager=PackageManager.PIP), tree=[])
        section = InstallationGenerator().generate(repo)

        assert "pip install -r requirements.txt" in section.content

    def test_node_yarn_uses_yarn_command(self):
        repo = _repo(
            stack=_stack(
                language=ProjectType.JAVASCRIPT,
                package_manager=PackageManager.YARN,
            )
        )
        section = InstallationGenerator().generate(repo)

        assert "yarn" in section.content
        assert "Node.js" in section.content

    def test_rust_uses_cargo(self):
        repo = _repo(stack=_stack(language=ProjectType.RUST, package_manager=PackageManager.CARGO))
        section = InstallationGenerator().generate(repo)

        assert "cargo build" in section.content
        assert "cargo run" in section.content

    def test_python_version_override_in_prerequisites(self):
        repo = _repo(
            stack=_stack(language=ProjectType.PYTHON, python_version="3.12"),
        )
        section = InstallationGenerator().generate(repo)

        assert "Python 3.12+" in section.content


# ------------------------------------------------------------------ #
# Voice / quality checks
# ------------------------------------------------------------------ #


class TestVoiceQuality:
    @pytest.mark.parametrize(
        "topic,expected_phrase",
        [
            ("github-action", "GitHub Action"),
            ("json-resume", "JSON Resume support"),
            ("cv-generator", "CV / resume generator"),
            ("typescript", "Written in TypeScript"),
        ],
    )
    def test_known_topics_produce_natural_language(self, topic, expected_phrase):
        section = FeaturesGenerator().generate(_repo(topics=[topic]))
        assert expected_phrase in section.content
