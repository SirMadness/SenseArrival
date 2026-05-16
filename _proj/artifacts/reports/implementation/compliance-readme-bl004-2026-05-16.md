# Implementation: BL-004 Compliance README + Demo Playbook

## Summary

Produced two documentation artifacts for the hackathon submission:
1. `README.md` at repo root — the public judging artifact. Names PS#1 explicitly, frames the dual-card model as the architectural answer to it, states the honest built-today scope, and provides an offline-safe quickstart command.
2. `_proj/deliverables/04-guides/demo-playbook.md` — the demo-readiness and resilience playbook. Contains the tight 3-minute Delay-to-Delight script, the ADR-001 cut order (NEVER cut the diff), tier-switching guidance, contingency responses, and pre-demo offline rehearsal checklist.

Both artifacts are accurate to the actual built state as of commit `3115007` (BL-003 critical fixes). No capabilities are overclaimed.

## Changes Made

| File | Change Type | Description |
|------|-------------|-------------|
| `README.md` | Added | Repo-root public README: PS#1 framing, dual-card model, built-today scope table, current status, offline quickstart, configuration table, stack overview |
| `_proj/deliverables/04-guides/demo-playbook.md` | Added | Demo playbook: pre-demo checklist, 3-min script with time targets, cut order table, tier-switching guide, contingency responses, Q&A prep, sections needing final pass, user action items |

## Acceptance Criteria Coverage

| Criterion | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| TREQ-015 / US-009: README names PS#1 explicitly | "Problem Statement #1: Hyper-Personalized Arrival Orchestration" in README | Met | README header line 3; also in Hackathon section at foot |
| TREQ-015 / US-009: "Built Today" scope section | Explicit section with table: what is built, what is synthetic/fixture, what is out of scope | Met | "Built Today (2026-05-16) — Honest Scope" section with 3 subsections and table |
| TREQ-015 / US-009: Offline-safe quickstart | `OFFLINE_MODE=true uvicorn sense_arrival.main:app` command | Met | Quickstart → "Offline-safe demo (zero network required)" subsection |
| TREQ-015 / US-009: Honest current status | Spine COMPLETE / voice-synthesis-polish in progress or cuttable | Met | "Current Status" section explicitly states spine complete, names BL-005/008/006 as in-progress/cuttable |
| TREQ-024: Dual-card model framed as PS#1 answer | Dual-card model section referencing Radha Arora validation | Met | "The Answer to Problem Statement #1: The Dual-Card Model" section; Radha Arora named and role stated; both card types defined |
| TREQ-017: Demo playbook with ~3-min script | Timed Delay-to-Delight script | Met | "3-Minute Demo Script" with 0:00–3:00 time targets per segment |
| TREQ-017: Cut order matching ADR-001, NEVER cut TREQ-006 | Cut order table with NEVER CUT = diff panel | Met | "Cut Order" table; first row: NEVER CUT — Re-plan diff panel |
| TREQ-017: Backup asset guidance | Checklist item for screenshots/GIF | Met | Pre-Demo Checklist "Backup assets" block; also in User Action Items |
| TREQ-017: Offline rehearsal checklist | Pre-demo checklist covering env, HTMX, tier switching | Met | "Pre-Demo Checklist" section with Environment, Fallback verification, Network-available, and Backup assets blocks |
| TREQ-017: Sections needing final pass flagged | Final-pass sections marked before 5PM | Met | "Sections Needing Final Pass Before 5PM" section explicitly marks voice TTS step, staff note → synthesis, selector demo |

## User Action Items (Flag prominently)

**These must be done by the builder before 5PM. The build system cannot do them.**

1. **Make GitHub repo public** — go to `https://github.com/SirMadness/SenseArrival` → Settings → Danger Zone → Change visibility → Public. Required by hackathon rules. Judges check.

2. **Capture backup screenshots and GIF** — with `OFFLINE_MODE=true` running: screenshot the baseline dashboard, screenshot the post-replan state with diff panel, and capture a GIF or screen recording of the full Inject Delay → diff flow. Store locally, not only on the running server.

## Flagged Items

- DQ: The GitHub repo at `https://github.com/SirMadness/SenseArrival` must be **public** before judges access it. The Docs agent cannot change repo visibility — this is a required user action before 5PM.
- DQ: Backup screenshot/GIF capture requires the running app and a screen capture tool. This must be done by the builder, not the build system. Explicitly listed as a user action item in both the playbook and this report.
- TD: `static/audio/briefing_cached.mp3` is absent (noted from BL-001, BL-002, BL-003 follow-up items). The TTS "Play Briefing" button is present in the UI but returns a silent stub in OFFLINE_MODE. README correctly states TTS is "stubbed" in the built-today scope table. Demo playbook cut order lists TTS as "cut if needed" so a missing audio file does not break the demo narrative.
- TD: The README dual-card model section references "The Carlyle New York" and "Castiglion del Bosco" as provenance properties — matching the reconciled fixture set from BL-001. This differs from the ADR-002 Delta 5 illustrative names (Rosewood London + Rosewood Beijing). The README is accurate to the actual fixtures built.
- BLOCKER: None. All acceptance criteria satisfiable from actual built state. No overclaiming required.

## Reasoning

**Scope accuracy decisions:**

1. The built-today table explicitly marks guest/property selector, voice TTS, and browser mic STT as "Stubbed" — matching the BL-001/BL-002 Known Limitations sections. Describing these as "complete" would be a disqualification risk since judges can run the app.

2. The dual-card section names Radha Arora's title and organization accurately per the Notes.md entry. The framing is factual, not promotional.

3. The diff panel is explicitly labeled NEVER CUT in the playbook cut order table, matching ADR-001's "never cut item 1" instruction verbatim.

4. Demo script time targets (0:30, 1:00, 1:45, 2:15, 2:45, 3:00) are tuned to the actual content depth. The inject-delay moment is allocated the most time (0:45 of 3:00) because it is the 45%-weighted Live Demo differentiator.

5. Tier-3 (OFFLINE_MODE) is recommended as the entry-room default, not Claude live. This matches the resilience reasoning in Notes.md and ADR-001 ("Test in offline mode before walking into the judging room. Switch to live mode only if the network is confirmed stable").

**Constraints applied:** documentation only; accurate over impressive; no code or fixture modifications; user action items flagged explicitly.

**Confidence:** High. Both documents are accurate to the actual implemented state (BL-001 through BL-003 + critical fixes, commits b0317ae → 38f766f → 62030fa → 3115007). No feature is claimed built that is not verified in the implementation reports.

## Commit SHA:

> Docs-only commit pending. Files written: `README.md` (repo root) and `_proj/deliverables/04-guides/demo-playbook.md`. No code, fixture, or state file changes. Commit on branch `build/sense-arrival-mvp` is a user action — add and commit both files before 5PM submission.
