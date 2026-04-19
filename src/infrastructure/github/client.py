"""GitHub API client for RepoDoc AI."""

import base64
import logging

import httpx

from .auth import GitHubAuthenticator

logger = logging.getLogger(__name__)

__all__ = ["GitHubClient"]


class GitHubClient:
    """GitHub API client for RepoDoc AI.

    Provides typed methods for interacting with the GitHub REST API,
    including repository inspection, file management, branch creation,
    and pull request workflows.
    """

    API_BASE = "https://api.github.com"

    def __init__(self, auth: GitHubAuthenticator) -> None:
        """Initialise the client.

        Args:
            auth: Authenticator instance for obtaining installation tokens.
        """
        self._auth = auth
        self._installation_id: int | None = None

    def set_installation_id(self, installation_id: int) -> None:
        """Set the installation ID for subsequent API requests.

        Args:
            installation_id: The GitHub App installation ID.
        """
        self._installation_id = installation_id

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an authenticated request to the GitHub API.

        Args:
            method: HTTP method (GET, POST, PUT, etc.).
            path: API path (e.g. ``/repos/owner/repo``).
            **kwargs: Additional arguments passed to ``httpx.AsyncClient.request``.

        Returns:
            Parsed JSON response as a dictionary, or empty dict for empty responses.

        Raises:
            httpx.HTTPStatusError: If the request returns an error status.
            ValueError: If no installation ID has been set.
        """
        if self._installation_id is None:
            raise ValueError("Installation ID must be set before making API requests")

        token = await self._auth.get_installation_token(self._installation_id)
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method,
                f"{self.API_BASE}{path}",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github+json",
                },
                **kwargs,
            )
            resp.raise_for_status()
            return resp.json() if resp.content else {}

    async def get_repo(self, owner: str, repo: str) -> dict:
        """Get repository metadata.

        Args:
            owner: Repository owner (user or organisation).
            repo: Repository name.

        Returns:
            Repository metadata dictionary.
        """
        return await self._request("GET", f"/repos/{owner}/{repo}")

    async def get_tree(self, owner: str, repo: str, branch: str = "main", recursive: bool = True) -> list[dict]:
        """Get the file tree for a repository branch.

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch: Branch name to retrieve the tree from.
            recursive: Whether to retrieve the full recursive tree.

        Returns:
            List of tree entry dictionaries.
        """
        data = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/git/trees/{branch}",
            params={"recursive": "1" if recursive else "0"},
        )
        return data.get("tree", [])

    async def get_file_content(self, owner: str, repo: str, path: str) -> str | None:
        """Get the decoded content of a file in the repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: File path within the repository.

        Returns:
            Decoded file content as a string, or ``None`` if the file
            cannot be read.
        """
        try:
            data = await self._request("GET", f"/repos/{owner}/{repo}/contents/{path}")
            return base64.b64decode(data["content"]).decode("utf-8")
        except Exception:
            logger.debug("Failed to read file %s/%s/%s", owner, repo, path)
            return None

    async def get_commits(self, owner: str, repo: str, count: int = 20) -> list[dict]:
        """Get recent commits for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            count: Maximum number of commits to return.

        Returns:
            List of commit dictionaries.
        """
        return await self._request(
            "GET",
            f"/repos/{owner}/{repo}/commits",
            params={"per_page": count},
        )

    async def get_languages(self, owner: str, repo: str) -> dict:
        """Get language breakdown for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Dictionary mapping language names to byte counts.
        """
        return await self._request("GET", f"/repos/{owner}/{repo}/languages")

    async def create_branch(self, owner: str, repo: str, branch_name: str, from_sha: str) -> None:
        """Create a new branch from a given SHA.

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch_name: Name for the new branch.
            from_sha: SHA to create the branch from.
        """
        await self._request(
            "POST",
            f"/repos/{owner}/{repo}/git/refs",
            json={"ref": f"refs/heads/{branch_name}", "sha": from_sha},
        )
        logger.info("Created branch %s in %s/%s", branch_name, owner, repo)

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
            content: File content as a string.
            message: Commit message.
            branch: Branch to commit to.
            sha: Existing file SHA (required for updates, omit for creation).

        Returns:
            API response dictionary with commit and content info.
        """
        payload: dict = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha
        return await self._request(
            "PUT",
            f"/repos/{owner}/{repo}/contents/{path}",
            json=payload,
        )

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
            body: PR body / description.
            head: Head branch name.
            base: Base branch name.

        Returns:
            API response dictionary with PR details.
        """
        result = await self._request(
            "POST",
            f"/repos/{owner}/{repo}/pulls",
            json={"title": title, "body": body, "head": head, "base": base},
        )
        logger.info("Created PR #%s in %s/%s", result.get("number"), owner, repo)
        return result

    async def get_default_branch_sha(self, owner: str, repo: str) -> str:
        """Get the SHA of the default branch head.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            The SHA string of the latest commit on the default branch.
        """
        data = await self._request("GET", f"/repos/{owner}/{repo}/git/ref/heads/main")
        return data["object"]["sha"]
