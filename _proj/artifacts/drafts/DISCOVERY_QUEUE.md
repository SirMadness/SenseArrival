# Discovery Queue

> Observations logged during execution. Normal DQs batch at next /discover; blocking DQs surface in /status and halt associated BL items until resolved. See TREQ-023.
>
> **DQ fields**: Status (first field), Title, Area, Observed, Description, Impact, Estimated scope, **Urgency** (normal|blocking, default normal), **Blocks** (BL-### required when Urgency=blocking).

<!-- DQ Format Reference
  Lifecycle state field (first body field, required on every DQ):
    Status  — pending (default) | promoted | resolved
             Canonical source of truth for lifecycle. Used by discovery-status.sh counts.

  Core fields (required on every DQ):
    Title, Area, Observed, Description, Impact, Estimated scope

  Urgency fields (required on new DQs, implicit normal on legacy entries):
    Urgency  — normal (default) | blocking
    Blocks   — BL-### (required when Urgency=blocking)

  Pointer fields (added when DQ is promoted or resolved):
    Promoted to   — DD-### reference when promoted to a Discussion Point
    Resolved via  — BL-###/TD-### reference when resolved directly

  Optional annotation fields:
    Note     — additional context or considerations
    Related  — cross-references to other DQs or TDs

  DQ heading format: plain "## DQ-###" (no suffix).
  Status is tracked in the body Status field, not in the heading.

  Example entry:
    ## DQ-001
    - **Status:** pending
    - **Title:** Short title of the observation
    - **Area:** Architecture
    - **Observed:** 2026-01-01
    - **Description:** What was observed and why it matters.
    - **Impact:** Non-blocking — triage quality improvement
    - **Estimated scope:** Low
    - **Urgency:** normal
    - **Blocks:** _none_
-->

## DQ-001
- **Status:** pending
- **Title:** Guest personality archetype taxonomy for dossiers
- **Area:** Product / Domain Model
- **Observed:** 2026-05-16
- **Description:** Introduce a guest-archetype layer classifying each dossier by TRAVEL INTENT / emotional register (not demographics), giving staff a shared vocabulary and the orchestration engine archetype-level choreography defaults. Proposed intent-based set (refine in /discover): Restorer (Ms. Chen — decompress/recover, high autonomy, protect solitude); Connoisseur (James Okafor — collector-grade taste depth, match domain expertise); Scholar/Origin-Seeker (Priya Nair — provenance & learning driven, behind-the-scenes); Celebrant (occasion/milestone, e.g. anniversary/honeymoon — recognition + signature moment); Legacy Host (multigenerational/family group dynamic); Working Traveler (business-anchored, time-compressed, friction removal + reclaimed delight). Deliberately replaces the weaker demographic draft (Young Power Couple / Wellness Pilgrim / Family Legacy / Elder Affluent / Founder Recovery): intent-based labels are actionable for first-five-minutes choreography and non-presumptuous. CONSTRAINT: must remain a Markdown dossier-section convention — NO parser / structured schema (preserves locked 'raw MD as prompt context, no parser' rule per CLAUDE.md / TREQ-019 scope guard). Pairs with the preference-category DQ.
- **Impact:** Non-blocking — post-MVP domain enrichment; queued for next /discover cycle. Does NOT touch the locked/finalized demo path. Creativity-axis feature, strictly behind the never-cut spine.
- **Estimated scope:** Medium
- **Urgency:** normal
- **Blocks:** _none_

## DQ-002
- **Status:** pending
- **Title:** Structured preference categories within guest dossiers
- **Area:** Product / Domain Model
- **Observed:** 2026-05-16
- **Description:** Break dossier preference signal into named CATEGORIES so authoring is consistent across guests and the orchestration engine can reason per-dimension instead of from a prose blob. Proposed categories (refine in /discover): (1) Dining & Provenance — cuisine, dietary, beverage/wine depth, meal timing, in-suite vs venue, sourcing interest; (2) Activities & Recreation — athletic/endurance, cultural/performance, art/museum, nature/outdoor, wellness/spa; (3) Room & Ambiance — light, view, floor/height, noise, scent, materials; (4) Rhythm & Pacing — early riser, post-show late dining, solitude windows, do-not-disturb patterns, working breakfast; (5) Mobility & Transport — self-directed walking, declines drivers, bike, private transfer; (6) Engagement Style — autonomy vs concierge-led, depth of staff interaction, recognition vs discretion; (7) Reading & Information — newspapers, briefing materials. CONSTRAINT: implement as headed Markdown sections in the dossier template — human-editable, loaded as raw prompt context, NO parser / schema (TREQ-019 scope guard, ADR-002 raw-MD model preserved). Companion to DQ-001: archetype = WHY they travel; preference categories = HOW each dimension should be handled. Related: DQ-001.
- **Impact:** Non-blocking — post-MVP; queued for next /discover cycle. Locked/finalized demo unaffected. Improves dossier authoring consistency and gives the engine per-dimension preference signal.
- **Estimated scope:** Medium
- **Urgency:** normal
- **Blocks:** _none_

## DQ-003
- **Status:** pending
- **Title:** Stay timeline: timestamped status cards across the guest journey
- **Area:** Product / Domain Model
- **Observed:** 2026-05-16
- **Description:** Concierge-facing chronological timeline of the guest's stay — a sequence of cards spanning travel-to / arrival / check-in / dining / activities / spa / departure, each with a timestamp and a status (occurred | in-progress | scheduled). Gives the concierge one view of what has happened vs what is upcoming. Cards mutate on two event types: guest REQUESTS ('clean towels please' -> adds a scheduled card) and guest COMPLETIONS ('went to a concert' -> flips a card to occurred). UPDATE MECHANISM is a natural extension of the existing BL-005 typed-text staff-observation path (classify -> HTMX card update) — that ingestion seam already exists; this generalizes it from one-shot re-plan to an append/update event log over a stay. RELATIONSHIP: complements TREQ-006 — the never-cut diff is the per-replan DELTA; this timeline is the stay-long LEDGER those deltas write into. ARCHITECTURAL TENSION (must resolve before any build, likely a new ADR): introduces MUTABLE STATEFUL SESSION STATE — a departure from the stateless deterministic fixtures-in/ArrivalPlan-out model — and edges toward the locked 'no CRUD / no chat-edit UI' anti-project boundary. Open decisions for /discover to decompose: (a) state model — in-memory session vs fixture-seeded replayable event log; (b) how to stay demo-deterministic & zero-network replayable for offline judging; (c) crisp delineation from a chatbot/CRUD/PMS app so it stays a choreography view not a ticketing system; (d) scope of journey stages in demo. CONSTRAINT: events are fixture/replay-seeded scripted demo beats, NOT live PMS/flight/weather feeds (TREQ-019 scope guard preserved). Timeline cards should reuse the DQ-002 preference categories and DQ-001 archetype framing. Related: DQ-001, DQ-002.
- **Impact:** Non-blocking — post-MVP creativity-axis feature, strictly behind the never-cut spine; queued for next /discover. Locked/finalized demo path untouched. Largest of the queued DQs: requires an architect ADR (stateful session model + anti-project boundary) before implementation.
- **Estimated scope:** High
- **Urgency:** normal
- **Blocks:** _none_
