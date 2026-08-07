"""AriexCore expert model definitions.

The blueprint describes a fleet of five specialized models (Meaw, Fab, Ops,
Sony, Helex) sharing a unified multimodal backbone (UME). Locally we cannot
materialize trillion-parameter MoE weights, so each "expert" here is a
logical capability profile that maps to the best available provider/model
and carries a lightweight routing signature.

Each expert is a frozen dataclass so the router/fleet can reason about it
without instantiating heavy objects.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExpertModel:
    """A single AriexCore expert model profile."""

    name: str  # e.g. "meaw"
    role: str  # short human-readable purpose
    capability: str  # routing tag: reasoning | enterprise | creative | general | fast
    keywords: tuple[str, ...]  # classification hints for the auto-router
    preferred_provider: str  # "ollama" | "openai" | "anthropic"
    preferred_model: str  # model name on that provider
    think: bool = False  # Meaw-style hidden chain-of-thought scratchpad
    top_k: int = 1  # MoE-style routing width (kept symbolic)
    weight: float = 1.0  # relative routing weight for tie-breaking


# --- The five AriexCore experts -------------------------------------------

MEAW = ExpertModel(
    name="meaw",
    role="The Reasoning Colossus — deep reasoning, math, science, complex code",
    capability="reasoning",
    keywords=(
        "prove", "proof", "theorem", "derive", "reason", "logic", "scientific",
        "physics", "math", "algorithm", "architecture", "design pattern",
        "why", "explain deeply", "optimize", "review", "refactor", "complex",
    ),
    preferred_provider="ollama",
    preferred_model="hermes3:8b",
    think=True,
    top_k=2,
    weight=2.0,
)

FAB = ExpertModel(
    name="fab",
    role="Enterprise Intelligence — business, SQL, documents, compliance, RAG",
    capability="enterprise",
    keywords=(
        "sql", "query", "database", "enterprise", "business", "compliance",
        "legal", "regulatory", "financial", "report", "document", "hr",
        "policy", "contract", "forecast", "budget", "audit", "rag",
    ),
    preferred_provider="anthropic",
    preferred_model="claude-3-5-haiku-latest",
    top_k=3,
    weight=1.5,
)

OPS = ExpertModel(
    name="ops",
    role="Creative Powerhouse — design, fiction, poetry, marketing, UX",
    capability="creative",
    keywords=(
        "design", "ui", "ux", "logo", "poster", "story", "poem", "fiction",
        "creative", "write a story", "marketing", "advert", "brand", "color",
        "layout", "prototype", "imagery", "script", "tone", "aesthetic",
    ),
    preferred_provider="openai",
    preferred_model="gpt-4o-mini",
    think=True,
    weight=1.2,
)

SONY = ExpertModel(
    name="sony",
    role="Versatile Assistant — general knowledge, conversation, daily tasks",
    capability="general",
    keywords=(
        "hello", "hi", "what is", "who is", "define", "explain", "chat",
        "help", "summarize", "translate", "general", "conversation",
        "recommend", "tips", "how do i", "tell me about",
    ),
    preferred_provider="ollama",
    preferred_model="hermes3:8b",
    weight=1.0,
)

HELEX = ExpertModel(
    name="helex",
    role="Light Speed Specialist — quick lookups, classification, on-device",
    capability="fast",
    keywords=(
        "quick", "short", "yes or no", "true or false", "classify", "label",
        "lookup", "definition", "fast", "status", "check", "convert", "parse",
    ),
    preferred_provider="ollama",
    preferred_model="hermes3:8b",
    weight=0.6,
)

# Ordered list: the canonical fleet order used by the router for cascading.
FLEET: dict[str, ExpertModel] = {m.name: m for m in (MEAW, FAB, OPS, SONY, HELEX)}

# Cascade ladder: when a lighter model is unsure, escalate up this chain.
CASCADE = ("helex", "sony", "meaw")


def get_expert(name: str) -> ExpertModel:
    """Return an expert by name.

    Raises
    ------
    KeyError
        If ``name`` is not a known expert.
    """
    return FLEET[name.lower()]


def all_experts() -> list[ExpertModel]:
    """Return all experts in canonical fleet order."""
    return list(FLEET.values())
