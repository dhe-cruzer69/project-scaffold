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

# Fallback models tried (in order) when DEFAULT_MODEL is not installed on the
# local Ollama server. Keeps the router functional across machines that have a
# different set of models pulled locally.
FALLBACK_MODELS = ("llama3.2:latest", "llama3.1:latest", "qwen2.5-coder:1.5b")


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
        self._resolved_model: str | None = None

    async def _resolve_model(self) -> str:
        """Return an installed model, falling back if the default is missing."""
        if self._resolved_model is not None:
            return self._resolved_model

        candidates = (self.model,) + FALLBACK_MODELS
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                tags = await client.get(f"{self.base_url}/api/tags")
                tags.raise_for_status()
                installed = {m["name"] for m in tags.json().get("models", [])}
            except (httpx.HTTPError, KeyError, TypeError):
                installed = set()

        for name in candidates:
            if name in installed:
                self._resolved_model = name
                return name

        # None of the known models are installed; return the configured default
        # so the caller sees the model's own error (e.g. "not found").
        self._resolved_model = self.model
        return self.model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Send a chat request and return the assistant's text."""
        model = await self._resolve_model()
        payload = {
            "model": kwargs.pop("model", model),
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
