"""Self-test for the ARIEX AI service layer.

Run from the project root:

    python test_ai.py

Useful to verify the router, provider health checks, and fallback logic
are wired up correctly.
"""

import asyncio
import sys

from arx.ai import AIRouter, OllamaProvider, OpenAIProvider, AnthropicProvider


async def main() -> None:
    router = AIRouter(
        providers=[
            OllamaProvider(),
            OpenAIProvider(),
            AnthropicProvider(),
        ]
    )

    print("=== Provider health ===")
    for provider in router.providers:
        ok = await provider.health()
        print(f"  {provider.name:<10} healthy={ok}")

    print("\n=== Generate via router (default route) ===")
    try:
        text = await router.generate("Say hello in one short sentence.")
        print(f"  response: {text[:200]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  generate failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
