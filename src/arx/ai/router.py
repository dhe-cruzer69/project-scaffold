"""Router that centralizes provider selection and fallback.

Agents call ``await ai.generate(prompt)`` and the router decides which
provider to use. The default order is offline-first: prefer the local
Ollama model, and only fall back to cloud providers when a specialized
capability is needed or the local provider is unavailable.
"""

from __future__ import annotations

from loguru import logger

from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .provider import Provider


class AIRouter:
    """Selects a provider based on priority and health."""

    def __init__(
        self,
        providers: list[Provider] | None = None,
        strict: bool = False,
    ) -> None:
        # Default order: local first, cloud fallbacks after.
        self.providers: list[Provider] = providers or [
            OllamaProvider(),
            OpenAIProvider(),
            AnthropicProvider(),
        ]
        # When strict, do not silently fall back to another provider.
        self.strict = strict

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a completion using the first available provider."""
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                if not await provider.health():
                    logger.debug("Provider '{}' unhealthy, skipping", provider.name)
                    continue
                logger.debug("Using provider '{}'", provider.name)
                return await provider.generate(prompt, **kwargs)
            except Exception as exc:  # noqa: BLE001 - fallback should be robust
                last_error = exc
                logger.warning("Provider '{}' failed: {}", provider.name, exc)
                if self.strict:
                    raise

        if last_error:
            raise last_error
        raise RuntimeError("No AI provider is available/healthy.")


# Convenience singleton used by agents.
ai = AIRouter()
