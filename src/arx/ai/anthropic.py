"""Anthropic provider (cloud fallback).

Uses the official ``anthropic`` async client. Reports unhealthy when the
API key is missing so the router can fall back to a local model.
"""

from __future__ import annotations

import os
from typing import Any

from .provider import Provider

DEFAULT_MODEL = "claude-3-5-haiku-latest"
DEFAULT_MAX_TOKENS = 1024


class AnthropicProvider(Provider):
    """Async provider backed by the Anthropic API."""

    name = "anthropic"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        timeout: float = 120.0,
        max_retries: int = 2,
    ) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = None

    def _get_client(self) -> Any:
        """Lazily build the ``AsyncAnthropic`` client.

        Raises
        ------
        ValueError
            If no API key is configured.
        ImportError
            If the ``anthropic`` package is not installed.
        """
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "No ANTHROPIC_API_KEY configured. Set the environment variable "
                    "or pass an api_key to AnthropicProvider."
                )
            from anthropic import AsyncAnthropic  # pylint: disable=import-error,import-outside-toplevel

            self._client = AsyncAnthropic(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )
        return self._client

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion via the Anthropic Messages API.

        Parameters
        ----------
        prompt:
            The user-facing prompt.
        **kwargs:
            Provider options. ``model`` and ``max_tokens`` default to the
            provider/model and ``DEFAULT_MAX_TOKENS`` respectively. A
            ``system`` prompt is sent via Anthropic's native ``system`` field.

        Returns
        -------
        str
            The concatenated text of the response's text blocks.
        """
        client = self._get_client()
        system = kwargs.pop("system", None)
        max_tokens = kwargs.pop("max_tokens", DEFAULT_MAX_TOKENS)
        if max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer.")

        message = await client.messages.create(
            model=kwargs.pop("model", self.model),
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **({"system": system} if system else {}),
            **kwargs,
        )
        return "".join(
            block.text
            for block in message.content
            if getattr(block, "type", "") == "text" and block.text
        )

    async def health(self) -> bool:
        """Return ``True`` only when the SDK is importable and a key exists.

        This is deliberately stricter than a bare key check (as in
        ``OpenAIProvider``) because Anthropic cannot operate without its
        optional SDK installed.
        """
        if not self.api_key:
            return False
        try:
            import anthropic  # pylint: disable=import-error,import-outside-toplevel,unused-import

            return True
        except ImportError:
            return False
