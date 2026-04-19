"""Abstract interfaces for RepoDoc AI."""

from abc import ABC, abstractmethod

from src.domain.entities import (
    CommitInfo,
    FileNode,
    ReadmeDocument,
    RepoInfo,
    Section,
    TechStack,
)

__all__ = [
    "IRepoScanner",
    "IFileParser",
    "ICommitAnalyzer",
    "ITechDetector",
    "ISectionGenerator",
    "IReadmeGenerator",
    "IGitHubClient",
]


class IRepoScanner(ABC):
    """Scans a repository's file tree and metadata."""

    @abstractmethod
    async def scan(self, owner: str, repo: str) -> tuple[list[FileNode], dict]:
        """Scan a repository and return its file tree and metadata.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            A tuple of (file tree, metadata dict).
        """


class IFileParser(ABC):
    """Parses configuration files from a repository."""

    @abstractmethod
    async def parse(self, owner: str, repo: str, path: str) -> dict:
        """Parse a configuration file and return structured data.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: Path to the file within the repository.

        Returns:
            A dict of parsed fields.
        """


class ICommitAnalyzer(ABC):
    """Analyzes commit history of a repository."""

    @abstractmethod
    async def analyze(self, owner: str, repo: str, count: int = 20) -> list[CommitInfo]:
        """Analyze recent commits.

        Args:
            owner: Repository owner.
            repo: Repository name.
            count: Number of recent commits to analyze.

        Returns:
            A list of CommitInfo objects.
        """


class ITechDetector(ABC):
    """Detects the technology stack from file tree and config data."""

    @abstractmethod
    def detect(self, tree: list[FileNode], config_data: dict) -> TechStack:
        """Detect the technology stack.

        Args:
            tree: The repository file tree.
            config_data: Parsed configuration file data.

        Returns:
            A TechStack describing the detected technologies.
        """


class ISectionGenerator(ABC):
    """Generates a single README section."""

    @abstractmethod
    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate a README section from repo info.

        Args:
            repo_info: Complete repository analysis result.

        Returns:
            A Section for the README.
        """


class IReadmeGenerator(ABC):
    """Generates a complete README document."""

    @abstractmethod
    def generate(self, repo_info: RepoInfo) -> ReadmeDocument:
        """Generate a complete README document.

        Args:
            repo_info: Complete repository analysis result.

        Returns:
            A ReadmeDocument with all sections.
        """


class IGitHubClient(ABC):
    """Client for interacting with the GitHub API."""

    @abstractmethod
    async def get_tree(self, owner: str, repo: str, ref: str = "HEAD") -> list[dict]:
        """Get the file tree of a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ref: Git reference (branch, tag, or SHA).

        Returns:
            A list of tree entry dicts.
        """

    @abstractmethod
    async def get_repo(self, owner: str, repo: str) -> dict:
        """Get repository metadata.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            A dict of repository metadata.
        """

    @abstractmethod
    async def get_commits(self, owner: str, repo: str, count: int = 20) -> list[dict]:
        """Get recent commits.

        Args:
            owner: Repository owner.
            repo: Repository name.
            count: Number of commits to retrieve.

        Returns:
            A list of commit dicts.
        """

    @abstractmethod
    async def get_file_content(self, owner: str, repo: str, path: str) -> str:
        """Get the content of a file.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: File path within the repository.

        Returns:
            The file content as a string.
        """

    @abstractmethod
    async def create_branch(self, owner: str, repo: str, branch: str, from_ref: str) -> None:
        """Create a new branch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch: New branch name.
            from_ref: Source reference to branch from.
        """

    @abstractmethod
    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
        sha: str | None = None,
    ) -> dict:
        """Create or update a file in the repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: File path within the repository.
            content: New file content.
            message: Commit message.
            branch: Target branch.
            sha: SHA of the file to update (None for new files).

        Returns:
            A dict with the commit details.
        """

    @abstractmethod
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> dict:
        """Create a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            title: PR title.
            body: PR body/description.
            head: Head branch.
            base: Base branch.

        Returns:
            A dict with the PR details.
        """
