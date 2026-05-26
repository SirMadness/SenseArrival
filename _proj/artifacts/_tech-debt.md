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

- **Total Items**: 10
- **Open**: 10
- **Resolved**: 0
- **Critical**: 0
- **High**: 0
- **Medium**: 1
- **Low**: 9
- **Last Updated**: 2026-05-16

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

<!-- Example entry:
- [ ] **TD-003**: Inconsistent error handling in API layer
  - **Impact**: Low - Some errors return wrong HTTP status codes
  - **Source**: [review-api-errors-20260128.md](review/review-api-errors-20260128.md)
  - **Created**: 2026-01-28
  - **Owner**: Unassigned
  - **Estimated Effort**: 0.5 days
  - **Notes**: Create centralized error handler middleware
-->



- [ ] **TD-022**: Ollama/unknown-backend failure-fallback not tagged is_fallback_fixture (silent wrong-guest on Tier-2 failure)
  - **Priority**: Medium
  - **Impact**: _call_ollama except-block + plan()/replan() unknown-backend guards return load_offline_response() raw (untagged) — if BACKEND=ollama and Ollama fails, the guest-blind Ms-Chen fixture renders silently as the selected guest (same bug Fix C closed for Claude). OFF every rehearsed path: demo=claude (verified correct), network fallback=OFFLINE_MODE/replay (intentional, gold banner, correctly untagged). Fix = mirror Fix C tagging in 3 spots. Deferred: not a claude-primary-demo blocker per code-quality review.
  - **Source**: [review-fix-abc-20260516](review-fix-abc-20260516)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: TBD

---

## Low (Nice to Have)

> Minor improvements, cleanup tasks, or optimizations with no urgency.

<!-- Example entry:
- [ ] **TD-004**: Remove deprecated `calculateLegacyScore` function
  - **Impact**: None - Dead code, no longer called
  - **Source**: [review-cleanup-20260125.md](review/review-cleanup-20260125.md)
  - **Created**: 2026-01-25
  - **Owner**: Unassigned
  - **Estimated Effort**: 10 minutes
  - **Notes**: Was replaced by `calculateScore` in v2.0
-->


- [ ] **TD-007**: Silent swallow in load_provenance_cards() + Arrival-Property fallback
  - **Priority**: Low
  - **Impact**: Masks typos/missing fields during BL-002 dynamic dossier work
  - **Source**: [review-foundation-bl001-2026-05-16.md](review-foundation-bl001-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: 15m
  - **Notes**: Add logger.warning in both paths


- [ ] **TD-008**: ADR-002 Delta 5 illustrative provenance names vs deployed carlyle/castiglion
  - **Priority**: Low
  - **Impact**: Doc drift only — code fully reconciled; annotate ADR-002 for clarity
  - **Source**: [review-foundation-bl001-2026-05-16.md](review-foundation-bl001-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: 10m
  - **Notes**: Annotate ADR-002 Delta 5


- [ ] **TD-012**: @app.on_event('startup') deprecated in FastAPI 0.111+
  - **Priority**: Low
  - **Impact**: Deprecation warning only, no crash risk; replace with lifespan post-hackathon
  - **Source**: [review-orchestration-bl002-2026-05-16.md](review-orchestration-bl002-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: post-hackathon


- [ ] **TD-013**: Diff reason mapping fixture-tuned (Ollama no backfill; _ROLE_REASONS substring keys; 1/16 Spa entry generic)
  - **Priority**: Low
  - **Impact**: Tier-2/live-only cosmetic; REPLAY demo path unaffected; reasons may be generic off-fixture
  - **Source**: [review-delay-to-delight-bl003-2026-05-16.md](review-delay-to-delight-bl003-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: post-hackathon


- [ ] **TD-015**: _silent_frame() returns 44 null bytes (invalid audio); Play hangs if m4a ever absent
  - **Priority**: Low
  - **Impact**: Unreachable now TD-006 resolved; defensive only
  - **Source**: [review-voice-layer-bl005-2026-05-16.md](review-voice-layer-bl005-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: post-hackathon
  - **Notes**: Return 503 or minimal ftyp atom


- [ ] **TD-018**: Offline synthesis always returns Ms. Chen synthesis_fixture.json for all 3 guests
  - **Priority**: Low
  - **Impact**: Known/accepted per ADR-002 Delta 5; rehearsed demo path is Ms.Chen; live mode synthesizes all 3 correctly
  - **Source**: [review-portfolio-synthesis-bl008-2026-05-16.md](review-portfolio-synthesis-bl008-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: accepted


- [ ] **TD-019**: Stale live_replanned on /select guest-switch without intervening /replan; +pre-existing unescaped {exc} main.py:279 & card_id_slug attr main.py:610
  - **Priority**: Low
  - **Impact**: Not demo-reachable (selector 503 in OFFLINE_MODE; fixture-controlled values); post-hackathon hardening
  - **Source**: [review-dashboard-polish-bl007-2026-05-16.md](review-dashboard-polish-bl007-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: post-hackathon


- [ ] **TD-020**: json.JSONDecodeError not in suppressions fixture except clause; synthesis-OOB doesn't refresh suppression panel on staff-note
  - **Priority**: Low
  - **Impact**: Degrades correctly to []; suppressions intentionally shift only on full replan (demo-correct); author-controlled fixtures
  - **Source**: [review-suppression-bl006-2026-05-16.md](review-suppression-bl006-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: post-hackathon


- [ ] **TD-021**: Live Claude call ~22-28s (standard-tier throughput floor)
  - **Priority**: Low
  - **Impact**: ACCEPTED CONSTRAINT not a bug: ~4600 input + ~2100 output tok at ~100 tok/s (Haiku, standard tier) = ~24s irreducible. TD-010 fixed (async, spinner animates, fast 35s graceful fallback). Mitigation per ADR-001: OFFLINE_MODE=true is the rehearsed instant zero-code fallback for the judged room if live latency/network is a risk. No further fix without higher API service tier or streaming-render (post-deadline).
  - **Source**: [live-latency-fix-20260516](live-latency-fix-20260516)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: TBD

---

## Resolved Items

> Recently resolved tech debt (kept for 30 days for reference).


<!-- Example entry:
- [x] **TD-010**: Sync anthropic.Anthropic client in async _call_claude blocks event loop 3-8s
  - **Priority**: Low
  - **Impact**: No impact single-user demo; upgrade to AsyncAnthropic if load matters
  - **Source**: [review-orchestration-bl002-2026-05-16.md](review-orchestration-bl002-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: BL-005
  - **Resolved**: 2026-05-16
  - **Resolution**: Fixed in live-latency-fix 2026-05-16: _call_claude now uses anthropic.AsyncAnthropic + await (event loop never blocked; HTMX spinner animates during live call). Real impact was ~55-80s not 3-8s — root-caused as standard-tier throughput-bound.

- [x] **TD-016**: POST /select calls orchestrator.plan() with 3 positional args, index() passes 4 (missing session_observations)
  - **Priority**: Low
  - **Impact**: P1/demo-optional selector path arg mismatch; verify before BL-009 selector use
  - **Source**: [review-voice-layer-bl005-2026-05-16.md](review-voice-layer-bl005-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: BL-009
  - **Notes**: Align plan() call signature
  - **Resolved**: 2026-05-16
  - **Resolution**: Resolved BL-007 (d9bd1d4), code-quality confirmed: blank-submit 200+visible / html.escape all 4 OOB builders / /select sets live_baseline + correct plan() args

- [x] **TD-009**: POST /select does not update app.state.live_baseline
  - **Priority**: Medium
  - **Impact**: Using guest selector then GET /diff diffs mismatched guests; fix before demo rehearsal if selector is in judge interaction
  - **Source**: [review-orchestration-bl002-2026-05-16.md](review-orchestration-bl002-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: BL-009
  - **Notes**: Set app.state.live_baseline=response in select_guest()
  - **Resolved**: 2026-05-16
  - **Resolution**: Resolved BL-007 (d9bd1d4), code-quality confirmed: blank-submit 200+visible / html.escape all 4 OOB builders / /select sets live_baseline + correct plan() args

- [x] **TD-017**: Inline HTML builders in main.py inject staff-note/synthesis text without html.escape()
  - **Priority**: Medium
  - **Impact**: Safe in offline/fixture demo (controlled content); live Claude mode with crafted note containing < would render raw HTML
  - **Source**: [review-portfolio-synthesis-bl008-2026-05-16.md](review-portfolio-synthesis-bl008-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: BL-007
  - **Notes**: Wrap with stdlib html.escape() — ~5 lines
  - **Resolved**: 2026-05-16
  - **Resolution**: Resolved BL-007 (d9bd1d4), code-quality confirmed: blank-submit 200+visible / html.escape all 4 OOB builders / /select sets live_baseline + correct plan() args

- [x] **TD-014**: Blank textarea submit returns 400; HTMX no swap on non-2xx -> silent failure on P0 typed path
  - **Priority**: Medium
  - **Impact**: Demo: empty Submit-as-text shows no feedback, looks broken
  - **Source**: [review-voice-layer-bl005-2026-05-16.md](review-voice-layer-bl005-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: BL-007
  - **Notes**: Add required attr to textarea OR return 200+inline error
  - **Resolved**: 2026-05-16
  - **Resolution**: Resolved BL-007 (d9bd1d4), code-quality confirmed: blank-submit 200+visible / html.escape all 4 OOB builders / /select sets live_baseline + correct plan() args

- [x] **TD-006**: static/audio/briefing_cached.mp3 absent — replay TTS returns synthetic silent frame
  - **Priority**: Low
  - **Impact**: Offline TTS demo beat has no audible briefing until a real cached MP3 is generated
  - **Source**: [foundation-runtime-bl001-2026-05-16.md](foundation-runtime-bl001-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: BL-004
  - **Notes**: Generate+commit real cached briefing MP3
  - **Resolved**: 2026-05-16
  - **Resolution**: Resolved BL-005: real cached briefing_cached.m4a (159KB) committed; offline Play Briefing audible; code-quality confirmed REPLAY zero-network

- [x] **TD-011**: No len==6 enforcement in _parse_tool_response (live Claude could return <6 cards)
  - **Priority**: Low
  - **Impact**: Live render degrades visually if Claude returns fewer than 6 role cards; no crash
  - **Source**: [review-orchestration-bl002-2026-05-16.md](review-orchestration-bl002-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: BL-003
  - **Notes**: Add len check + backfill
  - **Resolved**: 2026-05-16
  - **Resolution**: Resolved BL-003: _backfill_role_cards() guarantees 6-card grid on Claude+REPLAY (demo paths); Ollama gap tracked separately

- [x] **TD-005**: replanned_plan.json action strings cause noisy diff (20+/20- per role)
  - **Priority**: Medium
  - **Impact**: Demo diff panel shows every role fully changed vs focused 3-5 action delta until real Claude fixtures frozen in BL-003
  - **Source**: [review-foundation-bl001-2026-05-16.md](review-foundation-bl001-2026-05-16.md)
  - **Created**: 2026-05-16
  - **Owner**: Unassigned
  - **Estimated Effort**: BL-003
  - **Notes**: Align unchanged action text between baseline/replanned JSON
  - **Resolved**: 2026-05-16
  - **Resolution**: Resolved BL-003: baseline/replanned fixtures share exact text for unchanged actions; diff now 8+/8-/12-unchanged focused delta, code-quality independently verified

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
