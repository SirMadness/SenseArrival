# SenseArrival — First Five Minutes

**Problem Statement #1: Hyper-Personalized Arrival Orchestration**
Hospitality 2030 Hackathon @ Rosewood Sand Hill — 2026-05-16

---

## What This Is

SenseArrival is an **arrival choreography engine** for luxury hotels. It is not a chatbot. Given a guest dossier and a property context, it produces a structured arrival plan: a mood classification, six role-specific staff briefing cards (valet, front desk, dining, housekeeping, concierge, MOD), a suppression panel listing what *not* to offer, and a "what changed & why" diff panel when conditions change mid-arrival.

The headline demo narrative is **Delay-to-Delight**: Ms. Chen's flight is delayed 120 minutes. One button re-plans all six role cards in place — no page reload — and the diff panel shows exactly what changed and why, room-legible from across a judging table.

---

## The Answer to Problem Statement #1: The Dual-Card Model

Rosewood **manually collects** each guest's data into a profile across visits. The product requirement — validated directly in conversation with **Radha Arora, President of Rosewood Hotels & Resorts** — is to tailor each arrival to *both* the guest profile *and* the local culture and activities of where that specific hotel is located.

SenseArrival operationalizes this as a **dual-card model**:

- **Guest Dossier** — the portable cross-visit profile: nationality, dietary needs, access needs, style, and staff observations accumulated across prior stays at other Rosewood properties.
- **Property Card (Sense of Place)** — the destination-culture card for the arrival property: named local experiences, landmarks, food scene, outdoor anchors (e.g., Bluejay Bikes on the Portola Valley loop, Ridge Winery rosé tasting, Asaya Spa, Madera). Not generic on-property copy — the place itself.

Both cards are fed as raw Markdown context into a single Claude structured tool-use call. The output is grounded in both simultaneously: the guest's history *and* the destination. Provenance cards from prior-stay properties (e.g., The Carlyle New York, Castiglion del Bosco) feed cross-visit synthesis, surfacing inferred preferences that span properties.

This dual-card architecture is the direct technical response to PS#1. It is not a chatbot, not basic RAG, and not a generic recommendation engine.

---

## Built Today (2026-05-16) — Honest Scope

### What was built during the event window

| Component | Status | Notes |
|-----------|--------|-------|
| Full Python package (`sense_arrival/`) | Complete | FastAPI + Jinja2/HTMX, single-process |
| Pydantic data models | Complete | GuestDossier, PropertyCard, GuestSynthesis, ArrivalPlan, RoleCard, PlanDiff, PlanDiffEntry |
| 3-tier pluggable LLM backend | Complete | Tier-1 Claude (primary), Tier-2 Ollama (local fallback), Tier-3 fixture-replay (zero-network) |
| Markdown fixture library | Complete | 3 guest dossiers (Ms. Chen, Priya Nair, James Okafor); 3 property cards (Rosewood Sand Hill, The Carlyle New York, Castiglion del Bosco) |
| Offline fixture plans | Complete | Hand-authored `baseline_plan.json` / `replanned_plan.json` with clean 12-unchanged / 8-changed diff story |
| Baseline dashboard render | Complete | Mood banner + 6 role cards + synthesis panel + suppression panel + guest message |
| Inject Delay → live HTMX re-plan | Complete | `POST /replan` → HTMX `#dashboard-root innerHTML` swap, no full-page reload |
| "What Changed & Why" diff panel | Complete | 16 structured entries, orange trigger banner, +NEW/-OUT badges, one-line reason per change; room-legible |
| HTMX vendored locally | Complete | `htmx.min.js` committed to repo — zero CDN dependency in the judging room |
| Typed-text staff note fallback | Complete | Same code path as mic STT; `POST /voice/transcribe` endpoint functional |
| Tier-1 Claude tool-use orchestrator | Complete | `_call_claude()` with `tool_choice`, graceful fallback on any exception |
| Guest/property selector | Stubbed | `GET /select` / `POST /select` routes exist; disabled in OFFLINE_MODE (returns 503) |
| Voice TTS (ElevenLabs) | Stubbed | `GET /voice/tts/{card_id}` route present; live path raises NotImplementedError in BL-001 (BL-005 scope) |
| Browser mic STT capture | Stubbed | `app.js` mic guard present; ElevenLabs Scribe server path not fully wired (BL-005 scope) |
| Portfolio cross-visit synthesis UI | Partial | Synthesis panel renders in dashboard; staff-note → re-synthesis HTMX loop is BL-008 scope |
| Suppression panel UI | Partial | Data present in plan; full interactive panel is BL-006 scope |
| Dashboard polish / interactive selector | In progress | BL-006/BL-007/BL-009, P1/cuttable |

### What is synthetic / fixture data

- Guest dossiers and property cards are **hand-authored Markdown** — synthetic, rights-cleared, no real guest PII.
- `baseline_plan.json` and `replanned_plan.json` are hand-authored offline fixtures matching the Ms. Chen / Rosewood Sand Hill demo path. In live mode, these are replaced by real Claude output.
- `delay_event.json` is a synthetic 120-minute JFK ATC hold event.
- Cached TTS audio (`static/audio/briefing_cached.mp3`) is a placeholder; real TTS requires ElevenLabs key at runtime.

### Explicitly out of scope

- No live flight or weather APIs.
- No Streamlit (banned by event rules).
- No real guest PII or production Rosewood data.
- No persistent database — all state is in-memory or fixture files.
- No live ElevenLabs STT via browser mic (typed-text fallback is the demo path).
- No multi-user / multi-worker deployment.

---

## Current Status

**Spine: COMPLETE and offline-demo-safe.**

The never-cut sequence is fully working in `OFFLINE_MODE`:

```
GET /  (baseline render)
→ POST /replan  (one-click delay inject → HTMX swap, no reload)
→ GET /diff  (diff panel: 16 structured entries, trigger + reason)
```

All three steps work deterministically with zero network. HTMX is vendored locally.

**Voice / TTS / synthesis polish: IN PROGRESS** — BL-005 (voice TTS + staff note), BL-008 (synthesis UI shim), BL-006/009 (polish) are in progress or cuttable before 5PM.

**Claude live path:** Tier-1 tool-use call is implemented and falls back gracefully to fixtures on any error. Live output quality requires `ANTHROPIC_API_KEY` at runtime.

---

## Quickstart

### Prerequisites

- Python 3.11+
- (Optional) Anthropic API key for live Claude path
- (Optional) ElevenLabs API key for live TTS
- (Optional) Ollama running locally for Tier-2 fallback

### Setup

```bash
git clone https://github.com/SirMadness/SenseArrival.git
cd SenseArrival
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add ANTHROPIC_API_KEY and/or ELEVENLABS_API_KEY if available
```

### Offline-safe demo (zero network required)

```bash
OFFLINE_MODE=true uvicorn sense_arrival.main:app --reload
# Open http://127.0.0.1:8000
```

Click "Inject Delay & Re-plan" to run the full Delay-to-Delight narrative. The diff panel populates immediately from fixtures.

### Live Claude path (requires API key)

```bash
# In .env: ANTHROPIC_API_KEY=sk-ant-...
BACKEND=claude uvicorn sense_arrival.main:app --reload
```

Falls back to fixtures automatically if the API call fails.

### Ollama local fallback (Tier-2)

```bash
# Ollama must be running locally with a compatible model
BACKEND=ollama uvicorn sense_arrival.main:app --reload
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OFFLINE_MODE` | `true` = fixture-replay, zero network | `false` |
| `BACKEND` | `replay` / `claude` / `ollama` | `claude` |
| `ANTHROPIC_API_KEY` | Anthropic API key for Tier-1 path | (none) |
| `ELEVENLABS_API_KEY` | ElevenLabs key for TTS/STT | (none) |
| `OLLAMA_BASE_URL` | Ollama base URL for Tier-2 path | `http://localhost:11434` |

`OFFLINE_MODE=true` is an alias for `BACKEND=replay`.

---

## Stack

Python 3.11 + FastAPI + Jinja2 + HTMX (vendored) + Pydantic v2 + Anthropic SDK + ElevenLabs Python SDK. Single process, no frontend build step, no Node runtime. Full rationale in `_proj/deliverables/02-architecture/adr/ADR-001-stack-selection.md`.

---

## Project Structure

```
sense_arrival/
  main.py                    # FastAPI app, all routes
  orchestrator.py            # Claude tool-use loop: plan(), replan(), diff()
  models.py                  # Pydantic models
  voice.py                   # ElevenLabs TTS + STT stubs
  config.py                  # Settings, Backend enum, 3-tier resolver
  fixture_loader.py          # Markdown + JSON fixture loading, scope guard
  fixtures/
    dossiers/                # Guest Markdown dossiers (ms-chen, priya-nair, james-okafor)
    properties/              # Property Markdown cards (sand-hill, carlyle, castiglion)
    plans/                   # Offline-replay JSON fixtures
  templates/                 # Jinja2 HTML templates
  static/                    # CSS, JS, vendored htmx.min.js
requirements.txt
.env.example
_proj/deliverables/02-architecture/adr/  # ADR-001 (stack) + ADR-002 (guest graph)
```

---

## Sponsors

Built with Anthropic Claude (Tier-1 orchestration) and ElevenLabs (TTS/STT). Rosewood Hotels & Resorts provided the problem statement.

---

## Hackathon

Hospitality 2030 @ Rosewood Sand Hill — 2026-05-16. Solo build, ~6-hour window, hard 5PM submission. Problem Statement #1: Hyper-Personalized Arrival Orchestration.
