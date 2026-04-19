"""File parser — reads and parses configuration files from a repository."""

from __future__ import annotations

import json
import logging
from typing import Any

from src.domain.exceptions import ScanError
from src.domain.interfaces import IFileParser, IGitHubClient

__all__ = ["FileParser"]

logger = logging.getLogger(__name__)

# Mapping of config filenames to their parser method names
_PARSERS: dict[str, str] = {
    "package.json": "_parse_package_json",
    "pyproject.toml": "_parse_pyproject_toml",
    "Cargo.toml": "_parse_cargo_toml",
    "go.mod": "_parse_go_mod",
    "composer.json": "_parse_composer_json",
    "Gemfile": "_parse_gemfile",
}


class FileParser(IFileParser):
    """Reads and parses configuration files from a GitHub repository.

    Supports package.json, pyproject.toml, Cargo.toml, go.mod,
    composer.json, and Gemfile.
    """

    def __init__(self, github_client: IGitHubClient) -> None:
        self._client = github_client

    async def parse(self, owner: str, repo: str, path: str) -> dict:
        """Parse a configuration file and return structured data.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: Path to the file within the repository.

        Returns:
            A dict of parsed fields.

        Raises:
            ScanError: If parsing fails.
        """
        filename = path.rsplit("/", 1)[-1] if "/" in path else path
        parser_name = _PARSERS.get(filename)

        if parser_name is None:
            logger.warning("No parser for file: %s", filename)
            return {}

        try:
            content = await self._client.get_file_content(owner, repo, path)
            parser = getattr(self, parser_name)
            return parser(content)
        except ScanError:
            raise
        except Exception as exc:
            raise ScanError(
                f"Failed to parse {path} in {owner}/{repo}: {exc}"
            ) from exc

    @staticmethod
    def _parse_package_json(content: str) -> dict[str, Any]:
        """Parse a package.json file.

        Args:
            content: Raw file content.

        Returns:
            Dict with name, version, description, scripts, dependencies.
        """
        data = json.loads(content)
        return {
            "name": data.get("name", ""),
            "version": data.get("version", ""),
            "description": data.get("description", ""),
            "scripts": data.get("scripts", {}),
            "dependencies": {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            },
        }

    @staticmethod
    def _parse_pyproject_toml(content: str) -> dict[str, Any]:
        """Parse a pyproject.toml file.

        Args:
            content: Raw file content.

        Returns:
            Dict with name, version, description, dependencies, python_requires.
        """
        # Simple TOML parsing without external dependency
        result: dict[str, Any] = {
            "name": "",
            "version": "",
            "description": "",
            "dependencies": [],
            "python_requires": "",
        }

        lines = content.splitlines()
        current_section = ""

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("["):
                current_section = stripped.strip("[]").strip()
                continue

            if "=" not in stripped:
                continue

            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if current_section == "project":
                if key == "name":
                    result["name"] = value
                elif key == "version":
                    result["version"] = value
                elif key == "description":
                    result["description"] = value
                elif key == "requires-python":
                    result["python_requires"] = value
            elif current_section in (
                "project.dependencies",
                "tool.poetry.dependencies",
            ):
                result["dependencies"].append(key)

        return result

    @staticmethod
    def _parse_cargo_toml(content: str) -> dict[str, Any]:
        """Parse a Cargo.toml file.

        Args:
            content: Raw file content.

        Returns:
            Dict with name, version, description.
        """
        result: dict[str, Any] = {"name": "", "version": "", "description": ""}
        current_section = ""

        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith("["):
                current_section = stripped.strip("[]").strip()
                continue

            if "=" not in stripped:
                continue

            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if current_section == "package":
                if key in result:
                    result[key] = value

        return result

    @staticmethod
    def _parse_go_mod(content: str) -> dict[str, Any]:
        """Parse a go.mod file.

        Args:
            content: Raw file content.

        Returns:
            Dict with module and go_version.
        """
        result: dict[str, Any] = {"module": "", "go_version": ""}

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("module "):
                result["module"] = stripped.split(maxsplit=1)[1]
            elif stripped.startswith("go "):
                result["go_version"] = stripped.split(maxsplit=1)[1]

        return result

    @staticmethod
    def _parse_composer_json(content: str) -> dict[str, Any]:
        """Parse a composer.json file.

        Args:
            content: Raw file content.

        Returns:
            Dict with name and description.
        """
        data = json.loads(content)
        return {
            "name": data.get("name", ""),
            "description": data.get("description", ""),
        }

    @staticmethod
    def _parse_gemfile(content: str) -> dict[str, Any]:
        """Parse a Gemfile.

        Args:
            content: Raw file content.

        Returns:
            Dict with ruby_version if specified.
        """
        result: dict[str, Any] = {"ruby_version": ""}

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("ruby "):
                # e.g. ruby '3.2.0' or ruby "3.2.0"
                version = stripped.split(maxsplit=1)[1].strip("'\"")
                result["ruby_version"] = version
                break

        return result
