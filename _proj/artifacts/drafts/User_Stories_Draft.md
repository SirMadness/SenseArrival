# User Stories

<!-- US Format Reference
  Core fields: Title, Feature, Requirements, Status, Priority, Acceptance Criteria
  Title format: "As [role], I can [action]"
  Acceptance criteria are injected into agent prompts at delegation time.
  Graduated to deliverables/01-requirements/user-stories.md during reconciliation.
-->

## US-001
- **Title:** As front-desk staff, I can see a role-specific arrival card so I know exactly how to greet the returning guest
- **Feature:** FEAT-001
- **Requirements:** TREQ-002, TREQ-003
- **Status:** MIGRATED
- **Priority:** P0
- **Acceptance Criteria:**
  - Loading the dashboard renders an arrival mood banner and a Front Desk card with `arrival mode`, `action`, and `do-not` fields
  - All six role cards (valet, front desk, dining, housekeeping, concierge, MOD) are present
  - Card content reflects Ms. Chen's preferences from the fixture (not generic copy)

## US-002
- **Title:** As a hotel operator, I can inject a flight delay and watch the arrival plan re-choreograph live
- **Feature:** FEAT-002
- **Requirements:** TREQ-005, TREQ-006
- **Status:** MIGRATED
- **Priority:** P0
- **Acceptance Criteria:**
  - A single visible control injects the delay event
  - Affected role cards and the mood banner update in under ~10 seconds
  - No full-page reload is required (HTMX fragment swap)

## US-003
- **Title:** As a judge/observer, I can see exactly what changed and why between the baseline and the re-plan
- **Feature:** FEAT-002
- **Requirements:** TREQ-006
- **Status:** MIGRATED
- **Priority:** P0
- **Acceptance Criteria:**
  - The diff panel lists each change with its trigger and a one-line reason
  - Baseline vs. re-plan deltas are unambiguous at a glance from across a room
  - The panel renders even in offline/fixture mode

## US-004
- **Title:** As staff, I can leave a voice or typed observation and see the relevant role cards update
- **Feature:** FEAT-004
- **Requirements:** TREQ-010, TREQ-011
- **Status:** MIGRATED
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
- **Status:** MIGRATED
- **Priority:** P0
- **Acceptance Criteria:**
  - At least one role card has a working "Play Briefing" control
  - Audio is generated from the card's current text via ElevenLabs TTS
  - Playback works after a re-plan (reads the updated briefing)

## US-006
- **Title:** As the concierge, I can see what the system chose NOT to suggest and why
- **Feature:** FEAT-003
- **Requirements:** TREQ-007
- **Status:** MIGRATED
- **Priority:** P1
- **Acceptance Criteria:**
  - The suppression panel lists at least one withheld suggestion with a reason
  - Suppressions change appropriately after the delay re-plan (e.g., spa/activity held)

## US-007
- **Title:** As the demo presenter, I can run the entire demo deterministically with zero network
- **Feature:** FEAT-005
- **Requirements:** TREQ-013, TREQ-017
- **Status:** MIGRATED
- **Priority:** P0
- **Acceptance Criteria:**
  - An env/UI toggle switches between Claude cloud, Ollama local, and fixture-replay with no code change
  - In fixture-replay mode the full demo (baseline → re-plan → diff → at least one TTS) runs with no outbound calls
  - The offline path is rehearsed and documented in the demo playbook

## US-008
- **Title:** As a returning guest (Ms. Chen), my arrival reflects my past preferences and Rosewood Sand Hill's sense of place
- **Feature:** FEAT-001
- **Requirements:** TREQ-004
- **Status:** MIGRATED
- **Priority:** P0
- **Acceptance Criteria:**
  - At least two outputs reference named Sand Hill anchors (e.g., Asaya Spa, Madera, Flamingo Estate tea, Ridge Rosé, Bluejay Bikes)
  - References are contextually appropriate to the guest's mood/preferences, not generic name-drops

## US-009
- **Title:** As a judge, I can verify the public repo names Problem Statement #1 and the built-today scope
- **Feature:** FEAT-007
- **Requirements:** TREQ-015
- **Status:** MIGRATED
- **Priority:** P0
- **Acceptance Criteria:**
  - The repo is public
  - The README states "Problem Statement #1: Hyper-Personalized Arrival Orchestration" and an explicit built-today scope section
  - Commit history reflects work done during the event window

## US-010
- **Title:** As the demo presenter, I can show a room-legible dashboard that a judge can read from across the room
- **Feature:** FEAT-006
- **Requirements:** TREQ-018
- **Status:** MIGRATED
- **Priority:** P1
- **Acceptance Criteria:**
  - Three clear panels: inputs/triggers · mood + diff + suppression · role cards with Play Briefing
  - High-contrast, large-font; primary actions (inject delay, submit observation, play briefing) are single-click and obvious
  - Layout holds without horizontal scroll on a typical laptop/projector resolution
