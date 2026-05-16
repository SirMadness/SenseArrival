# SenseArrival — Project Instructions

SenseArrival "First Five Minutes" — a hyper-personalized arrival **choreography engine** for Hospitality 2030 @ Rosewood Sand Hill (Problem Statement #1: Hyper-Personalized Arrival Orchestration). Returning-guest profile + arrival context → arrival mood banner + six role-based staff cards, with a live delay-to-delight re-plan and a "what changed & why" diff.

@_proj/CLAUDE.md

## Project-Specific Instructions

### What this is (and is not)
- **Is:** a deterministic, schema-validated arrival choreography engine — fixtures in, structured `ArrivalPlan` out, rendered as role cards + mood banner + re-plan diff. Every model output passes through Pydantic models / Claude tool-use so malformed output cannot break the demo.
- **Is NOT:** a chatbot, a RAG loop, or a free-form chat UI. Banned anti-projects: Streamlit, LangChain/LangGraph/CrewAI, any live flight/weather API, any CRUD / card-authoring / chat-edit UI.

### Hard constraints (hackathon)
- Solo build, **hard 5:00 PM submission today (2026-05-16)** — no post-deadline hardening window.
- Judging weight: **45% Live Demo · 35% Creativity/Originality · 20% Impact.** Zero crashes and room-legible visuals beat code elegance.
- Stack is locked (ADR-001): **Python 3.11 + FastAPI + Jinja2/HTMX + Anthropic SDK + ElevenLabs Python SDK + Pydantic v2.** Single process, no frontend build, one-command restart. Check with architect before expanding.

### The never-cut spine
- Build/demo spine: **BL-001 foundation → BL-002 orchestration → BL-003 re-plan + diff.**
- **TREQ-006 (the "what changed & why" diff panel) is NEVER cut** — it is the creative proof the system acts on changing context. Under time pressure follow the ADR-001 cut order (drop mic STT → guest message → suppression first; keep the mood banner — it's one line).
- Creativity features (FEAT-008 portfolio guest graph / cross-visit synthesis, FEAT-009 selector) are **strictly behind the spine** — they must never displace or delay the re-plan diff.

### Resilience model
- **The showcased demo runs live: Claude cloud + ElevenLabs TTS** (Tier 1, sponsor-aligned — this is the intended path). 3-tier LLM backend, switchable with **no code change** via `BACKEND` (`claude` | `ollama` | `replay`) or `OFFLINE_MODE=true` — see `sense_arrival/config.py`.
- `replay`/`OFFLINE_MODE` is the **resilience fallback for a flaky judging-room network, not the default** — switch to it only if connectivity is unreliable at demo time. The full demo (baseline → re-plan → diff → ≥1 TTS) must still run end-to-end in `replay` with zero outbound network, and that fallback path is rehearsed before the room.
- The typed-text staff-observation path is mandatory and built **before** mic capture; mic→Scribe-STT is a cuttable extension on the identical server path.

### Scope guard (TREQ-019)
- Guest & property **data is fixtures only — no live flight/weather/PMS data integrations**. This is the banned external-data surface; it is *distinct from* the Claude/ElevenLabs backends, which are live and showcased (see Resilience model). One rehearsed demo path; the selector (FEAT-009) is demo-optional and never on the rehearsed path.
- Loadable fixtures are capped at 3 guest dossiers / 3 properties — enforced by `ALLOWED_DOSSIERS` / `ALLOWED_PROPERTIES` in `config.py`. Any expansion is gated on a clean 3/3 scenario test.
- Dossier and per-property "sense of place" cards are Markdown, template-driven, human-editable — loaded as raw prompt context, no parser.

### Canonical scope
- Locked specs are the source of truth for Execution — do not infer scope from code alone:
  - Requirements / features / user-stories: `_proj/deliverables/01-requirements/`
  - Architecture decisions: `_proj/deliverables/02-architecture/adr/` (ADR-001 stack selection, ADR-002 portfolio guest graph)
