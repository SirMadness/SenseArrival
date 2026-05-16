# Report Registry

> **Purpose**: Index of all completed and active work. Read this before starting any task to understand project context and prior decisions.
>
> **Updated By**: Main agent only (after verifying deliverables)
>
> **Archive Policy**: Entries older than 7 days moved to `archive/` folder
>
> **Query tools**: Use `.claude/scripts/query-state.sh` or `context-digest.sh` to query this file — do not inline-awk this file for aggregations.

---

## Quick Stats

- **Total Reports**: 0
- **Active Work**: 0
- **Completed This Week**: 0
- **Last Updated**: -

---

## Active Work

| Report | Category | Agent | Started | Summary |
|--------|----------|-------|---------|---------|

_No active work._

---

## Completed Work (Last 7 Days)

| Report | Category | Agent | Completed | Summary |
|--------|----------|-------|-----------|---------|

_No completed work yet._

---

## Abandoned/Reverted Work

| Report | Category | Agent | Date | Status | Reason |
|--------|----------|-------|------|--------|--------|

_None._

---

## Report Categories

| Category | Description | Count |
|----------|-------------|-------|
| `analysis` | Research, EDA, data exploration | 0 |
| `arch` | Architecture decisions, ADRs | 0 |
| `bugs` | Bug reports, root cause analysis | 0 |
| `commits` | Commit summaries, changelogs | 0 |
| `design` | UI/UX reviews, design specs | 0 |
| `exec` | Execution logs, command outputs | 0 |
| `handoff` | Agent coordination, context transfers | 0 |
| `implementation` | Implementation plans, code specs | 0 |
| `review` | Code reviews, PR reviews | 0 |
| `tests` | Test plans, coverage reports | 0 |
| `security` | Scans, threat models, compliance | 0 |
| `sre` | SLOs, postmortems, capacity | 0 |
| `rfc` | Design proposals | 0 |
| `ci` | CI pipeline results | 0 |

---

## How to Use This Registry

### For Main Agent
1. **Before delegating**: Read this registry to understand context
2. **Extract relevant entries**: Pass summaries (not full text) to subagents
3. **After task completes**: Verify deliverable, then add entry here
4. **If work abandoned/reverted**: Record with reason so the team learns from it
5. **Weekly**: Run archive script to move old entries

### For Subagents
**DO NOT read this registry directly.** You will receive relevant context from Main via Agent tool prompt.

### Status Values
| Status | When to Use |
|--------|-------------|
| `Active` | Work in progress |
| `Completed` | Work finished and verified |
| `Abandoned` | Work started but intentionally stopped (wrong approach, requirements changed, etc.) |
| `Reverted` | Work completed but rolled back (broke something, failed validation, etc.) |

### Entry Format
```markdown
| [category]-[topic]-YYYYMMDD | [category] | [agent] | YYYY-MM-DD | [one-line summary] |
```

### Example Entries
```markdown
## Completed
| review-auth-api-20260202 | review | code-quality | 2026-02-02 | L1 review: 3 issues found, 2 blocking |
| arch-database-redesign-20260201 | arch | architect | 2026-02-01 | ADR-003: Switched to event sourcing |

## Abandoned/Reverted
| impl-redis-cache-20260205 | implementation | engineer | 2026-02-05 | Abandoned | Switched to in-memory cache — Redis overkill for current scale |
| impl-graphql-api-20260210 | implementation | engineer | 2026-02-10 | Reverted | Broke existing REST clients, need migration plan first |
```

---

## Archived Reports

See `archive/` folder for reports older than 7 days.

To search archives:
```bash
grep -r "keyword" artifacts/reports/archive/
```
