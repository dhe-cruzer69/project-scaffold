"""Abstract provider interface for the ARIEX AI service layer.

All LLM providers (Ollama, OpenAI, Anthropic, ...) implement this
interface so agents can call ``await ai.generate(prompt)`` without
knowing which provider is behind the router.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """Base class for a single LLM provider."""

    name: str = "base"

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a completion for ``prompt``.

        Parameters
        ----------
        prompt:
            The user-facing prompt to send to the model.
        **kwargs:
            Provider-specific options (temperature, max_tokens, model, ...).

        Returns
        -------
        str
            The generated text content.
        """
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> bool:
        """Return ``True`` if the provider is reachable/ready."""
        raise NotImplementedError
