"""
main.py — SenseArrival FastAPI application.

Single-process server. All routes defined here.
Start with: uvicorn sense_arrival.main:app --reload

Routes (ADR-001 + ADR-002 Delta 4):
  GET  /               — Dashboard (placeholder until BL-002)
  POST /replan         — Inject delay event → re-plan
  GET  /diff           — Return PlanDiff panel fragment
  POST /voice/transcribe — Browser audio → STT → transcript
  GET  /voice/tts/{card_id} — ElevenLabs TTS → MP3 stream
  GET  /offline        — Offline-replay mode info
  GET  /select         — Guest/property selector form
  POST /select         — Accept selection → run plan → dashboard
"""
from __future__ import annotations

import json
import logging

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

    plan_diff = orchestrator.diff(
        baseline_resp.arrival_plan,
        replanned_resp.arrival_plan,
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

    plan_diff = orchestrator.diff(
        baseline_resp.arrival_plan,
        replanned_resp.arrival_plan,
    )
    return templates.TemplateResponse(request, "diff_panel.html", {"diff": plan_diff})


# ---------------------------------------------------------------------------
# POST /voice/transcribe  — STT + observation loop
# ---------------------------------------------------------------------------

@app.post("/voice/transcribe")
async def voice_transcribe(
    request: Request,
    audio: UploadFile | None = File(default=None),
    text_input: str | None = Form(default=None),
    source: str = Form(default="mic"),
) -> JSONResponse:
    """
    Receive browser audio blob OR typed text → return transcript.

    source=mic: audio bytes → ElevenLabs STT
    source=text: text_input used directly (typed-text fallback — build first)

    If classification returns 'dossier_observation', appends to
    app.state.session_observations (TREQ-023 in-memory shim).
    """
    backend: Backend = app.state.backend

    if source == "text" and text_input:
        transcript = text_input
    elif audio is not None:
        audio_bytes = await audio.read()
        transcript = await voice.stt(audio_bytes, backend=backend)
    else:
        return JSONResponse({"error": "No audio or text provided."}, status_code=400)

    # BL-002 classification step: for now tag everything as observation
    classification = "dossier_observation"  # BL-002 will implement real classification
    if classification == "dossier_observation":
        app.state.session_observations.append(transcript)

    return JSONResponse(
        {
            "transcript": transcript,
            "classification": classification,
            "observation_count": len(app.state.session_observations),
        }
    )


# ---------------------------------------------------------------------------
# GET /voice/tts/{card_id}  — TTS audio stream
# ---------------------------------------------------------------------------

@app.get("/voice/tts/{card_id}")
async def voice_tts(card_id: str, request: Request) -> Response:
    """
    Stream MP3 audio for a role card briefing.
    card_id: role slug, e.g. "concierge", "spa"

    Replay mode: returns cached MP3.
    Live mode: calls ElevenLabs generate() — BL-002 scope.
    """
    backend: Backend = app.state.backend

    # Placeholder briefing text — BL-002 replaces with real card briefing
    briefing_text = f"Briefing for {card_id} role card."

    try:
        audio_bytes = await voice.tts(briefing_text, backend=backend)
    except NotImplementedError:
        return Response(
            content=b"",
            media_type="audio/mpeg",
            headers={"X-TTS-Status": "not-implemented"},
        )

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f'inline; filename="{card_id}.mp3"'},
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
    })
