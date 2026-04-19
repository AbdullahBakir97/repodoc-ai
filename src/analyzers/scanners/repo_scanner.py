"""Repository scanner — fetches file tree and metadata from GitHub."""

from __future__ import annotations

import logging

from src.domain.entities import FileNode
from src.domain.exceptions import ScanError
from src.domain.interfaces import IGitHubClient, IRepoScanner

__all__ = ["RepoScanner"]

logger = logging.getLogger(__name__)


class RepoScanner(IRepoScanner):
    """Scans a GitHub repository for its file tree and metadata.

    Uses the GitHub API to retrieve the directory tree (up to 2 levels deep)
    and repository metadata such as description, topics, default branch, and
    homepage.
    """

    def __init__(self, github_client: IGitHubClient) -> None:
        self._client = github_client

    async def scan(self, owner: str, repo: str) -> tuple[list[FileNode], dict]:
        """Scan a repository and return its file tree and metadata.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            A tuple of (file tree, metadata dict).

        Raises:
            ScanError: If scanning fails.
        """
        try:
            repo_data = await self._client.get_repo(owner, repo)
            tree_data = await self._client.get_tree(owner, repo)

            metadata = {
                "description": repo_data.get("description", ""),
                "topics": repo_data.get("topics", []),
                "default_branch": repo_data.get("default_branch", "main"),
                "homepage": repo_data.get("homepage"),
                "has_readme": False,
                "existing_readme": None,
            }

            tree = self._build_tree(tree_data, max_depth=2)

            # Check for existing README
            for node in tree:
                if node.name.lower() in ("readme.md", "readme.rst", "readme.txt"):
                    metadata["has_readme"] = True
                    try:
                        metadata["existing_readme"] = (
                            await self._client.get_file_content(
                                owner, repo, node.path
                            )
                        )
                    except Exception:
                        logger.warning("Could not read existing README")
                    break

            return tree, metadata

        except ScanError:
            raise
        except Exception as exc:
            raise ScanError(f"Failed to scan {owner}/{repo}: {exc}") from exc

    def _build_tree(
        self, tree_data: list[dict], max_depth: int = 2
    ) -> list[FileNode]:
        """Build a list of FileNode objects from raw GitHub tree data.

        Args:
            tree_data: Raw tree entries from the GitHub API.
            max_depth: Maximum directory depth to include.

        Returns:
            A list of top-level FileNode objects with nested children.
        """
        nodes_by_path: dict[str, FileNode] = {}
        root_nodes: list[FileNode] = []

        # Sort so directories come first, then by path
        sorted_entries = sorted(tree_data, key=lambda e: e.get("path", ""))

        for entry in sorted_entries:
            path = entry.get("path", "")
            depth = path.count("/")

            if depth >= max_depth:
                continue

            is_dir = entry.get("type") == "tree"
            name = path.rsplit("/", 1)[-1] if "/" in path else path
            size = entry.get("size", 0) if not is_dir else 0

            node = FileNode(
                path=path,
                name=name,
                is_dir=is_dir,
                size=size,
            )
            nodes_by_path[path] = node

            # Find parent
            if "/" in path:
                parent_path = path.rsplit("/", 1)[0]
                parent = nodes_by_path.get(parent_path)
                if parent and parent.is_dir:
                    parent.children.append(node)
                else:
                    root_nodes.append(node)
            else:
                root_nodes.append(node)

        return root_nodes
