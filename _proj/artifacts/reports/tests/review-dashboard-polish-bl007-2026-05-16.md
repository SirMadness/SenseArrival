# Code Review: BL-007 Dashboard Polish + TD-014/017/009/016 Fixes

**Agent:** Code-Quality
**Date:** 2026-05-16
**Commit:** `d9bd1d4` on `build/sense-arrival-mvp`
**Mode:** review (CRITICAL/blocking only — hard 5PM hackathon)
**Status:** COMPLETE

---

## Summary

BL-007 restructures `dashboard.html` into a 3-panel CSS grid, adds responsive collapse, and resolves four tech-debt items (TD-014, TD-017, TD-009, TD-016) entirely in `main.py`. The `orchestrator.py` and `models.py` diffs are zero lines — confirmed. The never-cut spine is untouched. All four TD fixes are correctly implemented. One pre-existing unescaped path (`{exc}` in the diff-panel error handler) was not introduced by this commit and is not demo-reachable in the canonical path; it is noted as a low-priority carry item only. No CRITICAL findings.

**VERDICT: PASS WITH TECH DEBT**

---

## Strengths

- All four TD fixes are present, correctly placed, and narrowly scoped. Zero structural changes to the spine.
- `html.escape()` is applied at every LLM/user-derived injection point in all four inline HTML builder functions. The BL-008 medium finding (TD-017) from the prior review is now fully resolved.
- TD-014 fix (200 vs. 400) closes both the form-submit path and the JS mic path, which the prior review noted `required` would not cover.
- TD-009 (`app.state.live_baseline = response`) and TD-016 (`session_observations` arg) are one-line additions each, correctly placed and do not alter any other route.
- CSS grid with `260px 1fr 1fr` and `@media (max-width:1100px)` fallback to `1fr` is sound. At 1280px the grid produces columns of 260 / 510 / 510 — no element has a fixed width exceeding those bounds; no horizontal scroll surfaces exist.
- Jinja2 template render path in `dashboard.html` continues to auto-escape all `{{ }}` expressions, so the Jinja2-rendered sections (initial page load) carry no XSS risk.
- `orchestrator.py` / `models.py` confirmed zero-change by `git diff` byte count (0 lines).
- `GET /diff` JSON confirmed: keys are `['changed_roles', 'added_actions', 'removed_actions', 'rationale', 'entries']` — no `synthesis` or `inferred_from` fields.

---

## Issues Found

### Critical

None.

### High Priority

None.

### Medium Priority

None introduced by this commit.

### Low Priority / Nitpicks

**L-001 — Pre-existing: `{exc}` unescaped in diff-panel error handler (`main.py:279`)**

`_render_diff_panel_error` at lines 277–282 injects a Python exception string directly into HTML:

```python
f'<p><strong>Diff unavailable:</strong> {exc}</p>'
```

`exc` is a Python exception message from `orchestrator.diff()`, not user input. In normal operation this path is unreachable (`orchestrator.diff()` does not raise on valid `ArrivalPlan` inputs). It was present before BL-007 and was not introduced or worsened by this commit. Not demo-reachable in the canonical rehearsed path. Log as carry-forward tech debt.

**L-002 — `card_id_slug` is injected into `hx-get` URL attribute without escaping (`main.py:610`)**

```python
card_id_slug = card.role.lower().replace(" ", "-")
f'<button hx-get="/voice/tts/{card_id_slug}" ...'
```

`card.role` is an LLM-derived string. `html.escape()` was correctly applied to the visible text (`html.escape(card.role)` in the `<h3>`), but `card_id_slug` inserted into the `hx-get` attribute is not HTML-attribute-escaped. In practice, role names from the fixture and Claude tool schema are controlled values (`"Front Desk"`, `"Concierge"`, etc.) that produce safe slugs. A crafted role name with `"` or `>` characters could break the attribute boundary but cannot reach this path in the demo. Pre-existing pattern; not introduced by BL-007. Log as carry-forward tech debt.

---

## TD Fix Verification

| TD | Claim | Verification | Status |
|----|-------|-------------|--------|
| TD-014 | Blank textarea returns HTTP 200 with visible error fragment; HTMX always swaps it | `main.py:375–381`: `else` branch returns `HTMLResponse(..., status_code=200)` with `<p class="observation-error">`. HTMX swaps 2xx responses into `#staff-note-result` by default. Both form-submit and JS mic paths are covered (mic path posts audio; text path requires non-empty `text_input.strip()` to bypass this branch). | **RESOLVED** |
| TD-017 | `html.escape()` applied to all LLM/user-derived strings in all 4 inline HTML builders | Confirmed at: `_render_dossier_observations_oob` (line 440: `display`); `_render_synthesis_oob` (lines 471, 474, 475, 481, 485, 494: `item.text`, `item.source_property`, `item.source_observation`, each `p` in `inferred_preferences`, each `pid` in `provenance_properties`, `syn.unified_understanding`); `_render_observation_feedback` (lines 536, 538: `display_text`, `role_label`); `_render_role_cards_oob` (lines 572, 578, 586, 597, 609, 614: `priority_actions`, `mood`, `suppressed` items both branches, `card.role`, `card.briefing`). All sinks covered. | **RESOLVED** |
| TD-009 | `POST /select` sets `app.state.live_baseline` to the selected plan | `main.py:765`: `app.state.live_baseline = response` appears immediately after `orchestrator.plan()` returns and before the `except NotImplementedError` guard. A subsequent `GET /diff` reads `app.state.live_baseline` at line 224. Correct. | **RESOLVED** |
| TD-016 | `orchestrator.plan()` in `/select` receives `session_observations` | `main.py:761`: `app.state.session_observations` passed as the fourth positional arg, matching the `index()` call pattern (line 119) and `replan()` call pattern (line 179). `session_observations` is optional with default `None` in the orchestrator signature, so the prior 3-arg call was safe but incomplete. | **RESOLVED** |

---

## TD-009 Residual Note (not a blocker)

`POST /select` sets `app.state.live_baseline = response` but does NOT reset `app.state.live_replanned`. After a guest-switch via `/select`, if the user then calls `GET /diff` without first running `/replan`, `live_replanned` will hold the stale replanned plan from the prior guest. The `GET /diff` handler requires both `live_baseline` and `live_replanned` to be non-None; if `live_replanned` is still set from a prior session, the diff will be calculated between the new guest's baseline and the old guest's replanned plan — producing a misleading diff.

This is a P1/demo-optional path (selector is disabled in offline mode; the canonical demo path does not use it). It does not affect the rehearsed demo. Log as tech debt for the live-mode guest-switch flow.

---

## Never-Cut Spine Certification

**CERTIFIED CLEAN — 5th consecutive certification.**

Evidence:
1. `git diff d9bd1d4^ d9bd1d4 -- sense_arrival/orchestrator.py sense_arrival/models.py` = 0 lines.
2. `orchestrator.diff()`, `PlanDiff`, `PlanDiffEntry`, `ArrivalPlan`, `GuestSynthesis` boundary: byte-identical to BL-008 delivery.
3. `GET /diff` handler (lines 219–242) reads `arrival_plan` only; `OrchestratorResponse.synthesis` not referenced.
4. `GET /diff-panel` handler (lines 249–283) identical structural pattern.
5. `_render_synthesis_oob()` is only called from `voice_transcribe` when `classification == "dossier_observation"` — structurally unreachable from `GET /diff`, `GET /diff-panel`, `POST /replan`.
6. Engineer smoke test: `GET /diff` JSON keys = `['changed_roles', 'added_actions', 'removed_actions', 'rationale', 'entries']`, 16 entries, no synthesis fields.

---

## Offline Zero-Network Certification

**CERTIFIED CLEAN.**

Evidence:
1. `POST /select` in `Backend.REPLAY` returns HTTP 503 before any `orchestrator.plan()` call (line 748–752). TD-009/TD-016 fixes only activate in live mode. Zero new network exposure in offline mode.
2. All changed code paths in `main.py` are either pure Python string builds (`_render_*` helpers) or sync state assignments. No new I/O introduced.
3. `import html` (stdlib) introduces no network-capable dependency.
4. `GET /` in `Backend.REPLAY`: still reads from `app.state.cached_baseline`/`cached_replanned` (fixture). The 3-panel grid template restructure does not touch the data-loading path.

---

## Demo-Legibility Sanity Check (US-010)

| Criterion | Assessment |
|-----------|-----------|
| 3 panels present | `#three-panel-grid` with `.panel-inputs` / `.panel-signals` / `.panel-roles` confirmed in dashboard.html diff. |
| No horizontal scroll at 1280–1440px | `grid-template-columns: 260px 1fr 1fr`. At 1280px: 260 + 510 + 510 = 1280 exactly. No fixed-width child exceeds column bounds. `@media (max-width:1100px)` collapses to `1fr`. `max-width:1440px` on `body` prevents overflow on wide screens. Sound. |
| Primary actions single-click obvious | Inject Delay (`btn-inject`) in Panel A: `display:block; width:100%; font-size:1.15rem; font-weight:bold`. Submit Observation (`obs-submit-btn`): `btn-primary`. Play Briefing (`tts-btn`): changed from ghost to filled rosewood. All three are the visually dominant element in their column. |
| Suppression empty-state placeholder | `{% else %}` branch renders `.suppression-panel--placeholder` with `<h2>` and explanatory `<p>`. Layout structurally identical to populated state — no layout break. |
| BL-008 synthesis/dossier panels intact | Both `#synthesis-panel` and `#dossier-panel` moved to full-width rows below the grid. Structural markup unchanged from BL-008 delivery; only the surrounding grid wrapper was added. OOB swap targets (`#synthesis-panel`, `#dossier-observations-list`) unchanged. |

---

## Security Assessment

- [x] Input validation present — blank/whitespace textarea returns 200 inline error (TD-014); audio path falls back on STT failure.
- [x] No injection vulnerabilities — all 4 inline HTML builders now escape LLM/user-derived content with `html.escape()`. Jinja2 template rendering auto-escapes. One pre-existing carry item (L-001 `{exc}`, not demo-reachable) and one attribute-context gap (L-002 `card_id_slug`) noted as low-priority.
- [x] Auth/authz — n/a for demo app, no auth surface.
- [x] Secrets not exposed — no API keys in changed files.

---

## Performance Assessment

- [x] No N+1 queries — no database.
- [x] No new I/O in any changed path — all `_render_*` helpers are pure string builds.
- [x] No memory leaks — `session_observations` list unchanged; no new state added.
- CSS grid layout adds no JS or render-blocking resources.

---

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Three clear panels: inputs/triggers, mood+diff+suppression, role cards with Play | Met | `#three-panel-grid` with `.panel-inputs` / `.panel-signals` / `.panel-roles`. Inject in A, diff+mood+suppression in B, role cards+TTS in C. Synthesis+dossier full-width below. |
| High-contrast, large-font; three primary actions single-click and obvious | Met | `btn-inject` 1.15rem bold on rosewood; Play changed to filled rosewood; Submit uses `btn-primary`. All three are the highest-contrast element in their column. |
| Layout holds without horizontal scroll at 1280–1440px | Met | `260px 1fr 1fr` grid; at 1280px columns sum exactly to viewport width; `@media (max-width:1100px)` collapses to single-column; no fixed-width overflow surfaces. |
| Suppression renders gracefully when no suppression data | Met | `{% else %}` branch renders `.suppression-panel--placeholder`. Structural layout identical to populated state. |

---

## Flagged Items

- **TD-014: RESOLVED** — blank textarea `POST /voice/transcribe` now returns HTTP 200 with visible inline error; HTMX swaps it correctly.
- **TD-017: RESOLVED** — `html.escape()` applied at every LLM/user-derived sink in all 4 inline HTML builders. No unescaped sink remains in the demo-reachable path for user or LLM content.
- **TD-009: RESOLVED (with residual)** — `POST /select` sets `app.state.live_baseline`. Residual: `live_replanned` is not cleared on guest-switch, so a `/select` followed immediately by `GET /diff` (without `/replan`) could diff new-guest baseline vs old-guest replanned. Not demo-reachable (selector disabled in offline mode; canonical demo does not use selector). Log as TD for live-mode guest-switch.
- **TD-016: RESOLVED** — `orchestrator.plan()` in `/select` now receives `app.state.session_observations` as the fourth positional arg.
- **TD (carry-forward, LOW):** `{exc}` at `main.py:279` injects exception string into HTML without escaping. Pre-existing; not demo-reachable. Post-hackathon hardening.
- **TD (carry-forward, LOW):** `card_id_slug` at `main.py:610` injected into `hx-get` URL attribute without HTML-attribute-escaping. Role names are fixture/schema-controlled; not exploitable in demo path. Post-hackathon hardening.

---

## Verdict

**PASS WITH TECH DEBT**

BL-007 is approved to close.

Critical blockers: none.

All 4 TD fixes (TD-014, TD-017, TD-009, TD-016) are correctly implemented and verified against source.

Never-cut spine: intact and certified clean for the 5th consecutive review.

Offline zero-network: preserved. TD fixes do not activate any new code path in `Backend.REPLAY`.

Demo-legibility: 3-panel grid is structurally sound at 1280–1440px. All three primary actions are single-click and visually dominant. Suppression empty-state renders correctly. BL-008 synthesis and dossier panels are preserved and their OOB swap targets are unchanged.

Two low-priority carry items noted (pre-existing, not introduced by this commit, not demo-reachable in the canonical path). No MEDIUM or CRITICAL findings.

---

## Reasoning

**Decision chain:**

1. The TD-017 review was the highest-risk item. Each of the four inline HTML builders was traced individually against the diff, verifying `html.escape()` at every data-derived injection point. `badge_class` and `card_id_slug` were checked separately: `badge_class` is constructed from `classification`, which is a hardcoded return value from `_classify_observation()` — not user content — so omitting escape there is correct. `card_id_slug` is inserted into an HTML attribute context (not text content), where `html.escape()` would still help but the value is constrained by the schema. Neither creates a demo-exploitable path.

2. TD-014: the 200 vs. 400 fix was confirmed correct by reading the `else` branch at lines 375–381. The branch is reached when `source == "text"` and `text_input` is falsy or whitespace-only. The mic path (`audio is not None`) is handled by the preceding `elif`, so both submission paths are covered.

3. TD-009: `live_baseline` assignment at line 765 is placed after `orchestrator.plan()` succeeds and before the `except NotImplementedError` guard. If `plan()` raises, `live_baseline` is not set — correct behavior (no partial state). The residual (stale `live_replanned` on guest-switch) is real but confined to the live-mode selector path, which is disabled in OFFLINE_MODE and outside the canonical demo.

4. TD-016: the fourth positional arg addition is safe because `session_observations` has a default value in the orchestrator signature. Verified that `index()` and `replan()` use the same call pattern.

5. Never-cut spine: `git diff` byte count = 0 for `orchestrator.py` and `models.py`. All diff handler routes verified to pass only `arrival_plan` to `orchestrator.diff()`. Spine certification is structural, not test-execution-based.

6. The pre-existing `{exc}` unescaped injection was not introduced by BL-007 but surfaces in the diff of the surrounding function. It was assessed as low-priority because: (a) `orchestrator.diff()` only raises on truly unexpected internal errors; (b) the exception message would originate from Pydantic or Python internals, not user input; (c) not demo-reachable in the canonical path.

**Constraints applied:** CRITICAL/blocking only per hackathon hard-5PM constraint. Skipped style, naming, test depth, and pixel aesthetics per delegation instructions.

**Confidence:** High. All changed lines in `main.py` were read in full. The `dashboard.html` diff was read in full for structural correctness; Jinja2 auto-escape covers the template path. CSS grid was verified mathematically against the 1280px target. TD fix correctness verified by line-level source reading, not solely from the engineer report.

---

*Agent: Code-Quality | Date: 2026-05-16 | Commit: d9bd1d4 | Branch: build/sense-arrival-mvp*
*Status: PASS WITH TECH DEBT — BL-007 approved to close*
