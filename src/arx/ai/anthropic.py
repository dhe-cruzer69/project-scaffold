"""Anthropic provider (cloud fallback).

Uses the official ``anthropic`` async client. Reports unhealthy when the
API key is missing so the router can fall back to a local model.
"""

from __future__ import annotations

import os
from typing import Any

from .provider import Provider

DEFAULT_MODEL = "claude-3-5-haiku-latest"


class AnthropicProvider(Provider):
    """Async provider backed by the Anthropic API."""

    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from anthropic import AsyncAnthropic

            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        client = self._get_client()
        message = await client.messages.create(
            model=kwargs.pop("model", self.model),
            max_tokens=kwargs.pop("max_tokens", 1024),
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return "".join(block.text for block in message.content if getattr(block, "type", "") == "text")

    async def health(self) -> bool:
        return bool(self.api_key)
