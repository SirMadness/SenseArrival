"""
voice.py — ElevenLabs TTS (text→audio bytes) + STT (audio→transcript).

BL-005 implementation:
  - tts(): ElevenLabs text_to_speech.convert() in live mode; cached M4A in REPLAY mode.
  - stt(): ElevenLabs speech_to_text.convert() in live mode; hardcoded transcript in REPLAY mode.

OFFLINE_MODE constraints (ADR-001):
  - No ElevenLabs client is instantiated at import scope — only on first live call.
  - REPLAY mode returns cached audio or hardcoded transcript without any network call.
  - The ELEVENLABS_API_KEY is read lazily (at call time), never at import.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path

from sense_arrival.config import Backend, settings

logger = logging.getLogger(__name__)

_STATIC = Path(__file__).parent / "static"
# Offline cached audio — generated at build time via macOS `say` + afconvert.
# Named .m4a (AAC/MP4 container). Mime type: audio/mp4.
_AUDIO_CACHE_M4A = _STATIC / "audio" / "briefing_cached.m4a"

# ElevenLabs voice to use for TTS (Rachel — warm, clear, hotel-appropriate)
_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs "Rachel" voice
_TTS_MODEL = "eleven_multilingual_v2"   # Best quality model

# Return type constants
MIME_MP3 = "audio/mpeg"
MIME_M4A = "audio/mp4"


async def tts(text: str, *, backend: Backend | None = None) -> tuple[bytes, str]:
    """
    Convert text to audio bytes via ElevenLabs TTS.

    Returns (audio_bytes, mime_type) tuple so callers can set the correct
    Content-Type header regardless of whether the source is live or cached.

    REPLAY mode: returns cached M4A bytes (audio/mp4).
    CLAUDE/OLLAMA mode: calls ElevenLabs generate() → returns MP3 bytes (audio/mpeg).

    Never instantiates the ElevenLabs client at import scope.
    """
    effective = backend or settings.default_backend

    if effective == Backend.REPLAY:
        return _load_cached_audio(), MIME_M4A

    # Live path — lazy client instantiation (OFFLINE_MODE safety: never imported at module scope)
    return await _tts_elevenlabs(text)


async def stt(audio_bytes: bytes, *, backend: Backend | None = None) -> str:
    """
    Transcribe audio bytes to text via ElevenLabs Scribe STT.

    REPLAY mode: returns hardcoded demo transcript (zero network).
    CLAUDE/OLLAMA mode: calls ElevenLabs speech_to_text.convert().

    Never instantiates the ElevenLabs client at import scope.
    """
    effective = backend or settings.default_backend

    if effective == Backend.REPLAY:
        return (
            "Guest mentioned they'd love to get out on a bike tomorrow morning "
            "if weather permits — they asked specifically about local road cycling routes."
        )

    return await _stt_elevenlabs(audio_bytes)


# ---------------------------------------------------------------------------
# Offline helpers
# ---------------------------------------------------------------------------

def _load_cached_audio() -> bytes:
    """Return pre-recorded M4A bytes for offline TTS playback (TD-006)."""
    if _AUDIO_CACHE_M4A.exists():
        return _AUDIO_CACHE_M4A.read_bytes()
    logger.warning(
        "TD-006: cached audio file not found at %s — returning silent frame. "
        "Commit briefing_cached.m4a to resolve.",
        _AUDIO_CACHE_M4A,
    )
    return _silent_frame()


def _silent_frame() -> bytes:
    """
    Minimal valid MP4/M4A-like fallback frame.
    Returns bytes that won't crash the audio element but will be inaudible.
    The real file (briefing_cached.m4a) should always be present.
    """
    # Return a minimal silent filler — 44 bytes of pseudo-audio
    # This is a last-resort guard; the real file should be committed.
    return bytes(44)


# ---------------------------------------------------------------------------
# ElevenLabs live paths (lazy-imported — never at module scope)
# ---------------------------------------------------------------------------

async def _tts_elevenlabs(text: str) -> tuple[bytes, str]:
    """
    Call ElevenLabs TTS and return (mp3_bytes, audio/mpeg).
    Falls back to cached audio on any failure.
    """
    if not settings.elevenlabs_api_key:
        logger.warning(
            "ELEVENLABS_API_KEY not set — falling back to cached audio for TTS."
        )
        return _load_cached_audio(), MIME_M4A

    try:
        # Import inside function: ElevenLabs client is NEVER imported at module scope.
        # This preserves the OFFLINE_MODE guarantee (ADR-001).
        from elevenlabs import ElevenLabs  # noqa: PLC0415

        client = ElevenLabs(api_key=settings.elevenlabs_api_key)

        # collect() returns bytes; convert() returns Iterator[bytes]
        audio_chunks = client.text_to_speech.convert(
            voice_id=_VOICE_ID,
            text=text,
            model_id=_TTS_MODEL,
            output_format="mp3_44100_128",
        )
        audio_bytes = b"".join(audio_chunks)
        logger.info("ElevenLabs TTS: generated %d bytes for text length %d", len(audio_bytes), len(text))
        return audio_bytes, MIME_MP3

    except Exception as exc:
        logger.error(
            "ElevenLabs TTS failed (%s: %s) — falling back to cached audio.",
            type(exc).__name__,
            exc,
        )
        return _load_cached_audio(), MIME_M4A


async def _stt_elevenlabs(audio_bytes: bytes) -> str:
    """
    Call ElevenLabs Scribe STT and return transcript string.
    Falls back to hardcoded demo transcript on any failure.
    """
    if not settings.elevenlabs_api_key:
        logger.warning(
            "ELEVENLABS_API_KEY not set — returning hardcoded transcript for STT."
        )
        return _hardcoded_transcript()

    try:
        # Import inside function: never at module scope (OFFLINE_MODE safety).
        from elevenlabs import ElevenLabs  # noqa: PLC0415

        client = ElevenLabs(api_key=settings.elevenlabs_api_key)

        # ElevenLabs Scribe STT: speech_to_text.convert(model_id=..., file=...)
        # `file` accepts a tuple of (filename, bytes, mime_type) or a file-like object
        audio_file = ("recording.webm", io.BytesIO(audio_bytes), "audio/webm")

        result = client.speech_to_text.convert(
            model_id="scribe_v1",
            file=audio_file,
        )
        transcript = result.text if hasattr(result, "text") else str(result)
        logger.info("ElevenLabs STT: transcript length %d chars", len(transcript))
        return transcript

    except Exception as exc:
        logger.error(
            "ElevenLabs STT failed (%s: %s) — returning hardcoded transcript.",
            type(exc).__name__,
            exc,
        )
        return _hardcoded_transcript()


def _hardcoded_transcript() -> str:
    """
    Hardcoded fallback transcript for OFFLINE_MODE or when STT fails.
    This is the deterministic demo path per ADR-001.
    """
    return (
        "Guest mentioned they'd love to get out on a bike tomorrow morning "
        "if weather permits — they asked specifically about local road cycling routes."
    )
