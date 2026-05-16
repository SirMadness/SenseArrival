# Action Plan

> **Purpose**: Living project plan that defines what we're building, why, and in what order. Checked at the start of every session to understand current priorities.
>
> **Updated By**: Orchestrator agent (plan/execute modes) or user directly
>
> **Lifecycle**: Create when starting a project or major initiative. Update as work progresses. Archive when complete.
>
> **Query tools**: Use `.claude/scripts/query-state.sh`, `plan-health.sh`, or `cascade-unblock.sh` to query this file — do not inline-awk this file for aggregations.

---

## Quick Stats

- **Status**: Planning
- **Total Phases**: 7
- **Completed Phases**: 0
- **Current Phase**: -
- **Last Updated**: 2026-05-16

---

## Goal

Build SenseArrival 'First Five Minutes' arrival-choreography engine for Rosewood Sand Hill (Problem Statement #1): fixture-driven Pydantic/tool-use ArrivalPlan rendering 6 role cards + mood banner grounded in Sand Hill anchors, one-click delay re-plan with a never-cut what-changed diff, ElevenLabs TTS + typed/mic staff notes, 3-tier LLM resilience with offline replay — demo-ready before the hard 5PM submission.

---

## Success Criteria

<!-- How do we know when we're done? Measurable outcomes. -->


- [ ] Baseline dashboard renders mood banner + all 6 role cards grounded in >=2 named Sand Hill anchors (US-001, US-008)

- [ ] One-click delay injection re-plans in <~10s with a what-changed diff panel that renders even offline — NEVER CUT (US-002, US-003, TREQ-006)

- [ ] Full demo (baseline -> re-plan -> diff -> >=1 TTS) runs end-to-end in fixture-replay mode with zero outbound calls (US-007)

- [ ] Typed staff observation updates the correct role cards via the same endpoint that backs mic STT (US-004)

- [ ] Public repo README names 'Problem Statement #1' + explicit built-today scope; offline rehearsal documented (US-009, TREQ-017)

---

## Current Phase

_No active phase. Use the orchestrator in plan mode to create a plan, or add phases manually._

<!-- Example of an active phase:
### Phase 2: Authentication API
- **Status**: Planning
- **Agent**: engineer (backend mode)
- **Started**: 2026-03-01
- **Depends On**: Phase 1
- **Deliverables**:
  - [ ] JWT token endpoint
  - [x] User registration endpoint
  - [ ] Password reset flow
- **Notes**: Using bcrypt for hashing per security audit recommendation
-->

---

## Phases

<!-- Ordered list of all phases. Move the active one to "Current Phase" above. -->

| # | Phase | Status | Agent | Depends On | Target |
|---|-------|--------|-------|------------|--------|

<!-- Example: | N | Phase name | Status | agent | Depends On | Target date | -->

| 1 | Foundation & Runtime | Pending | engineer (backend) | none | TBD |

| 2 | Arrival Orchestration Core | Pending | engineer (backend) | Phase 1 | TBD |

| 3 | Delay-to-Delight Re-plan & Diff | Pending | engineer (fullstack) | Phase 2 | TBD |

| 4 | Compliance & Demo Readiness | Pending | docs | Phase 3 | TBD |

| 5 | Voice Layer | Pending | engineer (fullstack) | Phase 2 | TBD |

| 6 | Originality & UI Polish | Pending | engineer (frontend) | Phase 5 | TBD |

| 7 | Portfolio Guest Graph & Cross-Visit Synthesis | Pending | engineer (fullstack) | Phase 5 | TBD |

---

## Phase Details

<!-- Detail blocks for pending phases. Created by add-phase --value --features. Archived by complete-phase. -->

_No phase details yet._

<!-- Example:
### Phase 2: Authentication API
- **Status**: Planning
- **Agent**: engineer (backend)
- **Depends On**: Phase 1
- **Target**: 2026-04-15
- **Value**: Users can securely register, log in, and reset passwords across all client applications
- **Features**:
  - FEAT-005: User Registration (P0) — REQ-010
  - FEAT-006: Password Reset (P1) — REQ-011
- **Backlog**: BL-005, BL-006, BL-002
- **Priority**: 1x P0, 1x P1
-->

---

## Completed Phases

_No completed phases yet._

<!-- Example:
### Phase 1: Database Schema Design (Completed 2026-03-01)
- **Agent**: architect (system mode)
- **Deliverables**: ADR-004, migration scripts
- **Registry**: arch-database-schema-20260301
- **Notes**: Chose event sourcing per ADR-003
-->

---

## Decisions & Constraints

<!-- Key decisions made during planning that affect execution. -->



<!-- Example:
- **2026-03-01**: Using PostgreSQL over MongoDB — need ACID for financial transactions
- **2026-03-02**: Targeting Python 3.12+ only — allows using match/case statements
- **2026-03-03**: Auth tokens expire after 15 min — compliance requirement
-->

- **2026-05-16**: Re-discovery cycle 2 entered before any phase started — scope widening (portfolio guest graph + cross-visit synthesis). All 6 phases pending; backlog will be regenerated on /execute re-entry after reconciliation.

- **2026-05-16**: Re-entry resequencing (cycle 2, user-approved at reconciliation lock): execution order = Phase1->2->3->4->5->7(FEAT-008 Portfolio Graph, depends Phase5 because TREQ-023 staff-note->dossier shim reuses the Voice path)->6(Polish, now also carries FEAT-009, runs last/cuttable). FEAT-008 STRICTLY behind never-cut spine BL-001->002->003. Analyst property-culture research (BL-010) runs in parallel from start, off critical path. BL-001 TREQ-016->TREQ-019; BL-002 +TREQ-020 grounding hook; BL-004 +TREQ-024 README framing — corrected TREQs injected fresh from v001.02 deliverables at delegation time (BL ref text is non-authoritative per agent-coordination).

- **2026-05-16**: ADR-002 accepted (architecture gate cleared for BL-001/002). RECONCILE PENDING: ADR-002 used placeholder provenance fixture names rosewood-london.md/rosewood-beijing.md; analyst BL-010 was guided to The Carlyle (NY, Broadway/theatre — matches user's 'Annie' example) + Hotel de Crillon (Paris). On BL-010 return, rename ADR-002 provenance fixtures + offline-path comment to the analyst's chosen 2 properties (non-architectural edit; ADR-002 decisions unchanged).

- **2026-05-16**: RECONCILE RESOLVED: provenance = The Carlyle (New York) + Rosewood Castiglion del Bosco (Tuscany); arrival-deep = Rosewood Sand Hill. Canonical demo guest = 'Ms. Chen' (preserves locked US-008) using analyst Dossier A demo-grade content (cyclist + wine-terroir + solo-decompressor + cultural appetite; prior stays Carlyle + Castiglion). Guests B/C = Priya Nair, James Okafor. Fixtures supersede ADR-002 placeholders: dossiers/{ms-chen,priya-nair,james-okafor}.md ; properties/{rosewood-sand-hill,the-carlyle-new-york,castiglion-del-bosco}.md ; offline canonical = ms-chen@rosewood-sand-hill. ADR-002 design decisions unchanged (names were illustrative).

- **2026-05-16**: PROJECT LOCKED 2026-05-16: P0 set + dashboard polish (BL-007) + suppression (BL-006) complete & committed. BL-009 interactive selector CUT (demo-optional, per ADR-001 cut order, user-confirmed). Never-cut spine certified clean 6x. Proceeding to lock activities: final offline end-to-end smoke check + demo-playbook finalization. No further feature build.

---

## How to Use This Plan

### Creating a Plan

```bash
# Use the orchestrator to generate a plan
claude --agent orchestrator "Plan: [describe the project or initiative]"

# Add phases with manifest (recommended)
.claude/scripts/update-action-plan.sh add-phase "Phase name" "agent" "depends-on" "target-date" \
  --value "What user capability this phase unlocks" \
  --features "FEAT-001:Title:P0:REQ-001,FEAT-002:Title:P1:REQ-002"

# Add phases without manifest (legacy)
.claude/scripts/update-action-plan.sh add-phase "Phase name" "agent" "depends-on" "target-date"
```

### Updating Progress

```bash
# Start a phase
.claude/scripts/update-action-plan.sh start-phase [phase-number]

# Complete a phase
.claude/scripts/update-action-plan.sh complete-phase [phase-number] "[registry-entry]"

# Update the goal
.claude/scripts/update-action-plan.sh set-goal "[goal description]"

# Archive a completed plan
.claude/scripts/update-action-plan.sh archive-plan
```

### Lifecycle

1. **Plan** → Orchestrator creates phases from requirements
2. **Execute** → Work through phases, updating status as tasks complete
3. **Track** → Completed work goes to `_registry.md`, deferred issues to `_tech-debt.md`
4. **Close** → When all success criteria are met, archive the plan with `archive-plan`
