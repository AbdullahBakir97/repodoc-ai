"""Custom exceptions for RepoDoc AI."""

__all__ = [
    "RepoDocError",
    "ScanError",
    "GenerationError",
    "GitHubAPIError",
    "ConfigurationError",
]


class RepoDocError(Exception):
    """Base exception for all RepoDoc AI errors."""


class ScanError(RepoDocError):
    """Raised when repository scanning fails."""


class GenerationError(RepoDocError):
    """Raised when README generation fails."""


class GitHubAPIError(RepoDocError):
    """Raised when a GitHub API call fails."""


class ConfigurationError(RepoDocError):
    """Raised when configuration is invalid or missing."""
