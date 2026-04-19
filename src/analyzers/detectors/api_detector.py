"""API detector — finds API routes and endpoints in source code."""

from __future__ import annotations

import logging
import re

from src.domain.entities import FileNode
from src.domain.interfaces import IGitHubClient

__all__ = ["APIDetector"]

logger = logging.getLogger(__name__)

# Patterns for Python API routes
_PYTHON_ROUTE_PATTERNS: list[re.Pattern[str]] = [
    # FastAPI / Flask style: @app.get("/path") or @router.post("/path")
    re.compile(
        r"@(?:app|router)\.(get|post|put|patch|delete)\(\s*[\"']([^\"']+)[\"']"
    ),
    # Django urlpatterns: path("route/", view, name="...")
    re.compile(r"path\(\s*[\"']([^\"']+)[\"']"),
]

# Patterns for JavaScript/TypeScript API routes
_JS_ROUTE_PATTERNS: list[re.Pattern[str]] = [
    # Express style: app.get("/path", ...) or router.post("/path", ...)
    re.compile(
        r"(?:app|router)\.(get|post|put|patch|delete)\(\s*[\"']([^\"']+)[\"']"
    ),
    # Next.js API route export
    re.compile(r"export\s+(?:default\s+)?(?:async\s+)?function\s+(\w+)"),
]

# File extensions to scan
_PYTHON_EXTS = {".py"}
_JS_EXTS = {".js", ".jsx", ".ts", ".tsx"}


class APIDetector:
    """Finds API routes and endpoints in repository source code.

    Scans Python and JavaScript/TypeScript files within the first 2 levels
    of the src/ directory for common API route patterns.
    """

    def __init__(self, github_client: IGitHubClient) -> None:
        self._client = github_client

    async def detect(
        self, owner: str, repo: str, tree: list[FileNode]
    ) -> list[tuple[str, str, str]]:
        """Find API routes in the repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            tree: The repository file tree.

        Returns:
            A list of (method, path, description) tuples.
        """
        candidates = self._find_candidates(tree, max_depth=2)
        routes: list[tuple[str, str, str]] = []

        for file_node in candidates:
            try:
                content = await self._client.get_file_content(
                    owner, repo, file_node.path
                )
                ext = self._get_ext(file_node.name)

                if ext in _PYTHON_EXTS:
                    routes.extend(self._scan_python(content, file_node.path))
                elif ext in _JS_EXTS:
                    routes.extend(self._scan_js(content, file_node.path))
            except Exception:
                logger.debug("Could not scan %s for API routes", file_node.path)

        return routes

    def _find_candidates(
        self, tree: list[FileNode], max_depth: int = 2, current_depth: int = 0
    ) -> list[FileNode]:
        """Find source files that might contain API route definitions.

        Only scans files within src/ directory up to max_depth levels.

        Args:
            tree: File tree nodes.
            max_depth: Maximum depth to scan.
            current_depth: Current recursion depth.

        Returns:
            A list of candidate FileNode objects.
        """
        candidates: list[FileNode] = []

        for node in tree:
            if node.is_dir:
                if current_depth < max_depth:
                    candidates.extend(
                        self._find_candidates(
                            node.children, max_depth, current_depth + 1
                        )
                    )
            else:
                ext = self._get_ext(node.name)
                if ext in _PYTHON_EXTS or ext in _JS_EXTS:
                    # Only include files in src/ or at root level with relevant names
                    if (
                        node.path.startswith("src/")
                        or "routes" in node.path.lower()
                        or "api" in node.path.lower()
                        or "views" in node.path.lower()
                        or "urls" in node.path.lower()
                        or "app" in node.name.lower()
                        or "main" in node.name.lower()
                        or "server" in node.name.lower()
                    ):
                        candidates.append(node)

        return candidates

    @staticmethod
    def _scan_python(
        content: str, file_path: str
    ) -> list[tuple[str, str, str]]:
        """Scan Python source code for API routes.

        Args:
            content: File content.
            file_path: Path for description context.

        Returns:
            A list of (method, path, description) tuples.
        """
        routes: list[tuple[str, str, str]] = []

        for pattern in _PYTHON_ROUTE_PATTERNS:
            for match in pattern.finditer(content):
                groups = match.groups()
                if len(groups) == 2:
                    method, path = groups
                    routes.append((
                        method.upper(),
                        path,
                        f"Defined in {file_path}",
                    ))
                elif len(groups) == 1:
                    # Django-style path
                    routes.append((
                        "ANY",
                        groups[0],
                        f"URL pattern in {file_path}",
                    ))

        return routes

    @staticmethod
    def _scan_js(
        content: str, file_path: str
    ) -> list[tuple[str, str, str]]:
        """Scan JavaScript/TypeScript source code for API routes.

        Args:
            content: File content.
            file_path: Path for description context.

        Returns:
            A list of (method, path, description) tuples.
        """
        routes: list[tuple[str, str, str]] = []

        for pattern in _JS_ROUTE_PATTERNS:
            for match in pattern.finditer(content):
                groups = match.groups()
                if len(groups) == 2:
                    method, path = groups
                    routes.append((
                        method.upper(),
                        path,
                        f"Defined in {file_path}",
                    ))
                elif len(groups) == 1:
                    # Next.js style export
                    func_name = groups[0]
                    method = func_name.upper() if func_name in (
                        "GET", "POST", "PUT", "PATCH", "DELETE"
                    ) else "HANDLER"
                    routes.append((
                        method,
                        file_path,
                        f"Export function {func_name}",
                    ))

        return routes

    @staticmethod
    def _get_ext(name: str) -> str:
        """Get the file extension including the dot.

        Args:
            name: File name.

        Returns:
            Extension string like ".py" or empty string.
        """
        if "." in name:
            return "." + name.rsplit(".", 1)[-1]
        return ""
