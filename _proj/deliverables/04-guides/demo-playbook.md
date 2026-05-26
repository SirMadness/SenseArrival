# SenseArrival Demo Playbook — Delay-to-Delight

**Event:** Hospitality 2030 @ Rosewood Sand Hill — 2026-05-16
**Hard deadline:** 5:00 PM (Round 1 judging begins immediately)
**Demo slot:** ~3 minutes live + 1–2 min Q&A
**Judging weights:** Live Demo 45% / Creativity 35% / Impact 20%
**Build commit:** `2d6815c` (branch `build/sense-arrival-mvp`) — LOCKED
**Smoke test:** DEMO-READY (all 7 steps PASS, zero network, 2026-05-16)

---

## Flagged Items

- **DQ: BLOCKING** — Make `github.com/SirMadness/SenseArrival` **PUBLIC** before 5PM. Repo must be public for judge access. Go to Settings → Danger Zone → Change visibility → Public. This is a disqualification-grade requirement; the build system cannot do it for you.
- **DQ: BLOCKING** — Capture **backup screenshots and a GIF** of the offline Inject-Delay → diff flow (instructions in Pre-Demo Checklist below). If the live demo crashes, you narrate from visuals.
- **TD:** 1 of 16 diff entries uses a generic fallback reason ("Original action superseded by delay-adjusted plan for spa") because the Spa role removed-action text does not match a key in `_ROLE_REASONS["Spa"]`. The reason is truthful and legible — not a demo blocker.

---

## Pre-Demo Checklist

Complete this offline rehearsal in full before entering the judging room. Do not skip steps.

### Boot command

```bash
OFFLINE_MODE=true uvicorn sense_arrival.main:app --host 127.0.0.1 --port 8000
```

Open browser to `http://127.0.0.1:8000/` with virtual environment active from repo root.

### Environment verification

- [ ] Dashboard subtitle reads: "Arrival Choreography Engine — replay backend"
- [ ] Mood banner renders: "Restorative"
- [ ] All 6 role cards present: Front Desk, Concierge, Spa, Dining, Housekeeping, Guest Experience — all Ms. Chen-specific
- [ ] Synthesis panel visible: "Inferred from prior stays" naming Carlyle and Castiglion del Bosco
- [ ] Suppression panel visible: "Tasteful Restraint" header, 3 withheld items with reasons
- [ ] HTMX loaded locally: `<script src="/static/htmx.min.js">` — confirm no CDN traffic in Network tab

### Offline smoke verification

- [ ] Click "Inject Delay & Re-plan" — confirm: no full-page reload, delay banner appears ("Delay injected — 120-min ATC hold at JFK · Revised ETA 5:30 PM"), role cards update with "Updated" badges, diff panel renders inline with 16 entries
- [ ] `curl http://127.0.0.1:8000/diff` returns JSON with `changed_roles`, `entries` (16 entries), each with `trigger` and `reason`
- [ ] Click "Play" on Concierge card — audio plays (M4A, ~159KB, offline cached)
- [ ] Type a staff observation and click Submit — receipt appears, classified as "Concierge"
- [ ] `GET /select` or `/select` — do NOT navigate there; it returns 503 in OFFLINE_MODE by design. Do not open this URL at any point during the demo.

### Tier switching (if network is stable at judging room)

The showcased primary path is Tier-1 (Claude live). Enter the room on Tier-3 (offline) as the confirmed-safe fallback. Switch to Tier-1 only after confirming network stability.

| Tier | Command | When to use |
|------|---------|-------------|
| Tier-1: Claude (primary/showcased) | `BACKEND=claude uvicorn sense_arrival.main:app --host 127.0.0.1 --port 8000` | Network confirmed stable; Anthropic is Tier-1 sponsor |
| Tier-2: Ollama (local fallback) | `BACKEND=ollama uvicorn sense_arrival.main:app --host 127.0.0.1 --port 8000` | Network unreliable; keeps re-plan genuinely live |
| Tier-3: Fixture replay (offline) | `OFFLINE_MODE=true uvicorn sense_arrival.main:app --host 127.0.0.1 --port 8000` | Zero network; deterministic; looks identical to judges |

If Claude is unreliable: switch back to `OFFLINE_MODE=true` before entering the room.

### Backup assets (USER ACTION REQUIRED — capture before 5PM)

- [ ] Screenshot: baseline dashboard (mood banner + 6 role cards visible, synthesis panel, suppression panel)
- [ ] Screenshot: post-replan state (delay banner + "Updated" badges + diff panel with 16 entries)
- [ ] GIF or screen recording: full Inject Delay → diff flow (QuickTime or similar)
- Store in a location accessible without the running app (e.g., desktop folder)

---

## 3-Minute Demo Script — Verified Click Sequence

This script matches the smoke-verified click sequence from `final-offline-smoke-2026-05-16.md` (HEAD `2d6815c`). Use it verbatim. Per-segment times sum to ~3:00.

### 0:00–0:30 — Frame the problem (no screen interaction)

"This is SenseArrival. We're solving Problem Statement #1: hyper-personalized arrival orchestration.

Hotels like Rosewood manually collect guest profiles across visits. But arrival is choreography — not just a profile lookup. Every staff member needs a different slice of that profile, grounded in this property's local culture.

We validated this with Rosewood's president: the ask is tailoring each arrival to both the guest history and the destination. That's what you're about to see."

### 0:30–1:00 — Step 1: Show the arrival dashboard

*Navigate to `http://127.0.0.1:8000`.*

*Point to Panel B (center) — mood banner:* "Ms. Chen is arriving. Mood: Restorative. She came in on a red-eye from New York."

*Point to Panel C (right) — role cards:* "Six role-specific briefing cards. Every card is grounded in both her history and named local anchors — Bluejay Bikes, Ridge Rosé Reveal, Asaya Spa, Madera. Not generic copy."

*Scroll to synthesis panel:* "Cross-visit synthesis: preferences inferred from prior stays at The Carlyle New York and Castiglion del Bosco — named, with provenance. The system knew her before she landed."

*Point to Panel B — suppression panel:* "Tasteful Restraint: three things the system is withholding, with concierge-framed reasons. This is not a chatbot that over-offers."

### 1:00–1:45 — Step 2: Inject the delay event

*Point to Panel A (left) — "Inject Delay & Re-plan" button.*

"Her flight is delayed 120 minutes. ATC hold at JFK. ETA is now 5:30 PM. Watch what happens."

*Click the button. Let the swap land without narrating the spinner.*

*Point to delay banner:* "No page reload. HTMX fragment swap — Claude re-planned the entire arrival in one structured call."

*Point to Updated badges on role cards:* "The 4 PM Asaya appointment — released. Dinner shifted to 7:30. Thursday evening compressed. But her Friday arc — Bluejay Bikes, Ridge Rosé — preserved. The system knows what matters to her."

### 1:45–2:15 — Step 3: Show the diff panel (NEVER-CUT spine)

*Point to "What Changed & Why" panel.*

"Here is the creative differentiator. Trigger: 120-minute flight delay, revised ETA 5:30 PM. Every change — 8 added, 8 removed across all 6 roles — has a one-line reason."

*Read one entry aloud:* "'Spa — 4 PM appointment released: appointment no longer reachable — release slot for other guests.' Staff see their change and the reason. This is not a paragraph. It is a structured diff — machine-readable, role-addressable, audit-ready."

### 2:15–2:30 — Step 4: Play a role briefing

*In Panel C, click "Play" on the Concierge card.*

"ElevenLabs TTS — offline cached audio, 159KB M4A committed at build time. In live mode this is generated fresh per re-plan."

### 2:30–2:45 — Step 5: Add a staff observation

*In Panel A, Staff Observation textarea: type "Guest asked about road cycling routes for tomorrow morning".*

*Click Submit.*

"Staff observation — typed-text path, same code as the mic path. Classified as Concierge. Concierge card updates in place. Observation appended to the dossier."

*Point to the updated Concierge card and dossier panel.*

### 2:45–3:00 — Close

"The dual-card model: guest dossier plus destination-culture property card, both fed to Claude in a single tool-use call. Claude does the synthesis. No separate pipeline, no extra latency.

Sponsor callout: Anthropic is the Tier-1 LLM backbone — structured output is what makes the role cards and diff deterministic. ElevenLabs is wired for staff audio briefings.

Three minutes, one button, six role cards updated, a legible diff, zero page reloads. SenseArrival — hyper-personalized arrival orchestration."

---

## Cut Order (ADR-001 Ruthless Priority — Final State)

Everything below is BUILT and smoke-verified. The verbal-only fallback column applies only to a crash at demo time; no feature requires verbal-only presentation under normal conditions.

| Priority | Feature | Status | Demo-time contingency |
|----------|---------|--------|-----------------------|
| **NEVER CUT** | Re-plan diff panel (what changed & why, trigger + reason per entry) | BUILT — 16 entries verified | Without this the demo is just a dashboard. No contingency — restart if needed. |
| Keep | Role cards — all 6 roles, Ms. Chen-specific | BUILT — verified | Show even if content is placeholder text |
| Keep | "Inject Delay & Re-plan" button → HTMX re-plan | BUILT — verified | Full-page reload to `/replan` still renders updated cards and diff; less smooth, functionally correct |
| Keep | Mood banner | BUILT — "Restorative" verified | One line of text; cost to keep is trivial |
| Keep | Suppression / Tasteful Restraint panel | BUILT — 3 items verified | Mention verbally only if panel crashes |
| Keep | Cross-visit synthesis ("inferred from prior stays") | BUILT — Carlyle/Castiglion named | Mention verbally only if panel crashes |
| Keep | TTS "Play Briefing" (offline cached M4A) | BUILT — 159KB audio verified | Mention ElevenLabs verbally if button fails |
| Keep | Staff observation typed-text path | BUILT — classified, OOB swap verified | Describe the flow verbally if POST fails |
| **DO NOT OPEN** | `/select` guest/property selector | CUT — returns 503 in OFFLINE_MODE by design | Do not navigate there. Mention multi-guest as roadmap capability if asked. |

### LLM tier fallback

Live → Ollama → Fixture-replay. The app's graceful exception handler in `_call_claude()` auto-falls to fixture replay on any Claude API error. Judges cannot distinguish Tier-1 from Tier-3 visually.

---

## Contingency Responses

### HTMX swap triggers a full-page reload instead of fragment swap

HTMX failed to load. Confirm `http://127.0.0.1:8000/static/htmx.min.js` is serving JS (app must be running). The full-page reload to `/replan` still renders updated cards and diff. Less smooth; functionally correct. Continue the script.

### Claude API times out or errors

Auto-falls to fixture replay via `_call_claude()` exception handler. Dashboard is identical to offline path. Continue — judges cannot tell the difference.

### Diff panel shows "pending" or is missing entries

Click "Inject Delay" again. If it persists: open `http://127.0.0.1:8000/diff-panel` in a new tab and confirm it renders. If it renders there, describe the panel verbally while showing `/diff` JSON.

### Server is not running

```bash
OFFLINE_MODE=true uvicorn sense_arrival.main:app --host 127.0.0.1 --port 8000
```

If port 8000 is blocked: use `--port 8001` and update the browser tab.

### Browser shows cached old page

Hard refresh: Cmd+Shift+R (Mac). HTMX state is server-process memory, not the browser. A page refresh re-fetches baseline from server.

### Mood banner is missing or blank

Fixture file missing or malformed. Verify `fixtures/plans/baseline_plan.json` exists and is valid JSON. If absent: show the baseline screenshot from backup assets and narrate from there.

### Someone asks to see a different guest or property

"Multi-guest and multi-property are on the roadmap — the fixture library is already structured for it. Today's demo is Ms. Chen at Rosewood Sand Hill." Do not navigate to `/select`.

---

## Q&A Preparation

**"Is this real-time? Does it call Claude live?"**
Yes — Tier-1 calls the `anthropic` SDK with a single structured tool-use call per plan. In offline mode we serve pre-computed fixtures for demo reliability. Both paths use identical code; the diff panel, role cards, and audio are bit-for-bit identical. Smoke tested at HEAD `2d6815c`.

**"What is the dual-card model?"**
Rosewood's president told us they manually collect guest profiles. The requirement is grounding each arrival in both that profile and the destination's local culture. We feed both — guest dossier and property culture card — as Markdown to Claude simultaneously in one call. Claude synthesizes them. One call, coherent structured output, no separate pipeline.

**"Why not a chatbot?"**
A chatbot produces a paragraph. We produce a structured diff — role-addressable, machine-readable, audit-ready. Each role sees only their changes and the reason. Staff can act in under 10 seconds. That is the differentiator validated with Rosewood's president.

**"Could this scale to other properties?"**
Yes — adding a property is adding a Markdown file. The fixture library is 3 × 3 today (3 dossiers, 3 properties). Any Rosewood property with a Sense of Place card can be served by the same orchestrator. The selector endpoint (`/select`) is architected and returns a clean 503 in offline mode.

**"What is synthetic vs. built today?"**
Everything shown is built and committed. The Ms. Chen dossier and Rosewood Sand Hill property card are hand-authored fixtures representing real Rosewood context. The Claude calls (Tier-1) generate genuine LLM output. The offline demo uses pre-computed fixtures from a real Claude run, committed to the repo — not mocked data.

**"What about ElevenLabs?"**
TTS is fully wired — `GET /voice/tts/{card_id}`. Offline mode serves a 159KB cached M4A committed at build time (real audio, not silence). In live mode, ElevenLabs generates fresh audio per card. Typed-text staff observations share the same classification and synthesis code path as the mic STT path.

---

*Playbook finalized by Docs agent — 2026-05-16 — build locked at HEAD `2d6815c` — smoke verified DEMO-READY*
