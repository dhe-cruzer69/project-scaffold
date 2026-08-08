"""Self-test for the ARIEX AI service layer.

Run from the project root:

    python test_ai.py

Useful to verify the router, provider health checks, and fallback logic
are wired up correctly.
"""

import asyncio
import sys
from pathlib import Path

# Ensure the `arx` package under `src/` is importable when running from the
# project root without installing the package into the environment.
SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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
