# Discussion Points

<!-- DD Format Reference
  Core fields (required on every DD):
    Title, Area, Description, Decision, Status, REQS

  Conditional fields (added when applicable):
    Possible Mitigations            — risk/threat DDs listing mitigation options
    Possible Mitigations / Approaches — broader option analysis for complex DDs
    Open questions                  — unresolved questions within the DD scope
    Scope of change                 — estimated impact footprint

  Status values: OPEN | RESOLVED | DEFERRED | REJECTED
  Area values: UX, Architecture, Privacy, Business Logic, Integration, Discovery,
               Template Design, Install / Migration, State Management, etc.

  Sub-decisions: Captured inline in Description prose, labeled "Sub-decision (YYYY-MM-DD):".
  The Decision field stays blank until Status → RESOLVED.
  CRITICAL: Never mark RESOLVED without explicit user confirmation.
-->

## DD-001
- **Status:** RESOLVED
- **Title:** Concept positioning lock: First Five Minutes by SenseArrival
- **Area:** Product Strategy
- **Description:** Hackathon concept for Problem Statement 1 (Hyper-Personalized Arrival Orchestration), tailored to Rosewood Sand Hill Menlo Park. Options: (A) First Five Minutes by SenseArrival as product with Delay-to-Delight as headline demo branch; (B) narrow to Delay-to-Delight only; (C) broader Arrival Mood Calibration. Sub-decision (2026-05-16): Which positioning? Option A. [User-flagged consolidated doc first_five_minutes_sensearrival.md; broadest platform story with one rock-solid demo path; Delay-to-Delight is the 45%-Live-Demo magic moment.]
- **Decision:** Product = First Five Minutes by SenseArrival (arrival choreography engine: arrival mood + role-based staff cards + suppression panel). Headline demo branch = Delay-to-Delight (baseline plan -> inject delay -> live re-plan -> staff voice note -> cards update -> what-changed diff). Platform breadth lives in pitch/Q&A, not the build.
- **REQS:** TREQ-001,TREQ-002,TREQ-003,TREQ-004,TREQ-005,TREQ-006,TREQ-007,TREQ-008,TREQ-018

## DD-002
- **Status:** RESOLVED
- **Title:** ElevenLabs voice layer scope
- **Area:** Scope
- **Description:** How far the voice layer goes given solo builder + ~6hr window + room-based judging fragility. Options: TTS briefing only; TTS + staff voice-note capture (STT); + guest audio confirm; full guest voice agent. Sub-decision (2026-05-16): Scope? TTS staff briefing playback PLUS staff voice-note capture (STT) that re-routes and updates role cards. [Most agentic/differentiated combo per consolidated doc; STT is the only live-audio risk; guest voice agent rejected as too fragile for room judging.]
- **Decision:** Voice = ElevenLabs TTS 'Play Briefing' on role cards (safe, generated text) + staff voice-note capture via STT that classifies the note, re-routes, and updates role cards live. Guest audio confirm = stretch only. Full guest voice agent = REJECTED (room-judging fragility).
- **REQS:** TREQ-009,TREQ-010,TREQ-011

## DD-003
- **Status:** RESOLVED
- **Title:** Build capacity and scoping posture
- **Area:** Project Constraints
- **Description:** Team size calibrates must-have vs defer aggressiveness. Sub-decision (2026-05-16): Capacity? Solo builder. [Ruthless scope: single returning-guest persona (Ms. Chen), fixtures only, one demo path. Cut order: voice -> messaging -> live APIs; never cut the re-plan diff.]
- **Decision:** Solo builder. Ruthless scope: one returning-guest persona (Ms. Chen), Sand Hill local context, fixtures only (no live flight/weather APIs). Cut order if slipping: full guest voice -> guest SMS send -> live APIs -> extra roles. Never cut: re-plan diff, staff brief, one Sand Hill-specific delight.
- **REQS:** TREQ-008,TREQ-015,TREQ-016,TREQ-017

## DD-004
- **Status:** RESOLVED
- **Title:** Implementation tech stack selection
- **Area:** Architecture
- **Description:** Stack that drives all engineering work: Python+FastAPI vs TypeScript+Next.js (or other), incl. ElevenLabs TTS+STT integration path, for a SOLO builder in a ~6hr hackathon window. NO Streamlit (banned anti-project). User requested an architect full analysis before locking. Decision pending architect ADR.
- **Decision:** Stack = Python 3.11 + FastAPI + Jinja2/HTMX + Anthropic SDK + ElevenLabs Python SDK + Pydantic v2, single-process, no frontend build (per ADR-001). NO Streamlit. Resilience = 3-tier pluggable LLM backend: (1) Anthropic Claude cloud = PRIMARY/showcased path (robust + Anthropic is sponsor); (2) Ollama local LLM = dynamic offline fallback (still live re-plan, no network); (3) fixture-replay OFFLINE_MODE = deterministic last-resort. Switchable by env/UI without code change. ElevenLabs STT server-side with mandatory typed-text fallback on same code path.
- **REQS:** TREQ-001,TREQ-011,TREQ-012,TREQ-013,TREQ-014

## DD-005
- **Status:** RESOLVED
- **Title:** Scope guard widening: single Ms. Chen persona -> portfolio guest graph (3 dossiers / 3 properties)
- **Area:** Scope
- **Description:** DD-003 locked a single returning-guest persona (Ms. Chen), fixtures only, one demo path; TREQ-016 encodes that scope guard. User now wants a portfolio guest graph. CONFLICT: new scope vs locked TREQ-016. Sub-decision (2026-05-16): Resolve how? REPLACE TREQ-016 with a widened scope guard. [User chose 3 guests / 3 properties (1 deep arrival property + 2 provenance), expandable ONLY after the 3/3 scenario tests clean; fixtures-only + no-live-API + single REHEARSED demo path are PRESERVED — only the persona-count constraint changes. Narrow-slice spirit of ADR-001 retained.]
- **Decision:** REPLACE TREQ-016 with TREQ-019 — widened scope guard: fixed library of 3 guest dossiers + 3 Rosewood property cards (1 deep arrival + 2 provenance), expandable only after the 3/3 scenario tests clean; fixtures-only / no-live-API / single-rehearsed-path PRESERVED. README (TREQ-024) frames the dual-card model as the PS#1 answer, validated with Rosewood president Radha Arora.
- **REQS:** TREQ-019,TREQ-024

## DD-006
- **Status:** RESOLVED
- **Title:** Portfolio guest graph, cross-visit synthesis, and card data format
- **Area:** Product/Architecture
- **Description:** Guest = profile + prior stays, each stay tagged with a Rosewood property + that site's staff-generated observations; per-property 'sense of place' card library; orchestrator infers a unified cross-visit understanding (e.g. high-end road bike rental -> cyclist; Carlyle concierge logged 'Annie' -> theatre) before choreographing the arrival. Sub-decision (2026-05-16): Synthesis priority? NEW P0, STRICTLY behind the never-cut spine (must not displace BL-001->002->003) [user-blessed]. Sub-decision (2026-05-16): Card format? PROPOSED (pending lock-confirm): dossiers + property cards = Markdown source (editable, judge-visible, raw prompt context, no parser); output/replay fixtures stay JSON; NO runtime chat-create/edit subsystem; 'new guest' = add a .md. Sub-decision (2026-05-16): Property content? agent-researched at BUILD time (analyst), parallel to engineering, no live-demo API risk.
- **Decision:** Guest dossier = profile + cross-property prior stays carrying each site's staff observations (TREQ-020); per-property card = destination local culture/activities, broader than amenities (TREQ-020 EXTENDS TREQ-004); cross-visit synthesis = P0 STRICTLY behind the never-cut spine (TREQ-021); card format = Markdown source / JSON only for offline-replay / NO runtime chat-create-edit subsystem; live staff-voice-note -> dossier demo-shim loop, in-memory, reuses FEAT-004 capture (TREQ-023); per-property 'sense of place' content agent-researched at build time.
- **REQS:** TREQ-020,TREQ-021,TREQ-023

## DD-007
- **Status:** RESOLVED
- **Title:** Interactive multi vs single-path demo
- **Area:** UX/Scope
- **Description:** User wants the rehearsed 3-min demo to stay single-path (one guest, one arrival property) to protect the 45% Live Demo + ADR-001 narrow slice, BUT the code should support an interactive guest/property selector so multi can be shown on request and the builder can tune/pick the final demo profile. Sub-decision (2026-05-16): Build interactive? YES — thin fixture-swap selector reusing the existing render path; demo script stays single-path; explicitly NOT a CRUD/authoring/chat-edit UI. [user-blessed]
- **Decision:** Build a thin interactive guest/property selector (fixture swap reusing the existing render path) so the builder can tune and pick the final demo profile and show multi-property on request; rehearsed 3-min demo stays single-path; explicitly NOT a CRUD/authoring/chat-edit UI (TREQ-022, P1/cuttable).
- **REQS:** TREQ-022
