"""AriexCore ModelFleet orchestrator.

Binds the five expert profiles to provider backends and exposes a single
``fleet.generate(query)`` entry point. The fleet:

- classifies the query into a capability (reasoning / enterprise /
  creative / general / fast),
- routes it to the matching expert,
- applies model cascading (Helex -> Sony -> Meaw) when an expert is
  uncertain or its provider is unavailable,
- reports health across all experts.

This is a working, local manifestation of the blueprint's "specialized
model fleet + auto-model router" on top of the existing provider layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger

from .models import all_experts, get_expert, ExpertModel, CASCADE
from .provider import Provider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider


@dataclass
class FleetResult:
    """Outcome of a fleet generation call."""

    text: str  # the generated response
    expert: str  # which expert finally produced it
    provider: str  # which provider backend served it
    routed_via: str  # capability tag used for routing
    cascade: list[str]  # ordered list of experts tried before success


def _default_providers() -> dict[str, Provider]:
    """Build a provider registry keyed by provider name."""
    reg: dict[str, Provider] = {}
    for p in (OllamaProvider(), OpenAIProvider(), AnthropicProvider()):
        reg[p.name] = p
    return reg


class ModelFleet:
    """AriexCore expert fleet: routing + cascading + health reporting."""

    def __init__(
        self,
        providers: dict[str, Provider] | None = None,
        experts: list[ExpertModel] | None = None,
    ) -> None:
        # Preserve backward-compatible default provider order.
        self._providers: dict[str, Provider] = providers or _default_providers()
        # Keep the canonical order for reports and cascading.
        self._experts: list[ExpertModel] = experts or all_experts()

    # -- Public API ---------------------------------------------------------

    async def generate(self, prompt: str, *, expert: str | None = None, **kwargs: Any) -> FleetResult:
        """Generate a response for ``prompt``.

        Parameters
        ----------
        prompt:
            The user-facing query.
        expert:
            Optional explicit expert name. When omitted, the auto-router
            picks the best expert for the query.
        **kwargs:
            Passed through to the underlying provider.

        Returns
        -------
        FleetResult
            The response plus routing metadata (expert, provider, cascade).
        """
        target = get_expert(expert) if expert else self._classify(prompt)
        routed_via = target.capability

        # Model cascading: try the target, then escalate up the ladder.
        cascade: list[str] = []
        candidates = self._cascade_order(target)
        for exp in candidates:
            cascade.append(exp.name)
            provider = self._resolve_provider(exp)
            if provider is None:
                logger.debug("No provider for expert '{}', skipping", exp.name)
                continue
            if not await provider.health():
                logger.debug("Provider '{}' unhealthy for '{}'", provider.name, exp.name)
                continue
            try:
                text = await provider.generate(
                    self._build_system(exp, prompt),
                    model=exp.preferred_model,
                    **kwargs,
                )
                return FleetResult(
                    text=text,
                    expert=exp.name,
                    provider=provider.name,
                    routed_via=routed_via,
                    cascade=cascade,
                )
            except Exception as exc:  # noqa: BLE001 - fallback should be robust
                logger.warning("Expert '{}' failed: {}", exp.name, exc)

        raise RuntimeError("No expert in the fleet could serve the request.")

    async def health(self) -> dict[str, dict[str, Any]]:
        """Report provider + expert health as a nested dict."""
        report: dict[str, dict[str, Any]] = {}
        for exp in self._experts:
            provider = self._resolve_provider(exp)
            ok = bool(provider) and await provider.health()
            report[exp.name] = {
                "capability": exp.capability,
                "provider": provider.name if provider else None,
                "healthy": ok,
            }
        return report

    # -- Internals ----------------------------------------------------------

    def _classify(self, prompt: str) -> ExpertModel:
        """Route a query to the best expert using lightweight keyword scoring."""
        text = prompt.lower()
        best: ExpertModel | None = None
        best_score = 0.0
        for exp in self._experts:
            score = sum(1 for kw in exp.keywords if kw.lower() in text)
            weighted = score * exp.weight
            if weighted > best_score:
                best_score = weighted
                best = exp

        # No keyword matched -> default to the general assistant (Sony).
        if best is None:
            return get_expert("sony")
        return best

    def _cascade_order(self, target: ExpertModel) -> list[ExpertModel]:
        """Return experts to try: target first, then escalation up the ladder."""
        names = [target.name]
        for name in CASCADE:
            if name not in names:
                names.append(name)
        return [get_expert(n) for n in names]

    def _resolve_provider(self, exp: ExpertModel) -> Provider | None:
        """Return the provider backend for an expert, or ``None``."""
        return self._providers.get(exp.preferred_provider)

    def _build_system(self, exp: ExpertModel, prompt: str) -> str:
        """Build a prompt that frames the request for the expert's role."""
        if exp.think:
            return (
                f"You are {exp.name}, AriexCore's {exp.role}. "
                f"Think step-by-step before answering. User: {prompt}"
            )
        return f"You are {exp.name}, AriexCore's {exp.role}. User: {prompt}"


# Convenience singleton used by agents.
fleet = ModelFleet()

