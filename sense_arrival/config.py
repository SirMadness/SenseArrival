"""
config.py — Environment config and LLM backend selector.

Supports three backends selected via BACKEND env var (or UI toggle stored in
app.state.backend at runtime):

  claude   — Anthropic Claude cloud (requires ANTHROPIC_API_KEY)
  ollama   — Local Ollama instance (requires OLLAMA_BASE_URL, default
              http://localhost:11434)
  replay   — Fixture-replay: zero outbound network; serves pre-computed JSON

OFFLINE_MODE=true is a shortcut alias that forces backend=replay.

No code change is required to switch backends; set the env var before starting
uvicorn.
"""
from __future__ import annotations

import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()


class Backend(str, Enum):
    CLAUDE = "claude"
    OLLAMA = "ollama"
    REPLAY = "replay"


def _resolve_backend() -> Backend:
    """
    Precedence:
    1. OFFLINE_MODE=true  → replay
    2. BACKEND env var    → claude | ollama | replay
    3. Default            → claude
    """
    if os.getenv("OFFLINE_MODE", "").lower() in ("1", "true", "yes"):
        return Backend.REPLAY

    raw = os.getenv("BACKEND", "claude").lower().strip()
    try:
        return Backend(raw)
    except ValueError:
        # Unknown value; fall back to claude and let runtime fail loudly if key absent
        return Backend.CLAUDE


class Settings:
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    default_backend: Backend = _resolve_backend()

    # Scope guard: only these fixture slugs are loadable (TREQ-019)
    ALLOWED_DOSSIERS: frozenset[str] = frozenset({"ms-chen", "priya-nair", "james-okafor"})
    ALLOWED_PROPERTIES: frozenset[str] = frozenset(
        {"rosewood-sand-hill", "the-carlyle-new-york", "castiglion-del-bosco"}
    )


settings = Settings()
