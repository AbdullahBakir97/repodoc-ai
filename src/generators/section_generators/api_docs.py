"""API documentation section generator for README documents."""

from __future__ import annotations

import re

from src.domain.entities import FileNode, RepoInfo, Section

__all__ = ["APIDocsGenerator"]

# Patterns to detect API route definitions across frameworks
_ROUTE_PATTERNS: list[re.Pattern[str]] = [
    # FastAPI / Flask decorators: @app.get("/path")
    re.compile(r"@\w+\.(get|post|put|patch|delete)\s*\(\s*[\"']([^\"']+)[\"']"),
    # Express-style: router.get("/path", ...)
    re.compile(r"\w+\.(get|post|put|patch|delete)\s*\(\s*[\"']([^\"']+)[\"']"),
]


class APIDocsGenerator:
    """Generates the API Reference section from detected endpoints."""

    ORDER = 40

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the API documentation section.

        If no API endpoints are detected, the section is disabled.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered API reference markdown,
            or a disabled section if no endpoints are found.
        """
        endpoints = self._detect_endpoints(repo_info)

        if not endpoints:
            return Section(
                title="API Reference",
                content="",
                order=self.ORDER,
                enabled=False,
            )

        lines = [
            "## API Reference",
            "",
            "| Method | Endpoint | Description |",
            "|--------|----------|-------------|",
        ]
        for method, path in endpoints:
            description = self._infer_description(method, path)
            lines.append(f"| {method.upper()} | {path} | {description} |")

        return Section(
            title="API Reference",
            content="\n".join(lines),
            order=self.ORDER,
            enabled=True,
        )

    def _detect_endpoints(self, repo_info: RepoInfo) -> list[tuple[str, str]]:
        """Detect API endpoints from the file tree structure.

        Looks for common API-related file names and directories
        that suggest route definitions.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A list of (method, path) tuples for detected endpoints.
        """
        endpoints: list[tuple[str, str]] = []

        # Look for route/api files in the tree
        api_files = self._find_api_files(repo_info.tree)

        if not api_files:
            return endpoints

        # Generate placeholder endpoints based on file names
        for file_node in api_files:
            name = file_node.name.replace(".py", "").replace(".ts", "").replace(".js", "")
            if name in ("__init__", "index", "main", "app"):
                continue
            base_path = f"/api/{name}"
            endpoints.append(("GET", base_path))
            endpoints.append(("POST", base_path))

        return endpoints

    def _find_api_files(self, nodes: list[FileNode]) -> list[FileNode]:
        """Recursively find files in API-related directories.

        Args:
            nodes: The file tree nodes to search.

        Returns:
            A list of FileNode objects that appear to define API routes.
        """
        api_files: list[FileNode] = []
        api_dir_names = {"routes", "routers", "endpoints", "api", "controllers", "views"}

        for node in nodes:
            if node.is_dir and node.name.lower() in api_dir_names:
                api_files.extend(self._collect_files(node.children))
            elif node.is_dir:
                api_files.extend(self._find_api_files(node.children))

        return api_files

    def _collect_files(self, nodes: list[FileNode]) -> list[FileNode]:
        """Collect all non-directory file nodes.

        Args:
            nodes: The nodes to collect files from.

        Returns:
            A list of file (non-directory) FileNode objects.
        """
        files: list[FileNode] = []
        for node in nodes:
            if not node.is_dir:
                files.append(node)
            else:
                files.extend(self._collect_files(node.children))
        return files

    def _infer_description(self, method: str, path: str) -> str:
        """Infer a brief description from the HTTP method and path.

        Args:
            method: The HTTP method (GET, POST, etc.).
            path: The endpoint path.

        Returns:
            A human-readable description string.
        """
        resource = path.rstrip("/").split("/")[-1] if "/" in path else path
        resource = resource.replace("-", " ").replace("_", " ").title()

        descriptions = {
            "GET": f"List or retrieve {resource}",
            "POST": f"Create {resource}",
            "PUT": f"Update {resource}",
            "PATCH": f"Partially update {resource}",
            "DELETE": f"Delete {resource}",
        }
        return descriptions.get(method.upper(), f"Manage {resource}")
