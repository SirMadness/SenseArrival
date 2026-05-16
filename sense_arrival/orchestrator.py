"""
orchestrator.py — Claude tool-loop stubs: plan(), replan(), diff().

BL-001 scope: stub signatures that raise NotImplementedError.
BL-002 implements the full Claude tool-use loop.

OFFLINE_MODE / Backend.REPLAY: fixture-replay path is wired here so BL-002
can slot the live Claude path in without changing the call site.
"""
from __future__ import annotations

from sense_arrival.config import Backend, settings
from sense_arrival.fixture_loader import load_offline_response
from sense_arrival.models import ArrivalPlan, OrchestratorResponse, PlanDiff


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
    """
    effective_backend = backend or settings.default_backend

    if effective_backend == Backend.REPLAY:
        return load_offline_response(replanned=False)

    # BL-002 implements live Claude / Ollama paths
    raise NotImplementedError(
        "plan() live backend not yet implemented — BL-002 scope. "
        "Set OFFLINE_MODE=true or BACKEND=replay to use fixture replay."
    )


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

    raise NotImplementedError(
        "replan() live backend not yet implemented — BL-002 scope."
    )


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
