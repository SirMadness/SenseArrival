# ADR-001: Stack Selection — SenseArrival "First Five Minutes"

## Status
Accepted

### Amendment — 2026-05-16
**What changed:** The demo-mode default posture in the "Fixture-Replay / Offline Mode" section was corrected. The original closing sentence implied offline mode was the default and live mode was the exception ("Switch to live mode only if the network is confirmed stable"). That sentence inverted the builder's actual intent.

**Corrected posture:** The showcased demo runs **live** — Claude cloud + ElevenLabs TTS — as the primary, sponsor-aligned path (per TREQ-013, which designates Tier 1 / live API as "primary/showcased"). `OFFLINE_MODE` / fixture-replay is the **resilience fallback** for an unreliable judging-room network, not the default. The fallback is still rehearsed end-to-end before the judging room as the safety net; it remains a first-class engineering concern.

**Compatibility:** ADR-002 Delta 5 ("Offline-Replay Canonical Path") already frames live mode as the richer multi-guest path and offline replay as the Ms. Chen @ Rosewood Sand Hill single-guest canonical path. This amendment is fully consistent with that framing; no change to ADR-002 is required.

**Scope:** Wording correction to the Fixture-Replay / Offline Mode section only. Stack decision, dependencies, route table, cut order, and all other sections are unchanged.

## Context

Solo builder, ~6-hour build window, hard 5:00 PM submission. Judging weights: 45% Live Demo, 35% Creativity/Originality, 20% Impact. A 3-minute demo in a judging room with unpredictable network and no guarantees on audio hardware. The product is an arrival choreography engine — not a chatbot — with structured role-card outputs, live re-plan diffs, ElevenLabs TTS playback, and browser mic STT for staff voice notes.

Key forcing functions:

- The 45% demo weight means visual polish and zero crashes matter more than code elegance.
- ElevenLabs has a mature Python SDK (`elevenlabs`) and a JS SDK (`@elevenlabs/elevenlabs-js`). STT/transcription from a browser mic must either stream to a server endpoint or run client-side via the Web Speech API.
- Anthropic structured output (tool use / `response_format`) is most ergonomic in Python with the official `anthropic` SDK and Pydantic models.
- A solo builder loses 30–45 minutes context-switching between a TypeScript frontend and a Python backend if they are separate processes. A unified Python stack eliminates that seam.
- FastAPI + Jinja2 + HTMX delivers server-side-rendered, reactively updating HTML with zero build step — meaning a full stack restart is a single `uvicorn` command and there is no React hydration surface to break under pressure.

## Decision

**Recommended stack: Python 3.11 + FastAPI + Jinja2/HTMX + Anthropic SDK + ElevenLabs Python SDK + Pydantic v2.**

This is a single-process Python server. The browser is a thin HTML/JS client that POSTs to FastAPI endpoints and swaps HTML fragments via HTMX `hx-swap`. No separate frontend build process, no Node runtime, no TypeScript compilation step.

### Exact Dependencies

```
# requirements.txt
anthropic>=0.28          # structured tool-use, async client
elevenlabs>=1.0          # TTS generate + STT transcribe (server-side)
fastapi>=0.111
uvicorn[standard]>=0.29
jinja2>=3.1
python-multipart>=0.0.9  # for audio file upload from browser
pydantic>=2.7
httpx>=0.27              # async HTTP if needed for fixture loading
python-dotenv>=1.0
```

No other dependencies. Resist adding any.

### Project Layout

```
sense_arrival/
  main.py                  # FastAPI app, all routes
  orchestrator.py          # Claude tool-loop: plan(), replan(), diff()
  models.py                # Pydantic: GuestProfile, ArrivalPlan, RoleCard, PlanDiff
  voice.py                 # ElevenLabs TTS (text→audio bytes) + STT (audio→transcript)
  fixtures/
    ms_chen.json           # Guest persona fixture
    sand_hill_context.json # Spa, Madera, Bluejay Bikes, etc.
    delay_event.json       # The injected delay payload
    baseline_plan.json     # Pre-computed offline plan (fixture-replay mode)
    replanned_plan.json    # Pre-computed offline re-plan (fixture-replay mode)
  templates/
    base.html
    dashboard.html         # Full arrival dashboard: mood banner, role cards, suppression panel
    role_card.html         # HTMX-swappable fragment
    diff_panel.html        # What-changed audit log fragment
    guest_message.html
  static/
    app.js                 # Mic capture → POST /voice/transcribe; ElevenLabs TTS play
    style.css
  .env                     # ANTHROPIC_API_KEY, ELEVENLABS_API_KEY
```

### Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Dashboard, render baseline plan |
| POST | `/replan` | Inject delay event → Claude re-plan → return updated HTML fragments |
| GET | `/diff` | Return diff panel fragment showing what changed |
| POST | `/voice/transcribe` | Receive browser audio blob → ElevenLabs STT → return transcript + classify |
| GET | `/voice/tts/{card_id}` | ElevenLabs TTS → stream MP3 bytes for role card briefing |
| GET | `/offline` | Serve fixture-replay mode (no API calls) |

## Browser Mic → STT Path

This is the only significant live-audio risk. The approach:

1. **Browser** uses `navigator.mediaDevices.getUserMedia({audio:true})` + `MediaRecorder` to capture a blob (WebM/Opus or WAV, ~10–30 seconds).
2. **`app.js`** POSTs the blob as `multipart/form-data` to `POST /voice/transcribe`.
3. **`voice.py`** receives the file, calls `elevenlabs.speech_to_text.convert(audio=file_bytes, model_id="scribe_v1")` (the ElevenLabs Scribe STT endpoint), returns the transcript as JSON.
4. **`orchestrator.py`** classifies the transcript (spa request / dining preference / accessibility need) via a single Claude call and routes the update to the appropriate role card.
5. The HTMX response swaps the affected role card HTML fragment in-place.

**Typed-text fallback (MANDATORY, build this first):** Every STT flow has a parallel `<textarea>` + "Submit as text" button that bypasses mic capture entirely and POSTs the same payload to `/voice/transcribe` with `source=text`. Wire this up before touching `getUserMedia`. If mic fails in the judging room, type the staff observation, demo continues without pause.

**Mic permission guard:** On page load, call `getUserMedia` once and cache the stream. If it throws, toggle a visible "Text mode" banner — do not let the error surface silently.

## Fixture-Replay / Offline Mode

All Claude and ElevenLabs calls are gated by an `OFFLINE_MODE=true` env var (or a toggle in the UI). When offline:

- `orchestrator.py` loads `fixtures/baseline_plan.json` or `fixtures/replanned_plan.json` directly and skips the API call.
- `voice.py` TTS returns a pre-recorded MP3 from `static/audio/briefing_cached.mp3`.
- STT returns a hardcoded transcript string.
- The "Inject Delay" button still fires the re-plan route but serves the fixture diff instantly.

This means the demo can run end-to-end with zero network. **The showcased demo runs live** — Claude cloud + ElevenLabs TTS is the primary, sponsor-aligned path (TREQ-013 designates Tier 1 as "primary/showcased"). Fixture-replay / `OFFLINE_MODE` is the **resilience fallback for a flaky judging-room network, not the default** — switch to it only if connectivity is unreliable at demo time. Rehearse the full fallback path (baseline → re-plan → diff → ≥1 TTS) end-to-end with zero outbound network before walking into the judging room, so the safety net is confirmed ready.

## Ruthless Cut Order

Cut in this order if time runs short. Never cut item 1.

| Priority | Feature | Cut decision |
|----------|---------|--------------|
| NEVER CUT | Re-plan diff panel (what changed & why) | This is the creative proof. Without it, it's just a dashboard. |
| Keep | Role cards (all 6 roles, even if some are placeholder text) | Visual completeness matters for the 3-min demo scan |
| Keep | "Inject Delay" button → live re-plan | This IS the demo narrative |
| Keep | TTS "Play Briefing" on at least one card | ElevenLabs integration is a differentiator |
| Cut if needed | Mic STT capture | Fall back to typed-text input; same code path downstream |
| Cut if needed | Guest message panel | Nice but not in the core narrative |
| Cut if needed | Suppression panel ("what NOT to offer") | Mention verbally if not rendered |
| Cut last resort | Mood banner | One line of text, keep it; cost is trivial |

## If I Had to Start Coding in 10 Minutes

Run `mkdir sense_arrival && cd sense_arrival && python -m venv .venv && source .venv/bin/activate && pip install anthropic elevenlabs fastapi uvicorn[standard] jinja2 python-multipart pydantic python-dotenv`, create `.env` with both API keys, write `models.py` with the four Pydantic models (`GuestProfile`, `RoleCard`, `ArrivalPlan`, `PlanDiff`), then write `orchestrator.py` with a single `plan()` function that calls Claude with `response_format` or a tool schema returning an `ArrivalPlan`. Hardcode Ms. Chen's fixture inline for the first pass. Get `GET /` rendering a dashboard with six role cards in the browser before touching voice, re-plan, or diff. That first working render is the foundation everything else bolts onto — it takes 45 minutes and de-risks the rest of the build.

## Alternatives Considered

**TypeScript + Next.js + Anthropic SDK + Tailwind**
- Faster to polish visually with Tailwind component libraries.
- `@elevenlabs/elevenlabs-js` is the native JS SDK for TTS; browser mic capture is native JS with no proxy needed.
- Rejected because: Zod schema maintenance across API routes adds friction; Next.js cold starts and build errors under time pressure are high-variance failure modes; a solo builder context-switching between TS frontend and a Python orchestration layer (if needed for Pydantic guarantees) loses 30+ minutes; FastAPI/HTMX delivers sufficient visual fidelity for a 3-minute demo.

**LangChain / LangGraph / CrewAI orchestration layer**
- Rejected. Heavy abstraction, longer install, harder to debug live. The tool-loop in this product is a single Claude call with a structured schema. Raw `anthropic` SDK is five lines; a framework adds hundreds.

**Streamlit**
- Explicitly banned by event rules.

## Consequences

- No TypeScript type safety on the frontend; disciplined Pydantic models on the server compensate.
- HTMX requires careful `hx-target` and `hx-swap` hygiene to avoid partial-update bugs; the mitigation is to keep fragment boundaries simple and test the re-plan swap early.
- ElevenLabs STT via server proxy adds one network hop (browser → FastAPI → ElevenLabs); this is acceptable and keeps API keys server-side, which is correct practice.
- Offline fixture replay is a first-class engineering concern, not an afterthought — this is a feature, not a hack. It is framed as the resilience fallback (live mode is the showcased default); the fallback path is rehearsed before the judging room so it is confirmed ready. See Amendment 2026-05-16.
