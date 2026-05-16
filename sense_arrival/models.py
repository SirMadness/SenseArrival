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


class InferredPreference(BaseModel):
    """
    A single inferred guest preference with attribution to the source property.
    Used by the synthesis panel to render "inferred from prior stays" elements.
    BL-008: deepened from bare string to structured attribution.
    """
    text: str                       # the preference as a displayable string
    source_property: str            # property_id that contributed the observation
    source_observation: str         # brief summary of the staff observation that grounded this


class GuestSynthesis(BaseModel):
    """
    Cross-visit synthesis produced alongside ArrivalPlan.
    MUST NOT participate in PlanDiff — it is UI context only.
    BL-008: deepened with structured inferred_from attribution.
    """
    unified_understanding: str          # 2–4 sentence prose: cross-visit inference
    inferred_preferences: list[str]     # bare bullet list (backward compat / live LLM output)
    provenance_properties: list[str]    # property_id list that contributed observations
    # BL-008 addition: structured preferences with provenance attribution for "inferred from" UI
    inferred_from: list[InferredPreference] = []  # empty = fall back to inferred_preferences


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


class PlanDiffEntry(BaseModel):
    """
    A single change entry in the diff panel (TREQ-006 / US-003).
    Each entry carries the change, its trigger (what caused it), and a
    one-line reason (why it matters for this guest).
    Synthesis never enters this path — arrival_plan fields only.
    """
    role: str           # which role card this entry belongs to
    action: str         # the changed action text
    change_type: str    # "added" | "removed"
    trigger: str        # what triggered this change (e.g. "120-min flight delay")
    reason: str         # one-line: why this specific change was made


class PlanDiff(BaseModel):
    """
    Structured diff between baseline and re-planned ArrivalPlan.
    This is the never-cut spine (TREQ-006). Synthesis never enters this path.
    """
    changed_roles: list[str]        # role names that changed
    added_actions: list[str]        # new priority actions added in the replan
    removed_actions: list[str]      # actions removed in the replan
    rationale: str                  # plain-English explanation of why the plan changed
    entries: list[PlanDiffEntry] = []  # structured per-change entries for the diff panel


# ---------------------------------------------------------------------------
# Suppression model (BL-006 / TREQ-007 / US-006)
# ARCHITECTURE NOTE: Suppression is a SEPARATE field on OrchestratorResponse.
# It MUST NEVER be added to ArrivalPlan, PlanDiff, PlanDiffEntry, or pass
# through orchestrator.diff(). The diff() function is the never-cut spine
# (TREQ-006) and operates exclusively on ArrivalPlan fields.
# ---------------------------------------------------------------------------

class Suppression(BaseModel):
    """
    A single withheld suggestion with a concierge-framed reason.
    Surface in the "Tasteful Restraint" panel — what we chose NOT to offer and why.
    BL-006 / TREQ-007 / US-006.
    """
    suggestion: str     # the withheld item (e.g. "Group tours / guided excursions")
    reason: str         # one-line concierge-framed reason (e.g. "solo decompressor — wrong energy")


# ---------------------------------------------------------------------------
# Orchestrator envelope (ADR-002 Delta 3 + BL-006 additive extension)
# ---------------------------------------------------------------------------

class OrchestratorResponse(BaseModel):
    """
    Outer Claude response envelope.  synthesis and arrival_plan travel together
    but only arrival_plan feeds PlanDiff.
    BL-006: suppressions is an ADDITIVE field — structurally excluded from diff().
    """
    synthesis: GuestSynthesis
    arrival_plan: ArrivalPlan
    # BL-006: suppression panel data — NEVER enters diff() or PlanDiff.
    # Populated independently from the synthesis/plan fields.
    suppressions: list[Suppression] = []
