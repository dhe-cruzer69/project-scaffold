"""Ollama provider backed by the local Ollama HTTP API.

Uses ``httpx.AsyncClient`` so it fits naturally into ARIEX's async
architecture. The default endpoint is ``http://localhost:11434``.
"""

from __future__ import annotations

from typing import Any

import httpx

from .provider import Provider

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "hermes3:8b"
DEFAULT_TIMEOUT = 120.0


class OllamaProvider(Provider):
    """Async provider that talks to a local Ollama server."""

    name = "ollama"

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_URL,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Send a chat request and return the assistant's text."""
        payload = {
            "model": kwargs.pop("model", self.model),
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            **kwargs,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()

        return response.json()["message"]["content"]

    async def health(self) -> bool:
        """Return ``True`` if the Ollama server responds."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
                return response.status_code < 500
        except httpx.HTTPError:
            return False
