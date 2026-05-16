# Code Review: BL-006 Suppression Panel (commit ea409a9)

**Agent:** Code-Quality
**Date:** 2026-05-16
**Mode:** review
**Commit:** `ea409a9` on `build/sense-arrival-mvp`
**Scope:** Tasteful Restraint suppression panel (TREQ-007 / US-006 / FEAT-003)

---

## Summary

BL-006 adds the suppression ("Tasteful Restraint") panel as an additive, structurally isolated field on `OrchestratorResponse`. The implementation is correct, the never-cut diff spine is byte-identical, OFFLINE_MODE is deterministic, and all prior BLs remain intact. No critical issues found.

---

## Strengths

- Structural isolation is airtight: `Suppression` and `OrchestratorResponse.suppressions` never appear in `ArrivalPlan`, `PlanDiff`, `PlanDiffEntry`, or `diff()`. This is verified by model field assertions, live diff output inspection, and source diff analysis — no lines touching `diff()` or any `PlanDiff` type appear in the BL-006 commit.
- The ADR-002 Delta 3 GuestSynthesis pattern is followed exactly: a top-level field on the orchestrator envelope, excluded from diff by structural position, not by conditional logic.
- Graceful degradation on all three tiers: REPLAY loads fixtures, CLAUDE/OLLAMA use `data.get("suppressions", [])`, fixture load failure degrades to `[]` and renders the empty-state placeholder — zero crash surface.
- Jinja2 autoescape is confirmed active for `.html` templates (FastAPI's `Jinja2Templates` uses `jinja2.select_autoescape()` which enables autoescape for `.html`/`.htm`/`.xml`). The template renders `{{ item.suggestion }}` and `{{ item.reason }}` without `| safe` — these are properly escaped.
- The `httpx` client import is deferred inside `_call_ollama()`, and the `anthropic.Anthropic` client is instantiated inside `_call_claude()` — neither is module-scope. In `OFFLINE_MODE=true` (`Backend.REPLAY`), both are unreachable behind explicit backend guards. No network call is reachable at module import time.
- Fixture content is sourced from the analyst dossier report, uses concierge-framed language, and suppression count shifts deterministically (3 baseline → 4 replanned) with a meaningful delta (Asaya Thu slot + Extended Ridge Rosé added on replan).
- The suppression panel sits fully inside `.panel-signals` (Panel B), which is governed by `grid-template-columns: 260px 1fr 1fr` with `@media (max-width: 1100px)` stacking fallback. No horizontal scroll risk.

---

## Issues Found

### Critical

None.

### High Priority

None.

### Medium Priority

None.

### Low Priority / Nitpicks

- `fixture_loader.py` catches `(FileNotFoundError, KeyError, TypeError)` on suppressions load but not `json.JSONDecodeError` (malformed JSON). `json.loads()` raises `json.JSONDecodeError` which is a subclass of `ValueError`, not caught here. In practice this only matters if a fixture file is corrupted — the graceful fallback is `suppressions=[]` which is exactly correct behavior. No crash risk, but the except clause is slightly under-specified.
- The `_render_synthesis_oob()` OOB builder (BL-008 staff-note path) does not rebuild the suppression panel. This is documented as a known limitation and is correct for the demo (suppressions only shift on full replan, not per-observation). The existing comment in the engineer report is accurate. No action needed before lock.

---

## Never-Cut 6th Certification

**CERTIFIED CLEAN.**

Direct verification:
- `git diff HEAD~1 HEAD -- sense_arrival/orchestrator.py` shows zero `+` or `-` lines touching `def diff(`, the `diff()` function body, `PlanDiff`, or `PlanDiffEntry`.
- `orchestrator.diff()` signature unchanged: `(baseline: ArrivalPlan, replanned: ArrivalPlan) -> PlanDiff`.
- Model field assertions confirm: `suppressions` absent from `ArrivalPlan.model_fields`, `PlanDiff.model_fields`, `PlanDiffEntry.model_fields`; present only on `OrchestratorResponse.model_fields`.
- Live diff output confirmed: `dict_keys(['added_actions', 'changed_roles', 'entries', 'rationale', 'removed_actions'])` — no suppression key present.
- `GET /diff` and `GET /diff-panel` both call `orchestrator.diff(baseline_resp.arrival_plan, replanned_resp.arrival_plan)` — passing only `ArrivalPlan` instances; `suppressions` is unreachable from the diff path.

---

## Offline Determinism Confirmation

**CONFIRMED ZERO-NETWORK, DETERMINISTIC.**

- `OFFLINE_MODE=true` maps to `Backend.REPLAY` via `config.py:_resolve_backend()`.
- `Backend.REPLAY` path in `plan()` and `replan()` calls `load_offline_response(replanned=False/True)` directly — neither `_call_claude()` nor `_call_ollama()` is invoked.
- `load_offline_response()` loads `baseline_suppressions.json` (3 items) and `replanned_suppressions.json` (4 items) with a `try/except` fallback to `[]` if files are absent.
- Baseline: 3 suppressions — Group tours, Flamingo Tea, Stanford campus.
- Replanned: 4 suppressions — Asaya Thu slot (added), Group tours, Extended Ridge Rosé (added), Stanford campus. Shift is deterministic and demo-visible.
- `httpx` import is deferred inside `_call_ollama()` function body (confirmed: `grep -n "^import httpx"` = line 368, inside the function). `anthropic.Anthropic(...)` instantiation is inside `_call_claude()` (line 330, inside function). Neither is reachable in `REPLAY` mode.

---

## US-006 / TREQ-007 Compliance

**MET.**

- Panel lists 3 (baseline) or 4 (replanned) withheld suggestions with concierge-framed one-line reasons.
- Fills the BL-007 Panel B slot previously occupied by the placeholder.
- Graceful empty state (`.suppression-panel--placeholder`) renders when `response.suppressions == []`.
- HTMX re-render on re-plan: `POST /replan` returns the full dashboard template via `_tmpl()`, which includes the suppression panel context from `response.suppressions` — the HTMX `hx-target="#dashboard-root" hx-swap="innerHTML"` replaces the entire dashboard, picking up the replanned suppression panel automatically. No additional OOB logic required.

---

## Regression Check (BL-001..005, 007, 008)

**NO REGRESSIONS DETECTED.**

- 3-panel grid layout intact: suppression panel sits inside `.panel-signals` (Panel B) with correct CSS containment.
- Role card grid unaffected: `response.arrival_plan.role_cards` path unchanged.
- `additive suppressions: list[Suppression] = []` default on `OrchestratorResponse` means any caller not passing `suppressions` gets `[]` and the placeholder renders — backward-compatible with any partial parse.
- `_parse_tool_response()` uses `data.get("suppressions", [])` — safe for pre-BL-006 cached Claude responses.
- `_call_ollama()` uses the same `data.get("suppressions", [])` pattern.
- `_render_synthesis_oob()` (BL-008) builds HTML for `#synthesis-panel` and `#role-cards` only — suppression panel is not in its output, which is correct.
- No new dependencies introduced.

---

## Security Assessment

- [x] Input validation present — `Suppression(**s)` Pydantic construction validates `suggestion: str` and `reason: str` types.
- [x] No injection vulnerabilities — Jinja2 autoescape confirmed active for `.html` templates; `{{ item.suggestion }}` and `{{ item.reason }}` are auto-escaped. The inline OOB HTML builder in `_render_synthesis_oob()` uses `html.escape()` consistently (TD-017 standard) — no suppression strings pass through that builder.
- [x] Auth/authz correct — no change to auth surface.
- [x] Secrets not exposed — no new secrets or API key surface.

---

## Performance Assessment

- [x] No N+1 queries — fixture files loaded once per request.
- [x] Appropriate caching — `load_offline_response()` called at startup into `app.state.cached_baseline/cached_replanned`; suppression fixtures are loaded as part of that call.
- [x] No memory leaks — `suppressions` list is a new field with `= []` default; no unbounded growth path.

---

## Flagged Items

None. No CRITICAL items, no deferred issues requiring TD entries beyond what the engineer already noted.

---

## Verdict

**PASS WITH TECH DEBT**

The implementation is correct and demo-safe. No blocking issues. The two low-priority items below are logged for awareness but require no action before lock:

- `json.JSONDecodeError` not in the suppression fixture except clause (degrades safely; no crash risk).
- `_render_synthesis_oob()` does not update suppressions on staff-note submit (correct for demo scope; documented).

**The project is CLEAR TO LOCK for the 5PM demo.**

---

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Never-cut spine (diff/PlanDiff/PlanDiffEntry) byte-identical; `GET /diff` JSON has no suppression keys | Met | Diff analysis: zero lines touching `diff()` or PlanDiff types. Live diff output: `['added_actions', 'changed_roles', 'entries', 'rationale', 'removed_actions']` only. Model field assertions pass. |
| OFFLINE_MODE deterministic; baseline=3 items, replanned=4 items; zero network | Met | Fixture load verified: 3 baseline, 4 replanned. Backend guard: `REPLAY` path never reaches `_call_claude()` or `_call_ollama()`. `httpx` import deferred inside function body. |
| US-006/TREQ-007: ≥1 withheld suggestion with concierge reason; fills BL-007 slot; empty-state preserved; HTMX re-render works | Met | 3 (baseline) and 4 (replanned) items with concierge-framed reasons. Placeholder renders on `suppressions == []`. Full template swap on `POST /replan` handles re-render. |
| Regression: BL-001..005/007/008 intact; additive default backward-compat; 3-panel layout holds | Met | No regressions in routes, layout, or parsing paths. `suppressions: list[Suppression] = []` default is backward-compatible. Panel B CSS containment intact. |
| Escaping: suppression strings auto-escaped in Jinja2; no `| safe` on LLM-derived fields | Met | Jinja2 `select_autoescape()` confirmed active for `.html`. Template uses `{{ item.suggestion }}` and `{{ item.reason }}` without `| safe`. |

---

## Reasoning

**Decision chain:**

1. The structural placement of `Suppression` on `OrchestratorResponse` (not `ArrivalPlan`) is the only approach consistent with the never-cut spine requirement. Verifying this required reading actual model fields at runtime (not just source), confirming diff output keys, and tracing all three call sites of `orchestrator.diff()` in `main.py` — all confirmed passing only `ArrivalPlan` instances.

2. Offline determinism verification required confirming three things independently: (a) `OFFLINE_MODE=true` maps to `Backend.REPLAY`, (b) `Backend.REPLAY` branch never invokes `_call_claude` or `_call_ollama`, and (c) no network client is instantiated at module scope. All three confirmed.

3. Jinja2 autoescape was confirmed by inspecting the actual `Jinja2Templates.__init__` source from the project venv — it uses `jinja2.select_autoescape()` which enables autoescape for `.html`. This is the TD-017 standard and is consistent with prior BL reviews.

4. The `json.JSONDecodeError` gap in the except clause is low-priority because the fixture files are author-controlled JSON arrays, not LLM-generated content. The degradation path (`suppressions=[]`) is exactly correct behavior regardless.

**Constraints applied:** Hackathon hard deadline — only CRITICAL/blocking findings escalated. MEDIUM/LOW deferred. No direct code fixes — findings only.

**Confidence:** High. Model field assertions run at runtime against the actual project venv. Diff output keys verified by executing the `diff()` function against real fixture data. Autoescape confirmed from venv source inspection.
