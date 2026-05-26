> **Version:** v001.02
> **Last updated:** 2026-05-16
> **Source of truth** for Execution phase. History: [archive/](archive/)

# User Stories

> Locked from Discovery cycle 1. Acceptance criteria are injected into agent prompts at delegation time.

## US-001
- **Title:** As front-desk staff, I can see a role-specific arrival card so I know exactly how to greet the returning guest
- **Feature:** FEAT-001
- **Requirements:** TREQ-002, TREQ-003
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - Loading the dashboard renders an arrival mood banner and a Front Desk card with `arrival mode`, `action`, and `do-not` fields
  - All six role cards (valet, front desk, dining, housekeeping, concierge, MOD) are present
  - Card content reflects Ms. Chen's preferences from the fixture (not generic copy)

## US-002
- **Title:** As a hotel operator, I can inject a flight delay and watch the arrival plan re-choreograph live
- **Feature:** FEAT-002
- **Requirements:** TREQ-005, TREQ-006
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - A single visible control injects the delay event
  - Affected role cards and the mood banner update in under ~10 seconds
  - No full-page reload is required (HTMX fragment swap)

## US-003
- **Title:** As a judge/observer, I can see exactly what changed and why between the baseline and the re-plan
- **Feature:** FEAT-002
- **Requirements:** TREQ-006
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - The diff panel lists each change with its trigger and a one-line reason
  - Baseline vs. re-plan deltas are unambiguous at a glance from across a room
  - The panel renders even in offline/fixture mode

## US-004
- **Title:** As staff, I can leave a voice or typed observation and see the relevant role cards update
- **Feature:** FEAT-004
- **Requirements:** TREQ-010, TREQ-011
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - A typed observation submitted via textarea updates the correct role cards (P0 path)
  - The same server endpoint backs both typed and mic-captured input
  - Mic capture, when available, transcribes via server-side STT and follows the identical path (P1)
  - An ambiguous note routes to a sensible default without crashing

## US-005
- **Title:** As staff, I can play an audio briefing of my role card
- **Feature:** FEAT-004
- **Requirements:** TREQ-009
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - At least one role card has a working "Play Briefing" control
  - Audio is generated from the card's current text via ElevenLabs TTS
  - Playback works after a re-plan (reads the updated briefing)

## US-006
- **Title:** As the concierge, I can see what the system chose NOT to suggest and why
- **Feature:** FEAT-003
- **Requirements:** TREQ-007
- **Status:** LOCKED
- **Priority:** P1
- **Acceptance Criteria:**
  - The suppression panel lists at least one withheld suggestion with a reason
  - Suppressions change appropriately after the delay re-plan (e.g., spa/activity held)

## US-007
- **Title:** As the demo presenter, I can run the entire demo deterministically with zero network
- **Feature:** FEAT-005
- **Requirements:** TREQ-013, TREQ-017
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - An env/UI toggle switches between Claude cloud, Ollama local, and fixture-replay with no code change
  - In fixture-replay mode the full demo (baseline → re-plan → diff → at least one TTS) runs with no outbound calls
  - The offline path is rehearsed and documented in the demo playbook

## US-008
- **Title:** As a returning guest (Ms. Chen), my arrival reflects my past preferences and Rosewood Sand Hill's sense of place
- **Feature:** FEAT-001
- **Requirements:** TREQ-004
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - At least two outputs reference named Sand Hill anchors (e.g., Asaya Spa, Madera, Flamingo Estate tea, Ridge Rosé, Bluejay Bikes)
  - References are contextually appropriate to the guest's mood/preferences, not generic name-drops

## US-009
- **Title:** As a judge, I can verify the public repo names Problem Statement #1 and the built-today scope
- **Feature:** FEAT-007
- **Requirements:** TREQ-015
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - The repo is public
  - The README states "Problem Statement #1: Hyper-Personalized Arrival Orchestration" and an explicit built-today scope section
  - Commit history reflects work done during the event window

## US-010
- **Title:** As the demo presenter, I can show a room-legible dashboard that a judge can read from across the room
- **Feature:** FEAT-006
- **Requirements:** TREQ-018
- **Status:** LOCKED
- **Priority:** P1
- **Acceptance Criteria:**
  - Three clear panels: inputs/triggers · mood + diff + suppression · role cards with Play Briefing
  - High-contrast, large-font; primary actions (inject delay, submit observation, play briefing) are single-click and obvious
  - Layout holds without horizontal scroll on a typical laptop/projector resolution

## US-011
- **Title:** As staff at any Rosewood property, my observations about a guest are recorded on their dossier so future arrivals at any property reflect them
- **Feature:** FEAT-008
- **Requirements:** TREQ-020
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - A guest dossier holds >=2 prior stays, each tagged with a Rosewood property and that site's staff observations
  - Dossier and property cards are Markdown files generated from a documented template
  - Editing a card's Markdown changes the next render with no code change

## US-012
- **Title:** As a returning guest, my arrival reflects a unified understanding synthesized across my prior stays at different Rosewood properties
- **Feature:** FEAT-008
- **Requirements:** TREQ-021, TREQ-019
- **Status:** LOCKED
- **Priority:** P0
- **Acceptance Criteria:**
  - The arrival plan visibly reflects >=2 inferred traits derived from cross-property prior observations (e.g., cyclist, theatre-goer)
  - The UI surfaces an explicit "inferred from prior stays" element naming the source property/observation
  - Synthesis runs without displacing or delaying the never-cut re-plan diff spine
  - Works for all 3 seeded guest dossiers across the 3-property fixture set

## US-013
- **Title:** As the builder/presenter, I can switch the active guest/property to tune the final demo profile and show multi-property on request
- **Feature:** FEAT-009
- **Requirements:** TREQ-022
- **Status:** LOCKED
- **Priority:** P1
- **Acceptance Criteria:**
  - A selector swaps the active guest and arrival property and re-renders via the existing path
  - The rehearsed 3-min demo does not depend on the selector (single-path safe)
  - No card creation or editing happens through the UI (Markdown-file workflow only)

## US-014
- **Title:** As staff, when I leave a voice or typed observation during the visit, it is added to the guest's dossier and the arrival immediately re-choreographs to reflect it
- **Feature:** FEAT-008
- **Requirements:** TREQ-023, TREQ-021
- **Status:** LOCKED
- **Priority:** P1
- **Acceptance Criteria:**
  - A staff voice or typed note captured live is visibly appended to the on-screen guest dossier panel
  - The cross-visit synthesis re-runs and the arrival plan / affected role cards update
  - The what-changed diff reflects the new observation as the trigger
  - The loop runs in-session (in-memory) without disk persistence and does not block or delay the never-cut spine
