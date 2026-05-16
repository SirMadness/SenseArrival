# Notes

**Updated:** 2026-05-16

---

**Topic:** Hackathon constraints (Hospitality 2030 @ Rosewood Sand Hill)
**Date:** 2026-05-16
**Info:** Problem Statement #1 — Hyper-Personalized Arrival Orchestration. Hacking 10:30 AM, submissions due **5:00 PM** (hard, no post-deadline hardening — Round 1 judging starts 5:00 PM in separate rooms). Round 1 weights: Live Demo 45% / Creativity 35% / Impact 20%; ~3-min live demo + 1–2 min Q&A; top 6 → Round 2 (equal weights). Public repo required; only built-today work counts; **Streamlit banned**; basic RAG/chatbot = anti-projects; synthetic/rights-cleared data only. Sponsors: Anthropic, ElevenLabs, Greycroft.
**Related DDs:** DD-001, DD-003

---

**Topic:** Locked product concept
**Date:** 2026-05-16
**Info:** "First Five Minutes by SenseArrival" — arrival **choreography engine** (not a chatbot). Inputs: guest profile + arrival context + staff observations. Outputs: arrival mood, role-based staff cards (valet, front desk, dining, housekeeping, concierge, MOD), suppression panel ("what NOT to offer"), optional guest message, "what changed & why" diff. Headline demo branch = **Delay-to-Delight** (baseline → inject delay → re-plan → staff voice note → cards update → diff → TTS revised briefing). Persona = returning guest "Ms. Chen". Sand Hill local anchors: Asaya Spa, Madera, Afternoon Tea w/ Flamingo Estate, Ridge Rosé Reveal, Friday Nights @ Madera, Bluejay Bikes.
**Related DDs:** DD-001, DD-002

---

**Topic:** Stack decision (architect ADR-001)
**Date:** 2026-05-16
**Info:** Recommended: **Python 3.11 + FastAPI + Jinja2/HTMX + Anthropic SDK + ElevenLabs Python SDK + Pydantic v2**, single-process, no frontend build. Browser mic → `MediaRecorder` → POST → ElevenLabs Scribe STT (server-side), with **mandatory typed-text fallback** on the same code path. Cut order: never cut re-plan diff; cut mic STT → guest message → suppression panel last. Full ADR: `_proj/deliverables/02-architecture/adr/ADR-001-stack-selection.md`.
**Related DDs:** DD-004 (LOCKED)

---

**Topic:** LLM resilience — 3-tier pluggable backend
**Date:** 2026-05-16
**Info:** User confirmed **Ollama is running locally** on the demo machine. Resilience tiers, switchable by env/UI with no code change: **(1) Anthropic Claude cloud = primary/showcased path** (expected robust; Anthropic is a sponsor → also aids Creativity/Impact framing); **(2) Ollama local = dynamic fallback** — keeps the re-plan genuinely "live" with zero network if cloud is hostile; **(3) fixture-replay OFFLINE_MODE = deterministic last resort** (pre-computed baseline/replan JSON, cached TTS MP3). Test all three before the judging room; demo on Claude unless network proves unstable.
**Related DDs:** DD-004

<!-- Notes Format Reference
  Core fields (required on every note):
    Topic, Info, Related DDs

  Optional fields:
    Date        — when the note was captured (use for snapshots and dated events)
    Active RFCs — cross-reference to open RFCs when applicable

  Entries are separated by --- dividers.
  Timestamp the file (Updated header) on each update.
  Only append new information — do not re-log already captured content.
-->
