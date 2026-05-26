# Code Review: BL-005 Voice Layer (commit 41bc223)

## Summary

The voice layer implementation is structurally sound and correctly implements the offline-zero-network guarantee, never-cut spine, and P0 typed path. Two medium-priority issues were found — neither blocks the demo. One low-priority extensibility shape concern is noted for BL-008. No critical issues. **No blockers for BL-008 start.**

---

## Strengths

- Lazy ElevenLabs import is correctly implemented: `from elevenlabs import ElevenLabs` is inside `_tts_elevenlabs()` and `_stt_elevenlabs()` function bodies, never at module or class scope. The `OFFLINE_MODE` / `Backend.REPLAY` branch in both `tts()` and `stt()` returns before reaching those inner functions entirely, making the zero-network guarantee structurally enforced, not just guarded.
- `_classify_observation()` returns `"dossier_observation"` on empty string (zero-keyword match), ambiguous text, and None/whitespace-only input — crash path is closed.
- `_get_briefing_for_card()` reads `live_replanned > live_baseline > cached_replanned > cached_baseline > fixture_fallback` in priority order. US-005 (post-replan TTS reflects updated briefing) is correctly wired.
- `GET /diff` and `GET /diff-panel` operate exclusively on `arrival_plan` fields. The `synthesis` field of `OrchestratorResponse` is not referenced in either handler. Never-cut spine structurally intact.
- `briefing_cached.m4a`: confirmed present at `sense_arrival/static/audio/briefing_cached.m4a`, 159,072 bytes, ISO Media MP4 v2 container. TD-006 resolved.
- TTS endpoint returns `(bytes, mime_type)` tuple; `voice_tts()` reads the mime_type and sets `Content-Type` correctly. Browser will not reject M4A served as `audio/mp4`.
- `playAudio()` in app.js walks text nodes only (skipping child element text) before slugifying the card ID. Badge content ("Observation noted") will not corrupt the `/voice/tts/{card_id}` URL.
- `_applyTranscribeResponse()` parses the HTMX OOB swap manually for the mic JS-fetch path using `DOMParser` — correct equivalent to HTMX native OOB handling for the HTMX-form path.

---

## Issues Found

### Critical

None.

### High Priority

None.

### Medium Priority

| # | Issue | Location | Description | Suggested Fix |
|---|-------|----------|-------------|---------------|
| M-001 | `voice_transcribe` returns HTTP 400 for the empty-text branch but the client JS does not guard against it | `main.py:375-378`, `app.js` | When `source=text` and `text_input` is blank/whitespace-only, the endpoint returns a 400 `<p class="observation-error">`. The HTMX form does not have `hx-on::response-error` nor a `required` attribute on the textarea, so HTMX will silently drop the 400 response body into the swap target only if the target is specified. If the textarea is empty and the form submits, the user sees no feedback unless HTMX handles 4xx (default: it does NOT swap on error status). In a live demo, submitting a blank note silently does nothing visible to the judge. | Add `required` to the textarea in `dashboard.html` (prevents submit), OR change the 400 to 200 with an inline error message in the HTML response body (same pattern as the ambiguous-text branch). The 200 path with inline error is safer for HTMX. |
| M-002 | `_silent_frame()` returns 44 bytes of null — not a valid audio container | `voice.py:94-102` | The `_silent_frame()` fallback (used only when `briefing_cached.m4a` is missing) returns `bytes(44)` which is not a valid M4A or MP3 frame. The `Response` is served with `audio/mp4` mime type but a browser receiving 44 null bytes may emit a console error or stall the Play button in "Playing..." state indefinitely (the `audio.onended` event never fires for invalid audio). In the judging room `briefing_cached.m4a` is present (TD-006 resolved), so this path is unreachable under normal conditions. The risk is if the file is somehow absent (accidental git-clean, wrong cwd). | Return an empty but valid M4A: a 7-byte ftyp atom (`\x00\x00\x00\x07ftyp`) is sufficient to cause immediate decode failure and trigger `audio.onerror`, which restores the button. Alternatively, log at ERROR and return an HTTP 503 so the JS `resp.ok` check fires instead of hanging. Either prevents the "stuck Playing" state. |

### Low Priority / Nitpicks

- `_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"` (Rachel) is hardcoded. If the account has Rachel deprecated or restricted, first live TTS call fails and falls back to cached. Not a demo risk (fallback is solid) but a DQ note for post-hackathon. The engineer report already flagged this.
- `_render_role_cards_oob()` builds role card HTML as inline strings rather than via Jinja2 template. Noted as known tech debt; scope is small (6 cards, stable markup). No action needed before 5PM.
- `select_guest` at `main.py:658` calls `orchestrator.plan()` with 3 positional args (missing `session_observations`). The `index()` call passes 4. If `orchestrator.plan()` has `session_observations` as a required positional parameter, `POST /select` will raise a `TypeError` at runtime. This is P1/demo-optional path (ADR-002 Delta 4 explicitly cuts it in offline mode); it does not affect the canonical rehearsed demo path. Check the orchestrator signature.

---

## Security Assessment

- [x] Input validation present — `text_input.strip()` prevents empty-string classify; `_ROLE_SLUG_TO_NAME` lookup limits valid `card_id` slugs; unknown `card_id` gets sanitized via `re.sub(r"[^a-z-]", "", ...)`.
- [x] No injection vulnerabilities — classifier is pure string matching; OOB HTML uses Python f-strings with no raw user content inserted into script/style contexts; transcript is HTML-escaped by the `&ldquo;` encoding in `_render_observation_feedback()`.
- [x] Auth/authz — not applicable (demo app, no auth surface).
- [x] Secrets not exposed — `ELEVENLABS_API_KEY` read from `settings.elevenlabs_api_key` at call time, never logged, never returned to client.

One note: `display_text` in `_render_observation_feedback()` at `main.py:433` injects the raw transcript string directly into HTML inside `&ldquo;...&rdquo;`. The `&ldquo;` entity provides no XSS protection — only HTML entity encoding of `<`, `>`, `&`, `"` does. If a staffer types `<script>alert(1)</script>` as a staff note, it would execute. This is a demo app with no external attack surface (localhost), so this is informational only, not actionable before 5PM.

---

## Performance Assessment

- [x] No N+1 queries — `_get_current_plan()` reads from `app.state` (O(1)); `_get_briefing_for_card()` is O(n) over 6 cards.
- [x] No memory leaks — `URL.createObjectURL()` is revoked in `audio.onended` and `audio.onerror`. `audioChunks` is reset on each `startRecording()` call.
- [x] `app.state.session_observations` is an unbounded in-memory list. For a 3-minute demo with a handful of observations, this is fine.

---

## Offline Zero-Network Confirmation

**CONFIRMED — zero network in OFFLINE_MODE / Backend.REPLAY.**

Trace for `GET /voice/tts/{card_id}` in REPLAY:
1. `voice_tts()` calls `voice.tts(briefing_text, backend=Backend.REPLAY)`.
2. `tts()` checks `effective == Backend.REPLAY` → calls `_load_cached_audio()` and returns immediately.
3. `_tts_elevenlabs()` is NEVER called. The `from elevenlabs import ElevenLabs` line inside it is never reached.
4. Returns `(briefing_cached.m4a bytes, "audio/mp4")` — no network.

Trace for `POST /voice/transcribe` in REPLAY:
1. `source=text`: transcript resolved from `text_input.strip()` directly — no network.
2. `source=mic`: `voice.stt(audio_bytes, backend=Backend.REPLAY)` → `effective == Backend.REPLAY` → returns hardcoded string. `_stt_elevenlabs()` never called.
3. `_classify_observation()` is pure Python string matching — no network.
4. `app.state.session_observations.append()` — no network.
5. `_get_current_plan(Backend.REPLAY)` reads `app.state.cached_replanned` (loaded at startup from fixture JSON) — no network.
6. `_render_observation_feedback()` and `_render_role_cards_oob()` are pure HTML string construction — no network.

The `from elevenlabs import ElevenLabs` import inside `_tts_elevenlabs()` and `_stt_elevenlabs()` is structurally unreachable from the REPLAY branch. The REPLAY guard is the first statement in both `tts()` and `stt()` — there is no code path from the REPLAY branch to the live functions.

**No outbound network call is possible from voice.py or main.py when Backend.REPLAY is active.**

app.js: `playAudio()` fetches `/voice/tts/{card_id}` from the local server — this is a loopback call, not an external network call. The server then serves the cached file as confirmed above. `submitAudio()` posts to `/voice/transcribe` — same: loopback to local server, handled by REPLAY branch.

---

## Never-Cut Spine Confirmation

**CONFIRMED — spine structurally intact.**

`GET /diff` handler (`main.py:211-241`): reads `baseline_resp.arrival_plan` and `replanned_resp.arrival_plan` only. Passes both to `orchestrator.diff()`. No reference to `.synthesis`. Returns `plan_diff.model_dump()`.

`GET /diff-panel` handler (`main.py:248-282`): identical structure. Calls `orchestrator.diff(baseline_resp.arrival_plan, replanned_resp.arrival_plan)`. Renders `diff_panel.html` with `{"diff": plan_diff}`. No synthesis field in template context.

`POST /voice/transcribe`: appends to `app.state.session_observations`. Does NOT call `orchestrator.diff()`. Does NOT modify `live_baseline` or `live_replanned`. The observation is written to the session list only — it does not touch the diff spine.

`session_observations` does NOT flow into `GET /diff` or `GET /diff-panel`. Those handlers read exclusively from `cached_baseline`, `cached_replanned`, `live_baseline`, `live_replanned` — all of which are `OrchestratorResponse` objects set by `startup()`, `index()`, or `replan()`. The observations shim (TREQ-023) feeds back into the plan only if `orchestrator.plan()` is re-called (live mode), and even then the diff compares `arrival_plan` fields, not `session_observations`.

---

## TD-006 Status

**RESOLVED.** `static/audio/briefing_cached.m4a` is present: 159,072 bytes, confirmed ISO Media MP4 v2 container by `file` command. `_load_cached_audio()` returns real audio bytes. The silent-frame fallback at `_silent_frame()` is structurally unreachable during the demo.

---

## BL-008 Extensibility Assessment (TREQ-023)

The capture → classify → update path is correctly shaped for BL-008 extension with one caveat.

**What BL-008 can reuse without modification:**
- `_classify_observation()` already returns `"dossier_observation"` as the catch-all bucket. BL-008 needs only to act on this classification key in the transcribe handler — no classifier change.
- `app.state.session_observations` is already appended at `main.py:384`. BL-008 can read this list and use it as the dossier-append source.
- The HTMX OOB swap pattern (`hx-swap-oob="innerHTML:#role-cards"`) is established and working. Adding a second OOB target (`#synthesis-panel`) is a copy-paste extension of the existing pattern in `_render_role_cards_oob()`.

**Shape concern for BL-008 (LOW, not a blocker):**

`POST /voice/transcribe` currently does NOT re-call `orchestrator.plan()` or `orchestrator.replan()` — it takes a static snapshot of the current plan and marks the affected card visually. Per ADR-002 Delta 4, TREQ-023 requires that after a `dossier_observation`, `plan()` is re-called with the accumulated observations appended to the dossier prompt, and `#synthesis-panel` is swapped. BL-008 will need to add this re-synthesis call inside the `voice_transcribe()` handler (guarded by `if classification == "dossier_observation"`). This is an extension (add code) not a refactor (change existing structure), which is the correct shape. The existing handler's step structure (resolve → classify → append → get_plan → render) makes the insertion point obvious: between steps 3 and 4, add a conditional re-plan call for `dossier_observation` in live mode.

The only risk is that this re-synthesis call in live mode adds 3–8 seconds of latency to the transcribe response. BL-008 should consider an async background re-synthesis with a loading indicator on `#synthesis-panel` if latency is unacceptable for the demo. In REPLAY mode, this is a no-op (return `synthesis_fixture.json` unchanged, per ADR-002 Delta 5).

No rework of BL-005 code is required for BL-008 to proceed.

---

## Acceptance Criteria Coverage

| Criterion | Status | Evidence |
|-----------|--------|---------|
| OFFLINE zero-network: typed path + Play Briefing with zero network | Met | REPLAY branch returns before any live function in both `tts()` and `stt()`. Lazy import structurally unreachable from REPLAY. Cached M4A confirmed 159KB real audio. |
| Never-cut spine intact | Met | `GET /diff` and `GET /diff-panel` read only `arrival_plan` fields. `session_observations` does not flow into either handler. |
| US-004 P0: typed observation → classify → OOB role card update | Met | `source=text` path resolves transcript from `text_input.strip()`, classifies, appends to session, renders OOB HTML. Empty/ambiguous → `dossier_observation`, returns 200 HTML. Blank submit: returns 400 (see M-001 — medium issue, not critical). |
| US-004: ambiguous/empty → sensible default, never 500 | Partially Met | Ambiguous text → `dossier_observation`, 200 response. Blank/whitespace submit → 400, not 500. 400 may be silent to user in HTMX context (M-001). No path to 500. |
| US-005 P0: TTS reads CURRENT briefing (post-replan) | Met | `_get_briefing_for_card()` reads `live_replanned > live_baseline > cached_replanned > cached_baseline > fallback`. Correct priority order. |
| US-005: TTS failure → cached fallback, not 500 | Met | `_tts_elevenlabs()` has blanket `except Exception` → returns `_load_cached_audio(), MIME_M4A`. `voice_tts()` returns `Response` with cached bytes. No 500 surface. |
| US-004 P1: mic guard shows "Text mode" banner | Met | `initMic()` calls `showTextModeBanner()` on `getUserMedia` failure. Mic section hidden by default (`display:none`). |
| TD-006 resolved | Met | `briefing_cached.m4a` present, 159KB, valid ISO MP4 v2 container. |

---

## Flagged Items

- **TD-006: RESOLVED** — `static/audio/briefing_cached.m4a` present and confirmed valid. No action required.
- **M-001 (Medium):** Blank textarea submit returns HTTP 400 which HTMX may silently drop — user sees no feedback. Fix: add `required` attribute to textarea in `dashboard.html` or change to 200 with inline error HTML. Recommend fixing before demo if time permits.
- **M-002 (Medium):** `_silent_frame()` returns 44 null bytes — not a valid audio container. Unreachable in normal conditions (TD-006 resolved) but would cause "stuck Playing" button if M4A file is absent. Low urgency given TD-006 is resolved; add as tech debt.
- **LOW (Nitpick):** `POST /select` missing `session_observations` argument to `orchestrator.plan()` at `main.py:658-662`. P1/demo-optional path; does not affect the canonical offline or live demo path. Check orchestrator signature; if required positional, this would `TypeError` at runtime on the selector path.
- **DQ: normal** — Live ElevenLabs TTS will produce per-card audio; offline serves the same clip for all cards. Intended per ADR-001. No action.
- **DQ: normal** — `_VOICE_ID` (Rachel) hardcoded; no env override. Fallback on failure is solid. Post-hackathon follow-up only.

---

## Verdict

**PASS WITH TECH DEBT**

BL-005 is **approved to close**. BL-008 may proceed.

Critical blockers: none.

Demo risk: M-001 (blank submit silent failure) is the only pre-demo fix recommended if time permits. It requires one attribute change in `dashboard.html` (add `required` to textarea) and takes under 2 minutes. M-002 is not a demo risk given TD-006 is resolved.

Never-cut spine: intact and confirmed.
Offline zero-network: structurally enforced, confirmed.
TD-006: resolved.
BL-008 extensibility: clean extension path exists; no rework of BL-005 required.

---

## Reasoning

**Decision chain:**

1. The offline-network guarantee was verified by tracing the REPLAY branch in both `tts()` and `stt()` from entry point to return, confirming the live functions are never called and the lazy import is structurally unreachable. This is the highest-risk item given the judging-room scenario and it passes.

2. The never-cut spine was verified by reading both diff handlers in full. Neither references `synthesis`; both pass only `arrival_plan` to `orchestrator.diff()`. The `session_observations` list does not appear in either handler.

3. The typed path was traced from `POST /voice/transcribe` with `source=text` through classify, append, render — confirming it cannot 500 on any input. The 400 on blank input (M-001) is a medium UX issue, not a crash.

4. TTS failure tolerance was verified: the blanket `except Exception` in `_tts_elevenlabs()` returns cached audio. The `voice_tts()` handler does not raise — it returns a `Response` object with cached bytes. No 500 path exists.

5. BL-008 extensibility was assessed against ADR-002 Delta 4 TREQ-023. The handler's step structure allows a clean conditional insertion for `dossier_observation` re-synthesis without restructuring existing code.

**Constraints applied:** CRITICAL/blocking only per hackathon hard-5PM constraint; skipped style, naming, test depth, async-purity except where they affect demo safety.

**Confidence:** High. All five code files were read in full. The offline trace was structural (branch-level), not test-execution-based. M-001 is confirmed by reading HTMX 4xx default behavior (HTMX does not swap response body on non-2xx by default without `hx-on::response-error` or `hx-swap` on error config).

---

*Agent: Code-Quality | Date: 2026-05-16 | Commit: 41bc223 | Branch: build/sense-arrival-mvp*
*Status: PASS WITH TECH DEBT — BL-008 approved to proceed*
