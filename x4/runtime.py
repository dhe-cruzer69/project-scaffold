from __future__ import annotations

import ast
import json
import time
import uuid
from dataclasses import asdict
from pathlib import Path

from .core import Candidate, Constitution, Decision, Outcome, TaskDNA, TaskType


class PolicyViolation(PermissionError):
    pass


class PolicyWall:
    def __init__(self, constitution: Constitution | None = None) -> None:
        self.constitution = constitution or Constitution()

    def authorize(self, request: dict) -> None:
        budget = float(request.get("estimated_budget", 0.10))
        if budget > self.constitution.max_cost_usd:
            raise PolicyViolation(f"budget ${budget:.4f} exceeds hard limit ${self.constitution.max_cost_usd:.4f}")
        provider = request.get("preferred_provider")
        if provider and provider not in self.constitution.allowed_providers:
            raise PolicyViolation(f"provider {provider!r} is not allowed")

    def enforce(self, decision: Decision) -> Decision:
        c = self.constitution
        violations: list[str] = []
        if decision.expected_cost > c.max_cost_usd: violations.append("cost")
        if decision.expected_latency_ms > c.max_latency_ms: violations.append("latency")
        if decision.expected_quality < c.min_quality: violations.append("quality")
        if decision.expected_reliability < c.min_reliability: violations.append("reliability")
        if decision.expected_risk > c.max_risk: violations.append("risk")
        if decision.provider not in c.allowed_providers: violations.append("provider")
        if violations:
            raise PolicyViolation("decision rejected by policy wall: " + ", ".join(violations))
        return decision


class JudgmentEngine:
    def classify(self, prompt: str, task_type: str = "") -> TaskDNA:
        p = prompt.lower()
        if task_type:
            kind = TaskType(task_type)
        elif any(k in p for k in ("refactor", "fix this code", "debug")):
            kind = TaskType.CODE_REFACTOR
        elif any(k in p for k in ("write code", "generate code", "implement")):
            kind = TaskType.CODE_GENERATION
        elif any(k in p for k in ("what is", "who is", "when did")):
            kind = TaskType.FACTUAL_QUERY
        else:
            kind = TaskType.GENERAL_CHAT
        complexity = min(1.0, max(0.0, len(prompt) / 2000))
        code = kind in {TaskType.CODE_REFACTOR, TaskType.CODE_GENERATION}
        return TaskDNA(kind, complexity, 0.7 if code else 0.3, 0.25 if code else 0.10, 0.90 if code else 0.85)


class EconomicOptimizer:
    def select(self, candidates: list[Candidate], dna: TaskDNA, budget: float | None = None) -> Decision:
        viable = [c for c in candidates if c.quality >= dna.quality_requirement and c.reliability >= 0.90 and c.risk <= 0.30 and (budget is None or c.cost <= budget)]
        if not viable:
            raise RuntimeError("no viable provider/model satisfies the requested constraints")
        # Cost first, then quality and latency as tie-breakers.
        viable.sort(key=lambda c: (c.cost, -c.quality, c.latency_ms))
        c = viable[0]
        return Decision(c.provider, c.model, c.cost, c.quality, c.reliability, c.latency_ms, c.risk, f"selected lowest-cost viable candidate ({c.provider}/{c.model})")


class PythonVerifier:
    def verify(self, request: dict, content: str) -> dict:
        checks = [{"name": "non_empty", "passed": len(content.strip()) > 0}]
        kind = request.get("task_type", "")
        if kind in {TaskType.CODE_REFACTOR.value, TaskType.CODE_GENERATION.value}:
            checks.append({"name": "python_ast", "passed": self._python_ok(content)})
        if request.get("expected_keywords"):
            checks.append({"name": "keywords", "passed": all(k in content for k in request["expected_keywords"])})
        score = sum(int(x["passed"]) for x in checks) / len(checks)
        return {"passed": all(x["passed"] for x in checks), "score": score, "checks": checks}

    @staticmethod
    def _python_ok(content: str) -> bool:
        text = content.strip()
        if "```" in text:
            parts = text.split("```")
            candidates = [p for p in parts if p.strip() and not p.lstrip().startswith(("python", "py"))]
            text = candidates[0].strip() if candidates else text
        try:
            ast.parse(text)
            return True
        except SyntaxError:
            return False


class AuditLedger:
    def __init__(self, path: str = "data/x4-outcomes.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, outcome: Outcome) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(outcome), sort_keys=True) + "\n")


class Provider:
    def __init__(self, name: str, model: str, complete, health=lambda: True) -> None:
        self.name, self.model, self._complete, self._health = name, model, complete, health

    def healthy(self) -> bool:
        try:
            return bool(self._health())
        except Exception:
            return False

    def complete(self, prompt: str, system: str = "") -> str:
        return self._complete(prompt, system)


class X4MasterRuntime:
    def __init__(self, providers: dict[str, Provider], ledger: AuditLedger | None = None) -> None:
        self.providers = providers
        self.ledger = ledger or AuditLedger()
        self.policy = PolicyWall()
        self.judgment = JudgmentEngine()
        self.optimizer = EconomicOptimizer()
        self.verifier = PythonVerifier()

    def process(self, request: dict) -> dict:
        request_id = str(uuid.uuid4())
        started = time.perf_counter()
        self.policy.authorize(request)
        dna = self.judgment.classify(request.get("prompt", ""), request.get("task_type", ""))
        candidates = [
            Candidate("ollama", request.get("ollama_model", "llama3.2:3b"), 0.0, 0.70, 0.85, 800, 0.10),
            Candidate("groq", request.get("groq_model", "llama-3.3-70b-versatile"), 0.004, 0.92, 0.98, 2000, 0.20),
        ]
        candidates = [c for c in candidates if c.provider in self.providers and self.providers[c.provider].healthy()]
        decision = self.optimizer.select(candidates, dna, request.get("estimated_budget"))
        self.policy.enforce(decision)
        content = self.providers[decision.provider].complete(request["prompt"], request.get("system_instruction", ""))
        verification = self.verifier.verify(request, content)
        latency_ms = int((time.perf_counter() - started) * 1000)
        outcome = Outcome(request_id, decision.provider, decision.model, verification["passed"], verification["passed"], verification["score"], latency_ms, decision.expected_cost, {"task_type": dna.task_type.value, "checks": verification["checks"]})
        self.ledger.append(outcome)
        return {"response": content, "trace_id": request_id, "decision": asdict(decision), "verification": verification}
