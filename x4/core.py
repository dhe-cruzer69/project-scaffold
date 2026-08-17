from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskType(str, Enum):
    CODE_REFACTOR = "code_refactor"
    CODE_GENERATION = "code_generation"
    FACTUAL_QUERY = "factual_query"
    GENERAL_CHAT = "general_chat"


@dataclass(frozen=True)
class TaskDNA:
    task_type: TaskType
    complexity: float
    reasoning_required: float
    risk: float
    quality_requirement: float


@dataclass(frozen=True)
class Constitution:
    max_cost_usd: float = 0.50
    max_latency_ms: int = 30_000
    min_quality: float = 0.85
    min_reliability: float = 0.90
    max_risk: float = 0.30
    allowed_providers: frozenset[str] = frozenset({"ollama", "groq"})


@dataclass(frozen=True)
class Candidate:
    provider: str
    model: str
    cost: float
    quality: float
    reliability: float
    latency_ms: int
    risk: float
    capabilities: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Decision:
    provider: str
    model: str
    expected_cost: float
    expected_quality: float
    expected_reliability: float
    expected_latency_ms: int
    expected_risk: float
    rationale: str


@dataclass
class Outcome:
    request_id: str
    provider: str
    model: str
    success: bool
    verified: bool
    quality: float
    latency_ms: int
    cost: float
    metadata: dict[str, Any] = field(default_factory=dict)
