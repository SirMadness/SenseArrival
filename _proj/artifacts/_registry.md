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

- **Total Reports**: 20
- **Active Work**: 0
- **Completed This Week**: 20
- **Last Updated**: 2026-05-16

---

## Active Work

| Report | Category | Agent | Started | Summary |
|--------|----------|-------|---------|---------|

_No active work._

---

## Completed Work (Last 7 Days)

| Report | Category | Agent | Completed | Summary |
|--------|----------|-------|-----------|---------|
| final-offline-smoke-2026-05-16 | tests | code-quality | 2026-05-16 | VERDICT DEMO-READY — full rehearsed OFFLINE path verified 9/9 PASS, zero-network proven (8 code paths), <20ms responses, HTMX local, never-cut diff has no synthesis/suppression keys; verified click sequence produced; 1 LOW (generic Spa diff reason) |
| ADR-001-amendment-live-default-2026-05-16-2026-05-16 | architecture | architect | 2026-05-16 | ADR-001 amendment: corrected demo-mode default — live Claude+ElevenLabs is primary/showcased path (TREQ-013 Tier-1), OFFLINE_MODE/replay reframed as rehearsed network fallback not default; auditable dated amendment note added, Status stays Accepted, stack/routes/cut-order untouched; consistent w/ ADR-002 Delta 5 |
| review-suppression-bl006-2026-05-16 | tests | code-quality | 2026-05-16 | PASS WITH TECH DEBT — never-cut 6th cert CLEAN, offline determinism confirmed, US-006 met, no regressions; project CLEAR TO LOCK; 2 LOW no-action |
| suppression-bl006-2026-05-16 | implementation | engineer | 2026-05-16 | Tasteful-restraint suppression: Suppression model as separate OrchestratorResponse field (mirrors GuestSynthesis, never in PlanDiff); 3 baseline / 4 replanned offline fixtures for Ms.Chen; concierge-framed panel fills BL-007 slot. Commit ea409a9 |
| review-dashboard-polish-bl007-2026-05-16 | tests | code-quality | 2026-05-16 | PASS WITH TECH DEBT — 4 TD fixes confirmed resolved; never-cut spine 5th cert clean; offline zero-network certified; US-010 legibility met; 2 LOW pre-existing carry-forward |
| dashboard-polish-bl007-2026-05-16 | implementation | engineer | 2026-05-16 | Room-legible 3-panel dashboard (260px inputs | mood+diff+suppression | role cards w/ filled Play Briefing), no horiz scroll @1280-1440, empty-state suppression; resolved TD-014/017/009/016. Commit d9bd1d4 |
| review-portfolio-synthesis-bl008-2026-05-16 | tests | code-quality | 2026-05-16 | PASS WITH TECH DEBT — never-cut spine CERTIFIED CLEAN (4th, programmatic); offline zero-network + no-disk-write certified; 2 MED (HTML escape, offline single-guest synthesis) deferred; P0 set clear |
| portfolio-synthesis-bl008-2026-05-16 | implementation | engineer | 2026-05-16 | Cross-visit synthesis (InferredPreference + GuestSynthesis.inferred_from): explicit 'inferred from prior stays' panel naming source property+observation; staff-note->dossier->re-synthesis OOB shim (in-memory); offline deterministic. Commit 0812575 |
| review-voice-layer-bl005-2026-05-16 | tests | code-quality | 2026-05-16 | PASS WITH TECH DEBT — offline zero-network CONFIRMED, never-cut spine CONFIRMED, TD-006 resolved; M-001 blank-submit + M-002 silent-frame + LOW select-args deferred; BL-008 clear |
| voice-layer-bl005-2026-05-16 | implementation | engineer | 2026-05-16 | Voice layer: typed-text P0 path (classify->HTMX card update), ElevenLabs TTS Play Briefing reading current/re-planned briefing, mic STT P1 w/ guard+Text-mode fallback; offline cached m4a (TD-006). Commit 41bc223 |
| compliance-readme-bl004-2026-05-16 | implementation | docs | 2026-05-16 | Public README (PS#1 named, dual-card model + Radha Arora validation, honest Built-Today scope, offline quickstart) + demo-playbook (3-min script, ADR-001 cut order never-cut TREQ-006, offline rehearsal). 2 user actions flagged: make repo public, capture backup assets |
| review-delay-to-delight-bl003-2026-05-16 | tests | code-quality | 2026-05-16 | Never-cut invariant CERTIFIED CLEAN (7-path trace); TD-005/TD-011 verified resolved; 2 CRITICAL (CDN HTMX, unguarded diff) found+fixed in 3115007 + Main-verified |
| delay-to-delight-bl003-2026-05-16 | implementation | engineer | 2026-05-16 | Never-cut Delay-to-Delight: 1-click delay->HTMX re-plan (no reload), room-legible what-changed diff (trigger+reason/change), clean deterministic offline fixtures; HTMX vendored local + diff routes guarded. Commits 62030fa,3115007 |
| review-orchestration-bl002-2026-05-16 | tests | code-quality | 2026-05-16 | PASS WITH TECH DEBT — never-cut spine verified intact end-to-end; structured-output fallback sound; 3-tier toggle clean; 2 MED + 3 LOW deferred |
| orchestration-core-bl002-2026-05-16 | implementation | engineer | 2026-05-16 | Tier-1 Claude tool-use plan()/replan() returning OrchestratorResponse; GET / renders grounded baseline (mood + 6 role cards, Sand Hill anchors); 3-tier dispatch; graceful fixture fallback; spine clean. Commit 38f766f |
| review-foundation-bl001-2026-05-16 | tests | code-quality | 2026-05-16 | PASS WITH TECH DEBT — model conformance, scope guard, zero-network replay, never-cut spine all confirmed clean; 1 MED + 3 LOW deferred |
| foundation-runtime-bl001-2026-05-16 | implementation | engineer | 2026-05-16 | FastAPI app skeleton: 8 ADR-002 Pydantic models, raw-MD fixture loader, scope guard (frozenset allowlist, no live APIs), 3-tier backend selector, diff() spine works in replay; plan/replan/voice stubbed for BL-002. Commit b0317ae |
| rosewood-property-dossier-research-2026-05-16 | analysis | analyst | 2026-05-16 | 3 property profiles (Sand Hill deep/8 anchors; Carlyle NY + Castiglion del Bosco provenance) + 3 cross-property guest dossiers; demo-grade Dossier A drives cyclist/wine/solo-decompressor 'they just knew' synthesis |
| ADR-002-portfolio-guest-graph-2026-05-16 | architecture | architect | 2026-05-16 | Cycle-2 delta ADR: GuestProfile->GuestDossier + PropertyCard/GuestSynthesis; Markdown dossier/property fixtures + JSON replay; synthesis folded into plan()/replan() and EXCLUDED from PlanDiff (spine-safe); /select routes + /voice/transcribe reuse for staff-note shim (in-memory); canonical offline path = Ms.Chen@Sand Hill |
| ADR-001-stack-selection-2026-05-16 | architecture | architect | 2026-05-16 | Stack ADR for full 7-FEAT/18-TREQ set: Python/FastAPI/Jinja2-HTMX, Pydantic v2 models, route table, 3-tier LLM resilience (Claude->Ollama->fixtures), offline mode, ruthless cut order (never cut TREQ-006) |

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
