"""Application settings loaded from environment variables and .env file."""

from pydantic_settings import BaseSettings

__all__ = ["Settings"]


class Settings(BaseSettings):
    """Global application settings for RepoDoc AI.

    Values are loaded from environment variables and optionally from a
    ``.env`` file. All fields have sensible defaults for local development.
    """

    app_id: str = ""
    private_key: str = ""
    private_key_path: str = "./private-key.pem"
    webhook_secret: str = ""
    port: int = 8000
    env: str = "development"
    log_level: str = "INFO"
    allowed_origins: str = "*"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode.

        Returns:
            ``True`` if ``env`` is set to ``development``.
        """
        return self.env == "development"

    def get_private_key(self) -> str:
        """Get the PEM-encoded private key.

        If ``private_key`` is set directly (e.g. via env var), it is
        returned with escaped newlines restored. Otherwise the key is
        read from ``private_key_path``.

        Returns:
            The PEM-encoded RSA private key string.

        Raises:
            FileNotFoundError: If ``private_key_path`` does not exist.
        """
        if self.private_key:
            return self.private_key.replace("\\n", "\n")
        with open(self.private_key_path) as f:
            return f.read()
