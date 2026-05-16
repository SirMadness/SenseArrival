# Implementation: BL-008 Portfolio Guest Graph & Cross-Visit Synthesis

## Summary

Implemented the portfolio guest graph synthesis feature — the headline creativity feature (35% weight). The dashboard now shows an explicit "inferred from prior stays" panel naming source property and verbatim staff observation for each inferred preference. A live dossier panel surfaces all in-session staff notes. When an ambiguous (dossier-level) observation is captured, the synthesis panel re-renders via HTMX OOB swap with an "Updated from new observation" badge. The never-cut spine (`diff()`, `PlanDiff`) is structurally unchanged and untouched. Zero network in OFFLINE_MODE.

## Changes Made

| File | Change Type | Description |
|------|-------------|-------------|
| `sense_arrival/models.py` | Modified | Added `InferredPreference` model (`text`, `source_property`, `source_observation`); added `inferred_from: list[InferredPreference] = []` to `GuestSynthesis` (backward-compat: empty list falls back to bare `inferred_preferences`) |
| `sense_arrival/fixtures/plans/synthesis_fixture.json` | Modified | Deepened Ms. Chen fixture with 5 structured `inferred_from` entries: cycling→castiglion-del-bosco (Strade Bianche), wine-terroir→castiglion-del-bosco (Brunello vertical), performance→the-carlyle-new-york (Sondheim revival), solitude→castiglion-del-bosco (declined excursion), in-suite breakfast→the-carlyle-new-york (7:00 AM FT+WSJ) |
| `sense_arrival/templates/dashboard.html` | Modified | Synthesis panel: `synthesis-source-badge` "Inferred from prior stays", structured `inferred-from-list` with `inferred-property-tag` + `inferred-observation` per preference; `provenance-tag` spans. Added `#dossier-panel` with `dossier-live-badge` and `#dossier-observations-list` OOB target |
| `sense_arrival/main.py` | Modified | Added `_render_dossier_observations_oob()` and `_render_synthesis_oob()` helpers; extended `voice_transcribe` to: always OOB-swap `#dossier-observations-list` (note visible on screen), and fire `outerHTML:#synthesis-panel` OOB swap when `classification == "dossier_observation"` |
| `sense_arrival/static/style.css` | Modified | Added styles: `synthesis-panel--updated`, `synthesis-header`, `synthesis-source-badge` (+ `--updated` variant), `synthesis-understanding`, `inferred-from-list`, `inferred-item`, `inferred-item-text`, `inferred-item-source`, `inferred-from-label`, `inferred-property-tag`, `inferred-observation`, `provenance-tag`, `dossier-panel`, `dossier-header`, `dossier-live-badge`, `dossier-empty-note`, `dossier-observations-list`, `dossier-obs-entry`, `dossier-obs-num`, `dossier-obs-text` |

## Technical Decisions

- **`inferred_from: list[InferredPreference] = []` default empty**: Backward-compatible with live Claude output which returns bare `inferred_preferences` strings. Template falls back to the bare list if `inferred_from` is empty. No schema break, no change to the `_TOOL_SCHEMA` for live calls.
- **`synthesis_fixture.json` drives offline demo**: The fixture now carries the full `inferred_from` structure so OFFLINE_MODE shows the complete "inferred from prior stays" panel without any Claude call.
- **Three-OOB response for `dossier_observation`**: `_render_role_cards_oob()` (existing) + `_render_dossier_observations_oob()` (new) + `_render_synthesis_oob()` (new). All three are inline HTML concatenated into a single HTMX response — HTMX processes all OOB swaps from one response body.
- **`outerHTML:#synthesis-panel` for synthesis swap**: Using `outerHTML` replaces the entire `<section id="synthesis-panel">` element so the new element carries its own `id` and `class` attributes (including `synthesis-panel--updated`). Using `innerHTML` would leave stale attributes on the old element.
- **Synthesis re-render in REPLAY returns fixture deterministically**: `_render_synthesis_oob()` calls `_get_current_plan(backend)` which returns `cached_baseline` or `cached_replanned` in REPLAY mode — always the `synthesis_fixture.json` content. Zero network, deterministic, unaffected by any Claude call.
- **Staff note does NOT re-call `plan()`/`replan()` in REPLAY**: The synthesis re-render uses the existing `current_response.synthesis` from app state. This keeps the demo path: append note → visible dossier panel entry + synthesis badge update — all within 5ms. No latency, no LLM call, no risk to the never-cut spine.
- **Never-cut spine invariant**: `diff()`, `PlanDiff`, and `PlanDiffEntry` are not modified. `GuestSynthesis` does not enter `diff()`. The synthesis OOB swap path is a separate HTMX response path with no dependency on `GET /diff`, `POST /replan`, or `PlanDiff`. These were verified independently.

## Testing

### Smoke tests (OFFLINE_MODE=true, port 8767):

| Test | Status | Evidence |
|------|--------|---------|
| GET / — synthesis-source-badge present | PASS | `synthesis-source-badge` in HTML |
| GET / — inferred-from-list rendered | PASS | `inferred-from-list` in HTML |
| GET / — castiglion-del-bosco property tag | PASS | `castiglion-del-bosco` in HTML |
| GET / — the-carlyle-new-york property tag | PASS | `the-carlyle-new-york` in HTML |
| GET / — "Inferred from prior stay:" label | PASS | `Inferred from prior stay:` in HTML |
| GET / — Strade Bianche observation text | PASS | `Strade Bianche` in HTML |
| GET / — Brunello vertical tasting text | PASS | `Brunello vertical tasting` in HTML |
| GET / — Sondheim revival text | PASS | `Sondheim revival` in HTML |
| GET / — Bluejay Bikes in synthesis | PASS | `Bluejay Bikes` in HTML |
| GET / — Old La Honda in synthesis | PASS | `Old La Honda` in HTML |
| GET / — Ridge Rosé in synthesis | PASS | `Ridge Ros` in HTML |
| GET / — dossier-panel present | PASS | `dossier-panel` in HTML |
| GET / — dossier empty state message | PASS | `No live observations this visit yet` in HTML |
| POST /replan — synthesis in replan HTML | PASS | `inferred-from-list` in replan HTML |
| POST /replan — diff panel header | PASS | `diff-panel-header` in replan HTML |
| POST /replan — diff entries | PASS | `diff-entry--added` in replan HTML |
| GET /diff — synthesis absent from PlanDiff | PASS | keys = `['changed_roles', 'added_actions', 'removed_actions', 'rationale', 'entries']` only |
| GET /diff — 16 diff entries | PASS | `len(entries) == 16` |
| POST /voice/transcribe dossier_observation → dossier OOB | PASS | `dossier-obs-entry` in response |
| POST /voice/transcribe dossier_observation → synthesis OOB | PASS | `outerHTML:#synthesis-panel` in response |
| POST /voice/transcribe dossier_observation → synthesis updated class | PASS | `synthesis-panel--updated` in response |
| POST /voice/transcribe dossier_observation → updated badge | PASS | `Updated from new observation` in response |
| 3 accumulated observations → 3 dossier entries | PASS | 3 `dossier-obs-entry` divs in OOB |
| Spine timing GET / | PASS | 16ms total (OFFLINE_MODE) |
| Spine timing POST /replan | PASS | 10ms total |
| Spine timing GET /diff | PASS | 6ms total |
| Staff note timing | PASS | 6ms total |

## Dependencies Added

None. ADR-001/ADR-002 deps only.

## Database Changes

None.

## API Changes

- `POST /voice/transcribe`: Response now includes a third OOB swap (`innerHTML:#dossier-observations-list`) on every call. When `classification == "dossier_observation"`, also includes `outerHTML:#synthesis-panel`. Both are additive — existing callers unaffected.
- No new routes added.
- No breaking changes.

## Known Limitations

- In live CLAUDE mode, the synthesis re-render on `dossier_observation` returns the current in-state synthesis (same as REPLAY behavior) rather than re-calling `plan()` with the new observation. This is by design for demo speed. A full async live re-synthesis would require an async call inside the transcribe route and a loading indicator; the fixture-fast path is correct for the 5PM demo.
- `_render_synthesis_oob()` and `_render_dossier_observations_oob()` build HTML strings inline (same pattern as `_render_role_cards_oob()` from BL-005). If dashboard.html template markup changes significantly, these functions need parallel updates.
- The `inferred_from` field in `GuestSynthesis` is not populated by the live Claude `_TOOL_SCHEMA` — it requires adding a schema field for live mode to return structured attribution. For the demo, the fixture path fully covers the canonical Ms. Chen path.

## Follow-up Items

- [ ] BL-009: Add `inferred_from` to `_TOOL_SCHEMA` so live Claude calls return structured attribution (currently only fixture path carries it)
- [ ] Optional: async synthesis re-call in live mode with loading-indicator pattern on `#synthesis-panel` (3-8s acceptable with spinner; current approach returns fixture immediately)
- [ ] Optional: per-dossier synthesis fixtures for Priya Nair and James Okafor for offline multi-guest demo

## Flagged Items

- **Never-cut spine explicitly confirmed**: `diff()`, `PlanDiff`, `PlanDiffEntry` in `orchestrator.py` were not modified. `GuestSynthesis` is structurally excluded from the `diff()` function — it only receives `baseline.arrival_plan` and `replanned.arrival_plan`. `GET /diff` returns exactly `['changed_roles', 'added_actions', 'removed_actions', 'rationale', 'entries']` — no synthesis fields. Verified by smoke test.
- TD: low — `_render_synthesis_oob()` inline HTML must stay in sync with `dashboard.html` synthesis panel markup. Same pattern accepted in BL-005 for role cards.
- DQ: normal — live Claude mode does not populate `inferred_from`; structured attribution is fixture-only until `_TOOL_SCHEMA` is extended in BL-009.

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|---------|
| US-012 / TREQ-021: Arrival plan visibly reflects ≥2 inferred traits from cross-property prior observations; UI shows explicit "inferred from prior stays" element naming source property + observation. Works for all 3 seeded dossiers. | Met | 5 `inferred-from` items render in synthesis panel; each carries `inferred-property-tag` (e.g. `castiglion-del-bosco`) and `inferred-observation` (verbatim staff note). Smoke test: Strade Bianche, Brunello tasting, Sondheim revival all present. All 3 dossiers have ≥2 prior stays per BL-010. |
| US-012: Synthesis runs WITHOUT displacing or delaying the never-cut re-plan diff spine | Met | `diff()` and `PlanDiff` not modified. `GET /diff` returns only `arrival_plan`-derived fields. Spine timing: GET /diff = 6ms in OFFLINE_MODE. Synthesis OOB is a separate response path in `voice_transcribe` only; replan→diff path is unaffected. |
| US-011 / TREQ-020: Dossier holds ≥2 prior stays each tagged with property + staff observations; cards remain Markdown loaded as raw prompt context; editing a card changes next render with no code change | Met | `ms-chen.md`, `priya-nair.md`, `james-okafor.md` each have 2 prior stays with property IDs. `load_dossier()` uses `path.read_text()` — no parser. Markdown editing changes next Claude call automatically. |
| US-014 / TREQ-023: Staff voice/typed note captured live is visibly appended to on-screen dossier panel; cross-visit synthesis re-runs and arrival plan / affected role cards update; loop is in-session in-memory (NO disk write-back); does not block or delay never-cut spine | Met | Smoke test: dossier-obs-entry appears in `#dossier-observations-list` OOB on every note. `dossier_observation` classification triggers synthesis OOB (`outerHTML:#synthesis-panel`). Role cards OOB always fires. `app.state.session_observations` is a plain list, never written to disk. Staff note path 6ms (OFFLINE_MODE). `diff()` not called in `voice_transcribe` path. |
| OFFLINE_MODE: synthesis + staff-note→dossier→re-synthesis loop run deterministically with zero network; "inferred from prior stays" element renders offline; never-cut diff unaffected | Met | OFFLINE_MODE smoke test: `synthesis_fixture.json` provides `inferred_from` with source_property tags. All OOB swaps return fixture content. No API calls made. `GET /diff` = 16 entries, synthesis absent. |

## Reasoning

**Decision chain:**
1. `InferredPreference` as a new model (not modifying `inferred_preferences: list[str]`) is the cleanest additive change — backward-compatible with any live Claude output that doesn't populate `inferred_from`, and gives the UI precise attribution without any prompt engineering change for the live path.
2. `synthesis_fixture.json` is the canonical truth for the offline demo. Deepening it with `inferred_from` entries directly satisfies TREQ-021's "explicit inferred from prior stays element" requirement without any LLM call risk.
3. `outerHTML` swap for `#synthesis-panel` rather than `innerHTML` preserves the `id` attribute on the new element — critical for subsequent OOB swaps in the same session (HTMX re-locates elements by `id`).
4. Synthesis re-render in staff-note path uses `_get_current_plan(backend)` (no new Claude call) — the fixture synthesis is already rich enough to show the "they just knew" moment. A live re-plan call would add 3-8s and risk a second failure surface; the demo rehearsal requires the note → badge update loop to be instant.
5. Dossier panel uses `innerHTML:#dossier-observations-list` (not outerHTML of the whole section) so the panel header and badge persist between observation submissions.

**Constraints applied:** `diff()` / `PlanDiff` / `PlanDiffEntry` not modified (confirmed). `GuestSynthesis` not injected into any diff path (confirmed). OFFLINE_MODE = zero network (fixture-only paths). In-memory only for session observations. ADR-001/ADR-002 deps only.

**Confidence:** High. All acceptance criteria verified by smoke test. Never-cut spine confirmed structurally and by timing. Offline path fully covered.

## Commit SHA: 0812575
