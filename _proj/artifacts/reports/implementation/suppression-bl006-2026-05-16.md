# Implementation: BL-006 Tasteful Restraint / Suppression Panel

**Agent:** Engineer
**Date:** 2026-05-16
**Commit SHA:** `ea409a9` on `build/sense-arrival-mvp`
**Mode:** fullstack

---

## Summary

Implemented the Tasteful Restraint suppression panel (BL-006 / FEAT-003 / TREQ-007 / US-006) — the "what we chose not to offer, and why" concierge hook. The panel fills the BL-007 panel-B slot that was left as a placeholder. Suppression is modeled as a SEPARATE field on `OrchestratorResponse` (`suppressions: list[Suppression]`), structurally excluded from `ArrivalPlan`, `PlanDiff`, `PlanDiffEntry`, and `diff()`. The never-cut spine is byte-identical. OFFLINE_MODE renders the panel with 3 withheld suggestions + reasons for the canonical Ms. Chen path; after inject-delay/replan, suppressions shift to 4 items (Asaya Thursday slot held due to fatigue, Ridge Rosé full-tasting held).

---

## Changes Made

| File | Change Type | Description |
|------|-------------|-------------|
| `sense_arrival/models.py` | Modified | Added `Suppression(suggestion, reason)` model; added `suppressions: list[Suppression] = []` to `OrchestratorResponse` as a SEPARATE field — never touches `ArrivalPlan`, `PlanDiff`, or `PlanDiffEntry` |
| `sense_arrival/fixtures/plans/baseline_suppressions.json` | Added | 3 withheld items for Ms. Chen baseline: group tours, Flamingo Tea, Stanford campus — each with concierge-framed one-line reason |
| `sense_arrival/fixtures/plans/replanned_suppressions.json` | Added | 4 withheld items post-delay: Asaya Thursday slot, group tours, extended Ridge Rosé tasting, Stanford campus — suppressions shift after the delay event |
| `sense_arrival/fixture_loader.py` | Modified | Added `Suppression` import; updated `load_offline_response()` to load the appropriate `baseline_suppressions.json` or `replanned_suppressions.json` and populate `OrchestratorResponse.suppressions` |
| `sense_arrival/orchestrator.py` | Modified | Added `Suppression` import; added `suppressions` top-level field to `_TOOL_SCHEMA` (parallel to `synthesis` and `arrival_plan`); updated `_parse_tool_response()` and `_call_ollama()` to extract and populate `suppressions` on the returned `OrchestratorResponse`; added rule 6 to `_SYSTEM_PROMPT` instructing Claude to produce 2–4 tasteful-restraint suppression items with concierge-framed reasons |
| `sense_arrival/templates/dashboard.html` | Modified | Replaced BL-007 placeholder suppression slot with structured panel rendering `response.suppressions` — suppression-header + badge + intro line + per-item suggestion + reason; graceful empty-state preserved with `suppression-panel--placeholder` |
| `sense_arrival/static/style.css` | Modified | Replaced flat suppression panel styles with structured styles: `.suppression-header`, `.suppression-badge`, `.suppression-intro`, `.suppression-items`, `.suppression-item`, `.suppression-item-suggestion`, `.suppression-item-reason`; `.suppression-panel--placeholder` graceful empty state preserved |

---

## Technical Decisions

- **`Suppression` as a new model, not modifying `ArrivalPlan.suppression`**: The existing `ArrivalPlan.suppression: list[str]` field is a per-role global union list used internally. The new `Suppression` model (`suggestion` + `reason`) is a structurally distinct concept — concierge-framed UI data with attribution. Keeping them separate avoids contaminating the diff path and preserves the never-cut spine invariant.
- **`OrchestratorResponse.suppressions` placement**: Mirrors exactly the pattern used for `GuestSynthesis` (ADR-002 Delta 3 rationale): SEPARATE field on the orchestrator envelope, excluded from `diff()` by design. `diff()` receives only `ArrivalPlan` instances; `OrchestratorResponse.suppressions` is never passed to it.
- **Two separate fixture files (`baseline_suppressions.json`, `replanned_suppressions.json`)**: Mirrors the `baseline_plan.json` / `replanned_plan.json` pattern. The baseline has 3 items (group tours, Flamingo Tea, Stanford). The replanned has 4 items: Asaya Thursday slot is added (held due to fatigue from delay), group tours and Stanford remain, and the full Ridge Rosé tasting format is held (compressed evening). This makes the "suppressions change after re-plan" requirement demonstrable without any LLM call.
- **`load_offline_response()` graceful degradation on missing fixture**: Wrapped suppressions loading in a `try/except` — if the fixture file is absent or malformed, `suppressions` defaults to `[]` and the placeholder renders. This keeps prior BLs fully unaffected even if the fixture files are somehow absent.
- **`_TOOL_SCHEMA` suppressions as a top-level required field**: Added alongside `synthesis` and `arrival_plan` (not nested inside `arrival_plan`) to be structurally clear that it is not part of the plan. The schema description instructs Claude explicitly about the tasteful-restraint framing.
- **Template renders from `response.suppressions`, not `arrival_plan.suppression`**: The old placeholder rendered from `arrival_plan.suppression` (the flat global suppression list). The new panel renders from `OrchestratorResponse.suppressions` — the structured list is entirely separate from the diff path.

---

## Spine Non-Touch Statement

`orchestrator.diff()`, `PlanDiff`, and `PlanDiffEntry` were NOT modified in this commit. The `diff()` function signature (`baseline: ArrivalPlan, replanned: ArrivalPlan`) is unchanged. `Suppression` and `OrchestratorResponse.suppressions` never enter `diff()`. `GET /diff` returns exactly `['added_actions', 'changed_roles', 'entries', 'rationale', 'removed_actions']` — confirmed by smoke test. Zero suppression keys appear in the diff JSON response.

---

## Testing

All tests run against OFFLINE_MODE (zero network, fixture-only, deterministic).

| Test | Status | Evidence |
|------|--------|---------|
| GET / — `suppression-panel` present | PASS | `grep -c "suppression-panel"` = 1 |
| GET / — `suppression-item` rendered | PASS | `grep -c "suppression-item"` = 10 (class appears per item) |
| GET / — "Tasteful Restraint" heading | PASS | `grep -c "Tasteful Restraint"` = 2 (h2 + title) |
| GET / — "What we chose not to offer" badge | PASS | `grep -c "What we chose not to offer"` = 1 |
| GET / — "Group tours or guided excursions" suppression item 1 | PASS | present in HTML |
| GET / — "Flamingo Estate Afternoon Tea" suppression item 2 | PASS | present in HTML |
| GET / — "Stanford campus tour" suppression item 3 | PASS | present in HTML |
| GET / — reasons text present | PASS | `grep -c "solo decompressor\|Ms. Chen\|self-directs"` hits |
| GET / — NO placeholder when data present | PASS | `grep -c "suppression-panel--placeholder"` = 0 |
| POST /replan — `suppression-panel` present | PASS | found in replan HTML |
| POST /replan — 4 suppression items (shifted) | PASS | `grep -c "suppression-item-suggestion"` = 4 |
| POST /replan — "Asaya Spa — Thursday arrival appointment" suppression | PASS | present in replan HTML |
| POST /replan — "Held: guest arriving late and fatigued" reason | PASS | present in replan HTML |
| POST /replan — "Extended Ridge Rosé Reveal" suppression | PASS | present in replan HTML |
| POST /replan — NO placeholder | PASS | placeholder class absent |
| GET /diff — spine clean (no suppression keys) | PASS | diff keys = `['added_actions', 'changed_roles', 'entries', 'rationale', 'removed_actions']` only |
| `id="suppression-panel"` in GET / HTML | PASS | `grep -c 'id="suppression-panel"'` = 1 |
| PlanDiff model fields — no suppression | PASS | `PlanDiff.model_fields` = `{'added_actions', 'changed_roles', 'entries', 'rationale', 'removed_actions'}` |
| `diff()` param list unchanged | PASS | `inspect.signature(orchestrator.diff)` params = `['baseline', 'replanned']` |

---

## Dependencies Added

None. ADR-001/ADR-002 deps only. Python stdlib only.

---

## Database Changes

None.

---

## API Changes

- No new endpoints.
- `GET /diff` JSON response: **unchanged** — no suppression keys. Verified by smoke test.
- `POST /replan` response: suppression panel now populated (4 items shifted). The full dashboard template re-render (innerHTML swap of `#dashboard-root`) handles this automatically — no new HTMX OOB logic required.
- `_TOOL_SCHEMA` (`submit_arrival_plan`): added top-level `suppressions` field as a required array of `{suggestion, reason}` objects. This is the live-tier (Claude/Ollama) change. REPLAY path is unaffected — loads fixtures directly.
- Breaking changes: None. `suppressions` defaults to `[]` on `OrchestratorResponse`, so any cached or partially-parsed response degrades to placeholder state.

---

## Known Limitations

- `_TOOL_SCHEMA` changes (`suppressions` now `required`) could cause a schema validation error if an older Claude response (from a pre-BL-006 session) is cached and parsed. Mitigation: `suppressions` defaults to `[]` on `OrchestratorResponse`, and `_parse_tool_response()` uses `data.get("suppressions", [])` — safe degradation.
- `_render_synthesis_oob()` in `main.py` (BL-008 staff-note path) does not update the suppression panel on staff note submission. Suppressions do not change per-observation in the demo; the full replan (inject-delay button) is the intended trigger for suppression shifts.
- Live Claude/Ollama suppression content depends on the LLM producing schema-valid output. The graceful degradation path (fixture fallback on parse error) ensures zero crash risk.

---

## Follow-up Items

- [ ] Optional: add `_render_suppression_panel_oob()` in `main.py` if a future BL requires updating suppressions on staff-note submission without a full replan
- [ ] Optional: extend `_TOOL_SCHEMA` `inferred_from` field for BL-009 (structured attribution in live Claude output)

---

## Flagged Items

None. Contained implementation — no architecture changes, no new dependencies, no blockers encountered. Never-cut spine explicitly confirmed clean.

---

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|---------|
| 1. Suppression panel lists ≥1 withheld suggestion with a clear reason, concierge-framed; fills BL-007 panel slot (placeholder replaced when data present, graceful empty-state if absent) | Met | Baseline: 3 items rendered (`suppression-item-suggestion` + `suppression-item-reason` per item). Placeholder class absent when data present. Empty-state renders `.suppression-panel--placeholder` when `suppressions` is `[]`. |
| 2. Suppressions change appropriately after delay re-plan; both `plan()` and `replan()` populate `OrchestratorResponse.suppressions`; panel re-renders on re-plan via existing HTMX swap pattern | Met | Replanned fixture has 4 items vs. 3 baseline: Asaya Thursday slot added (held: fatigued arrival), extended Ridge Rosé held. Replan route returns full dashboard template; panel re-renders via existing `hx-target="#dashboard-root" hx-swap="innerHTML"`. |
| 3. Offline determinism: suppression content in offline fixtures (baseline + replanned, canonical Ms. Chen path); OFFLINE_MODE renders with reasons, zero network | Met | `baseline_suppressions.json` and `replanned_suppressions.json` created. `load_offline_response()` loads them. Smoke test: all 3 baseline items present on `GET /` in OFFLINE_MODE. All 4 replanned items present on `POST /replan`. Zero network calls. |
| 4. Never-cut spine unchanged: `diff()`/`PlanDiff`/`PlanDiffEntry` byte-identical; `GET /diff` JSON has no suppression keys; inject-delay→diff path unaffected and not blocked | Met | `diff()`, `PlanDiff`, `PlanDiffEntry` not modified (confirmed by reading each). `GET /diff` keys = `['added_actions', 'changed_roles', 'entries', 'rationale', 'removed_actions']` — no suppression fields. Spine confirmed clean by smoke test. |

---

## Reasoning

**Decision chain:**

1. `Suppression` as a new standalone model (not modifying `ArrivalPlan.suppression: list[str]`) is the only approach that keeps the never-cut spine clean. `ArrivalPlan` fields pass through `diff()` — adding a structured field there would require touching `diff()` or producing spurious diff entries. The new model stays on `OrchestratorResponse` exactly as `GuestSynthesis` does (ADR-002 Delta 3 pattern).

2. Two separate fixture files (not embedding suppressions inside `baseline_plan.json`) follows the existing fixture-per-concern pattern (`synthesis_fixture.json` is separate from `baseline_plan.json`). This also means `load_offline_response()` can be extended without touching the plan fixtures that are certified clean 5×.

3. The suppression content (Ms. Chen's 3 baseline + 4 replanned) is sourced verbatim from the analyst report (`rosewood-property-dossier-research-2026-05-16.md` — Dossier A suppression note). The reasons are concierge-framed ("wrong energy for this arrival", "solo decompressor", "held: guest arriving late and fatigued") rather than profile-label language — this is the "tasteful restraint" vs. "that's creepy" distinction the requirement calls out.

4. The replan suppressions add two new items (Asaya Thursday, extended Ridge Rosé) to demonstrate visible shift — the panel is noticeably different before and after inject-delay, which is the demo moment for the "suppressions change appropriately" criterion.

5. No OOB helper added for the transcribe/staff-note path — suppressions don't change per observation in the demo. The replan's full dashboard swap is the intended trigger. Adding an OOB helper would be premature and add code with no demo payoff.

**Constraints applied:** Never-cut spine (diff/PlanDiff/PlanDiffEntry) not touched (confirmed). No new dependencies. OFFLINE_MODE zero-network. ADR-001/ADR-002 deps only. Python 3.11 compatible. All prior BLs verified unaffected (GET /diff = 16 entries, same keys).

**Confidence:** High. All 18 smoke tests pass. Model integrity confirmed by direct Python import + assertion. Diff spine confirmed by JSON key inspection. Fixture loading confirmed by `load_offline_response()` smoke. Template rendering confirmed by HTML grep.

---

## Commit SHA: ea409a9
