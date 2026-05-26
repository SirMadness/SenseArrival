"""
fixture_loader.py — Markdown fixture library loader (ADR-002 Delta 2).

Loading convention (verbatim from ADR-002):
    def load_dossier(guest_id: str) -> str
    def load_property_card(property_id: str) -> str

Files are read with open().read() — NO Markdown parser.
Raw strings are injected into Claude prompts between labeled delimiters.

Typed object helpers parse the Markdown header fields into Pydantic models so
the orchestrator can pass typed objects to the UI without re-reading disk.

SCOPE GUARD (TREQ-019): raises ValueError for any slug not in the fixed
3-dossier × 3-property library.  No live APIs; fixtures only.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from sense_arrival.config import settings
from sense_arrival.models import (
    ArrivalPlan,
    GuestDossier,
    GuestSynthesis,
    OrchestratorResponse,
    PriorStay,
    PropertyCard,
    Suppression,
)

# Fixture root relative to this file's parent (sense_arrival/)
_FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Scope guard
# ---------------------------------------------------------------------------

def _guard_dossier(guest_id: str) -> None:
    if guest_id not in settings.ALLOWED_DOSSIERS:
        raise ValueError(
            f"Scope guard: dossier '{guest_id}' is not in the allowed fixture library. "
            f"Allowed: {sorted(settings.ALLOWED_DOSSIERS)}"
        )


def _guard_property(property_id: str) -> None:
    if property_id not in settings.ALLOWED_PROPERTIES:
        raise ValueError(
            f"Scope guard: property '{property_id}' is not in the allowed fixture library. "
            f"Allowed: {sorted(settings.ALLOWED_PROPERTIES)}"
        )


# ---------------------------------------------------------------------------
# Raw-text loaders (ADR-002 verbatim contract)
# ---------------------------------------------------------------------------

def load_dossier(guest_id: str) -> str:
    """Return raw Markdown text for a guest dossier. No parsing."""
    _guard_dossier(guest_id)
    path = _FIXTURES / "dossiers" / f"{guest_id}.md"
    return path.read_text(encoding="utf-8")


def load_property_card(property_id: str) -> str:
    """Return raw Markdown text for a property card. No parsing."""
    _guard_property(property_id)
    path = _FIXTURES / "properties" / f"{property_id}.md"
    return path.read_text(encoding="utf-8")


def load_provenance_cards(guest_id: str, exclude: str) -> list[str]:
    """
    Return list of raw Markdown strings for provenance properties referenced in
    the guest's prior stays, excluding the arrival property.
    (ADR-002 Delta 4 — load_provenance_cards helper)
    """
    dossier_md = load_dossier(guest_id)
    # Extract property IDs mentioned as "Property ID: <slug>" in the dossier
    mentioned = re.findall(r"\*\*Property ID:\*\*\s*([\w-]+)", dossier_md)
    provenance_texts: list[str] = []
    for pid in mentioned:
        if pid == exclude:
            continue
        try:
            provenance_texts.append(load_property_card(pid))
        except ValueError:
            pass  # skip any slug not in the allowed set
    return provenance_texts


# ---------------------------------------------------------------------------
# Typed-object builders (parse Markdown header fields into Pydantic models)
# ---------------------------------------------------------------------------

def _extract_field(text: str, label: str) -> str:
    """Extract '- **Label:** value' from Markdown."""
    pattern = rf"\*\*{re.escape(label)}:\*\*\s*(.+)"
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ""


def _extract_anchors(text: str) -> list[str]:
    """Extract bullet items from the Signature Anchors section."""
    section_match = re.search(r"## Signature Anchors\n(.*?)(?:\n##|\Z)", text, re.DOTALL)
    if not section_match:
        return []
    lines = section_match.group(1).strip().splitlines()
    anchors = []
    for line in lines:
        line = line.strip()
        if line.startswith("- "):
            anchors.append(line[2:].strip())
    return anchors


def _extract_sense_of_place(text: str) -> str:
    """Extract the Sense of Place section body."""
    m = re.search(r"## Sense of Place\n(.*?)(?:\n##|\Z)", text, re.DOTALL)
    return m.group(1).strip() if m else text


def _extract_prior_stays(text: str) -> list[PriorStay]:
    """Parse ### subsections under ## Prior Stays into PriorStay objects."""
    stays: list[PriorStay] = []
    # Locate the ## Prior Stays section (may be followed by blank lines before ###)
    prior_stays_match = re.search(
        r"^## Prior Stays\s*\n(.*?)(?:\n^## |\Z)", text, re.DOTALL | re.MULTILINE
    )
    if not prior_stays_match:
        return []

    block = prior_stays_match.group(1)

    # Split on ### headings — each heading starts a new stay section
    sections = re.split(r"^###\s+", block, flags=re.MULTILINE)
    for section in sections:
        if not section.strip():
            continue
        prop_id = _extract_field(section, "Property ID")
        if not prop_id:
            continue

        # First line of section: "Property Name — Month Year"
        header_line = section.splitlines()[0].strip()
        dates_match = re.search(r"—\s*(.+)", header_line)
        dates = dates_match.group(1).strip() if dates_match else ""

        # Staff observations: bullet lines after **Staff Observations:**
        obs_block_match = re.search(
            r"\*\*Staff Observations:\*\*\s*\n(.*?)(?:\n\*\*[A-Z]|\Z)", section, re.DOTALL
        )
        observations: list[str] = []
        if obs_block_match:
            for line in obs_block_match.group(1).splitlines():
                line = line.strip()
                if line.startswith("- "):
                    observations.append(line[2:].strip())

        stays.append(PriorStay(
            property_id=prop_id,
            dates=dates,
            staff_observations=observations,
        ))
    return stays


def build_guest_dossier(guest_id: str) -> GuestDossier:
    """
    Parse the dossier Markdown into a typed GuestDossier.
    The raw text is the source of truth; this is a convenience object.
    """
    text = load_dossier(guest_id)
    name = _extract_field(text, "Guest ID")
    # Prefer the H1 title for name
    h1 = re.search(r"^# Guest Dossier:\s*(.+)", text, re.MULTILINE)
    display_name = h1.group(1).strip() if h1 else guest_id

    return GuestDossier(
        guest_id=guest_id,
        name=display_name,
        nationality=_extract_field(text, "Nationality"),
        arrival_property_id=_extract_field(text, "Arrival Property") or "rosewood-sand-hill",
        profile_summary=_extract_field(text, "Summary"),
        prior_stays=_extract_prior_stays(text),
    )


def build_property_card(property_id: str) -> PropertyCard:
    """
    Parse the property Markdown into a typed PropertyCard.
    The raw text is the source of truth; this is a convenience object.
    """
    text = load_property_card(property_id)
    h1 = re.search(r"^# Property Card:\s*(.+)", text, re.MULTILINE)
    display_name = h1.group(1).strip() if h1 else property_id

    depth_raw = _extract_field(text, "Depth").lower()
    depth = "arrival" if "arrival" in depth_raw else "provenance"

    return PropertyCard(
        property_id=property_id,
        name=display_name,
        location=_extract_field(text, "Location"),
        depth=depth,  # type: ignore[arg-type]
        sense_of_place=_extract_sense_of_place(text),
        signature_anchors=_extract_anchors(text),
    )


# ---------------------------------------------------------------------------
# Offline-replay plan loaders
# ---------------------------------------------------------------------------

def load_plan_json(filename: str) -> dict:
    """Load a JSON file from fixtures/plans/."""
    path = _FIXTURES / "plans" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def load_offline_response(replanned: bool = False) -> OrchestratorResponse:
    """
    Construct an OrchestratorResponse from fixture JSON files.
    Used by orchestrator in OFFLINE_MODE / Backend.REPLAY.
    BL-006: loads suppressions from the appropriate fixture file.
    """
    plan_file = "replanned_plan.json" if replanned else "baseline_plan.json"
    plan_data = load_plan_json(plan_file)
    synthesis_data = load_plan_json("synthesis_fixture.json")

    # BL-006: load suppressions fixture — separate from arrival_plan (never enters diff)
    suppressions_file = "replanned_suppressions.json" if replanned else "baseline_suppressions.json"
    try:
        suppressions_data = load_plan_json(suppressions_file)
        suppressions = [Suppression(**s) for s in suppressions_data]
    except (FileNotFoundError, KeyError, TypeError):
        suppressions = []

    return OrchestratorResponse(
        synthesis=GuestSynthesis(**synthesis_data),
        arrival_plan=ArrivalPlan(**plan_data),
        suppressions=suppressions,
    )


def load_delay_event() -> dict:
    """Load the injected delay event payload."""
    path = _FIXTURES / "delay_event.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Selector helpers (TREQ-022)
# ---------------------------------------------------------------------------

def list_dossier_slugs() -> list[str]:
    """Return slugs of all available dossier fixtures (scope-guarded set)."""
    return sorted(settings.ALLOWED_DOSSIERS)


def list_property_slugs() -> list[str]:
    """Return slugs of all available property fixtures (scope-guarded set)."""
    return sorted(settings.ALLOWED_PROPERTIES)
