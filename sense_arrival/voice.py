"""
voice.py — ElevenLabs TTS (text→audio bytes) + STT (audio→transcript).

BL-001 scope: stub functions that return fixture audio / hardcoded transcripts
in replay mode.  Live ElevenLabs paths are wired here for BL-002 to complete.
"""
from __future__ import annotations

from pathlib import Path

from sense_arrival.config import Backend, settings

_STATIC = Path(__file__).parent / "static"
_AUDIO_CACHE = _STATIC / "audio" / "briefing_cached.mp3"


async def tts(text: str, *, backend: Backend | None = None) -> bytes:
    """
    Convert text to MP3 audio bytes via ElevenLabs TTS.

    Replay mode: returns cached MP3 bytes (or empty bytes if file absent).
    Live mode: calls ElevenLabs generate() — BL-002 implementation.
    """
    effective = backend or settings.default_backend

    if effective == Backend.REPLAY:
        if _AUDIO_CACHE.exists():
            return _AUDIO_CACHE.read_bytes()
        # Return a minimal silent MP3 frame so the endpoint doesn't error
        return _silent_mp3()

    raise NotImplementedError(
        "tts() live ElevenLabs path not yet implemented — BL-002 scope."
    )


async def stt(audio_bytes: bytes, *, backend: Backend | None = None) -> str:
    """
    Transcribe audio bytes to text via ElevenLabs STT (Scribe).

    Replay mode: returns hardcoded demo transcript.
    Live mode: calls ElevenLabs speech_to_text.convert() — BL-002 implementation.
    """
    effective = backend or settings.default_backend

    if effective == Backend.REPLAY:
        return (
            "Guest mentioned they'd love to get out on a bike tomorrow morning "
            "if weather permits — they asked specifically about local road cycling routes."
        )

    raise NotImplementedError(
        "stt() live ElevenLabs path not yet implemented — BL-002 scope."
    )


def _silent_mp3() -> bytes:
    """Minimal valid ID3v2 + silent MP3 frame (44 bytes). Prevents 500 errors."""
    # ID3v2.3 minimal header (no tags) + one silent MPEG1 Layer3 frame
    return bytes([
        0x49, 0x44, 0x33, 0x03, 0x00, 0x00,  # ID3v2.3 header
        0x00, 0x00, 0x00, 0x00,               # size=0
        0xFF, 0xFB, 0x90, 0x00,               # MPEG1 L3 frame header
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # silence data
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])
