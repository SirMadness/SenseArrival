# Backlog — Completed Archive

> **Purpose**: Permanent archive of all completed backlog items with full traceability.
> Items are appended here by `add-to-backlog.sh complete` and never deleted.
> Use this to answer "what was built for TREQ-###?" without cross-referencing git history.
>
> **Query tools**: Use `.claude/scripts/query-state.sh` to query this file — do not inline-awk this file for aggregations.

---

## Completed Items

<!-- Entries are appended by add-to-backlog.sh complete -->

<!-- Example entry format (for reference only):
- [x] **BL-NNN**: Design database schema
  - **Priority**: High
  - **Agent**: architect (system)
  - **Features**: FEAT-001
  - **Requirements**: TREQ-001
  - **UserStories**: US-001
  - **Depends On**: —
  - **Added**: 2026-03-01
  - **Details**: Initial schema for users, sessions, and audit tables
  - **Completed**: 2026-03-02
  - **Registry**: arch-database-schema-20260302
-->

- [x] **BL-010**: Rosewood per-property destination-culture research (3 properties + 3 dossiers)
  - **Priority**: High
  - **Agent**: analyst (research)
  - **Features**: FEAT-008
  - **Requirements**: TREQ-020
  - **UserStories**: US-008, US-011
  - **Depends On**: —
  - **Added**: 2026-05-16
  - **Details**: PARALLEL, off critical path — delegate early. Research real Rosewood properties' local culture/activities (1 deep arrival property + 2 provenance) -> Markdown property 'sense of place' cards + 3 guest dossiers w/ cross-property prior-stay staff observations. Build-time only; synthetic/rights-cleared; NO live demo APIs. Feeds BL-008. Output: Research -> _proj/artifacts/reports/analysis/.
  - **Started**: 2026-05-16
  - **Completed**: 2026-05-16
  - **Registry**: rosewood-property-dossier-research-2026-05-16


- [x] **BL-001**: FEAT-005 Resilient Runtime & Stack
  - **Priority**: Critical
  - **Agent**: engineer (backend)
  - **Features**: FEAT-005
  - **Requirements**: TREQ-013, TREQ-016
  - **UserStories**: US-007
  - **Depends On**: —
  - **Added**: 2026-05-16
  - **Details**: Action Plan Phase 1: Foundation & Runtime. Scaffold per ADR-001 layout. TREQ-012 (stack) satisfied by ADR-001 (Accepted). Build 3-tier pluggable LLM (Claude->Ollama->fixtures) + OFFLINE_MODE + scope guard (Ms. Chen, fixtures only, no live APIs).
  - **Started**: 2026-05-16
  - **Completed**: 2026-05-16
  - **Registry**: foundation-runtime-bl001-2026-05-16


- [x] **BL-002**: FEAT-001 Arrival Orchestration Core
  - **Priority**: Critical
  - **Agent**: engineer (backend)
  - **Features**: FEAT-001
  - **Requirements**: TREQ-001, TREQ-002, TREQ-003, TREQ-004, TREQ-014
  - **UserStories**: US-001, US-008
  - **Depends On**: —
  - **Added**: 2026-05-16
  - **Details**: Action Plan Phase 2: Arrival Orchestration Core. Depends BL FEAT-005. plan() -> 6 role cards + mood banner + Sand Hill anchors, all via Pydantic/tool-use; GET / renders baseline.
  - **Started**: 2026-05-16
  - **Completed**: 2026-05-16
  - **Registry**: orchestration-core-bl002-2026-05-16


- [x] **BL-003**: FEAT-002 Delay-to-Delight Re-plan & Diff
  - **Priority**: Critical
  - **Agent**: engineer (fullstack)
  - **Features**: FEAT-002
  - **Requirements**: TREQ-005, TREQ-006, TREQ-008
  - **UserStories**: US-002, US-003
  - **Depends On**: —
  - **Added**: 2026-05-16
  - **Details**: Action Plan Phase 3: Delay-to-Delight. Depends BL FEAT-001. TREQ-006 what-changed diff is NEVER CUT (ADR-001); must render even offline. Guest message preview is P1/cuttable.
  - **Started**: 2026-05-16
  - **Completed**: 2026-05-16
  - **Registry**: delay-to-delight-bl003-2026-05-16


- [x] **BL-004**: FEAT-007 Hackathon Compliance & Demo Readiness
  - **Priority**: Critical
  - **Agent**: docs
  - **Features**: FEAT-007
  - **Requirements**: TREQ-015, TREQ-017
  - **UserStories**: US-009
  - **Depends On**: —
  - **Added**: 2026-05-16
  - **Details**: Action Plan Phase 4: Compliance & Demo Readiness. DISQUALIFICATION GUARD. Land README (names PS#1 + built-today scope) early as low-risk commit; finalize 3-min script + cut order + offline rehearsal after spine works.
  - **Started**: 2026-05-16
  - **Completed**: 2026-05-16
  - **Registry**: compliance-readme-bl004-2026-05-16


- [x] **BL-005**: FEAT-004 Voice Layer (TTS + Staff Notes)
  - **Priority**: Critical
  - **Agent**: engineer (fullstack)
  - **Features**: FEAT-004
  - **Requirements**: TREQ-009, TREQ-010, TREQ-011
  - **UserStories**: US-004, US-005
  - **Depends On**: —
  - **Added**: 2026-05-16
  - **Details**: Action Plan Phase 5: Voice Layer. Depends BL FEAT-001. Build TREQ-011 typed-text path FIRST (P0, before getUserMedia); TREQ-009 TTS Play Briefing P0; TREQ-010 mic->Scribe STT P1, cuttable to typed path.
  - **Started**: 2026-05-16
  - **Completed**: 2026-05-16
  - **Registry**: voice-layer-bl005-2026-05-16


- [x] **BL-008**: FEAT-008 Portfolio Guest Graph & Cross-Visit Synthesis
  - **Priority**: Critical
  - **Agent**: engineer (fullstack)
  - **Features**: FEAT-008
  - **Requirements**: TREQ-020, TREQ-021, TREQ-023
  - **UserStories**: US-011, US-012, US-014
  - **Depends On**: BL-005
  - **Added**: 2026-05-16
  - **Details**: Action Plan Phase 7. STRICTLY behind never-cut spine BL-001->002->003. TREQ-020 grounding hook lands in BL-002; this BL = full cross-visit synthesis (TREQ-021) + staff-note->dossier demo-shim (TREQ-023, reuses BL-005 voice path). Consumes BL-010 researched property content. Criteria injected from v001.02 at delegation.
  - **Started**: 2026-05-16
  - **Completed**: 2026-05-16
  - **Registry**: portfolio-synthesis-bl008-2026-05-16


- [x] **BL-007**: FEAT-006 Demo Dashboard UI
  - **Priority**: High
  - **Agent**: engineer (frontend)
  - **Features**: FEAT-006
  - **Requirements**: TREQ-018
  - **UserStories**: US-010
  - **Depends On**: —
  - **Added**: 2026-05-16
  - **Details**: Action Plan Phase 6: Originality & UI Polish. P1. TREQ-018 Deliverable is Design->design but ADR-001 allows inlining under time pressure (engineer-led). Room-legible 3-panel, high-contrast, single-click actions.
  - **Started**: 2026-05-16
  - **Completed**: 2026-05-16
  - **Registry**: dashboard-polish-bl007-2026-05-16

