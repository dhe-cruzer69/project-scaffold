"""AI service layer for ARIEX — AriexCore model fleet.

Exposes the provider router and the AriexCore expert fleet so agents can
call either the generic router::

    from arx.ai import ai

    response = await ai.generate("Analyze this GitHub repository.")

or the fleet (auto-routing across the five experts)::

    from arx.ai import fleet

    result = await fleet.generate("Prove the Pythagorean theorem.")

    text, expert, provider = result.text, result.expert, result.provider
"""

from .provider import Provider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .router import AIRouter, ai

# AriexCore fleet additions
from .models import (
    ExpertModel,
    MEAW,
    FAB,
    OPS,
    SONY,
    HELEX,
    FLEET,
    CASCADE,
    get_expert,
    all_experts,
)
from .fleet import ModelFleet, FleetResult, fleet

__all__ = [
    "Provider",
    "OllamaProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "AIRouter",
    "ai",
    # AriexCore fleet
    "ExpertModel",
    "MEAW",
    "FAB",
    "OPS",
    "SONY",
    "HELEX",
    "FLEET",
    "CASCADE",
    "get_expert",
    "all_experts",
    "ModelFleet",
    "FleetResult",
    "fleet",
]
