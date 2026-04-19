"""Project structure section generator for README documents."""

from __future__ import annotations

from src.domain.entities import FileNode, RepoInfo, Section
from src.generators.templates import STRUCTURE_TEMPLATE

__all__ = ["StructureGenerator"]

# Directories to skip in the tree rendering
_IGNORED_DIRS: frozenset[str] = frozenset(
    {
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        ".env",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".eggs",
        "dist",
        "build",
        ".next",
        ".nuxt",
        "target",
        "coverage",
        ".coverage",
        "htmlcov",
    }
)

# Brief descriptions for well-known directories
_DIR_DESCRIPTIONS: dict[str, str] = {
    "src": "Source code",
    "lib": "Library code",
    "app": "Application code",
    "tests": "Test suite",
    "test": "Test suite",
    "docs": "Documentation",
    "doc": "Documentation",
    "scripts": "Utility scripts",
    "config": "Configuration",
    "public": "Static assets",
    "static": "Static files",
    "templates": "HTML templates",
    "migrations": "Database migrations",
    "assets": "Assets",
    "bin": "Executables",
    "cmd": "CLI commands",
    "pkg": "Package code",
    "internal": "Internal packages",
    "api": "API layer",
}

_MAX_DEPTH = 3


class StructureGenerator:
    """Generates the Project Structure section as an ASCII tree."""

    ORDER = 30

    def generate(self, repo_info: RepoInfo) -> Section:
        """Generate the project structure section.

        Renders the repository file tree as an ASCII tree diagram,
        limited to a depth of 3 levels and skipping common non-essential
        directories.

        Args:
            repo_info: The analyzed repository information.

        Returns:
            A Section containing the rendered structure markdown.
        """
        if not repo_info.tree:
            return Section(
                title="Project Structure",
                content="",
                order=self.ORDER,
                enabled=False,
            )

        tree_str = self._render_tree(repo_info.name, repo_info.tree)
        content = STRUCTURE_TEMPLATE.format(tree=tree_str)

        return Section(
            title="Project Structure",
            content=content,
            order=self.ORDER,
            enabled=True,
        )

    def _render_tree(self, root_name: str, nodes: list[FileNode]) -> str:
        """Render a list of FileNode objects as an ASCII tree.

        Args:
            root_name: The name to use for the root directory.
            nodes: Top-level file nodes to render.

        Returns:
            A string representing the ASCII tree.
        """
        lines: list[str] = [f"{root_name}/"]
        filtered = self._filter_and_sort(nodes)
        self._render_nodes(filtered, "", lines, depth=1)
        return "\n".join(lines)

    def _render_nodes(
        self,
        nodes: list[FileNode],
        prefix: str,
        lines: list[str],
        depth: int,
    ) -> None:
        """Recursively render nodes into ASCII tree lines.

        Args:
            nodes: The nodes to render at this level.
            prefix: The current indentation prefix string.
            lines: Accumulator list of rendered lines.
            depth: Current depth (1-based). Stops at _MAX_DEPTH.
        """
        for i, node in enumerate(nodes):
            is_last = i == len(nodes) - 1
            connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "

            # Add description comment for known directories
            comment = ""
            if node.is_dir and node.name in _DIR_DESCRIPTIONS:
                comment = f"  # {_DIR_DESCRIPTIONS[node.name]}"

            suffix = "/" if node.is_dir else ""
            lines.append(f"{prefix}{connector}{node.name}{suffix}{comment}")

            if node.is_dir and node.children and depth < _MAX_DEPTH:
                extension = "    " if is_last else "\u2502   "
                child_prefix = prefix + extension
                filtered_children = self._filter_and_sort(node.children)
                self._render_nodes(filtered_children, child_prefix, lines, depth + 1)

    def _filter_and_sort(self, nodes: list[FileNode]) -> list[FileNode]:
        """Filter out ignored directories and sort directories first.

        Args:
            nodes: The list of file nodes to filter and sort.

        Returns:
            A filtered and sorted list of file nodes.
        """
        filtered = [n for n in nodes if not (n.is_dir and n.name in _IGNORED_DIRS)]
        # Directories first, then files, alphabetical within each group
        return sorted(filtered, key=lambda n: (not n.is_dir, n.name.lower()))
