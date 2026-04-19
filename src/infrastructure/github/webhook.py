"""GitHub webhook signature verification using HMAC-SHA256."""

import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)

__all__ = ["WebhookVerifier"]


class WebhookVerifier:
    """Verifies GitHub webhook payloads using HMAC-SHA256 signatures.

    GitHub sends an ``X-Hub-Signature-256`` header with each webhook
    delivery. This class validates the payload against that signature
    to ensure it was genuinely sent by GitHub.
    """

    def __init__(self, secret: str) -> None:
        """Initialise the verifier.

        Args:
            secret: The webhook secret configured in the GitHub App settings.
        """
        self._secret = secret.encode("utf-8")

    def verify(self, payload: bytes, signature: str) -> bool:
        """Verify a webhook payload against its signature.

        Args:
            payload: The raw request body bytes.
            signature: The ``X-Hub-Signature-256`` header value
                       (e.g. ``sha256=abc123...``).

        Returns:
            ``True`` if the signature is valid, ``False`` otherwise.
        """
        if not signature.startswith("sha256="):
            logger.warning("Invalid signature format: missing sha256= prefix")
            return False

        expected = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        received = signature.removeprefix("sha256=")
        is_valid = hmac.compare_digest(expected, received)

        if not is_valid:
            logger.warning("Webhook signature verification failed")
        else:
            logger.debug("Webhook signature verified successfully")

        return is_valid
