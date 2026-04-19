"""RepoDoc AI domain layer — entities, enums, interfaces, and exceptions."""

from src.domain.entities import (
    CommitInfo,
    FileNode,
    GenerationResult,
    ReadmeDocument,
    RepoInfo,
    Section,
    TechStack,
)
from src.domain.enums import (
    CIProvider,
    Framework,
    LicenseType,
    PackageManager,
    ProjectType,
)
from src.domain.exceptions import (
    ConfigurationError,
    GenerationError,
    GitHubAPIError,
    RepoDocError,
    ScanError,
)
from src.domain.interfaces import (
    ICommitAnalyzer,
    IFileParser,
    IGitHubClient,
    IReadmeGenerator,
    IRepoScanner,
    ISectionGenerator,
    ITechDetector,
)

__all__ = [
    # Entities
    "CommitInfo",
    "FileNode",
    "GenerationResult",
    "ReadmeDocument",
    "RepoInfo",
    "Section",
    "TechStack",
    # Enums
    "CIProvider",
    "Framework",
    "LicenseType",
    "PackageManager",
    "ProjectType",
    # Exceptions
    "ConfigurationError",
    "GenerationError",
    "GitHubAPIError",
    "RepoDocError",
    "ScanError",
    # Interfaces
    "ICommitAnalyzer",
    "IFileParser",
    "IGitHubClient",
    "IReadmeGenerator",
    "IRepoScanner",
    "ISectionGenerator",
    "ITechDetector",
]
