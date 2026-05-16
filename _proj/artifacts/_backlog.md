# Backlog

> **Purpose**: Prioritized queue of work items ready to be picked up. This is the "what's next" list — items flow in from the action plan, user requests, and tech debt triage.
>
> **Updated By**: Orchestrator agent, or any agent/user adding work items
>
> **Relationship**: Action plan defines phases → backlog breaks phases into executable tasks → registry records completed tasks → tech debt captures deferred issues
>
> **Query tools**: Use `.claude/scripts/query-state.sh` or `plan-health.sh` to query this file — do not inline-awk this file for aggregations.

---

## Quick Stats

- **Total Items**: 0
- **Ready**: 0
- **In Progress**: 0
- **Blocked**: 0
- **Last Updated**: -

---

## In Progress

> Items currently being worked on. Limit: 3 concurrent items.

_No items in progress._

<!-- Example (for reference only — use the script to add real entries):
- [ ] **BL-NNN**: Implement JWT token endpoint
  - **Priority**: High
  - **Agent**: engineer (backend)
  - **Features**: FEAT-012
  - **Requirements**: TREQ-022
  - **UserStories**: US-010
  - **Depends On**: —
  - **Added**: 2026-03-01
  - **Details**: RS256 signing, 15-min expiry
  - **Started**: 2026-03-03
-->

---

## Ready (Prioritized)

> Items ready to be picked up, in priority order. Top item is next.

_No items in backlog._

<!-- Example (for reference only — use the script to add real entries):
- [ ] **BL-NNN**: Add password reset flow
  - **Priority**: High
  - **Agent**: engineer (fullstack)
  - **Features**: FEAT-008
  - **Requirements**: TREQ-015
  - **UserStories**: US-007
  - **Depends On**: BL-010
  - **Added**: 2026-03-01
  - **Details**: Email token flow, 1-hour expiry
-->

---

## Blocked

> Items that can't proceed until a dependency is resolved.

_No blocked items._

<!-- Example (for reference only):
- [ ] **BL-NNN**: Frontend auth integration
  - **Priority**: High
  - **Agent**: engineer (frontend)
  - **Features**: FEAT-009
  - **Requirements**: TREQ-016
  - **UserStories**: US-008
  - **Depends On**: BL-NNN
  - **Added**: 2026-03-01
  - **Details**: Waiting on JWT endpoint
  - **Blocked By**: JWT endpoint not ready (BL-NNN)
-->

---

## How to Use This Backlog

### Adding Items

```bash
# Required: priority, title, agent (with mode), requirements (TREQ-### or TD-###)
.claude/scripts/add-to-backlog.sh [priority] "[title]" "[agent (mode)]" "[requirements]"

# With optional flags
.claude/scripts/add-to-backlog.sh [priority] "[title]" "[agent (mode)]" "[requirements]" \
    [--features FEAT-###] [--user-stories US-###] [--depends BL-###] [--details "text"]

# Examples
.claude/scripts/add-to-backlog.sh High "Implement JWT endpoint" "engineer (backend)" "TREQ-022"
.claude/scripts/add-to-backlog.sh High "Implement JWT endpoint" "engineer (backend)" "TREQ-022" \
    --features FEAT-012 --user-stories US-010 --details "RS256 signing, 15-min expiry"
```

### Managing Items

```bash
# Start working on an item
.claude/scripts/add-to-backlog.sh start [BL-number]

# Complete an item (appends to _backlog_completed.md archive)
.claude/scripts/add-to-backlog.sh complete [BL-number] "[registry-entry]"

# Block an item
.claude/scripts/add-to-backlog.sh block [BL-number] "[reason]"

# Unblock an item
.claude/scripts/add-to-backlog.sh unblock [BL-number]
```

### Priority Guidelines

| Priority | Criteria | Pick Up |
|----------|----------|---------|
| **Critical** | Blocks other work, production issue | Immediately |
| **High** | Current phase deliverable, important feature | This session |
| **Medium** | Useful but not blocking, next phase prep | When capacity allows |
| **Low** | Nice to have, cleanup, minor improvement | Fill time |

### Workflow

1. **Orchestrator** breaks action plan phases into backlog items
2. **Items** are prioritized and picked up in order
3. **In Progress** items are limited to 3 to maintain focus
4. **Completed** items get a registry entry and are written directly to `_backlog_completed.md` (permanent archive)
5. **Blocked** items track their dependency so they auto-unblock
