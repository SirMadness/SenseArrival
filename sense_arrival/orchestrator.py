"""
orchestrator.py — Claude tool-loop: plan(), replan(), diff().

BL-001: REPLAY path wired; live paths raised NotImplementedError.
BL-002: Implements Tier-1 Claude tool-use path and Tier-2 Ollama path.

OFFLINE_MODE / Backend.REPLAY: fixture-replay path is zero-network and
deterministic.  Backend.CLAUDE makes a single structured tool-use call
to Claude and parses the JSON into OrchestratorResponse.  Backend.OLLAMA
uses the same prompt/schema via the Ollama chat endpoint.
"""
from __future__ import annotations

import json
import logging
import re

import anthropic

from sense_arrival.config import Backend, settings
from sense_arrival.fixture_loader import load_offline_response
from sense_arrival.models import (
    ArrivalPlan,
    GuestSynthesis,
    OrchestratorResponse,
    PlanDiff,
    RoleCard,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool schema: mirrors OrchestratorResponse exactly.
# Claude is asked to call this tool — the input_schema is the structured
# output format.  A single tool-use call returns synthesis + arrival_plan.
# ---------------------------------------------------------------------------

_TOOL_SCHEMA = {
    "name": "submit_arrival_plan",
    "description": (
        "Submit the complete arrival orchestration response, including cross-visit "
        "guest synthesis and a fully grounded arrival plan with role-specific briefings."
    ),
    "input_schema": {
        "type": "object",
        "required": ["synthesis", "arrival_plan"],
        "properties": {
            "synthesis": {
                "type": "object",
                "required": [
                    "unified_understanding",
                    "inferred_preferences",
                    "provenance_properties",
                ],
                "properties": {
                    "unified_understanding": {
                        "type": "string",
                        "description": (
                            "2–4 sentence prose: what the system infers cross-visit "
                            "about this guest's patterns, needs, and this arrival context."
                        ),
                    },
                    "inferred_preferences": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "3–6 bullet strings: specific inferred preferences "
                            "drawn from cross-property observations."
                        ),
                    },
                    "provenance_properties": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "List of property_id strings that contributed prior-stay "
                            "observations to this synthesis."
                        ),
                    },
                },
            },
            "arrival_plan": {
                "type": "object",
                "required": ["mood", "role_cards", "suppression", "guest_message"],
                "properties": {
                    "mood": {
                        "type": "string",
                        "description": (
                            "One-word arrival mood classifier. Must be one of: "
                            "Quiet, Restorative, Recovery, Celebratory, Work-Mode, "
                            "Family Landing, Exploratory."
                        ),
                    },
                    "role_cards": {
                        "type": "array",
                        "description": "Exactly 6 role cards — one per role listed.",
                        "items": {
                            "type": "object",
                            "required": [
                                "role",
                                "briefing",
                                "priority_actions",
                                "suppressed",
                            ],
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "description": (
                                        "Role name. Must be one of: Front Desk, "
                                        "Concierge, Spa, Dining, Housekeeping, "
                                        "Guest Experience."
                                    ),
                                },
                                "briefing": {
                                    "type": "string",
                                    "description": (
                                        "2–4 sentence prose briefing. Must reference "
                                        "specific guest details or named property anchors — "
                                        "not generic copy."
                                    ),
                                },
                                "priority_actions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "3–5 specific, actionable bullet strings.",
                                },
                                "suppressed": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Items explicitly NOT to offer this guest.",
                                },
                            },
                        },
                    },
                    "suppression": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Global do-not-offer list (union across all roles).",
                    },
                    "guest_message": {
                        "type": "string",
                        "description": (
                            "Personalised welcome note for the guest — 2–3 sentences, "
                            "specific to their dossier and current arrival context."
                        ),
                    },
                },
            },
        },
    },
}

_SYSTEM_PROMPT = """\
You are the SenseArrival orchestration engine for Rosewood Hotels & Resorts.

Your task is to read a guest dossier and arrival property card (and optionally provenance property \
cards from prior stays) and produce a fully grounded, schema-valid arrival plan for the hotel team.

Rules:
1. Every role card briefing MUST reference specific guest details from the dossier OR named anchors \
   from the arrival property card. No generic copy. If you reference a wine experience, name it. \
   If you reference a cycling route, name it.
2. The mood must match the guest's profile and arrival context. Arriving tired after a red-eye = \
   Restorative or Recovery. Business focus = Work-Mode. Family group = Family Landing.
3. The synthesis unified_understanding must draw on cross-property observations from prior stays — \
   do not invent preferences not evidenced in the dossier.
4. Exactly 6 role cards: Front Desk, Concierge, Spa, Dining, Housekeeping, Guest Experience.
5. At least 2 outputs must name specific Rosewood Sand Hill anchors from the property card \
   (e.g. Asaya Spa, Madera, Ridge Rosé Reveal, Bluejay Bikes, Old La Honda Road, Friday Nights at Madera, \
   Flamingo Estate Afternoon Tea) — contextually appropriate, not generic name-drops.
6. Call submit_arrival_plan exactly once with your complete response. Do not produce any other output.
"""


def _build_prompt_blocks(
    dossier_md: str,
    arrival_property_md: str,
    provenance_mds: list[str],
    delay_event: dict | None = None,
    session_observations: list[str] | None = None,
) -> str:
    """
    Assemble the human-turn prompt content per ADR-002 Delta 3 ordering.
    Returns a single string with labeled delimiter blocks.
    """
    parts: list[str] = []

    parts.append("--- GUEST DOSSIER ---")
    parts.append(dossier_md.strip())

    parts.append("--- PROPERTY CARD: ARRIVAL ---")
    parts.append(arrival_property_md.strip())

    # Provenance cards: extract property_id from each card's identity block
    for idx, pmd in enumerate(provenance_mds):
        # Try to extract the property_id from the card; fall back to index
        pid_match = re.search(r"\*\*Property ID:\*\*\s*([\w-]+)", pmd)
        pid = pid_match.group(1) if pid_match else f"provenance-{idx + 1}"
        parts.append(f"--- PROPERTY CARD: PROVENANCE: {pid} ---")
        parts.append(pmd.strip())

    if session_observations:
        parts.append("--- LIVE STAFF OBSERVATIONS (THIS VISIT) ---")
        for obs in session_observations:
            parts.append(f"- {obs}")

    if delay_event:
        parts.append("--- ARRIVAL EVENT ---")
        parts.append(json.dumps(delay_event, indent=2))
    else:
        parts.append("--- ARRIVAL EVENT ---")
        parts.append("No delay. Guest is arriving as scheduled.")

    return "\n\n".join(parts)


def _parse_tool_response(response: anthropic.types.Message) -> OrchestratorResponse:
    """
    Extract the submit_arrival_plan tool call input from a Claude response
    and parse it into an OrchestratorResponse.

    Raises ValueError if the tool call is absent or the schema is invalid.
    """
    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_arrival_plan":
            data = block.input
            synthesis = GuestSynthesis(**data["synthesis"])
            plan_data = data["arrival_plan"]
            role_cards = [RoleCard(**rc) for rc in plan_data["role_cards"]]
            arrival_plan = ArrivalPlan(
                mood=plan_data["mood"],
                role_cards=role_cards,
                suppression=plan_data.get("suppression", []),
                guest_message=plan_data.get("guest_message", ""),
            )
            return OrchestratorResponse(synthesis=synthesis, arrival_plan=arrival_plan)
    raise ValueError("No submit_arrival_plan tool call found in Claude response.")


async def _call_claude(
    dossier_md: str,
    arrival_property_md: str,
    provenance_mds: list[str],
    delay_event: dict | None = None,
    session_observations: list[str] | None = None,
) -> OrchestratorResponse:
    """
    Make a single Claude tool-use call and return a validated OrchestratorResponse.
    Falls back to the offline fixture if parsing fails (graceful degradation — TREQ-014).
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    human_content = _build_prompt_blocks(
        dossier_md, arrival_property_md, provenance_mds, delay_event, session_observations
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            tools=[_TOOL_SCHEMA],
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": human_content}],
        )
        return _parse_tool_response(response)
    except Exception as exc:
        logger.error(
            "Claude plan() call failed (%s: %s); falling back to offline fixture.",
            type(exc).__name__,
            exc,
        )
        # Graceful degradation: return fixture so the render never crashes (TREQ-014)
        return load_offline_response(replanned=bool(delay_event))


async def _call_ollama(
    dossier_md: str,
    arrival_property_md: str,
    provenance_mds: list[str],
    delay_event: dict | None = None,
    session_observations: list[str] | None = None,
) -> OrchestratorResponse:
    """
    Ollama Tier-2 path: POST to local Ollama chat endpoint with a JSON-schema
    prompt requesting the OrchestratorResponse structure.
    Falls back to offline fixture on any failure.
    """
    import httpx

    human_content = _build_prompt_blocks(
        dossier_md, arrival_property_md, provenance_mds, delay_event, session_observations
    )

    schema_instruction = (
        f"\n\nRespond with ONLY valid JSON matching this schema:\n"
        f"{json.dumps(_TOOL_SCHEMA['input_schema'], indent=2)}\n"
        f"Do not include any other text."
    )

    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT + schema_instruction},
            {"role": "user", "content": human_content},
        ],
        "stream": False,
        "format": "json",
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json=payload,
            )
            r.raise_for_status()
            raw = r.json()["message"]["content"]
            data = json.loads(raw)
            synthesis = GuestSynthesis(**data["synthesis"])
            plan_data = data["arrival_plan"]
            role_cards = [RoleCard(**rc) for rc in plan_data["role_cards"]]
            arrival_plan = ArrivalPlan(
                mood=plan_data["mood"],
                role_cards=role_cards,
                suppression=plan_data.get("suppression", []),
                guest_message=plan_data.get("guest_message", ""),
            )
            return OrchestratorResponse(synthesis=synthesis, arrival_plan=arrival_plan)
    except Exception as exc:
        logger.error(
            "Ollama plan() call failed (%s: %s); falling back to offline fixture.",
            type(exc).__name__,
            exc,
        )
        return load_offline_response(replanned=bool(delay_event))


async def plan(
    dossier_md: str,
    arrival_property_md: str,
    provenance_mds: list[str],
    session_observations: list[str] | None = None,
    *,
    backend: Backend | None = None,
) -> OrchestratorResponse:
    """
    Generate an arrival plan for a guest.

    Prompt assembly order (ADR-002 Delta 3):
        [System prompt]
        --- GUEST DOSSIER ---
        {dossier_md}
        --- PROPERTY CARD: ARRIVAL ---
        {arrival_property_md}
        --- PROPERTY CARD: PROVENANCE: <id> ---
        {provenance_md}
        [--- LIVE STAFF OBSERVATIONS (THIS VISIT) ---]
        {session_observations if any}
        --- ARRIVAL EVENT ---
        {base event}

    Returns OrchestratorResponse containing synthesis + arrival_plan.
    Tier-1 (Claude): single tool-use call → schema-validated OrchestratorResponse.
    Tier-2 (Ollama): chat endpoint with JSON format constraint.
    Tier-3 (Replay): fixture-only, zero network.
    """
    effective_backend = backend or settings.default_backend

    if effective_backend == Backend.REPLAY:
        return load_offline_response(replanned=False)

    if effective_backend == Backend.CLAUDE:
        return await _call_claude(
            dossier_md, arrival_property_md, provenance_mds,
            delay_event=None,
            session_observations=session_observations,
        )

    if effective_backend == Backend.OLLAMA:
        return await _call_ollama(
            dossier_md, arrival_property_md, provenance_mds,
            delay_event=None,
            session_observations=session_observations,
        )

    # Unknown backend — degrade
    logger.warning("Unknown backend %s; falling back to offline fixture.", effective_backend)
    return load_offline_response(replanned=False)


async def replan(
    dossier_md: str,
    arrival_property_md: str,
    provenance_mds: list[str],
    delay_event: dict,
    session_observations: list[str] | None = None,
    *,
    backend: Backend | None = None,
) -> OrchestratorResponse:
    """
    Re-generate arrival plan after a disruption event (e.g. flight delay).
    Same prompt structure as plan() with delay_event injected as ARRIVAL EVENT.
    """
    effective_backend = backend or settings.default_backend

    if effective_backend == Backend.REPLAY:
        return load_offline_response(replanned=True)

    if effective_backend == Backend.CLAUDE:
        return await _call_claude(
            dossier_md, arrival_property_md, provenance_mds,
            delay_event=delay_event,
            session_observations=session_observations,
        )

    if effective_backend == Backend.OLLAMA:
        return await _call_ollama(
            dossier_md, arrival_property_md, provenance_mds,
            delay_event=delay_event,
            session_observations=session_observations,
        )

    logger.warning("Unknown backend %s; falling back to offline fixture.", effective_backend)
    return load_offline_response(replanned=True)


def diff(baseline: ArrivalPlan, replanned: ArrivalPlan) -> PlanDiff:
    """
    Compute structured diff between two ArrivalPlans.
    Synthesis is explicitly excluded — only ArrivalPlan fields participate.
    This is the never-cut spine (TREQ-006).

    BL-001: minimal diff implementation (role-name comparison).
    BL-002 may enrich with Claude-generated rationale.
    """
    baseline_roles = {rc.role: rc for rc in baseline.role_cards}
    replanned_roles = {rc.role: rc for rc in replanned.role_cards}

    changed: list[str] = []
    added_actions: list[str] = []
    removed_actions: list[str] = []

    for role, new_card in replanned_roles.items():
        old_card = baseline_roles.get(role)
        if old_card is None:
            changed.append(role)
            added_actions.extend(new_card.priority_actions)
            continue
        old_set = set(old_card.priority_actions)
        new_set = set(new_card.priority_actions)
        if old_set != new_set:
            changed.append(role)
            added_actions.extend(new_set - old_set)
            removed_actions.extend(old_set - new_set)

    for role in baseline_roles:
        if role not in replanned_roles:
            changed.append(role)
            removed_actions.extend(baseline_roles[role].priority_actions)

    rationale = (
        f"Re-plan triggered by delay event. {len(changed)} role(s) updated."
        if changed
        else "No changes detected between baseline and re-plan."
    )

    return PlanDiff(
        changed_roles=changed,
        added_actions=added_actions,
        removed_actions=removed_actions,
        rationale=rationale,
    )
