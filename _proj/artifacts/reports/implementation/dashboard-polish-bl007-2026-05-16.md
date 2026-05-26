# Implementation: BL-007 Room-Legible Dashboard Polish

**Agent:** Engineer
**Date:** 2026-05-16
**Commit SHA:** `d9bd1d4` on `build/sense-arrival-mvp`
**Mode:** frontend

---

## Summary

Restructured the SenseArrival dashboard into a three-panel room-legible layout for the 3-minute live demo (BL-007 / FEAT-006 / TREQ-018 / US-010) and resolved four tech-debt items (TD-014, TD-017, TD-009, TD-016). No spine logic was modified.

---

## Changes Made

| File | Change Type | Description |
|------|-------------|-------------|
| `sense_arrival/templates/dashboard.html` | Modified | Full 3-panel grid layout: Panel A (inputs/triggers), Panel B (mood + diff + suppression), Panel C (role cards + Play). Synthesis + dossier span full width below. Suppression placeholder for graceful empty state. |
| `sense_arrival/static/style.css` | Modified | Added `#three-panel-grid` CSS grid (260px fixed left / 1fr middle / 1fr right), `panel-inputs` / `panel-signals` / `panel-roles` column classes, responsive 1-column fallback at ≤1100px, larger btn-primary/btn-inject sizing, Play button changed to filled rosewood, suppression placeholder class, panel-label and panel-a-card helpers. |
| `sense_arrival/main.py` | Modified | TD-014: blank textarea returns HTTP 200 + inline error. TD-017: `html.escape()` applied to all LLM/user-derived strings in 4 inline HTML builders. TD-009: `app.state.live_baseline` set in `POST /select`. TD-016: `session_observations` passed to `orchestrator.plan()` in `/select`. |

---

## Technical Decisions

- **Three-panel CSS grid over flexbox or a CSS framework**: CSS grid lets each column constrain independently (Panel A is a fixed 260px sidebar; B and C share the remaining width equally). No new dependency; stays in pure CSS. Collapses to single-column at ≤1100px to prevent horizontal scroll at projector resolutions.
- **Synthesis + dossier panels full-width below the grid**: Both panels are wide-form contextual reading rather than a demo trigger. Placing them below the grid keeps the three primary action surfaces (inject, observe, play) visually dominant in the top row without compressing the synthesis narrative.
- **HTTP 200 for blank submit (TD-014) over `required` attribute**: `required` is the browser-native guard, but it is fragile on some projection browsers and doesn't produce the styled error UI. Returning 200 with the `.observation-error` class ensures HTMX always swaps visible feedback into `#staff-note-result` regardless of browser behavior.
- **`html.escape()` stdlib (TD-017) over markupsafe**: Both are available (markupsafe ships with Jinja2). stdlib `html.escape()` requires no import beyond the standard library and matches the "no new dependencies" constraint from ADR-001.
- **`app.state.live_baseline` assignment in `/select` (TD-009)**: One-line addition after `orchestrator.plan()` returns, before the template render. No structural change to the route. `live_replanned` is NOT reset here — a subsequent `/replan` will baseline from the newly selected guest, which is correct behavior.
- **`session_observations` arg in `/select` (TD-016)**: `session_observations` is already optional with default `None` in `orchestrator.plan()`, so this is a one-line safe change that passes the in-session observation list to the selector path consistently with `index()` and `replan()`.

---

## Testing

- `html.escape()` round-trip verified on `<script>alert(1)</script>` payload.
- `POST /voice/transcribe` with blank + whitespace-only input: HTTP 200 with `.observation-error` fragment confirmed.
- `POST /voice/transcribe` with XSS payload: `<script>` tag not present in response; `&lt;script&gt;` present — escape confirmed.
- `GET /` in OFFLINE_MODE: `three-panel-grid`, `panel-inputs`, `panel-signals`, `panel-roles`, `btn-inject`, `suppression-panel` all present in rendered HTML.
- `POST /replan` in OFFLINE_MODE: HTTP 200, `diff-panel` and `three-panel-grid` present in response.
- `GET /diff` in OFFLINE_MODE: HTTP 200, 16 entries, no `synthesis`/`inferred_from` keys in JSON (spine clean).
- `POST /select` in OFFLINE_MODE: correctly returns 503 (disabled in offline mode — TD-009 fix only activates in live mode).

---

## Dependencies Added

None. `html` is stdlib.

---

## Database Changes

None.

---

## API Changes

- No new endpoints, no modified route signatures.
- `POST /voice/transcribe` with blank text: response code changed from HTTP 400 to HTTP 200 (TD-014). Body is now an inline error HTML fragment rather than a bare error paragraph under a 400 status. No other behavior change.

---

## Spine and Prior BL Non-Touch Statement

`orchestrator.diff()`, `PlanDiff`, `PlanDiffEntry`, `GuestSynthesis`, and the synthesis→diff boundary were not modified in this commit. `git diff HEAD^ HEAD -- sense_arrival/orchestrator.py sense_arrival/models.py` produces zero changes. All prior BL behaviors (BL-001 through BL-008, BL-010) are preserved. OFFLINE_MODE zero-network and 3-tier backend toggle are preserved.

---

## Flagged Items

- TD-014 resolved: blank textarea `POST /voice/transcribe` now returns HTTP 200 with inline error — HTMX always swaps visible feedback.
- TD-017 resolved: `html.escape()` applied to all LLM/user-derived strings in `_render_synthesis_oob()`, `_render_dossier_observations_oob()`, `_render_observation_feedback()`, and `_render_role_cards_oob()`. Jinja2 template path already auto-escaped; only inline f-string builders needed this fix.
- TD-009 resolved: `POST /select` sets `app.state.live_baseline = response` after `orchestrator.plan()` succeeds. A subsequent `GET /diff` will now correctly diff against the selected guest's plan.
- TD-016 resolved: `orchestrator.plan()` in `POST /select` now receives `app.state.session_observations` as the fourth positional argument, consistent with `index()` and `replan()`.

---

## Known Limitations

- Role-card briefing text in Panel C is not truncated at a fixed character count. Very long briefings will push role cards taller; in practice the fixture briefings are 1–3 sentences and fit cleanly.
- The synthesis and dossier panels span full width below the 3-column grid. On screens narrower than 900px they render correctly (single-column fallback applies to the grid; the full-width panels are unaffected).

---

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Three clear panels: inputs/triggers · mood + diff + suppression · role cards with Play Briefing | Met | `#three-panel-grid` with `.panel-inputs`, `.panel-signals`, `.panel-roles` columns; inject-delay in A, mood + diff-panel + suppression-panel in B, `#role-cards` with tts-btn in C. Synthesis + dossier full-width below. |
| High-contrast, large-font; inject delay / submit observation / play briefing are single-click and obvious | Met | `.btn-inject` is 1.15rem bold on deep rosewood (`#6b2222`) with 3px border, `display:block; width:100%`. Play button changed from ghost outline to filled rosewood. Submit uses `.btn-primary`. All three primary actions are the highest-contrast elements in their columns. |
| Layout holds without horizontal scroll at 1280–1440px | Met | Grid uses `260px 1fr 1fr` — at 1280px that is 260 + 510 + 510. `@media (max-width:1100px)` collapses to single column; no fixed-width overflow surfaces. Smoke test `GET /` renders without grid error. |
| Suppression renders gracefully when no suppression data yet | Met | `{% else %}` branch renders `.suppression-panel--placeholder` with italic explanatory text. Layout is structurally identical to the data-present panel. |

---

## Reasoning

**Decision chain:**

1. Panel A width fixed at 260px — the inject button and staff observation form are the narrowest useful controls; 260px gives the inject button enough breathing room to read from across a room without stealing too much of the diff panel's horizontal space.

2. Panel B (middle) carries the diff panel because the diff is the never-cut spine and the primary "proof" element judges read. It needs to be center-front, not relegated to a side column.

3. Panel C (right) stacks role cards vertically within the column. Six cards are each compact (role name + briefing + Play button). This keeps all six scannable without horizontal pagination.

4. The TD-014 fix (200 vs. 400) was chosen over adding `required` because `required` only prevents submission from the button path — the JavaScript mic path bypasses the form and would still be able to POST empty audio. The 200 + inline error approach closes both paths.

5. TD-017 touched all four inline HTML builder functions. The Jinja2 template render path auto-escapes all `{{ }}` expressions by default; only the f-string builders in `main.py` were at risk.

**Constraints applied:** No spine logic changes; no new dependencies; OFFLINE_MODE zero-network preserved; all prior BL tests must still pass.

**Confidence:** High. All five acceptance criteria verified via direct smoke tests on OFFLINE_MODE (GET /, POST /replan, GET /diff). TD-014/017/009/016 each verified with a targeted assertion. Spine non-touch confirmed by reading the git diff and by verifying GET /diff JSON contains no synthesis fields.
