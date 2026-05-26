# Implementation: BL-001 Foundation Runtime — SenseArrival

## Summary

Built the complete application foundation for SenseArrival per ADR-001 and ADR-002. The skeleton is a single-process FastAPI application bootable via one `uvicorn` command, with the full Pydantic data model, Markdown fixture library (3 dossiers × 3 property cards), scope guard, 3-tier pluggable LLM backend, and all ADR-001/ADR-002 routes stubbed or implemented. BL-002 (orchestrator) bolts directly onto `orchestrator.plan()` / `orchestrator.replan()` / `orchestrator.diff()` stubs and the typed models — no refactor required.

## Changes Made

| File | Change Type | Description |
|------|-------------|-------------|
| `sense_arrival/__init__.py` | Added | Package marker |
| `sense_arrival/models.py` | Added | All 8 Pydantic models: GuestDossier, PriorStay, PropertyCard, GuestSynthesis, OrchestratorResponse (ADR-002) + ArrivalPlan, RoleCard, PlanDiff (ADR-001 unchanged) |
| `sense_arrival/config.py` | Added | Settings class + Backend enum (claude/ollama/replay) + 3-tier resolver (OFFLINE_MODE alias → BACKEND env → default) + ALLOWED_DOSSIERS/ALLOWED_PROPERTIES scope guard sets |
| `sense_arrival/fixture_loader.py` | Added | Raw-text loaders (load_dossier, load_property_card, load_provenance_cards) + typed builders (build_guest_dossier, build_property_card) + offline JSON loaders + selector helpers + scope guard enforcement |
| `sense_arrival/orchestrator.py` | Added | plan()/replan() stubs with REPLAY path wired (load_offline_response); diff() implemented (set-based role-card comparison); BL-002 slots Claude/Ollama paths without changing signatures |
| `sense_arrival/voice.py` | Added | tts()/stt() stubs; replay returns cached MP3 or minimal silent frame; live paths raise NotImplementedError for BL-002 |
| `sense_arrival/main.py` | Added | FastAPI app; all 8 routes (GET /, POST /replan, GET /diff, POST /voice/transcribe, GET /voice/tts/{card_id}, GET /offline, GET /select, POST /select); app.state.session_observations (TREQ-023 shim); startup caches replay responses |
| `sense_arrival/templates/dashboard.html` | Added | Jinja2 template: offline banner, mood banner, synthesis panel, role cards grid with TTS buttons, suppression panel, guest message, staff observation form (typed-text fallback), selector form |
| `sense_arrival/static/style.css` | Added | Minimal functional styles; rosewood palette |
| `sense_arrival/static/app.js` | Added | TTS playback, mic capture with permission guard, text-mode fallback banner |
| `sense_arrival/fixtures/dossiers/ms-chen.md` | Added | Demo-grade dossier (Dossier A content, Ms. Chen name per US-008); prior stays at the-carlyle-new-york + castiglion-del-bosco |
| `sense_arrival/fixtures/dossiers/priya-nair.md` | Added | Dossier B; prior stays at the-carlyle-new-york + castiglion-del-bosco |
| `sense_arrival/fixtures/dossiers/james-okafor.md` | Added | Dossier C; prior stays at castiglion-del-bosco + the-carlyle-new-york |
| `sense_arrival/fixtures/properties/rosewood-sand-hill.md` | Added | Arrival property (depth=arrival); 8 signature anchors; ~580 words Sense of Place |
| `sense_arrival/fixtures/properties/the-carlyle-new-york.md` | Added | Provenance property (depth=provenance); 4 anchors |
| `sense_arrival/fixtures/properties/castiglion-del-bosco.md` | Added | Provenance property (depth=provenance); 4 anchors |
| `sense_arrival/fixtures/plans/baseline_plan.json` | Added | Pre-computed ArrivalPlan: 6 role cards, ms-chen @ rosewood-sand-hill, no delay |
| `sense_arrival/fixtures/plans/replanned_plan.json` | Added | Pre-computed ArrivalPlan: 6 role cards, ms-chen @ rosewood-sand-hill, delay injected |
| `sense_arrival/fixtures/plans/synthesis_fixture.json` | Added | Pre-computed GuestSynthesis for ms-chen canonical path |
| `sense_arrival/fixtures/delay_event.json` | Added | Flight delay event payload (120 min, JFK ATC hold) |
| `requirements.txt` | Added | ADR-001 exact dependency list; no additions |
| `.env.example` | Added | Environment template with BACKEND/OFFLINE_MODE/API key placeholders |
| `.gitignore` | Modified | Added Python cache, venv, .env, generated audio |

## Technical Decisions

- **Starlette 1.0 compat wrapper**: `_tmpl(request, context)` helper wraps `templates.TemplateResponse(request, "dashboard.html", context)` to handle the API change in Starlette 1.0 (request moved to first positional arg). This is a contained fix, not an architectural deviation.
- **Prior stays regex**: Markdown `## Prior Stays` section uses `re.DOTALL | re.MULTILINE` with `^## ` boundary to handle blank lines between the section header and first `###` subsection. The initial single-line regex failed because the ADR-002 template uses a blank line after `## Prior Stays`.
- **Fixture names vs ADR-002 illustrative names**: ADR-002 used `mr-okafor.md` / `dr-reyes.md` as illustrative slugs; the reconciled fixture set (per delegation brief) uses `priya-nair.md` / `james-okafor.md` matching the analyst research content. The property slugs also differ (the-carlyle-new-york vs rosewood-london, castiglion-del-bosco vs rosewood-beijing). This is the binding constraint superseding ADR-002's illustrative names.
- **diff() implemented in BL-001**: The never-cut spine (TREQ-006) has a working set-based diff so `/diff` returns a real PlanDiff in replay mode immediately — BL-002 can enrich the `rationale` field with Claude-generated text without changing the structure.
- **`OrchestratorResponse | None` throughout routes**: When the live backend raises NotImplementedError (BL-002 not implemented), routes pass `response=None` to the template and render the placeholder section instead of returning 500.

## Testing

- Manual boot test: `OFFLINE_MODE=true uvicorn sense_arrival.main:app` → `GET /` = 200, `GET /offline` = 200, `GET /diff` = 200 + correct PlanDiff JSON, `POST /voice/transcribe` = 200 + transcript JSON
- Manual degraded test: `BACKEND=claude` (no key) → `GET /` = 200 (placeholder body), `GET /diff` = 202 (graceful)
- Unit: fixture loader — all 3 dossiers parsed (prior_stays: 2 each, obs: 3+3 for ms-chen), all 3 property cards parsed (correct depth, anchor counts), scope guard fires on unknown slug, provenance card filter excludes arrival property
- Unit: models — all 8 Pydantic models import cleanly, OrchestratorResponse round-trips from fixture JSON

## Dependencies Added

None. ADR-001 dependency list exactly.

## Database Changes

None. No database; fixture files only.

## API Changes

New (all routes new — no prior code):
- GET /
- POST /replan
- GET /diff
- POST /voice/transcribe
- GET /voice/tts/{card_id}
- GET /offline
- GET /select
- POST /select

Breaking changes: none (no prior code).

## Known Limitations

- `plan()` / `replan()` raise NotImplementedError for claude and ollama backends — BL-002 scope.
- TTS returns a silent MP3 stub in replay mode if `static/audio/briefing_cached.mp3` is absent — BL-002 should generate and cache this file.
- `POST /voice/transcribe` classification always returns `dossier_observation` — real classification logic is BL-002 scope.
- The selector (`POST /select`) is disabled in offline mode per ADR-002 Delta 5 (returns 503).
- `build_guest_dossier()` extracts `arrival_property_id` from a `**Arrival Property:**` field not in the ADR-002 template; it falls back to `rosewood-sand-hill` if absent. BL-002 should verify this field is present in all dossier fixtures if it uses it programmatically.

## Follow-up Items

- [ ] BL-002: implement `plan()` / `replan()` Claude tool-use loop and wire real `arrival_plan` + `synthesis` fields
- [ ] BL-002: generate and cache `static/audio/briefing_cached.mp3` for offline TTS replay
- [ ] BL-002: implement real transcript classification (spa/dining/accessibility/dossier_observation) in POST /voice/transcribe
- [ ] BL-003: freeze real baseline_plan.json / replanned_plan.json from live Claude run (current fixtures are hand-authored placeholders — acceptable for BL-001)
- [ ] BL-004: offline rehearsal documentation (not in BL-001 scope per delegation)

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 1. Env/UI toggle switches claude/ollama/replay with no code change; replay = zero outbound network | Met | `BACKEND=replay` or `OFFLINE_MODE=true` → all routes return fixture data; orchestrator/voice stubs only call `load_offline_response()` in replay path; no HTTP client calls in that path |
| 2. Scope guard: only 3-dossier/3-property library loadable; no live APIs anywhere | Met | `_guard_dossier()` / `_guard_property()` raise ValueError for any slug outside ALLOWED sets; no external API calls exist in the codebase (all live paths are NotImplementedError stubs) |
| 3. App boots with single uvicorn command; GET / returns HTTP 200 without error | Met | Verified: `OFFLINE_MODE=true uvicorn sense_arrival.main:app` → `GET /` = 200; also 200 with `BACKEND=claude` (no key) via graceful degradation |
| 4. Pydantic models exactly match ADR-002 sketches | Met | GuestDossier (guest_id, name, nationality, arrival_property_id, profile_summary, prior_stays), PriorStay (property_id, dates, staff_observations), PropertyCard (property_id, name, location, depth: Literal["arrival","provenance"], sense_of_place, signature_anchors), GuestSynthesis (unified_understanding, inferred_preferences, provenance_properties); ArrivalPlan/RoleCard/PlanDiff unchanged from ADR-001 |
| 5. Markdown fixtures loaded as raw text; directory matches reconciled layout; all 6 fixtures populated from analyst report | Met | `open().read()` via Path.read_text() — no parser; paths: fixtures/dossiers/{ms-chen,priya-nair,james-okafor}.md + fixtures/properties/{rosewood-sand-hill,the-carlyle-new-york,castiglion-del-bosco}.md; content drawn from analyst research report sections (Dossier A→ms-chen with name preserved, B→priya-nair, C→james-okafor; all 3 property profiles) |

## Flagged Items

- TD: low — `build_guest_dossier()` parser uses a `**Arrival Property:**` Markdown field that is not in the ADR-002 template. Added it to the ms-chen/priya-nair/james-okafor dossiers to make typed object construction deterministic. If BL-002 generates dossier text dynamically without this field, the fallback is `rosewood-sand-hill`. Suggest adding `**Arrival Property:**` to the ADR-002 template formally.
- TD: low — `static/audio/briefing_cached.mp3` is absent; replay TTS returns a synthetic silent MP3 frame. BL-002 (or BL-004 offline rehearsal) should generate and commit a real cached audio file before the demo.
- DQ: normal — ADR-002 Delta 5 canonical offline path describes `ms-chen.md` with prior stays at `rosewood-london.md` + `rosewood-beijing.md`; the reconciled fixture set (delegation brief hard constraint) uses `the-carlyle-new-york.md` + `castiglion-del-bosco.md` instead. The `load_provenance_cards()` function reads prior-stay property IDs from the dossier text and loads matching fixture files — so provenance discovery is data-driven and correctly resolves the new slugs without code change.

## Reasoning

**Decision chain:**
1. Starlette 1.0 broke the dict-first `TemplateResponse` signature — discovered at boot test, fixed immediately with a one-line wrapper. No architectural impact.
2. Regex for prior stays section required MULTILINE + DOTALL + `^##` boundary because the ADR-002 Markdown template uses blank lines between `## Prior Stays` and the first `###` subsection. Standard single-line match returned empty string.
3. `diff()` was implemented (not stubbed) because the never-cut spine (TREQ-006) must work in replay mode for the demo narrative; raising NotImplementedError there would break the core demo flow even with fixtures loaded.
4. All live paths raise NotImplementedError (not silent no-ops) to give BL-002 a loud, clear signal if called without the backend configured.

**Constraints applied:** ADR-001 dep list only; Python 3.11 target (tested on 3.12, compatible); no Streamlit; no live APIs; working skeleton over polish; GuestSynthesis excluded from PlanDiff path.

**Confidence:** High. All acceptance criteria verified against running server. Fixture parsing confirmed for all 6 files. Models round-trip from JSON. Scope guard fires correctly.

## Commit SHA: b0317ae
