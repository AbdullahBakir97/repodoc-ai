"""Enumeration types for RepoDoc AI domain."""

from enum import StrEnum

__all__ = [
    "ProjectType",
    "Framework",
    "PackageManager",
    "CIProvider",
    "LicenseType",
]


class ProjectType(StrEnum):
    """Supported programming language/project types."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    RUBY = "ruby"
    CSHARP = "csharp"
    PHP = "php"
    UNKNOWN = "unknown"


class Framework(StrEnum):
    """Detected web/application frameworks."""

    FASTAPI = "FastAPI"
    DJANGO = "Django"
    FLASK = "Flask"
    EXPRESS = "Express"
    NEXTJS = "Next.js"
    REACT = "React"
    VUE = "Vue.js"
    ANGULAR = "Angular"
    SPRING = "Spring"
    RAILS = "Rails"
    LARAVEL = "Laravel"
    GIN = "Gin"
    ACTIX = "Actix"
    NONE = "None"


class PackageManager(StrEnum):
    """Package manager types."""

    PIP = "pip"
    POETRY = "poetry"
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    BUN = "bun"
    CARGO = "cargo"
    GO_MOD = "go mod"
    MAVEN = "maven"
    GRADLE = "gradle"
    COMPOSER = "composer"
    BUNDLER = "bundler"
    UNKNOWN = "unknown"


class CIProvider(StrEnum):
    """Continuous integration providers."""

    GITHUB_ACTIONS = "GitHub Actions"
    GITLAB_CI = "GitLab CI"
    CIRCLECI = "CircleCI"
    TRAVIS = "Travis CI"
    JENKINS = "Jenkins"
    NONE = "None"


class LicenseType(StrEnum):
    """Open source license types."""

    MIT = "MIT"
    APACHE2 = "Apache-2.0"
    GPL3 = "GPL-3.0"
    BSD3 = "BSD-3-Clause"
    ISC = "ISC"
    UNLICENSE = "Unlicense"
    PROPRIETARY = "Proprietary"
    UNKNOWN = "Unknown"
