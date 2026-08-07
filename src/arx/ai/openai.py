"""OpenAI provider (cloud fallback).

Uses the official ``openai`` async client. When the API key is missing
the provider reports itself unhealthy so the router can fall back to a
local model.
"""

from __future__ import annotations

import os
from typing import Any

from .provider import Provider

DEFAULT_MODEL = "gpt-4o-mini"


class OpenAIProvider(Provider):
    """Async provider backed by the OpenAI API."""

    name = "openai"

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        client = self._get_client()
        completion = await client.chat.completions.create(
            model=kwargs.pop("model", self.model),
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return completion.choices[0].message.content or ""

    async def health(self) -> bool:
        return bool(self.api_key)
