# Tech Debt Registry

> **Purpose**: Track deferred work, known issues, and improvements that were identified but not immediately addressed.
>
> **Updated By**: Orchestrator agent (when issues are deferred) or any agent (when discovering issues)
>
> **Review Cadence**: Weekly review of Critical/High items
>
> **Query tools**: Use `.claude/scripts/query-state.sh` to query this file — do not inline-awk this file for aggregations.

---

## Quick Stats

- **Total Items**: 0
- **Open**: 0
- **Resolved**: 0
- **Critical**: 0
- **High**: 0
- **Medium**: 0
- **Low**: 0
- **Last Updated**: -

---

## Critical (Blocks Feature Work)

> Items that must be addressed before new features can be built. Actively blocking progress.

_No critical tech debt items._

<!-- Example entry:
- [ ] **TD-001**: Legacy authentication system incompatible with SSO
  - **Impact**: High - Blocks all SSO integration work
  - **Source**: [security-audit-20260201.md](security/security-audit-20260201.md)
  - **Created**: 2026-02-01
  - **Owner**: @security
  - **Estimated Effort**: 2-3 days
  - **Notes**: Need to migrate from session-based to JWT before SSO
-->

---

## High (Causes Frequent Issues)

> Items causing repeated problems, degraded performance, or developer friction. Should be addressed soon.

_No high-priority tech debt items._

<!-- Example entry:
- [ ] **TD-002**: N+1 queries in dashboard API
  - **Impact**: Medium - Dashboard page load >5s for users with many projects
  - **Source**: [review-dashboard-20260130.md](review/review-dashboard-20260130.md)
  - **Created**: 2026-01-30
  - **Owner**: Unassigned
  - **Estimated Effort**: 1 day
  - **Notes**: Need to add eager loading for project.members relationship
-->

---

## Medium (Should Fix Soon)

> Items that degrade quality or maintainability but don't cause immediate problems.

_No medium-priority tech debt items._

<!-- Example entry:
- [ ] **TD-003**: Inconsistent error handling in API layer
  - **Impact**: Low - Some errors return wrong HTTP status codes
  - **Source**: [review-api-errors-20260128.md](review/review-api-errors-20260128.md)
  - **Created**: 2026-01-28
  - **Owner**: Unassigned
  - **Estimated Effort**: 0.5 days
  - **Notes**: Create centralized error handler middleware
-->

---

## Low (Nice to Have)

> Minor improvements, cleanup tasks, or optimizations with no urgency.

_No low-priority tech debt items._

<!-- Example entry:
- [ ] **TD-004**: Remove deprecated `calculateLegacyScore` function
  - **Impact**: None - Dead code, no longer called
  - **Source**: [review-cleanup-20260125.md](review/review-cleanup-20260125.md)
  - **Created**: 2026-01-25
  - **Owner**: Unassigned
  - **Estimated Effort**: 10 minutes
  - **Notes**: Was replaced by `calculateScore` in v2.0
-->

---

## Resolved Items

> Recently resolved tech debt (kept for 30 days for reference).

_No recently resolved items._

<!-- Example entry:
- [x] **TD-000**: Database connection pool exhaustion under load
  - **Impact**: Critical - Production outages during peak traffic
  - **Source**: [postmortem-db-outage-20260115.md](sre/postmortem-db-outage-20260115.md)
  - **Created**: 2026-01-15
  - **Resolved**: 2026-01-17
  - **Resolution**: Increased pool size, added connection timeout, implemented retry logic
  - **PR**: #234
-->

---

## How to Use This Registry

### Adding New Tech Debt

When deferring work during a review, audit, or implementation:

```markdown
- [ ] **TD-XXX**: [Brief title]
  - **Impact**: [Critical|High|Medium|Low] - [Why it matters]
  - **Source**: [link-to-report.md](category/report.md)
  - **Created**: YYYY-MM-DD
  - **Owner**: [agent or Unassigned]
  - **Estimated Effort**: [time estimate]
  - **Notes**: [Additional context]
```

### Resolving Tech Debt

1. Mark the checkbox as complete: `- [x]`
2. Add resolution details:
   ```markdown
   - **Resolved**: YYYY-MM-DD
   - **Resolution**: [What was done]
   - **PR**: #XXX (if applicable)
   ```
3. Move to "Resolved Items" section

### Priority Guidelines

| Priority | Criteria |
|----------|----------|
| **Critical** | Blocks feature work, causes outages, security vulnerability |
| **High** | Frequent issues, significant performance impact, major DX friction |
| **Medium** | Code quality issues, moderate impact, should fix in next sprint |
| **Low** | Cleanup, minor optimizations, no urgency |

### Weekly Review Process

1. Review all Critical items - any that can be addressed this week?
2. Review High items - any quick wins?
3. Assign owners to unassigned items if capacity allows
4. Archive resolved items older than 30 days

---

## Scripts

**Add tech debt entry:**
```bash
.claude/scripts/add-tech-debt.sh [priority] "[title]" "[impact]" "[source-report]"
```

**Generate tech debt report:**
```bash
.claude/scripts/query-state.sh tech-debt [--priority Critical|High|Medium|Low] [--keyword KEY]
```
