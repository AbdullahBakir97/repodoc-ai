"""Tech stack detector — analyzes file tree and config to detect technologies."""

from __future__ import annotations

import logging
from collections import Counter

from src.domain.entities import FileNode, TechStack
from src.domain.enums import (
    CIProvider,
    Framework,
    LicenseType,
    PackageManager,
    ProjectType,
)
from src.domain.interfaces import ITechDetector

__all__ = ["TechDetector"]

logger = logging.getLogger(__name__)

# File extension to language mapping
_EXT_TO_LANG: dict[str, ProjectType] = {
    ".py": ProjectType.PYTHON,
    ".js": ProjectType.JAVASCRIPT,
    ".jsx": ProjectType.JAVASCRIPT,
    ".mjs": ProjectType.JAVASCRIPT,
    ".ts": ProjectType.TYPESCRIPT,
    ".tsx": ProjectType.TYPESCRIPT,
    ".go": ProjectType.GO,
    ".rs": ProjectType.RUST,
    ".java": ProjectType.JAVA,
    ".rb": ProjectType.RUBY,
    ".cs": ProjectType.CSHARP,
    ".php": ProjectType.PHP,
}

# Dependency name to framework mapping
_DEP_TO_FRAMEWORK: dict[str, Framework] = {
    "fastapi": Framework.FASTAPI,
    "django": Framework.DJANGO,
    "flask": Framework.FLASK,
    "express": Framework.EXPRESS,
    "next": Framework.NEXTJS,
    "react": Framework.REACT,
    "vue": Framework.VUE,
    "@angular/core": Framework.ANGULAR,
    "spring-boot": Framework.SPRING,
    "rails": Framework.RAILS,
    "laravel/framework": Framework.LARAVEL,
    "gin-gonic/gin": Framework.GIN,
    "actix-web": Framework.ACTIX,
}

# Lock file to package manager mapping
_LOCKFILE_TO_PM: dict[str, PackageManager] = {
    "poetry.lock": PackageManager.POETRY,
    "package-lock.json": PackageManager.NPM,
    "yarn.lock": PackageManager.YARN,
    "pnpm-lock.yaml": PackageManager.PNPM,
    "bun.lockb": PackageManager.BUN,
    "Cargo.lock": PackageManager.CARGO,
    "go.sum": PackageManager.GO_MOD,
    "composer.lock": PackageManager.COMPOSER,
    "Gemfile.lock": PackageManager.BUNDLER,
}

# Config files that hint at package managers (fallback)
_CONFIG_TO_PM: dict[str, PackageManager] = {
    "pyproject.toml": PackageManager.POETRY,
    "setup.py": PackageManager.PIP,
    "requirements.txt": PackageManager.PIP,
    "package.json": PackageManager.NPM,
    "Cargo.toml": PackageManager.CARGO,
    "go.mod": PackageManager.GO_MOD,
    "pom.xml": PackageManager.MAVEN,
    "build.gradle": PackageManager.GRADLE,
    "composer.json": PackageManager.COMPOSER,
    "Gemfile": PackageManager.BUNDLER,
}


class TechDetector(ITechDetector):
    """Detects the technology stack from a repository's file tree and config data.

    Analyzes file extensions, dependency files, lock files, and project
    structure to determine languages, frameworks, package managers, CI,
    license, Docker, tests, and docs.
    """

    def detect(self, tree: list[FileNode], config_data: dict) -> TechStack:
        """Detect the technology stack.

        Args:
            tree: The repository file tree.
            config_data: Parsed configuration file data.

        Returns:
            A TechStack describing the detected technologies.
        """
        all_files = self._flatten(tree)
        file_names = {node.name for node in all_files}
        file_paths = {node.path for node in all_files}

        primary_language, languages = self._detect_languages(all_files)
        framework = self._detect_framework(config_data)
        package_manager = self._detect_package_manager(file_names)
        license_type = self._detect_license(file_names, config_data)
        has_docker = self._detect_docker(file_names)
        has_tests = self._detect_tests(all_files)
        has_docs = self._detect_docs(all_files)

        python_version = config_data.get("pyproject.toml", {}).get(
            "python_requires"
        )
        node_version = None

        return TechStack(
            primary_language=primary_language,
            languages=languages,
            framework=framework,
            package_manager=package_manager,
            ci_provider=CIProvider.NONE,  # Delegated to CIDetector
            license_type=license_type,
            has_docker=has_docker,
            has_tests=has_tests,
            has_docs=has_docs,
            python_version=python_version,
            node_version=node_version,
        )

    def _flatten(self, tree: list[FileNode]) -> list[FileNode]:
        """Flatten a nested file tree into a flat list.

        Args:
            tree: Nested list of FileNode objects.

        Returns:
            A flat list of all FileNode objects.
        """
        result: list[FileNode] = []
        for node in tree:
            result.append(node)
            if node.children:
                result.extend(self._flatten(node.children))
        return result

    def _detect_languages(
        self, files: list[FileNode]
    ) -> tuple[ProjectType, list[str]]:
        """Detect primary language and language distribution.

        Args:
            files: Flat list of all files.

        Returns:
            Tuple of (primary language, list of "Language X%" strings).
        """
        counter: Counter[ProjectType] = Counter()

        for f in files:
            if f.is_dir:
                continue
            ext = "." + f.name.rsplit(".", 1)[-1] if "." in f.name else ""
            lang = _EXT_TO_LANG.get(ext)
            if lang:
                counter[lang] += 1

        if not counter:
            return ProjectType.UNKNOWN, []

        total = sum(counter.values())
        primary = counter.most_common(1)[0][0]
        languages = [
            f"{lang.value.capitalize()} {count * 100 // total}%"
            for lang, count in counter.most_common()
        ]

        return primary, languages

    @staticmethod
    def _detect_framework(config_data: dict) -> Framework:
        """Detect framework from parsed config data dependencies.

        Args:
            config_data: Parsed configuration data keyed by filename.

        Returns:
            The detected Framework or Framework.NONE.
        """
        all_deps: set[str] = set()

        # Gather dependencies from all config files
        for _filename, data in config_data.items():
            deps = data.get("dependencies", {})
            if isinstance(deps, dict):
                all_deps.update(deps.keys())
            elif isinstance(deps, list):
                all_deps.update(deps)

        # Check for framework matches
        for dep_key, framework in _DEP_TO_FRAMEWORK.items():
            if dep_key in all_deps:
                return framework

        return Framework.NONE

    @staticmethod
    def _detect_package_manager(file_names: set[str]) -> PackageManager:
        """Detect package manager from lock files or config files.

        Args:
            file_names: Set of all file names in the repo.

        Returns:
            The detected PackageManager.
        """
        # Prefer lock files (more specific)
        for lockfile, pm in _LOCKFILE_TO_PM.items():
            if lockfile in file_names:
                return pm

        # Fall back to config files
        for config, pm in _CONFIG_TO_PM.items():
            if config in file_names:
                return pm

        return PackageManager.UNKNOWN

    @staticmethod
    def _detect_license(file_names: set[str], config_data: dict) -> LicenseType:
        """Detect license type from LICENSE file content.

        Args:
            file_names: Set of all file names in the repo.
            config_data: Parsed config data (may contain license info).

        Returns:
            The detected LicenseType.
        """
        # Check config data for license field
        for _filename, data in config_data.items():
            license_val = data.get("license", "")
            if isinstance(license_val, str):
                upper = license_val.upper()
                if "MIT" in upper:
                    return LicenseType.MIT
                if "APACHE" in upper:
                    return LicenseType.APACHE2
                if "GPL" in upper:
                    return LicenseType.GPL3
                if "BSD" in upper:
                    return LicenseType.BSD3
                if "ISC" in upper:
                    return LicenseType.ISC

        # Check if LICENSE file exists
        license_files = {"LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE"}
        if file_names & license_files:
            return LicenseType.UNKNOWN  # File exists but content not parsed here

        return LicenseType.UNKNOWN

    @staticmethod
    def _detect_docker(file_names: set[str]) -> bool:
        """Check if Docker is used.

        Args:
            file_names: Set of all file names in the repo.

        Returns:
            True if Dockerfile or docker-compose file exists.
        """
        docker_files = {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"}
        return bool(file_names & docker_files)

    @staticmethod
    def _detect_tests(files: list[FileNode]) -> bool:
        """Check if the repo has tests.

        Args:
            files: Flat list of all files.

        Returns:
            True if test directories or test files exist.
        """
        test_dirs = {"tests", "test", "__tests__", "spec"}
        for f in files:
            if f.is_dir and f.name in test_dirs:
                return True
            if not f.is_dir and (
                f.name.startswith("test_")
                or f.name.endswith("_test.py")
                or ".test." in f.name
                or ".spec." in f.name
            ):
                return True
        return False

    @staticmethod
    def _detect_docs(files: list[FileNode]) -> bool:
        """Check if the repo has documentation.

        Args:
            files: Flat list of all files.

        Returns:
            True if a docs directory exists.
        """
        for f in files:
            if f.is_dir and f.name in ("docs", "documentation", "doc"):
                return True
        return False
