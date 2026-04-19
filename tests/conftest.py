"""Shared test fixtures for RepoDoc AI."""

import pytest

from src.domain.entities import (
    CommitInfo,
    FileNode,
    RepoInfo,
    TechStack,
)
from src.domain.enums import (
    CIProvider,
    Framework,
    LicenseType,
    PackageManager,
    ProjectType,
)


@pytest.fixture
def sample_tree() -> list[FileNode]:
    """Sample file tree for a Python FastAPI project."""
    return [
        FileNode(path="src", name="src", is_dir=True, children=[
            FileNode(path="src/main.py", name="main.py", is_dir=False, size=500),
            FileNode(path="src/models", name="models", is_dir=True, children=[
                FileNode(path="src/models/user.py", name="user.py", is_dir=False, size=300),
            ]),
        ]),
        FileNode(path="tests", name="tests", is_dir=True, children=[
            FileNode(path="tests/test_main.py", name="test_main.py", is_dir=False, size=200),
        ]),
        FileNode(path="pyproject.toml", name="pyproject.toml", is_dir=False, size=800),
        FileNode(path="Dockerfile", name="Dockerfile", is_dir=False, size=200),
        FileNode(path="README.md", name="README.md", is_dir=False, size=1000),
    ]


@pytest.fixture
def sample_tech_stack() -> TechStack:
    """Sample detected tech stack."""
    return TechStack(
        primary_language=ProjectType.PYTHON,
        languages=["Python 70%", "HTML 20%", "JavaScript 10%"],
        framework=Framework.FASTAPI,
        package_manager=PackageManager.PIP,
        ci_provider=CIProvider.GITHUB_ACTIONS,
        license_type=LicenseType.MIT,
        has_docker=True,
        has_tests=True,
        has_docs=False,
        python_version="3.12",
    )


@pytest.fixture
def sample_commits() -> list[CommitInfo]:
    """Sample commit history."""
    return [
        CommitInfo(sha="abc123", message="feat: add user authentication", author="dev1", date="2026-04-18", files_changed=5),
        CommitInfo(sha="def456", message="fix: resolve login crash on empty email", author="dev1", date="2026-04-17", files_changed=2),
        CommitInfo(sha="ghi789", message="docs: update API documentation", author="dev2", date="2026-04-16", files_changed=1),
        CommitInfo(sha="jkl012", message="refactor: clean up database models", author="dev1", date="2026-04-15", files_changed=8),
    ]


@pytest.fixture
def sample_repo_info(sample_tree, sample_tech_stack, sample_commits) -> RepoInfo:
    """Complete sample repo info."""
    return RepoInfo(
        owner="testorg",
        name="test-project",
        description="A test project for unit testing",
        default_branch="main",
        tech_stack=sample_tech_stack,
        tree=sample_tree,
        recent_commits=sample_commits,
        contributors=["dev1", "dev2"],
        topics=["python", "fastapi", "api"],
        has_readme=True,
    )
