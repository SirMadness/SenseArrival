# Code Review: BL-002 Arrival Orchestration Core (commit 38f766f)

**Agent:** 🟡 Code-Quality
**Date:** 2026-05-16
**Status:** Complete
**Branch:** build/sense-arrival-mvp
**Scope:** `sense_arrival/orchestrator.py`, `sense_arrival/main.py`, `sense_arrival/templates/dashboard.html`, `sense_arrival/static/style.css`

---

## Summary

BL-002 completes the Tier-1 Claude tool-use path, wires `GET /diff` for live mode, and adds the Front Desk structured panel. The never-cut TREQ-006 spine is structurally intact: `GET /diff` passes `OrchestratorResponse.arrival_plan` — and only that — into `diff()`. `GuestSynthesis` has no path to `PlanDiff`. Structured-output robustness is sound under the broad `except Exception` fallback. Two medium-severity items require attention before or during demo rehearsal; no blockers to closing BL-002 and opening BL-003.

**VERDICT: PASS WITH TECH DEBT**

---

## Strengths

- Never-cut spine is clean. `orchestrator.diff()` accepts two `ArrivalPlan` arguments; `main.py GET /diff` passes `baseline_resp.arrival_plan` and `replanned_resp.arrival_plan` directly. `GuestSynthesis` is not referenced anywhere in the diff path — not in `diff()`, not in `PlanDiff`, not in the call site. Verified by live trace.
- The `202` guard in `GET /diff` (both `live_baseline` and `live_replanned` must be non-None before diff fires) prevents a crash when the demo starts. Correct and safe.
- `_call_claude()` and `_call_ollama()` both catch `Exception` broadly and return `load_offline_response()`. This means any failure mode — bad API key, network timeout, Pydantic schema mismatch, missing tool-use block — degrades to fixture render, not a 500.
- `anthropic.Anthropic()` is instantiated inside `_call_claude()` at call time (line 250), not at module scope. REPLAY path imports cleanly with zero network. Verified.
- Fixture baseline and replanned plans each contain exactly 6 role cards with the correct roles. Verified by direct inspection and live `model_dump()` round-trip.
- Scope guard (`_guard_dossier`, `_guard_property`) is applied at every `load_dossier()` / `load_property_card()` call site, including inside `load_provenance_cards()`. The allowed slug sets in `config.py` match the actual fixture files on disk (`james-okafor.md`, `priya-nair.md`, `the-carlyle-new-york.md`, `castiglion-del-bosco.md`).
- Tier-3 REPLAY path remains structurally unchanged from BL-001. Zero network calls at import or during replay execution. No live client is created until `_call_claude()` or `_call_ollama()` are entered.

---

## Issues Found

### Critical

None.

### High Priority

None.

### Medium Priority

| Issue | Location | Description | Suggested Fix |
|-------|----------|-------------|---------------|
| Sync client blocks event loop | `orchestrator.py:257` | `client.messages.create()` is a synchronous blocking call inside `async def _call_claude()`. For the 3–8 second Claude call, the uvicorn event loop is fully blocked. In a single-user demo this is acceptable — no concurrent requests. If the demo browser sends a second request (e.g., HTMX prefetch, status poll) during the Claude call, it will queue silently and recover. Not a crash risk; is a latency cliff if anything fires concurrently. | Wrap in `asyncio.get_event_loop().run_in_executor(None, ...)` or switch to `AsyncAnthropic` in BL-005. No action required before demo. |
| `POST /select` does not update `live_baseline` | `main.py:324-360` | If a judge triggers the guest selector mid-demo, the new plan is rendered on screen but `app.state.live_baseline` still holds the Ms. Chen plan. A subsequent `POST /replan` + `GET /diff` would diff Ms. Chen's baseline against the selected guest's replan — producing a meaningless diff. The `202` guard only protects the case where neither plan has been stored yet; it does not protect against a stale cross-guest baseline. | Set `app.state.live_baseline = response` after the `orchestrator.plan()` call in `select_guest()`. Low effort, prevents demo confusion if selector is used. |

### Low Priority / Nitpicks

- `@app.on_event("startup")` is deprecated in FastAPI 0.95+ (project requires `fastapi>=0.111`). Emits a deprecation warning at startup. Not a crash risk; replace with the `lifespan` context manager pattern before any production use.
- `tool_choice={"type": "any"}` is slightly more permissive than `{"type": "tool", "name": "submit_arrival_plan"}`. Already flagged by engineer as BL-003 cleanup. No risk with a single tool registered.
- `voice_transcribe` hardcodes `classification = "dossier_observation"` — every staff note is appended to `session_observations` with no filtering. The accumulation is unbounded within a demo session. For a 3-minute demo this is fine; for a longer judge session, the prompt will grow on every observation submission and eventually push the combined prompt token count up.
- The `NotImplementedError` catch in `index()` and `replan()` is BL-001 scaffolding that can never be reached in BL-002 (because `_call_claude()` catches all exceptions internally). Dead code; harmless.

---

## Security Assessment

- [x] Input validation present — scope guard on all fixture slug inputs
- [x] No injection vulnerabilities — Markdown loaded as raw string, no shell execution
- [x] No secrets exposed — `anthropic_api_key` read from env; not logged or rendered
- [x] Auth/authz not applicable — single-user demo, no auth layer required

---

## Performance Assessment

- [x] No N+1 queries — fixture files read once per request, provenance cards loaded in a single loop
- [ ] Sync HTTP call in async handler — acceptable for demo; noted above
- [x] No memory leaks — `session_observations` grows per observation but bounded by demo duration
- [x] Tier-3 replay is zero-network; cached in `app.state` at startup

---

## Spine Integrity Trace (TREQ-006 / Never-Cut)

**GET /diff live-mode path:**

```
GET /diff
  backend != REPLAY
  baseline_resp = app.state.live_baseline       # set by GET / → orchestrator.plan() → OrchestratorResponse
  replanned_resp = app.state.live_replanned     # set by POST /replan → orchestrator.replan() → OrchestratorResponse
  if either is None → 202 (safe)
  orchestrator.diff(baseline_resp.arrival_plan, replanned_resp.arrival_plan)
  # diff() signature: def diff(baseline: ArrivalPlan, replanned: ArrivalPlan) -> PlanDiff
  # GuestSynthesis: present in OrchestratorResponse but .synthesis field is never passed in
```

`GuestSynthesis` is structurally unreachable from `diff()`. There is no code path that passes synthesis into PlanDiff. The only way synthesis could leak is if `OrchestratorResponse` were passed directly to `diff()` — the call sites explicitly extract `.arrival_plan`. Confirmed clean.

---

## 6 Role Cards Guarantee (TREQ-002)

The tool schema description field states "Exactly 6 role cards — one per role listed" and the system prompt Rule 4 states "Exactly 6 role cards: Front Desk, Concierge, Spa, Dining, Housekeeping, Guest Experience." However, there is **no enforcement in `_parse_tool_response()`** — if Claude returns 4 cards, they are parsed as-is and the template renders 4 cards.

For replay mode: fixture verified to contain exactly 6 cards. Zero risk.

For live mode: the prompt instruction is strong and `tool_choice={"type":"any"}` forces a single structured call, reducing the probability of a short response. However, a prompt-only guarantee is not a code guarantee. If Claude returns fewer than 6 cards, the render degrades gracefully (renders what it gets) rather than crashing. The demo would look visually wrong but not error.

**Verdict on TREQ-002:** Met for replay; best-effort for live. Acceptable for hackathon. Adding a len check + backfill from fixture as BL-003 hardening would be ideal.

---

## Grounding / Prompt Fidelity (TREQ-004/020)

`_build_prompt_blocks()` injects: GUEST DOSSIER → ARRIVAL PROPERTY CARD → PROVENANCE cards (labeled with property_id) → LIVE STAFF OBSERVATIONS (if any) → ARRIVAL EVENT. ADR-002 Delta 3 ordering is followed exactly. System prompt Rule 1 mandates named anchors; Rule 5 names six specific Sand Hill anchors the model must reference. The prompt is structurally capable of producing named-anchor output.

Cannot verify live Claude output quality without an API key. This is flagged as a DQ item by the engineer and is the correct risk register for it.

---

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|----------|
| US-001: GET / renders mood banner + Front Desk card with arrival mode/action/do-not + all 6 role cards | Met | Template confirmed: mood banner at line 66, Front Desk `.fd-summary` block at lines 101-126, role card loop at line 86, fixture verified 6 cards |
| TREQ-003: Mood classified and shown as banner | Met | `response.arrival_plan.mood` rendered in `<span class="mood">` at line 66 |
| TREQ-004/020: ≥2 outputs reference named Sand Hill anchors | Met (fixture); best-effort (live) | Fixture contains Bluejay Bikes, Ridge Rosé Reveal, Asaya Spa, Madera, Old La Honda Road. System prompt names these explicitly. Live path verified by design. |
| TREQ-001/014: plan() is single tool-use call; malformed output does not crash | Met | `tool_choice={"type":"any"}` with single tool. Broad except in `_call_claude()` returns fixture on any failure. No crash path from Claude tool output to render. |
| TREQ-006: Tier-3 replay zero-network; GET /diff spine synthesis-free | Met | Spine trace above. Replay path verified by import analysis and live execution. |
| TREQ-002: Exactly 6 role cards | Met (fixture); best-effort (live) | Fixture confirmed 6 cards. No code enforcement for live path. |

---

## Flagged Items

- TD: medium — `POST /select` does not update `app.state.live_baseline`. If selector is used mid-demo, `GET /diff` will diff the wrong pair. Recommend adding `app.state.live_baseline = response` to `select_guest()` before BL-003 or before live demo rehearsal.
- TD: low — Sync `anthropic.Anthropic` client in `async def _call_claude()` blocks event loop for 3–8s. No demo impact for single-user. Wrap in `run_in_executor` or migrate to `AsyncAnthropic` in BL-005.
- TD: low — `@app.on_event("startup")` deprecated in FastAPI 0.111+. Emits warning at server start. Replace with `lifespan` in any post-hackathon cleanup.
- TD: low — No enforcement of exactly-6-role-cards in `_parse_tool_response()`. Live Claude could return fewer; render degrades but looks wrong. Add assertion + fixture backfill in BL-003.
- DQ: normal — Live end-to-end test (Tier-1 Claude producing grounded named-anchor output) not completed — no API key available during build. Prompt and schema designed for this; verify with key before demo.

---

## Reasoning

**Decision chain:**

1. The never-cut spine check was the highest priority. Traced the full `GET /diff` live path from `app.state` read through `orchestrator.diff()` call — `GuestSynthesis` never enters this path by construction (call site extracts `.arrival_plan` explicitly). The `202` guard for uninitialized state is correct and safe.

2. Structured-output robustness was verified by reading both the try block (which can only fail via `_parse_tool_response()` raising `ValueError` — also caught) and the broad `except Exception` fallback. All failure modes — network error, auth error, missing tool-use block, Pydantic validation error — map to `load_offline_response()`. This is the correct TREQ-014 implementation for a hackathon context.

3. The 6-card guarantee gap is real but not a blocker: replay is verified deterministic; live path has a strong prompt instruction. The demo rehearsal path (OFFLINE_MODE) is fully protected.

4. The sync client in async handler is a known acceptable trade-off for single-user demo; the engineer documented it explicitly. It is not a crash risk; it is a throughput limit that does not apply to this use case.

5. The `POST /select` missing `live_baseline` update is the only medium-severity finding: it produces logically wrong (not crashing) behavior if the selector is used before `GET /diff`. Since the canonical demo path is Ms. Chen → Inject Delay → View Diff, this only matters if a judge explicitly triggers the selector and then asks to see the diff. Worth fixing; not a blocker.

**Constraints applied:** Hackathon focus — CRITICAL only blocks BL-003. Style, naming, async purity deferred unless crash risk. Synthesis-exclusion from PlanDiff is a hard constraint per ADR-002 and was verified before all other items.

**Confidence:** High on spine integrity (traced + executed). High on Tier-3 replay correctness (verified). Medium on live Claude output quality (cannot verify without API key; prompt design is sound). Low risk on the sync-client concern for a single-user 3-minute demo.
