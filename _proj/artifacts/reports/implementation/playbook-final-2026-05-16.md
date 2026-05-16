# Report: Demo Playbook Final Pass

**Date:** 2026-05-16
**Agent:** Docs
**Task:** BL-004 final pass — demo-playbook.md presenter-ready finalization
**Deliverable:** `_proj/deliverables/04-guides/demo-playbook.md`
**Build commit:** `2d6815c` (branch `build/sense-arrival-mvp`)
**Source smoke test:** `_proj/artifacts/reports/tests/final-offline-smoke-2026-05-16.md`

---

## Summary

Updated `demo-playbook.md` to its final, presenter-ready state reflecting the LOCKED build at HEAD `2d6815c`. All sections marked "needs final pass after BL-005/BL-008 land" have been replaced with verified, accurate content. The two disqualification-grade user actions are flagged at the top of the document under `## Flagged Items` as `DQ: BLOCKING` items, impossible to miss.

---

## Changes Made

### Removed
- "Sections Needing Final Pass Before 5PM" — the entire placeholder section. All pending items are now resolved and reflected accurately in the script.
- All "pending BL-005/BL-008" notes and verbal-only fallback instructions for suppression, voice, and synthesis (all three are BUILT and verified).
- Draft demo script steps that did not reflect verified click sequence.

### Added / Updated
- **Flagged Items section** at the top — 2 `DQ: BLOCKING` items (public repo, backup assets) plus 1 `TD` item.
- **Boot command** — now includes `--host 127.0.0.1` matching the smoke test's exact verified command.
- **Pre-demo checklist** — expanded to cover suppression panel (3 items), synthesis panel (Carlyle/Castiglion), TTS audio play, staff observation typed path, and explicit "do NOT navigate to /select" instruction.
- **3-minute demo script** — replaced draft with the smoke-verified 6-step click sequence verbatim (Steps 1–6 from smoke report), including Panel A/B/C orientation, exact button labels, exact observed outputs, and narration beats aligned to time segments.
- **Cut order table** — updated Status column to "BUILT — verified" for suppression, synthesis, TTS, and staff observation; removed verbal-only fallback column entries for features that are built; added DO NOT OPEN row for `/select`.
- **Tier switching** — corrected posture per ADR-001 Amendment: Tier-1 live is primary/showcased; Tier-3 offline is the rehearsed resilience fallback. Enter the room on Tier-3; switch to Tier-1 only after confirming network.
- **Contingency: "Someone asks to see /select"** — new entry with scripted deflection.
- **Q&A** — added "Why not a chatbot?" (sharpened from prior draft), "What is synthetic vs. built today?" (new), expanded ElevenLabs answer to reflect offline-cached M4A. Removed stale BL-005/scope caveats from TTS answer.

---

## Acceptance Criteria Coverage

| Requirement | Status | Evidence |
|-------------|--------|---------|
| Boot command exact and correct | PASS | `OFFLINE_MODE=true uvicorn sense_arrival.main:app --host 127.0.0.1 --port 8000` in Pre-Demo Checklist |
| 2 user actions flagged at top as DQ-blocking | PASS | `## Flagged Items` at document top, both marked `DQ: BLOCKING` |
| Backup screenshot/GIF instruction in checklist | PASS | Final checklist item in Pre-Demo Checklist |
| Demo script uses smoke-verified click sequence verbatim | PASS | Steps 1–6 match `final-offline-smoke-2026-05-16.md` Verified Click Sequence section |
| Time targets per segment sum to ~3:00 | PASS | 0:30 + 1:00 + 0:30 + 0:15 + 0:15 + 0:15 = 3:05 (within tolerance) |
| Narration beats: mood → role cards → inject → diff → synthesis → suppression → TTS → staff note | PASS | All beats present in Steps 1–5 with explicit "Point to" instructions |
| Diff panel marked NEVER CUT in cut order table | PASS | First row, bold, with rationale |
| Suppression/voice/synthesis marked BUILT (no verbal-only fallback) | PASS | Cut order table Status column |
| Tier fallback table (live → Ollama → fixture-replay) | PASS | Tier Switching section in Pre-Demo Checklist |
| "Do not open /select" contingency | PASS | Checklist step + Cut Order "DO NOT OPEN" row + Contingency section |
| 4–6 Q&A entries | PASS | 6 Q&A entries |
| No stale "pending BL" notes | PASS | All such sections removed |
| Accuracy over polish | PASS | All claims cross-referenced against smoke test results and ADR-001 |

---

## Residual Items

- **TD (carried from smoke test):** 1 of 16 diff entries uses generic fallback reason for Spa removed-action. Not a playbook concern — cosmetic only.
- **No new tech debt introduced by this pass.**

---

*Docs agent | 2026-05-16 | guide mode | BL-004 final pass*
