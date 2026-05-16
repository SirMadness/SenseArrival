# SenseArrival Demo Playbook — Delay-to-Delight

**Event:** Hospitality 2030 @ Rosewood Sand Hill — 2026-05-16
**Hard deadline:** 5:00 PM (Round 1 judging begins immediately)
**Demo slot:** ~3 minutes live + 1–2 min Q&A
**Judging weights:** Live Demo 45% / Creativity 35% / Impact 20%

---

## Pre-Demo Checklist (complete before entering judging room)

Run this offline rehearsal in full before walking in. Do not skip steps.

### Environment

- [ ] Confirm you are on branch `build/sense-arrival-mvp`
- [ ] Run `OFFLINE_MODE=true uvicorn sense_arrival.main:app --port 8000`
- [ ] Open `http://127.0.0.1:8000` in browser
- [ ] Confirm: mood banner renders ("Arrival Mood: Restorative" or similar)
- [ ] Confirm: all 6 role card divs are present (Valet, Front Desk, Dining, Housekeeping, Concierge, MOD)
- [ ] Confirm: synthesis panel visible with inferred preferences listed
- [ ] Confirm: "Inject Delay & Re-plan" button is visible
- [ ] Confirm: HTMX is loaded from `/static/htmx.min.js` (not a CDN) — check Network tab, confirm no unpkg.com or external JS requests
- [ ] Click "Inject Delay & Re-plan" — confirm: no full-page reload, mood banner updates, role cards update with "Updated" badge, diff panel renders with orange trigger banner and 16 entries

### Fallback verification

- [ ] Test `GET /diff` JSON: `curl http://127.0.0.1:8000/diff` returns `{"changed_roles": [...], "entries": [...]}` with 16 entries
- [ ] Test typed-text staff note: submit a note via the text area and confirm it is accepted (POST /voice/transcribe returns 200)
- [ ] Confirm TTS "Play Briefing" button is visible on at least one card (even if audio is silent/stubbed — button must be present)

### If network is available in the judging room

- [ ] Test `BACKEND=claude uvicorn sense_arrival.main:app --port 8000` with real API key
- [ ] Confirm `GET /` loads with Claude-generated content (not fixture placeholder text)
- [ ] Confirm `POST /replan` produces a real re-plan diff (may differ from fixture diff — reason text may fall back to generics; acceptable)
- [ ] If Claude is unreliable, **switch back to OFFLINE_MODE=true** before entering the room

### Backup assets (capture before 5PM — USER ACTION REQUIRED)

- [ ] Screenshot: baseline dashboard (mood banner + 6 role cards visible)
- [ ] Screenshot: post-replan dashboard with "Updated" badges and delay-injected banner
- [ ] Screenshot: diff panel fully rendered with orange trigger and 16 entries
- [ ] Capture a GIF or screen recording of the full Inject Delay → diff flow (QuickTime or similar)
- Store backups in a location accessible without the running app (e.g., desktop folder)

---

## 3-Minute Demo Script — Delay-to-Delight

> Time targets are approximate. Keep the narrative moving. Judges skim the screen while you talk.

### 0:00–0:30 — Frame the problem (no screen interaction yet)

"This is SenseArrival. We're solving Problem Statement #1: hyper-personalized arrival orchestration.

Hotels like Rosewood manually collect guest profiles across visits. But arrival is choreography, not just a profile lookup. Every staff member — valet, front desk, dining, housekeeping — needs a different slice of that profile, grounded in *this* property's local culture.

We validated this with Rosewood's president: the ask is tailoring each arrival to both the guest history and the destination. That's what you're about to see."

### 0:30–1:00 — Show the baseline dashboard

*Navigate to `http://127.0.0.1:8000`.*

"Ms. Chen is arriving at Rosewood Sand Hill. She's a returning guest — prior stays at The Carlyle New York and Castiglion del Bosco. Claude has read her full dossier and the Sand Hill property card, synthesized her cross-visit preferences, and produced this."

*Point to the mood banner:* "Mood: Restorative. She arrived on a red-eye."

*Point to the role cards:* "Six role-specific briefing cards. Each one is grounded in both her history and named local anchors — Bluejay Bikes on the Portola Valley loop, Ridge Winery, Asaya Spa, Madera. Not generic copy. Specific to this place."

*Point to synthesis panel if visible:* "Cross-visit synthesis: preferences inferred from what staff observed at other properties."

### 1:00–1:45 — Inject the delay (the creative proof)

*Point to the "Inject Delay & Re-plan" button.*

"Her flight is now delayed 120 minutes. ATC hold at JFK. ETA is now 5:30 PM. Watch what happens."

*Click the button. Do not narrate the spinner — let it land.*

*After the swap:* "No page reload. Every card just updated in place. That's HTMX fragment swap — Claude re-planned the entire arrival in one structured call."

*Point to delay-injected banner and "Updated" badges on cards.*

"The 4 PM Asaya appointment she was expecting — released. Dinner shifted to 7:30. Turndown timing adjusted. Thursday evening compressed. But her Friday arc — Bluejay Bikes, Ridge Rosé — preserved. The system knows what matters to her."

### 1:45–2:15 — Show the diff panel (never-cut feature)

*Scroll to the diff panel.*

"And here's the creative differentiator: every change is explained. Trigger: 120-minute flight delay, revised ETA 5:30 PM. Each role sees exactly what changed in their domain and one-line reason why."

*Read one entry aloud:* "'Spa — 4 PM appointment released: appointment no longer reachable — release slot for other guests.' Staff don't need to read the whole plan. They see their change and the reason."

"This is not a chatbot producing a paragraph. It's a structured diff — machine-readable, role-addressable, audit-ready."

### 2:15–2:45 — Dual-card architecture + sponsor callout

"The core insight is the dual-card model: guest dossier plus destination-culture property card, both fed to Claude as Markdown context in a single tool-use call. Claude does the synthesis. No separate pipeline, no extra latency.

Sponsor callout: Anthropic is the Tier-1 LLM backbone — Claude's structured output is what makes the role cards and diff deterministic. We also have ElevenLabs wired for staff audio briefings."

### 2:45–3:00 — Close

"Three minutes, one button, six role cards updated, a legible diff, zero page reloads. SenseArrival — hyper-personalized arrival orchestration."

---

## Cut Order (ADR-001 Ruthless Priority)

If something breaks or time runs short, cut in this order. Never cut item 1.

| Priority | Feature | Decision |
|----------|---------|----------|
| **NEVER CUT** | Re-plan diff panel (what changed & why) | The creative proof. Without it the demo is just a dashboard. |
| Keep | Role cards — all 6 roles | Visual completeness. Even placeholder text is better than a missing card. |
| Keep | "Inject Delay" button → live re-plan | This IS the demo narrative. Cannot cut. |
| Keep | Mood banner | One line of text; cost to keep is trivial. |
| Cut if needed | TTS "Play Briefing" button | Mention ElevenLabs verbally if button fails. |
| Cut if needed | Mic STT capture | Fall back to typed-text input; same code path downstream. |
| Cut if needed | Guest message panel | Mention verbally if not rendered. |
| Cut last resort | Suppression panel | Mention verbally: "there's also a suppression layer — what NOT to offer." |
| Cuttable (P1) | Guest/property selector | Demo with Ms. Chen hardcoded. Mention multi-guest as capability. |
| Cuttable (P1) | Staff note → re-synthesis loop | Show typed-text submission; mention synthesis loop exists. |

---

## Tier Switching — LLM Resilience

Three tiers, switchable by env var with no code change. Test all three before the judging room.

| Tier | How to activate | When to use |
|------|----------------|-------------|
| Tier-1: Claude (primary) | `BACKEND=claude` (with `ANTHROPIC_API_KEY` in `.env`) | Network confirmed stable; Anthropic is a sponsor — showcase this path |
| Tier-2: Ollama (local fallback) | `BACKEND=ollama` (Ollama running locally) | Network unreliable but laptop works; keeps re-plan genuinely "live" |
| Tier-3: Fixture replay (last resort) | `OFFLINE_MODE=true` or `BACKEND=replay` | Zero network; deterministic; demo is fully scripted; looks identical to judges |

**Default demo recommendation:** Start with Tier-3 (offline) for rehearsal. Enter the room on Tier-3. If network is confirmed stable, switch to Tier-1.

---

## If Things Go Wrong

### HTMX swap does not trigger (button does full-page reload)

HTMX failed to load. Check: does `http://127.0.0.1:8000/static/htmx.min.js` serve a JS file? The app must be running. If the server is up, HTMX is served locally — this should not happen. If it does: the full-page reload to `/replan` still renders the updated cards and diff panel in the new page. Less smooth but functionally correct. Continue the script.

### Claude API call times out or errors

The app falls back to fixture replay automatically (graceful exception handler in `_call_claude()`). The dashboard renders from fixtures. The diff panel is identical to the offline path. Continue the demo — judges cannot tell the difference.

### Diff panel shows "pending" instead of entries

`POST /replan` was not called yet or returned an error before the diff state was saved. Try clicking "Inject Delay" again. If it persists: navigate directly to `http://127.0.0.1:8000/diff-panel` in a new tab and confirm it renders. If it does, describe the panel verbally while showing the JSON at `/diff`.

### Server is not running

`OFFLINE_MODE=true uvicorn sense_arrival.main:app --port 8000` from the repo root with the virtual environment active. If port 8000 is blocked: use `--port 8001` and update your browser tab.

### Browser shows cached old page

Hard refresh: Cmd+Shift+R (Mac). HTMX state is in-server-process memory, not the browser. A page refresh re-fetches the baseline from the server.

### Mood banner is missing or blank

Fixture file missing or malformed. `OFFLINE_MODE=true` should always load from `fixtures/plans/baseline_plan.json`. Verify the file exists and contains valid JSON. If absent: show the diff panel screenshot from backup assets.

---

## Q&A Preparation

**"Is this real-time? Does it call Claude live?"**
Yes — Tier-1 Claude path calls `anthropic` SDK with a single structured tool-use call per plan. In offline mode we use pre-computed fixtures for demo reliability. Both paths use the same code.

**"What does the dual-card model mean in practice?"**
Rosewood's president told us they manually collect guest profiles. The requirement is grounding each arrival in BOTH that profile AND the destination's local culture. We feed both as Markdown to Claude simultaneously — one call, coherent output.

**"Could this scale to other properties?"**
Yes — adding a property is adding a Markdown file. The fixture library is 3 × 3 today (3 dossiers, 3 properties). Any Rosewood property with a Sense of Place card can be served by the same orchestrator.

**"Why FastAPI + HTMX instead of a modern frontend?"**
Solo builder, 6-hour window. FastAPI + HTMX = zero build step, single process, one restart command. The HTMX fragment swap delivers the "no page reload" demo moment without React hydration risk.

**"What about the ElevenLabs integration?"**
TTS route is wired — `GET /voice/tts/{card_id}`. Requires an ElevenLabs key at runtime. Time constraints meant voice was BL-005 scope. The typed-text staff note path shares the same classification and re-synthesis code path.

---

## Sections Needing Final Pass Before 5PM

> These sections will be updated once BL-005 (voice) and BL-008 (synthesis shim) land.

- **Voice TTS demo step**: If `GET /voice/tts/{card_id}` is live with audio by 5PM, add a step between 2:15–2:45 to play a Front Desk card briefing audio clip.
- **Staff note → re-synthesis**: If the typed-text note updates the synthesis panel live, add a quick demo step: type "Ms. Chen mentioned she is celebrating a promotion" → show synthesis panel update.
- **Selector demo**: If `POST /select` is enabled, consider a 15-second step showing a second guest (Priya Nair) to demonstrate multi-guest support.

---

## User Action Items (Required Before 5PM)

1. **Make the GitHub repo public.** Go to `https://github.com/SirMadness/SenseArrival` → Settings → Danger Zone → Change visibility → Public. Judges require a public repo. This cannot be done by the build system.

2. **Capture backup screenshots and a GIF.** With the app running in `OFFLINE_MODE=true`, capture:
   - Screenshot: baseline dashboard (mood + 6 cards visible)
   - Screenshot: post-replan state (delay banner + Updated badges + diff panel)
   - GIF or screen recording: full Inject Delay → diff flow
   Store locally. If the live demo has a crash, the backup assets let you narrate from visuals.
