"""Domain entities for RepoDoc AI."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.enums import (
    CIProvider,
    Framework,
    LicenseType,
    PackageManager,
    ProjectType,
)

__all__ = [
    "FileNode",
    "TechStack",
    "CommitInfo",
    "RepoInfo",
    "Section",
    "ReadmeDocument",
    "GenerationResult",
]


@dataclass(slots=True)
class FileNode:
    """A file or directory in the repo tree."""

    path: str
    name: str
    is_dir: bool
    size: int = 0
    children: list[FileNode] = field(default_factory=list)


@dataclass(slots=True)
class TechStack:
    """Detected technology stack."""

    primary_language: ProjectType
    languages: list[str]  # with percentages like ["Python 60%", "JavaScript 30%"]
    framework: Framework
    package_manager: PackageManager
    ci_provider: CIProvider
    license_type: LicenseType
    has_docker: bool = False
    has_tests: bool = False
    has_docs: bool = False
    python_version: str | None = None
    node_version: str | None = None


@dataclass(slots=True)
class CommitInfo:
    """Summarized commit information."""

    sha: str
    message: str
    author: str
    date: str
    files_changed: int = 0


@dataclass(slots=True)
class RepoInfo:
    """Complete repository analysis result."""

    owner: str
    name: str
    description: str
    default_branch: str
    tech_stack: TechStack
    tree: list[FileNode]
    recent_commits: list[CommitInfo]
    contributors: list[str]
    topics: list[str]
    homepage: str | None = None
    has_readme: bool = False
    existing_readme: str | None = None


@dataclass(slots=True)
class Section:
    """A section of the generated README."""

    title: str
    content: str
    order: int
    enabled: bool = True


@dataclass(slots=True)
class ReadmeDocument:
    """The complete generated README."""

    sections: list[Section]

    @property
    def content(self) -> str:
        """Render all enabled sections in order."""
        return "\n\n".join(s.content for s in sorted(self.sections, key=lambda s: s.order) if s.enabled)


@dataclass(slots=True)
class GenerationResult:
    """Result of README generation."""

    readme: ReadmeDocument
    repo_info: RepoInfo
    branch_name: str = "repodoc/update-readme"
    pr_title: str = "docs: auto-update README.md"
    pr_body: str = ""
