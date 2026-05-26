# Features

<!-- FEAT Format Reference
  Core fields: Title, Requirements, Status, Priority, Description
  Status: DRAFT → LOCKED → MIGRATED → DEPRECATED
  Features group one or more TREQs into a deliverable capability; each FEAT → one BL item at /execute start.
  Graduated to deliverables/01-requirements/features.md during reconciliation.
-->

## FEAT-001
- **Title:** Arrival Orchestration Core
- **Requirements:** TREQ-001, TREQ-002, TREQ-003, TREQ-004, TREQ-014
- **Status:** MIGRATED
- **Priority:** P0
- **Description:** The engine: takes the Ms. Chen guest fixture + arrival context, calls the LLM with a Pydantic/tool-use schema, and renders an arrival mood banner plus six role-based staff cards grounded in Sand Hill anchors. This is the baseline "First Five Minutes" plan.

## FEAT-002
- **Title:** Delay-to-Delight Re-plan & Diff
- **Requirements:** TREQ-005, TREQ-006, TREQ-008
- **Status:** MIGRATED
- **Priority:** P0
- **Description:** One-click delay injection re-plans the arrival; the "what changed & why" panel shows baseline→re-plan deltas with trigger and reason; optional guest message preview. The headline demo branch and the never-cut creative proof.

## FEAT-003
- **Title:** Tasteful Restraint (Suppression)
- **Requirements:** TREQ-007
- **Status:** MIGRATED
- **Priority:** P1
- **Description:** A panel listing what the system deliberately chose NOT to suggest, with reasons — the "they just knew vs. that's creepy" originality hook. Cuttable to a verbal pitch point.

## FEAT-004
- **Title:** Voice Layer (TTS Briefing + Staff Notes)
- **Requirements:** TREQ-009, TREQ-010, TREQ-011
- **Status:** MIGRATED
- **Priority:** P0
- **Description:** ElevenLabs "Play Briefing" TTS on role cards (P0) and staff observation capture that updates cards live — typed-text path first (P0), mic→Scribe-STT as the cuttable extension (P1).

## FEAT-005
- **Title:** Resilient Runtime & Stack
- **Requirements:** TREQ-012, TREQ-013, TREQ-016
- **Status:** MIGRATED
- **Priority:** P0
- **Description:** Python/FastAPI/HTMX single-process app with a 3-tier pluggable LLM backend (Claude → Ollama → fixtures) and a scope guard (one persona, fixtures only, no live APIs). Removes the largest live-demo failure modes.

## FEAT-006
- **Title:** Demo Dashboard UI
- **Requirements:** TREQ-018
- **Status:** MIGRATED
- **Priority:** P1
- **Description:** Room-legible 3-panel dashboard: inputs/triggers · mood + diff + suppression · role cards with Play Briefing. High-contrast, large-font, one-click. May be inlined into implementation under time pressure.

## FEAT-007
- **Title:** Hackathon Compliance & Demo Readiness
- **Requirements:** TREQ-015, TREQ-017
- **Status:** MIGRATED
- **Priority:** P0
- **Description:** Public repo + README naming Problem Statement #1 and built-today scope (disqualification guard), plus the 3-min demo script, cut order, backup assets, and a tested offline rehearsal before the judging room.

## FEAT-008
- **Title:** Portfolio Guest Graph & Cross-Visit Synthesis
- **Requirements:** TREQ-020, TREQ-021, TREQ-023
- **Status:** MIGRATED
- **Priority:** P0
- **Description:** Guest dossiers (profile + cross-property prior stays carrying each site's staff observations) + a per-property "sense of place" card library that captures the destination's local culture & activities, Markdown-source and template-driven. The orchestrator synthesizes a unified cross-visit guest understanding that informs the arrival and is surfaced explicitly ("inferred from prior stays"). Includes the live staff-observation → dossier demo-shim loop (TREQ-023, reuses the FEAT-004 voice/typed capture path). Widened scope guard: 3 dossiers / 3 properties, fixtures only, single rehearsed demo path. The headline creativity feature — strictly behind the never-cut spine.

## FEAT-009
- **Title:** Interactive Fixture Selector (demo-optional)
- **Requirements:** TREQ-022
- **Status:** MIGRATED
- **Priority:** P1
- **Description:** Thin guest/property picker that swaps the loaded dossier/property and re-runs the plan via the existing render path. Lets the builder tune and pick the final demo profile and show multi-property on request. Cuttable; the rehearsed demo stays single-path. Not a CRUD/authoring/chat-edit UI.
