"""Self-test for the AriexCore model fleet.

Run from the project root:

    python test_fleet.py

Verifies:
- expert classification / auto-routing
- model cascading (Helex -> Sony -> Meaw)
- health reporting across all experts
- backward compatibility with the generic router
"""

import asyncio

from arx.ai import (
    fleet,
    all_experts,
    get_expert,
    CASCADE,
    FLEET,
    ExpertModel,
)


async def main() -> None:
    print("=== AriexCore Model Fleet ===")
    print(f"Experts: {', '.join(e.name for e in all_experts())}")
    print(f"Cascade ladder: {CASCADE}")
    print(f"Fleet registry: {list(FLEET.keys())}")

    print("\n=== Classification (auto-router) ===")
    samples = {
        "reasoning": "Prove the Pythagorean theorem and derive the limit.",
        "enterprise": "Write a SQL query to forecast quarterly revenue.",
        "creative": "Write a short poem about a poster design.",
        "general": "What is the capital of France?",
        "fast": "Classify this as a label: type, category, status.",
    }
    for expected, prompt in samples.items():
        expert = fleet._classify(prompt)
        status = "OK" if expert.capability == expected else "MISMATCH"
        print(f"  [{status}] expected={expected:10s} got={expert.capability:10s} ({expert.name})")

    print("\n=== Health report ===")
    report = await fleet.health()
    for name, info in report.items():
        print(f"  {name:<10} capability={info['capability']:<10} provider={info['provider']:<10} healthy={info['healthy']}")

    print("\n=== Fleet generation (routing + cascading) ===")
    try:
        result = await fleet.generate("Prove that the square root of 2 is irrational.")
        print(f"  expert   : {result.expert}")
        print(f"  provider : {result.provider}")
        print(f"  routed_via: {result.routed_via}")
        print(f"  cascade  : {result.cascade}")
        print(f"  response : {result.text[:200]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  fleet generate failed: {exc}")

    print("\n=== Backward compatibility (generic router 'ai') ===")
    from arx.ai import ai

    try:
        text = await ai.generate("Say hello in one short sentence.")
        print(f"  ai.generate -> {text[:200]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  ai.generate failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
