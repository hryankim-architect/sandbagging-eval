"""Model backends — dependency-free ``complete(prompt) -> str`` callables.

Plug one of these into ``responder.LLMResponder`` to run the *same* framing protocol
and scorer against a real model instead of the mock. ``ollama_complete`` talks to a
local Ollama server (no extra Python dependency, no external web fetch). A frontier
API is just another ``complete`` callable.
"""
from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable

ModelClient = Callable[[str], str]


def ollama_complete(model: str, host: str = "http://localhost:11434",
                    timeout: float = 180.0) -> ModelClient:
    """Return a complete(prompt)->str that calls a local Ollama /api/generate.

    Deterministic (temperature 0). Runs on the user's machine against a locally
    served model — not an external web fetch.
    """
    url = host.rstrip("/") + "/api/generate"

    def complete(prompt: str) -> str:
        payload = json.dumps({
            "model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0},
        }).encode("utf-8")
        req = urllib.request.Request(  # noqa: S310 — local Ollama endpoint
            url, data=payload, headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8")).get("response", "")

    return complete
