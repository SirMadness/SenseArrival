# Code Review: BL-003 Delay-to-Delight Re-plan & Never-Cut Diff Panel

**Agent:** 🟡 Code-Quality
**Date:** 2026-05-16
**Commit:** 62030fa on `build/sense-arrival-mvp`
**Status:** COMPLETE

---

## Summary

BL-003 delivers the headline demo sequence: one-click delay injection, HTMX fragment swap across all six role cards, and a structured diff panel with trigger + one-line reason per change. The never-cut invariant (TREQ-006) survived the `PlanDiffEntry`/`PlanDiff.entries` model change intact. Two CRITICAL-class findings require action before the 5PM deadline; both are fixable in under 10 minutes. The offline demo path is otherwise deterministic and safe.

---

## Strengths

- Never-cut invariant is structurally sound: `diff()` accepts only `ArrivalPlan` on both sides; `PlanDiff` has no synthesis fields; `GuestSynthesis` is unreachable from every diff path verified below.
- TD-005 fixture redesign delivers a focused, curated diff: 12 unchanged / 8 added / 8 removed across 6 roles — a clear Ms. Chen delay story per role.
- TD-011 `_backfill_role_cards()` correctly handles short live responses: 5-card input → 6-card output in canonical order, valid cards untouched.
- 15 of 16 diff entries carry specific, room-legible reasons. The `_reason_for()` substring lookup approach is appropriate for fixture-based offline demo.
- `POST /replan` diff failure is try/catch-wrapped and returns a diff-less but functional dashboard rather than a 500.
- `GET /diff` JSON spine handles the pre-replan live-mode case with a 202 and a descriptive message.

---

## Issues Found

### CRITICAL

| Issue | Location | Description | Suggested Fix |
|-------|----------|-------------|---------------|
| HTMX loaded from unpkg CDN — network call on every page load | `dashboard.html` line 7 | `<script src="https://unpkg.com/htmx.org@1.9.12">` fires a live DNS/TLS/HTTP request. In offline judging room without network, HTMX fails to load silently. The inject button renders as a plain `<form>` submit that causes a full-page reload (navigation to `/replan`), which returns a full HTML document rather than an `innerHTML` swap. The "no full-page reload" criterion (US-002) breaks. The diff panel still renders in the response body, but the HTMX indicator and swap behavior are lost. | Download `htmx.min.js` to `sense_arrival/static/htmx.min.js` and change the `<script>` src to `/static/htmx.min.js`. One file, no dependency changes. |
| `GET /diff` and `GET /diff-panel` lack error wrapping around `orchestrator.diff()` in REPLAY mode | `main.py` lines 230–234, 263–266 | In REPLAY mode both routes call `orchestrator.diff(baseline_resp.arrival_plan, replanned_resp.arrival_plan)` with no try/except. `diff()` is pure Python and the fixture data validated correctly, so this is a demo-safety concern rather than a known failure mode. However, the "View Diff (JSON)" button on the dashboard is always visible and a judge clicking it before `/replan` in LIVE mode falls through to the 202 branch correctly. In REPLAY mode there is no guard. If the diff call raises for any reason (e.g., corrupted in-memory state after a hot-reload), the route returns a 500 with no diagnostic. | Wrap both calls in a try/except; return JSONResponse or HTMLResponse with a descriptive error rather than a 500. Low probability but zero cost to fix. |

### Medium Priority

| Issue | Location | Description | Suggested Fix |
|-------|----------|-------------|---------------|
| `_call_ollama()` path does not apply TD-011 backfill | `orchestrator.py` lines 355–363 | `_parse_tool_response()` (Claude path) applies `_backfill_role_cards()`. `_call_ollama()` constructs `role_cards` directly without calling `_backfill_role_cards()`. If the Tier-2 Ollama path is used and the model returns <6 cards, the grid collapses. | Add `role_cards = _backfill_role_cards(role_cards)` before the `ArrivalPlan(...)` constructor call in `_call_ollama()`. |
| `GET /offline` and `POST /select` omit `plan_diff` and `replanned` from template context | `main.py` lines 357–363, 419–425 | Both routes call `_tmpl()` without `plan_diff` or `replanned`. In Jinja2, undefined context variables evaluate as `Jinja2.Undefined`, which is falsy but NOT `None`. The template's `{% set diff = plan_diff %}` + `{% elif diff is none %}` branch will silently skip the pending-diff panel section (falls to empty branch) rather than showing "Click Inject to see what changes." No 500, no visual corruption. Minor cosmetic regression vs. `/` behavior. | Add `"plan_diff": None, "replanned": False` to both route contexts. Two lines. |

### Low Priority / Nitpicks

- `Spa` REMOVED entry "Hold a Thursday 4 PM Asaya appointment block…" produces a generic fallback reason ("Original action superseded by delay-adjusted plan for spa") because the action text contains "Asaya" but not the substring key "9:30 AM", "Release", or "recovery-focused". The corresponding ADDED action ("Release Thursday 4 PM Asaya hold…") correctly matches "Release". 1 of 16 entries affected. Acceptable for the demo; a minor `_ROLE_REASONS` key addition would fix it.
- `synthesis_fixture.json` references provenance property IDs `the-carlyle-new-york` and `castiglion-del-bosco` but `config.py` `ALLOWED_PROPERTIES` contains those same slugs, so the scope guard is consistent.

---

## Never-Cut Invariant Certification (TREQ-006)

**CERTIFIED CLEAN.** Independent trace of every path:

1. **`diff()` signature:** `diff(baseline: ArrivalPlan, replanned: ArrivalPlan) -> PlanDiff` — confirmed unchanged. Accepts two `ArrivalPlan` objects only. `GuestSynthesis` is structurally unreachable as an argument.

2. **`PlanDiff` model fields (verified via `model_dump()`):** `['added_actions', 'changed_roles', 'entries', 'rationale', 'removed_actions']`. Keys `synthesis`, `unified_understanding`, `inferred_preferences`, `provenance_properties` are ABSENT.

3. **`PlanDiffEntry` fields:** `['action', 'change_type', 'reason', 'role', 'trigger']`. No synthesis fields.

4. **`diff()` internal body:** Iterates `arrival_plan.role_cards` on both sides using `_CANONICAL_ROLES` ordering. `OrchestratorResponse.synthesis` is never referenced. Entries derive from `priority_actions` set differences only.

5. **`POST /replan` call site:** `orchestrator.diff(baseline_resp.arrival_plan, response.arrival_plan)` — `.arrival_plan` is explicit on both sides. `baseline_resp.synthesis` and `response.synthesis` are not passed.

6. **`GET /diff` JSON call site:** `orchestrator.diff(baseline_resp.arrival_plan, replanned_resp.arrival_plan)` — same pattern.

7. **`GET /diff-panel` call site:** Same explicit `.arrival_plan` access.

8. **`diff_panel.html`:** Zero references to `synthesis`, `unified_understanding`, `inferred_preferences`, or `provenance_properties`. Template renders `diff.entries`, `diff.changed_roles`, `diff.rationale` only.

9. **`dashboard.html` diff block:** Lines 89–97 set `diff = plan_diff` and render `diff_panel.html` include. Synthesis fields appear exclusively in `#synthesis-panel` section (lines 100–111), which is a separate DOM section with no path into `plan_diff`.

---

## TD-005 Status: RESOLVED (confirmed)

Fixture diff verified independently via Python set comparison:
- Unchanged actions: **12** (exact string match across all 6 roles)
- Added actions: **8** (one focused change per role, mostly time adjustments)
- Removed actions: **8** (symmetric)
- Story coherence: 4PM spa hold released → dinner shifted to 7:30PM → turndown adjusted to 8PM → Thursday arc compressed → Friday cycling and Ridge Rosé arc intact.

The diff is a legible 16-entry panel, not a 20+/20+ noisy dump. TD-005 is fully resolved.

---

## TD-011 Status: RESOLVED (confirmed)

`_backfill_role_cards()` verified:
- 5-card input (missing Spa) → 6-card output in canonical role order: PASS
- Placeholder card correctly populated with stub briefing and actions: PASS
- Valid 6-card input → 6-card output with zero corruption to existing cards: PASS
- Applied in `_parse_tool_response()` (Claude path): YES
- Applied in `_call_ollama()` (Ollama path): NO — see Medium issue above.

TD-011 is resolved for the Claude and REPLAY paths (which cover the demo). Ollama path gap is a known partial resolution.

---

## Offline Determinism (US-003 / Demo Safety)

**PASS with one CRITICAL caveat (HTMX CDN load).**

REPLAY path:
- `GET /` → loads `baseline_plan.json` + `synthesis_fixture.json` from disk. Zero network. Pydantic validation clean.
- `POST /replan` → loads `replanned_plan.json` + `synthesis_fixture.json`. Calls `orchestrator.diff()` (pure Python, no I/O). 16 entries rendered with trigger and reason. Zero network from Python side.
- `GET /diff` → same diff from cached in-memory `OrchestratorResponse` objects. Zero network.
- `GET /diff-panel` → same. Zero network from Python side.

**CRITICAL:** The browser must load HTMX from `unpkg.com` to execute the fragment-swap behavior. Without network in the judging room, HTMX fails silently and the inject button falls back to a standard form submit (full navigation). The response body is correct, but the "no full-page reload" UX criterion (US-002) breaks and the HTMX indicator is not shown. This must be fixed before the demo.

---

## US-002 Assessment

- Single visible "Inject Delay & Re-plan" button: PASS (`.btn-inject` class, prominent placement).
- Affected role cards update with `role-card--changed` highlight and "Updated" badge: PASS (verified in template logic against `plan_diff.changed_roles`).
- Mood banner updates with `mood-banner--replanned` class: PASS.
- No full-page reload: CONDITIONAL PASS — only if HTMX is available. If HTMX CDN fails (offline room), this criterion fails. Fix the CDN issue.
- Under 10 seconds: PASS in REPLAY mode (fixture read is sub-second). PASS in Claude mode (single tool-use call, no chat loop).

---

## US-003 Legibility Assessment

- Diff panel renders with dark header, orange trigger banner, per-entry +NEW/-OUT badges, action text, and italic reason: PASS.
- 16 entries across 6 roles with role-group separators: PASS.
- 15/16 entries have specific, room-legible one-line reasons: PASS.
- 1/16 entry (Spa REMOVED "Hold a Thursday 4 PM Asaya") has generic reason: LOW severity.
- Trigger text "120-min flight delay — revised ETA 5:30 PM" consistently applied to all entries: PASS.

---

## Regression Assessment (BL-001/BL-002 Baseline)

- `GET /` context now includes `plan_diff=None, replanned=False`: additive, no breaking change. Template renders pending diff panel correctly.
- `_tmpl()` wrapper still routes to `dashboard.html`: unchanged.
- 3-tier backend toggle (`Backend.REPLAY` / `.CLAUDE` / `.OLLAMA`) logic in `plan()` and `replan()` is unchanged; new `diff()` is called after, not instead of, the backend dispatch.
- `GET /diff` JSON contract: `entries` field is additive (`entries: list[PlanDiffEntry] = []` default). Existing consumers of `changed_roles`, `added_actions`, `removed_actions`, `rationale` are unaffected.
- Model imports in `orchestrator.py` correctly include `PlanDiffEntry` alongside `PlanDiff`.
- No new dependencies.

**BL-001/BL-002 regression: NONE detected.**

---

## Security Assessment

- [ ] Input validation present — fixture loader scope guard (`ALLOWED_DOSSIERS`, `ALLOWED_PROPERTIES`) blocks path traversal via guest_id/property_id parameters.
- [x] No injection vulnerabilities — diff is pure Python set arithmetic on fixture data; no SQL, no shell.
- [x] Auth/authz correct — single-user demo app; no auth surface changed.
- [x] Secrets not exposed — `ANTHROPIC_API_KEY` remains env-only; not referenced in templates or JS.

---

## Performance Assessment

- [x] No N+1 queries — diff is O(n) over role cards; fixture reads are cached at startup.
- [x] Appropriate caching — `cached_baseline` and `cached_replanned` loaded at startup in REPLAY mode.
- [x] No memory leaks — `session_observations` is a plain list, reset on restart; no unbounded growth in the demo path.

---

## Flagged Items

- **BLOCKER:** HTMX loaded from `https://unpkg.com` CDN. In offline judging environment, HTMX will fail to load, breaking the fragment-swap UX and the "no full-page reload" criterion. Download `htmx.min.js` to `sense_arrival/static/` and update `dashboard.html` line 7. Fix time: ~3 minutes.
- **BLOCKER (low probability / fix anyway):** `GET /diff` and `GET /diff-panel` lack try/except around `orchestrator.diff()`. If diff raises in REPLAY mode (e.g., after a hot-reload that resets `app.state`), the route returns an unhandled 500. Fix time: ~5 minutes.
- **TD:** `_call_ollama()` does not apply `_backfill_role_cards()`. If Ollama path is used as fallback and model returns <6 cards, UI grid collapses. Ollama is Tier-2 and not used in the demo path; log as residual tech debt.
- **TD:** `GET /offline` and `POST /select` missing `plan_diff=None, replanned=False` in template context. Cosmetic only (pending diff panel not shown on those routes). Not in demo path.
- **TD (DQ carry-forward):** `_ROLE_REASONS` is tuned to current fixture action strings. Live Claude runs producing different wording fall back to generic reasons. Acceptable for demo; noted.
- **TD-005 resolved:** confirmed above.
- **TD-011 resolved (REPLAY + Claude paths):** confirmed above. Ollama gap noted.

---

## Verdict

**CRITICAL — FIX REQUIRED before demo**

The never-cut invariant is **certifiably intact** and TD-005/TD-011 are resolved as claimed. The demo sequence (baseline → inject delay → replan → diff panel) is deterministic and produces a legible, focused 16-entry diff with correct trigger and reasons — the creative proof works.

Two CRITICAL items must be fixed before the 5PM deadline:

1. **Vendor HTMX** — download `htmx.min.js` to `static/`, update `dashboard.html`. Without this, the offline demo room breaks US-002 ("no full-page reload").
2. **Wrap `diff()` calls in `GET /diff` and `GET /diff-panel`** — add try/except to prevent an unhandled 500 from reaching the judges. Low probability but zero cost.

Both fixes are mechanical, under 10 minutes combined, and do not touch the diff data model or the never-cut spine.

---

## Reasoning

**Decision chain:**
1. The highest-stakes question was whether `GuestSynthesis` could reach `PlanDiff` through the model delta. Independent trace of all seven paths (diff signature, model schema, three call sites in main.py, two templates) confirmed structural exclusion. No synthesis field exists on `PlanDiff` or `PlanDiffEntry`; the model_dump() proof seals it.
2. TD-005 was independently verified via Python set arithmetic — not taken from the engineer's self-report. 12 exact string matches, 8 symmetric changes, internally consistent Ms. Chen delay story.
3. TD-011 was independently exercised with 5-card and 6-card inputs. Both paths correct. The Ollama gap is a real but non-demo-path issue.
4. The HTMX CDN finding is CRITICAL because the judging room is stated as offline and US-002 depends on HTMX executing the swap. A fallback form submit still renders the correct HTML, but judges would see a full-page navigation, not the HTMX UX — this directly undermines the "magic moment" story.
5. The unprotected `diff()` calls in GET routes are low-probability CRITICAL risks. In REPLAY mode the fixture data is pre-validated and diff() is deterministic, so actual failure is unlikely. However, an unhandled 500 on the "View Diff (JSON)" spine URL during judging would be a visible failure.

**Constraints applied:** Hackathon deadline — only CRITICAL/blocking issues raised. Style, test depth, and non-demo-path issues logged as tech debt, not blocking.

**Confidence:** High. Never-cut invariant verified by static code trace + runtime model_dump() proof + template inspection. TD-005 verified by independent fixture analysis. TD-011 verified by independent unit simulation. HTMX CDN risk verified by template inspection + network dependency analysis.
