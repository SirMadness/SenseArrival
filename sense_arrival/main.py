"""
main.py — SenseArrival FastAPI application.

Single-process server. All routes defined here.
Start with: uvicorn sense_arrival.main:app --reload

Routes (ADR-001 + ADR-002 Delta 4):
  GET  /               — Dashboard (placeholder until BL-002)
  POST /replan         — Inject delay event → re-plan
  GET  /diff           — Return PlanDiff panel fragment
  POST /voice/transcribe — Browser audio/text → STT/text → classify → update role cards
  GET  /voice/tts/{card_id} — ElevenLabs TTS → MP3 stream of current briefing
  GET  /offline        — Offline-replay mode info
  GET  /select         — Guest/property selector form
  POST /select         — Accept selection → run plan → dashboard
"""
from __future__ import annotations

import json
import logging
import re

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from sense_arrival.config import Backend, settings
from sense_arrival.fixture_loader import (
    build_guest_dossier,
    build_property_card,
    list_dossier_slugs,
    list_property_slugs,
    load_delay_event,
    load_dossier,
    load_offline_response,
    load_property_card,
    load_provenance_cards,
)
from sense_arrival import orchestrator, voice
from sense_arrival.models import OrchestratorResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="SenseArrival", version="0.1.0")

# Static files and templates
_BASE = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(_BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(_BASE / "templates"))


def _tmpl(request: Request, context: dict) -> HTMLResponse:
    """
    Compat wrapper for Starlette 1.0+ TemplateResponse API change.
    Starlette 1.0 moves `request` to the first positional arg.
    """
    return templates.TemplateResponse(request, "dashboard.html", context)


# ---------------------------------------------------------------------------
# App state initialisation
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup() -> None:
    # In-memory staff observations (TREQ-023 shim) — reset on each restart
    app.state.session_observations: list[str] = []
    # Active backend (can be toggled per-request via UI in BL-002)
    app.state.backend: Backend = settings.default_backend
    # Cache the canonical offline response at startup for zero-latency replay
    app.state.cached_baseline: OrchestratorResponse | None = None
    app.state.cached_replanned: OrchestratorResponse | None = None
    # Live-mode plan storage: populated by index() and replan() for GET /diff
    app.state.live_baseline: OrchestratorResponse | None = None
    app.state.live_replanned: OrchestratorResponse | None = None

    if app.state.backend == Backend.REPLAY:
        app.state.cached_baseline = load_offline_response(replanned=False)
        app.state.cached_replanned = load_offline_response(replanned=True)

    logger.info(
        "SenseArrival started | backend=%s | offline=%s",
        app.state.backend,
        app.state.backend == Backend.REPLAY,
    )


# ---------------------------------------------------------------------------
# GET /  — Dashboard
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """
    Render the arrival dashboard for the canonical guest (Ms. Chen at Sand Hill).

    BL-001: returns a minimal placeholder confirming the app boots and routes
    work. BL-002 replaces this with the full Jinja2 dashboard template.
    """
    backend: Backend = app.state.backend

    if backend == Backend.REPLAY:
        response = app.state.cached_baseline or load_offline_response(replanned=False)
    else:
        # Live mode: load canonical guest and run plan()
        dossier_md = load_dossier("ms-chen")
        arrival_md = load_property_card("rosewood-sand-hill")
        provenance_mds = load_provenance_cards("ms-chen", exclude="rosewood-sand-hill")
        try:
            response = await orchestrator.plan(
                dossier_md, arrival_md, provenance_mds,
                app.state.session_observations,
                backend=backend,
            )
            # Store for GET /diff live-mode support
            app.state.live_baseline = response
        except NotImplementedError as exc:
            # BL-002 not yet implemented — degrade gracefully
            response = None
            logger.warning("plan() not implemented: %s", exc)

    return _tmpl(request, {
        "response": response,
        "backend": backend.value,
        "offline": backend == Backend.REPLAY,
        "dossier_slugs": list_dossier_slugs(),
        "property_slugs": list_property_slugs(),
        "plan_diff": None,
        "replanned": False,
    })


# ---------------------------------------------------------------------------
# POST /replan  — Inject delay event and re-plan
# ---------------------------------------------------------------------------

@app.post("/replan", response_class=HTMLResponse)
async def replan(request: Request) -> HTMLResponse:
    """
    Inject the delay event fixture and generate a re-planned arrival.
    Returns the dashboard fragment for HTMX swap, including the diff panel.
    """
    backend: Backend = app.state.backend
    delay_event = load_delay_event()

    if backend == Backend.REPLAY:
        baseline_resp = app.state.cached_baseline or load_offline_response(replanned=False)
        response = app.state.cached_replanned or load_offline_response(replanned=True)
    else:
        dossier_md = load_dossier("ms-chen")
        arrival_md = load_property_card("rosewood-sand-hill")
        provenance_mds = load_provenance_cards("ms-chen", exclude="rosewood-sand-hill")
        # Ensure we have a baseline to diff against
        baseline_resp = app.state.live_baseline
        if baseline_resp is None:
            # Baseline not yet loaded; load it now for the diff
            try:
                baseline_resp = await orchestrator.plan(
                    dossier_md, arrival_md, provenance_mds,
                    app.state.session_observations,
                    backend=backend,
                )
                app.state.live_baseline = baseline_resp
            except Exception as exc:
                logger.warning("baseline plan() failed during replan: %s", exc)
                baseline_resp = load_offline_response(replanned=False)

        try:
            response = await orchestrator.replan(
                dossier_md, arrival_md, provenance_mds,
                delay_event,
                app.state.session_observations,
                backend=backend,
            )
            # Store for GET /diff live-mode support
            app.state.live_replanned = response
        except NotImplementedError as exc:
            logger.warning("replan() not implemented: %s", exc)
            response = None
            baseline_resp = None

    # Compute the diff to include in the replan response
    plan_diff = None
    if response is not None and baseline_resp is not None:
        try:
            plan_diff = orchestrator.diff(
                baseline_resp.arrival_plan,
                response.arrival_plan,
            )
        except Exception as exc:
            logger.warning("diff() failed in replan handler: %s", exc)

    return _tmpl(request, {
        "response": response,
        "backend": backend.value,
        "offline": backend == Backend.REPLAY,
        "dossier_slugs": list_dossier_slugs(),
        "property_slugs": list_property_slugs(),
        "plan_diff": plan_diff,
        "replanned": True,
    })


# ---------------------------------------------------------------------------
# GET /diff  — PlanDiff JSON (spine endpoint, unchanged contract)
# ---------------------------------------------------------------------------

@app.get("/diff", response_class=JSONResponse)
async def get_diff(request: Request) -> JSONResponse:
    """
    Compute and return the PlanDiff between baseline and re-planned ArrivalPlan.
    This is the never-cut spine (TREQ-006). Synthesis does not participate.
    """
    backend: Backend = app.state.backend

    if backend == Backend.REPLAY:
        baseline_resp = app.state.cached_baseline or load_offline_response(replanned=False)
        replanned_resp = app.state.cached_replanned or load_offline_response(replanned=True)
    else:
        # Live mode: use stored plan responses (populated by GET / and POST /replan)
        baseline_resp = app.state.live_baseline
        replanned_resp = app.state.live_replanned
        if baseline_resp is None or replanned_resp is None:
            return JSONResponse(
                {"detail": "Diff not available — load the dashboard and run /replan first."},
                status_code=202,
            )

    try:
        plan_diff = orchestrator.diff(
            baseline_resp.arrival_plan,
            replanned_resp.arrival_plan,
        )
    except Exception as exc:
        return JSONResponse(
            {"error": "Diff computation failed", "detail": str(exc)},
            status_code=500,
        )
    return JSONResponse(plan_diff.model_dump())


# ---------------------------------------------------------------------------
# GET /diff-panel  — PlanDiff HTML fragment (HTMX target, TREQ-006 / US-003)
# ---------------------------------------------------------------------------

@app.get("/diff-panel", response_class=HTMLResponse)
async def get_diff_panel(request: Request) -> HTMLResponse:
    """
    Return the rendered diff panel HTML fragment for HTMX swap.
    Synthesis does not participate — arrival_plan only (TREQ-006 spine intact).
    """
    backend: Backend = app.state.backend

    if backend == Backend.REPLAY:
        baseline_resp = app.state.cached_baseline or load_offline_response(replanned=False)
        replanned_resp = app.state.cached_replanned or load_offline_response(replanned=True)
    else:
        baseline_resp = app.state.live_baseline
        replanned_resp = app.state.live_replanned
        if baseline_resp is None or replanned_resp is None:
            return HTMLResponse(
                '<div class="diff-panel diff-panel--pending">'
                '<p>Run <strong>Inject Delay &amp; Re-plan</strong> to see what changed.</p>'
                '</div>',
                status_code=200,
            )

    try:
        plan_diff = orchestrator.diff(
            baseline_resp.arrival_plan,
            replanned_resp.arrival_plan,
        )
    except Exception as exc:
        return HTMLResponse(
            f'<div class="diff-panel diff-panel--error">'
            f'<p><strong>Diff unavailable:</strong> {exc}</p>'
            f'</div>',
            status_code=200,
        )
    return templates.TemplateResponse(request, "diff_panel.html", {"diff": plan_diff})


# ---------------------------------------------------------------------------
# Observation classifier
# ---------------------------------------------------------------------------

# Keyword buckets for classifying staff observations.
# Classification determines which role card(s) get updated.
_CLASSIFY_RULES: list[tuple[str, list[str]]] = [
    # (classification_key, [keywords...])
    ("spa",       ["spa", "massage", "asaya", "treatment", "relax", "facial", "body"]),
    ("dining",    ["dining", "dinner", "lunch", "breakfast", "restaurant", "madera",
                   "food", "wine", "menu", "table", "meal", "dietary", "vegetarian",
                   "gluten", "allergy"]),
    ("concierge", ["bike", "cycling", "cycle", "hike", "hiking", "trail", "outdoor",
                   "tour", "excursion", "activity", "bluejay", "ridge", "old la honda",
                   "portola", "winery", "golf", "tennis"]),
    ("housekeeping", ["room", "suite", "pillow", "towel", "housekeeping", "cleaning",
                       "turndown", "amenity", "temperature", "ac", "air"]),
    ("front_desk", ["check-in", "checkout", "check out", "luggage", "bag", "key",
                    "upgrade", "early", "late"]),
]

# Roles that map from classification keys
_CLASSIFY_TO_ROLE: dict[str, str] = {
    "spa": "Spa",
    "dining": "Dining",
    "concierge": "Concierge",
    "housekeeping": "Housekeeping",
    "front_desk": "Front Desk",
}


def _classify_observation(text: str) -> str:
    """
    Classify a staff observation text into a category.

    Returns one of: 'spa', 'dining', 'concierge', 'housekeeping', 'front_desk',
    or 'dossier_observation' (general observation, updates whole plan).

    Ambiguous / no match → 'dossier_observation' (US-004: sensible default, never crash).
    """
    lower = text.lower()
    best_match: str | None = None
    best_count = 0

    for key, keywords in _CLASSIFY_RULES:
        count = sum(1 for kw in keywords if kw in lower)
        if count > best_count:
            best_count = count
            best_match = key

    return best_match if best_match and best_count > 0 else "dossier_observation"


# ---------------------------------------------------------------------------
# POST /voice/transcribe  — STT + classification + role card update
# ---------------------------------------------------------------------------

@app.post("/voice/transcribe")
async def voice_transcribe(
    request: Request,
    audio: UploadFile | None = File(default=None),
    text_input: str | None = Form(default=None),
    source: str = Form(default="mic"),
) -> HTMLResponse:
    """
    Receive browser audio blob OR typed text → classify → update role cards.

    source=text: text_input used directly (TREQ-011 typed-text path — P0)
    source=mic:  audio bytes → ElevenLabs STT → same downstream path (TREQ-010 — P1)

    Returns HTMX-compatible HTML:
    - Primary target (#staff-note-result): transcript + classification feedback.
    - OOB swap (#role-cards): updated role cards reflecting the new observation.

    Ambiguous note → dossier_observation category → sensible default (US-004, never crash).
    Classification → appends to app.state.session_observations (TREQ-023 shim).
    """
    backend: Backend = app.state.backend

    # Step 1: resolve transcript
    if source == "text" and text_input and text_input.strip():
        transcript = text_input.strip()
    elif audio is not None:
        audio_bytes = await audio.read()
        try:
            transcript = await voice.stt(audio_bytes, backend=backend)
        except Exception as exc:
            logger.error("STT failed: %s", exc)
            transcript = voice._hardcoded_transcript()
    else:
        return HTMLResponse(
            '<p class="observation-error">No observation provided.</p>',
            status_code=400,
        )

    # Step 2: classify (US-004 — ambiguous → sensible default, never crash)
    classification = _classify_observation(transcript)

    # Step 3: append to in-memory session observations (TREQ-023)
    app.state.session_observations.append(transcript)
    obs_count = len(app.state.session_observations)

    # Step 4: get updated plan state with new observation injected
    # In REPLAY mode, append observation but keep fixture plan (deterministic replay)
    # In live mode, re-synthesize so the observation appears in updated role cards
    current_response = _get_current_plan(backend)

    # Step 5: determine which role(s) are affected
    affected_role = _CLASSIFY_TO_ROLE.get(classification)  # None = all roles / dossier

    # Step 6: render HTML response with OOB swap
    # Primary target: observation feedback shown in #staff-note-result
    role_label = affected_role or "Dossier (all roles)"
    feedback_html = _render_observation_feedback(transcript, classification, role_label, obs_count)

    # OOB swap: updated role cards grid (reflects observation context)
    # The plan data doesn't change in REPLAY mode, but the "Updated" UI marks affected cards
    role_cards_html = _render_role_cards_oob(request, current_response, affected_role)

    # OOB swap: dossier panel — append the live observation (BL-008 / TREQ-023 / US-014)
    # This always runs so the note visibly appears in #dossier-observations-list.
    dossier_obs_html = _render_dossier_observations_oob(app.state.session_observations)

    # BL-008 / TREQ-023: if this is a dossier_observation, also re-run synthesis.
    # REPLAY: returns synthesis_fixture.json deterministically (zero network).
    # CLAUDE: returns fixture for demo speed (live re-synthesis is 3-8s; use fixture to keep demo tight).
    # The synthesis panel update is included as an OOB swap of #synthesis-panel.
    synthesis_html = ""
    if classification == "dossier_observation":
        synthesis_html = _render_synthesis_oob(current_response)

    # Combine: feedback inline + OOB role cards + OOB dossier panel + optional OOB synthesis
    return HTMLResponse(feedback_html + role_cards_html + dossier_obs_html + synthesis_html)


def _render_dossier_observations_oob(session_observations: list[str]) -> str:
    """
    BL-008 / TREQ-023 / US-014: Render the live dossier observations list as an HTMX OOB swap
    targeting #dossier-observations-list. Called on every staff note submission so the
    note visibly appears in the on-screen dossier panel.
    In-memory only — no disk write-back.
    """
    if not session_observations:
        inner = '<p class="dossier-empty-note">No live observations this visit yet.</p>'
    else:
        items = ""
        for i, obs in enumerate(session_observations, 1):
            display = obs if len(obs) <= 200 else obs[:197] + "…"
            items += (
                f'<div class="dossier-obs-entry">'
                f'<span class="dossier-obs-num">#{i}</span>'
                f'<span class="dossier-obs-text">{display}</span>'
                f'</div>'
            )
        inner = items

    return (
        f'<div hx-swap-oob="innerHTML:#dossier-observations-list">'
        f'{inner}'
        f'</div>'
    )


def _render_synthesis_oob(current_response: OrchestratorResponse) -> str:
    """
    BL-008 / TREQ-023: Render an updated synthesis panel as an HTMX OOB swap
    targeting #synthesis-panel. Called when a dossier_observation is captured.

    Uses the current synthesis from app state (fixture in REPLAY, live in CLAUDE).
    The synthesis panel re-renders with the same structured "inferred from prior stays"
    content — in REPLAY this is deterministic from synthesis_fixture.json.
    This keeps the never-cut spine (diff) completely unblocked.
    """
    syn = current_response.synthesis

    # Build inferred-from items HTML
    if syn.inferred_from:
        items_html = ""
        for item in syn.inferred_from:
            items_html += (
                f'<div class="inferred-item">'
                f'<div class="inferred-item-text">{item.text}</div>'
                f'<div class="inferred-item-source">'
                f'<span class="inferred-from-label">Inferred from prior stay:</span>'
                f'<span class="inferred-property-tag">{item.source_property}</span>'
                f'<span class="inferred-observation">{item.source_observation}</span>'
                f'</div>'
                f'</div>'
            )
        prefs_html = f'<div class="inferred-from-list">{items_html}</div>'
    else:
        items = "".join(f"<li>{p}</li>" for p in syn.inferred_preferences)
        prefs_html = f'<ul class="synthesis-prefs">{items}</ul>'

    prov_tags = " &middot; ".join(
        f'<span class="provenance-tag">{pid}</span>' for pid in syn.provenance_properties
    )

    synthesis_inner = (
        f'<div class="synthesis-header">'
        f'<h2>Guest Intelligence — Cross-Visit Synthesis</h2>'
        f'<span class="synthesis-source-badge synthesis-source-badge--updated">'
        f'Updated from new observation</span>'
        f'</div>'
        f'<p class="synthesis-understanding">{syn.unified_understanding}</p>'
        f'{prefs_html}'
        f'<p class="provenance">Prior stays at: {prov_tags}</p>'
    )

    return (
        f'<section hx-swap-oob="outerHTML:#synthesis-panel" '
        f'id="synthesis-panel" class="synthesis-panel synthesis-panel--updated">'
        f'{synthesis_inner}'
        f'</section>'
    )


def _get_current_plan(backend: Backend) -> OrchestratorResponse:
    """Return the current plan from app state (baseline or replanned)."""
    # Use replanned if available, otherwise baseline
    if backend == Backend.REPLAY:
        return (
            app.state.cached_replanned
            or app.state.cached_baseline
            or load_offline_response(replanned=False)
        )
    return (
        app.state.live_replanned
        or app.state.live_baseline
        or load_offline_response(replanned=False)
    )


def _render_observation_feedback(
    transcript: str,
    classification: str,
    role_label: str,
    obs_count: int,
) -> str:
    """Render the observation receipt shown in #staff-note-result."""
    badge_class = "obs-badge obs-badge--" + classification.replace("_", "-")
    # Truncate long transcripts for display
    display_text = transcript if len(transcript) <= 200 else transcript[:197] + "…"
    return (
        f'<div class="observation-receipt">'
        f'<p class="obs-transcript">&ldquo;{display_text}&rdquo;</p>'
        f'<p class="obs-meta">'
        f'<span class="{badge_class}">{role_label}</span> &nbsp;'
        f'<span class="obs-count">Observation {obs_count} recorded</span>'
        f'</p>'
        f'</div>'
    )


def _render_role_cards_oob(
    request: Request,
    response: OrchestratorResponse,
    affected_role: str | None,
) -> str:
    """
    Render the role cards grid as an HTMX OOB swap targeting #role-cards.
    Marks the affected role card with a visual "Observation noted" indicator.
    """
    cards_html_parts = []

    for card in response.arrival_plan.role_cards:
        is_affected = (affected_role is None) or (card.role == affected_role)
        obs_indicator = ""
        if is_affected and app.state.session_observations:
            obs_indicator = (
                f'<span class="obs-noted-badge">'
                f'&#128221; Observation noted</span>'
            )

        changed_class = " role-card--obs-updated" if is_affected else ""
        fd_class = " role-card--front-desk" if card.role == "Front Desk" else ""

        # Build priority actions HTML
        actions_html = ""
        if card.priority_actions:
            items = "".join(f"<li>{a}</li>" for a in card.priority_actions)
            if card.role == "Front Desk":
                actions_html = (
                    f'<div class="fd-summary">'
                    f'<div class="fd-row">'
                    f'<span class="fd-label">Arrival Mode</span>'
                    f'<span class="fd-value">{response.arrival_plan.mood.title()}</span>'
                    f'</div>'
                    f'<div class="fd-row">'
                    f'<span class="fd-label">Actions</span>'
                    f'<ul class="fd-actions">{items}</ul>'
                    f'</div>'
                )
                if card.suppressed:
                    sup_items = "".join(f"<li>{s}</li>" for s in card.suppressed)
                    actions_html += (
                        f'<div class="fd-row fd-row--suppressed">'
                        f'<span class="fd-label">Do NOT Offer</span>'
                        f'<ul class="fd-suppressed">{sup_items}</ul>'
                        f'</div>'
                    )
                actions_html += "</div>"
            else:
                actions_html = f'<ul class="actions">{items}</ul>'
                if card.suppressed:
                    sup_items = "".join(f"<li>{s}</li>" for s in card.suppressed)
                    actions_html += (
                        f'<details class="suppressed">'
                        f'<summary>Suppressed ({len(card.suppressed)})</summary>'
                        f'<ul>{sup_items}</ul>'
                        f'</details>'
                    )

        card_id_slug = card.role.lower().replace(" ", "-")
        cards_html_parts.append(
            f'<div class="role-card{fd_class}{changed_class}">'
            f'<div class="role-card-header">'
            f'<h3>{card.role} {obs_indicator}</h3>'
            f'<button hx-get="/voice/tts/{card_id_slug}" hx-swap="none" '
            f'class="tts-btn" onclick="playAudio(this)" title="Play briefing">'
            f'&#9654; Play</button>'
            f'</div>'
            f'<p>{card.briefing}</p>'
            f'{actions_html}'
            f'</div>'
        )

    cards_inner = "\n".join(cards_html_parts)
    # HTMX OOB swap: hx-swap-oob="innerHTML:#role-cards" replaces the content of #role-cards
    return (
        f'<div hx-swap-oob="innerHTML:#role-cards">'
        f'<h2 style="font-size:1rem;color:#5d7a8a;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:1rem;">Role Briefings</h2>'
        f'{cards_inner}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# GET /voice/tts/{card_id}  — TTS audio stream (BL-005)
# ---------------------------------------------------------------------------

_ROLE_SLUG_TO_NAME: dict[str, str] = {
    "front-desk": "Front Desk",
    "concierge": "Concierge",
    "spa": "Spa",
    "dining": "Dining",
    "housekeeping": "Housekeeping",
    "guest-experience": "Guest Experience",
}


def _get_briefing_for_card(card_id: str, backend: Backend) -> str:
    """
    Look up the CURRENT briefing text for a role card from app state.

    Reads from the most recent plan (replanned > baseline > fixture).
    This ensures TTS reflects the updated briefing after a re-plan (US-005).
    """
    role_name = _ROLE_SLUG_TO_NAME.get(card_id.lower())
    if not role_name:
        # Unknown card_id — strip badges from raw card_id and try again
        clean_id = re.sub(r"[^a-z-]", "", card_id.lower().strip())
        role_name = _ROLE_SLUG_TO_NAME.get(clean_id, card_id.replace("-", " ").title())

    # Get current plan from app state
    current = _get_current_plan(backend)
    if current:
        for card in current.arrival_plan.role_cards:
            if card.role == role_name:
                return card.briefing

    # Fallback: generate a contextual briefing text
    return f"Briefing for the {role_name} role at Rosewood Sand Hill for Ms. Chen's arrival."


@app.get("/voice/tts/{card_id}")
async def voice_tts(card_id: str, request: Request) -> Response:
    """
    Stream audio for a role card briefing via ElevenLabs TTS.
    card_id: role slug, e.g. "concierge", "spa", "front-desk"

    BL-005 (US-005): serves the CURRENT briefing text — reflects updated plan after re-plan.
    REPLAY mode: returns cached M4A (TD-006 — real spoken audio).
    CLAUDE mode: calls ElevenLabs TTS → MP3 bytes.
    """
    backend: Backend = app.state.backend

    # Get the current briefing text for this card (US-005: reads updated plan)
    briefing_text = _get_briefing_for_card(card_id, backend)

    audio_bytes, mime_type = await voice.tts(briefing_text, backend=backend)

    ext = "m4a" if mime_type == voice.MIME_M4A else "mp3"
    return Response(
        content=audio_bytes,
        media_type=mime_type,
        headers={"Content-Disposition": f'inline; filename="{card_id}.{ext}"'},
    )


# ---------------------------------------------------------------------------
# GET /offline  — Offline mode info
# ---------------------------------------------------------------------------

@app.get("/offline", response_class=HTMLResponse)
async def offline_info(request: Request) -> HTMLResponse:
    """
    Serve offline-mode status. In full offline mode, shows fixture-replay banner.
    """
    return _tmpl(request, {
        "response": load_offline_response(replanned=False),
        "backend": "replay",
        "offline": True,
        "dossier_slugs": list_dossier_slugs(),
        "property_slugs": list_property_slugs(),
        "plan_diff": None,
        "replanned": False,
    })


# ---------------------------------------------------------------------------
# GET /select  — Guest/property selector form
# GET returns selector form; POST runs plan and returns dashboard
# ---------------------------------------------------------------------------

@app.get("/select", response_class=HTMLResponse)
async def select_form(request: Request) -> HTMLResponse:
    """Return selector dropdowns for guest and property."""
    if app.state.backend == Backend.REPLAY:
        return HTMLResponse(
            "<div class='banner'>Selector disabled in offline mode.</div>",
            status_code=503,
        )
    return _tmpl(request, {
        "response": None,
        "backend": app.state.backend.value,
        "offline": False,
        "dossier_slugs": list_dossier_slugs(),
        "property_slugs": list_property_slugs(),
        "show_selector": True,
    })


@app.post("/select", response_class=HTMLResponse)
async def select_guest(
    request: Request,
    guest_id: str = Form(...),
    property_id: str = Form(...),
) -> HTMLResponse:
    """
    Accept guest_id + property_id, run plan(), return dashboard.
    Disabled in offline mode (ADR-002 Delta 5).
    """
    backend: Backend = app.state.backend

    if backend == Backend.REPLAY:
        return HTMLResponse(
            "<div class='banner'>Selector disabled in offline mode.</div>",
            status_code=503,
        )

    dossier_md = load_dossier(guest_id)
    property_md = load_property_card(property_id)
    provenance_mds = load_provenance_cards(guest_id, exclude=property_id)

    try:
        response = await orchestrator.plan(
            dossier_md, property_md, provenance_mds,
            backend=backend,
        )
    except NotImplementedError:
        response = None

    return _tmpl(request, {
        "response": response,
        "backend": backend.value,
        "offline": False,
        "dossier_slugs": list_dossier_slugs(),
        "property_slugs": list_property_slugs(),
        "plan_diff": None,
        "replanned": False,
    })
