"""
models.py — SenseArrival domain models (ADR-001 + ADR-002)

ADR-002 introduces: PriorStay, GuestDossier, PropertyCard, GuestSynthesis,
OrchestratorResponse.
ADR-001 originals unchanged: ArrivalPlan, RoleCard, PlanDiff.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# ADR-002 additions / replacements
# ---------------------------------------------------------------------------

class PriorStay(BaseModel):
    """Observations from a single prior Rosewood stay."""
    property_id: str            # slug matching PropertyCard.property_id
    dates: str                  # human-readable, e.g. "March 2024"
    staff_observations: list[str]   # 1–5 verbatim or paraphrased bullet strings


class GuestDossier(BaseModel):
    """Full guest profile with cross-property history (replaces ADR-001 GuestProfile)."""
    guest_id: str               # slug, e.g. "ms-chen"
    name: str
    nationality: str
    arrival_property_id: str    # which PropertyCard is "arrival" depth for this visit
    profile_summary: str        # stable persona: dietary, accessibility, style, tone
    prior_stays: list[PriorStay]    # ordered newest-first; empty for first-visit guests


class PropertyCard(BaseModel):
    """Property identity and destination context card."""
    property_id: str            # slug, e.g. "rosewood-sand-hill"
    name: str
    location: str               # city/region
    depth: Literal["arrival", "provenance"]  # arrival=full render; provenance=context only
    sense_of_place: str         # raw Markdown blob (local culture, landmarks, activities)
    signature_anchors: list[str]    # 3–6 specific named anchors for prompt grounding


class GuestSynthesis(BaseModel):
    """
    Cross-visit synthesis produced alongside ArrivalPlan.
    MUST NOT participate in PlanDiff — it is UI context only.
    """
    unified_understanding: str          # 2–4 sentence prose: cross-visit inference
    inferred_preferences: list[str]     # bullet list surfaced in UI
    provenance_properties: list[str]    # property_id list that contributed observations


# ---------------------------------------------------------------------------
# ADR-001 originals — DO NOT MODIFY SIGNATURES
# ---------------------------------------------------------------------------

class RoleCard(BaseModel):
    """Briefing card for a single hotel role (concierge, spa, dining, etc.)."""
    role: str               # e.g. "Concierge", "Spa", "Dining", "Front Desk"
    briefing: str           # prose briefing for this role
    priority_actions: list[str]   # 2–4 bullet actions
    suppressed: list[str]   # items explicitly NOT to offer/suggest


class ArrivalPlan(BaseModel):
    """Complete arrival choreography plan for a single guest visit."""
    mood: str               # one-word arrival mood classifier, e.g. "restorative"
    role_cards: list[RoleCard]
    suppression: list[str]  # global suppression list (union of role-level suppressed)
    guest_message: str      # personalised welcome note for the guest


class PlanDiff(BaseModel):
    """
    Structured diff between baseline and re-planned ArrivalPlan.
    This is the never-cut spine (TREQ-006). Synthesis never enters this path.
    """
    changed_roles: list[str]    # role names that changed
    added_actions: list[str]    # new priority actions added in the replan
    removed_actions: list[str]  # actions removed in the replan
    rationale: str              # plain-English explanation of why the plan changed


# ---------------------------------------------------------------------------
# Orchestrator envelope (ADR-002 Delta 3)
# ---------------------------------------------------------------------------

class OrchestratorResponse(BaseModel):
    """
    Outer Claude response envelope.  synthesis and arrival_plan travel together
    but only arrival_plan feeds PlanDiff.
    """
    synthesis: GuestSynthesis
    arrival_plan: ArrivalPlan
