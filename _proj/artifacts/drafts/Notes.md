# Notes

**Updated:** 2026-05-16

---

**Topic:** Hackathon constraints (Hospitality 2030 @ Rosewood Sand Hill)
**Date:** 2026-05-16
**Info:** Problem Statement #1 — Hyper-Personalized Arrival Orchestration. Hacking 10:30 AM, submissions due **5:00 PM** (hard, no post-deadline hardening — Round 1 judging starts 5:00 PM in separate rooms). Round 1 weights: Live Demo 45% / Creativity 35% / Impact 20%; ~3-min live demo + 1–2 min Q&A; top 6 → Round 2 (equal weights). Public repo required; only built-today work counts; **Streamlit banned**; basic RAG/chatbot = anti-projects; synthetic/rights-cleared data only. Sponsors: Anthropic, ElevenLabs, Greycroft.
**Related DDs:** DD-001, DD-003

---

**Topic:** Locked product concept
**Date:** 2026-05-16
**Info:** "First Five Minutes by SenseArrival" — arrival **choreography engine** (not a chatbot). Inputs: guest profile + arrival context + staff observations. Outputs: arrival mood, role-based staff cards (valet, front desk, dining, housekeeping, concierge, MOD), suppression panel ("what NOT to offer"), optional guest message, "what changed & why" diff. Headline demo branch = **Delay-to-Delight** (baseline → inject delay → re-plan → staff voice note → cards update → diff → TTS revised briefing). Persona = returning guest "Ms. Chen". Sand Hill local anchors: Asaya Spa, Madera, Afternoon Tea w/ Flamingo Estate, Ridge Rosé Reveal, Friday Nights @ Madera, Bluejay Bikes.
**Related DDs:** DD-001, DD-002

---

**Topic:** Stack decision (architect ADR-001)
**Date:** 2026-05-16
**Info:** Recommended: **Python 3.11 + FastAPI + Jinja2/HTMX + Anthropic SDK + ElevenLabs Python SDK + Pydantic v2**, single-process, no frontend build. Browser mic → `MediaRecorder` → POST → ElevenLabs Scribe STT (server-side), with **mandatory typed-text fallback** on the same code path. Cut order: never cut re-plan diff; cut mic STT → guest message → suppression panel last. Full ADR: `_proj/deliverables/02-architecture/adr/ADR-001-stack-selection.md`.
**Related DDs:** DD-004 (LOCKED)

---

**Topic:** LLM resilience — 3-tier pluggable backend
**Date:** 2026-05-16
**Info:** User confirmed **Ollama is running locally** on the demo machine. Resilience tiers, switchable by env/UI with no code change: **(1) Anthropic Claude cloud = primary/showcased path** (expected robust; Anthropic is a sponsor → also aids Creativity/Impact framing); **(2) Ollama local = dynamic fallback** — keeps the re-plan genuinely "live" with zero network if cloud is hostile; **(3) fixture-replay OFFLINE_MODE = deterministic last resort** (pre-computed baseline/replan JSON, cached TTS MP3). Test all three before the judging room; demo on Claude unless network proves unstable.
**Related DDs:** DD-004

---

**Topic:** Execution State Snapshot — Re-Discovery Entry (cycle 2)
**Date:** 2026-05-16
**Info:** Paused execution to run discovery cycle 2 (scope widening). Action plan at pause: no completed phases; no in-progress phase (all 6 freshly created, none started); pending = Phase 1 Foundation, Phase 2 Orchestration Core, Phase 3 Re-plan & Diff, Phase 4 Compliance, Phase 5 Voice, Phase 6 Polish. Backlog BL-001..BL-007 all Ready, none started. Working branch: build/sense-arrival-mvp. Registry last updated 2026-05-16 (1 completed: ADR-001). No code written yet — cost of re-locking now is near zero.
**Related DDs:** DD-005, DD-006, DD-007

---

**Topic:** Card data format decision (input vs replay)
**Date:** 2026-05-16
**Info:** Guest dossiers + property "sense of place" cards = **Markdown, one file each, template-driven** — human-editable, diff-friendly, judge-visible, loaded as raw prompt context (Claude reads prose; no parser). Output/offline-replay fixtures (baseline_plan.json, replanned_plan.json) **stay JSON** for deterministic Pydantic-validated replay. **No runtime chat-to-create/edit subsystem** (scope-creep guard): "new guest" = copy template .md; editing = edit the .md (optional hot-reload). Makes profile-tuning to pick the final demo guest trivial.
**Related DDs:** DD-006

---

**Topic:** Authoritative requirement validation — Radha Arora, President, Rosewood Hotels & Resorts
**Date:** 2026-05-16
**Info:** Direct source statement (user conversation): (1) Rosewood **manually collects** each customer's data into a profile; (2) tailor the visit to **BOTH the guest profile AND the local culture / activities of where the hotel is located**; (3) hence the importance of **both customer cards and hotel cards** — basis of the hackathon request/rules. Implications: the dual-card model (guest dossier + per-property local-culture card) is the validated CORE of Problem Statement #1, not scope creep — resolves the earlier ADR-001 narrow-slice-vs-breadth tension. "Manually collect into a profile" implies a staff-collection → persistent-profile loop, not only session-scoped card updates. "Local culture/activities of where the hotel is located" makes the hotel card destination-culture-centric (e.g., Broadway/theatre for The Carlyle), broader than on-property amenities.
**Related DDs:** DD-005, DD-006
**Related TREQs:** TREQ-019, TREQ-020, TREQ-021

<!-- Notes Format Reference
  Core fields (required on every note):
    Topic, Info, Related DDs

  Optional fields:
    Date        — when the note was captured (use for snapshots and dated events)
    Active RFCs — cross-reference to open RFCs when applicable

  Entries are separated by --- dividers.
  Timestamp the file (Updated header) on each update.
  Only append new information — do not re-log already captured content.
-->
