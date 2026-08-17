from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from x4.core import Candidate, Constitution, TaskType
from x4.runtime import AuditLedger, EconomicOptimizer, PolicyViolation, PolicyWall, PythonVerifier


def test_policy_rejects_instead_of_clamping() -> None:
    wall = PolicyWall(Constitution(max_cost_usd=0.01))
    with pytest.raises(PolicyViolation):
        wall.authorize({"estimated_budget": 0.02})


def test_optimizer_selects_lowest_cost_viable_candidate() -> None:
    optimizer = EconomicOptimizer()
    dna = type("DNA", (), {"quality_requirement": 0.85})()
    candidates = [
        Candidate("groq", "m", 0.004, 0.92, 0.98, 2000, 0.20),
        Candidate("ollama", "m", 0.001, 0.91, 0.95, 1500, 0.10),
    ]
    decision = optimizer.select(candidates, dna, 0.01)
    assert decision.provider == "ollama"


def test_python_verifier_uses_ast() -> None:
    verifier = PythonVerifier()
    assert verifier.verify({"task_type": TaskType.CODE_GENERATION.value}, "def add(a, b):\n    return a + b") ["passed"]
    assert not verifier.verify({"task_type": TaskType.CODE_GENERATION.value}, "def broken(:") ["passed"]


def test_ledger_is_append_only_jsonl() -> None:
    from x4.core import Outcome
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "outcomes.jsonl"
        ledger = AuditLedger(str(path))
        ledger.append(Outcome("r1", "ollama", "m", True, True, 1.0, 10, 0.0))
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        assert '"request_id": "r1"' in lines[0]
