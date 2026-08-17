from __future__ import annotations

import json
import os
import urllib.request
from urllib.error import HTTPError, URLError

from .runtime import Provider


def ollama(base_url: str = "http://localhost:11434", model: str = "llama3.2:3b") -> Provider:
    def complete(prompt: str, system: str = "") -> str:
        payload = json.dumps({"model": model, "prompt": prompt, "system": system, "stream": False}).encode()
        req = urllib.request.Request(f"{base_url}/api/generate", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode()).get("response", "")

    def health() -> bool:
        try:
            with urllib.request.urlopen(f"{base_url}/api/tags", timeout=3) as response:
                return response.status == 200
        except (OSError, HTTPError, URLError):
            return False

    return Provider("ollama", model, complete, health)


def groq(model: str = "llama-3.3-70b-versatile") -> Provider:
    api_key = os.getenv("GROQ_API_KEY", "")

    def complete(prompt: str, system: str = "") -> str:
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        payload = json.dumps({"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "max_tokens": 2048}).encode()
        req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode())
            return data["choices"][0]["message"]["content"]

    def health() -> bool:
        return bool(api_key)

    return Provider("groq", model, complete, health)
