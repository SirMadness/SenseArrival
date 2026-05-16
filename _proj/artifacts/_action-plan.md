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

- **Status**: Not Started
- **Total Phases**: 0
- **Completed Phases**: 0
- **Current Phase**: -
- **Last Updated**: -

---

## Goal

<!-- What are we building and why? One paragraph max. -->

_No goal defined yet._

---

## Success Criteria

<!-- How do we know when we're done? Measurable outcomes. -->

- [ ] _Define success criteria_

---

## Current Phase

_No active phase. Use the orchestrator in plan mode to create a plan, or add phases manually._

<!-- Example of an active phase:
### Phase 2: Authentication API
- **Status**: In Progress
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
| - | _No phases defined_ | - | - | - | - |

<!-- Example: | N | Phase name | Status | agent | Depends On | Target date | -->

---

## Phase Details

<!-- Detail blocks for pending phases. Created by add-phase --value --features. Archived by complete-phase. -->

_No phase details yet._

<!-- Example:
### Phase 2: Authentication API
- **Status**: Pending
- **Agent**: engineer (backend)
- **Depends On**: Phase 1
- **Target**: 2026-04-15
- **Value**: Users can securely register, log in, and reset passwords across all client applications
- **Features**:
  - FEAT-005: User Registration (P0) — REQ-010
  - FEAT-006: Password Reset (P1) — REQ-011
- **Backlog**: BL-005, BL-006
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

_No decisions recorded yet._

<!-- Example:
- **2026-03-01**: Using PostgreSQL over MongoDB — need ACID for financial transactions
- **2026-03-02**: Targeting Python 3.12+ only — allows using match/case statements
- **2026-03-03**: Auth tokens expire after 15 min — compliance requirement
-->

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
