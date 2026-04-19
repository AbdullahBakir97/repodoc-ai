"""GitHub App authentication with JWT generation and installation token caching."""

import logging
import time
from dataclasses import dataclass

import httpx
import jwt

logger = logging.getLogger(__name__)

__all__ = ["GitHubAuthenticator"]


@dataclass
class _CachedToken:
    """Cached installation access token with expiry."""

    token: str
    expires_at: float


class GitHubAuthenticator:
    """Handles GitHub App authentication via JWT and installation tokens.

    Generates short-lived JWTs signed with the app's private key, then
    exchanges them for installation access tokens. Tokens are cached and
    refreshed automatically before expiry.
    """

    API_BASE = "https://api.github.com"
    JWT_EXPIRY_SECONDS = 600  # 10 minutes (GitHub max)
    TOKEN_REFRESH_BUFFER = 60  # Refresh 60s before expiry

    def __init__(self, app_id: str, private_key: str) -> None:
        """Initialise the authenticator.

        Args:
            app_id: The GitHub App ID.
            private_key: PEM-encoded RSA private key for the app.
        """
        self._app_id = app_id
        self._private_key = private_key
        self._token_cache: dict[int, _CachedToken] = {}

    def _generate_jwt(self) -> str:
        """Generate a signed JWT for GitHub App authentication.

        Returns:
            A signed JWT string.
        """
        now = int(time.time())
        payload = {
            "iat": now - 60,  # Clock drift allowance
            "exp": now + self.JWT_EXPIRY_SECONDS,
            "iss": self._app_id,
        }
        token = jwt.encode(payload, self._private_key, algorithm="RS256")
        logger.debug("Generated new JWT for app %s", self._app_id)
        return token

    async def get_installation_token(self, installation_id: int) -> str:
        """Get an installation access token, using cache when possible.

        Args:
            installation_id: The GitHub App installation ID.

        Returns:
            A valid installation access token.

        Raises:
            httpx.HTTPStatusError: If the token request fails.
        """
        cached = self._token_cache.get(installation_id)
        if cached and cached.expires_at > time.time() + self.TOKEN_REFRESH_BUFFER:
            logger.debug("Using cached token for installation %d", installation_id)
            return cached.token

        logger.info("Requesting new installation token for installation %d", installation_id)
        app_jwt = self._generate_jwt()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.API_BASE}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {app_jwt}",
                    "Accept": "application/vnd.github+json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        token = data["token"]
        # GitHub tokens expire in 1 hour; parse or default
        expires_at = time.time() + 3600
        self._token_cache[installation_id] = _CachedToken(token=token, expires_at=expires_at)

        logger.info("Cached new token for installation %d", installation_id)
        return token
