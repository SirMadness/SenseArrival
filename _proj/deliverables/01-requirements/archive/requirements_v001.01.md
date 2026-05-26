> **Version:** v001.01
> **Last updated:** 2026-05-16
> **Source of truth** for Execution phase. History: [archive/](archive/)

# Requirements

> **Project:** SenseArrival "First Five Minutes" — Hospitality 2030 @ Rosewood Sand Hill, Problem Statement #1 (Hyper-Personalized Arrival Orchestration). Solo builder, ~6 hr, hard 5:00 PM submission.
> **Priority lens:** P0 = demo-critical spine for the 45% Live Demo weight. P1 = enhancer/cuttable per ADR-001 cut order. NEVER cut TREQ-006.
> Locked from Discovery cycle 1 (DD-001..DD-004). First cycle — no prior baseline to archive.

## TREQ-001
- **Title:** Arrival Plan Orchestrator generates a structured arrival plan from guest profile + arrival context (+ staff signals)
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-001, DD-004
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** The orchestrator is the product. Without a single call that turns fixtures into a coherent ArrivalPlan, there is no demo. Must be a deterministic, schema-validated transform, not a chat loop (avoids the banned chatbot/RAG anti-pattern).

## TREQ-002
- **Title:** Role-based staff cards rendered for six roles (valet, front desk, dining, housekeeping, concierge, manager-on-duty)
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-001
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Role cards (arrival mode / action / do-not) are the visible artifact that proves "choreography engine, not chatbot." Six cards give the 3-min demo visual completeness even if some are concise.

## TREQ-003
- **Title:** Arrival mood is classified and shown as a banner (e.g., Quiet, Restorative, Recovery, Celebratory, Work-Mode, Family Landing)
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-001
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** One-line mood label is the emotional through-line judges grasp instantly; trivial cost, high narrative payoff.

## TREQ-004
- **Title:** Outputs are grounded in Rosewood Sand Hill "Sense of Place" anchors from a property-context fixture
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-001
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Specific local anchors (Asaya Spa, Madera, Afternoon Tea with Flamingo Estate, Ridge Rosé Reveal, Friday Nights @ Madera, Bluejay Bikes) are the cheapest, highest-yield lever for the 35% Creativity/Originality weight. Generic luxury copy loses.

## TREQ-005
- **Title:** Manual delay-injection trigger causes a live re-plan of the arrival
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-001
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Delay-to-Delight is the locked headline branch. The one-click before/after is the magic moment for the 45% Live Demo weight; must run in <~10s.

## TREQ-006
- **Title:** "What changed & why" diff / audit panel shows baseline vs. re-plan deltas with trigger and reason
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-001
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** This is the creative proof that the system acts on changing context rather than emitting static prose. Per ADR-001 this is the single NEVER-CUT item.

## TREQ-007
- **Title:** Suppression panel surfaces recommendations the system chose NOT to make, with reasons
- **Priority:** P1
- **Status:** LOCKED
- **Source:** DD-001
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** "Tasteful restraint" directly answers the event's "they just knew vs. that's creepy" theme — strong originality. Cuttable: verbalize in the pitch if not rendered.

## TREQ-008
- **Title:** Optional guest-facing message preview (SMS-style, no real send)
- **Priority:** P1
- **Status:** LOCKED
- **Source:** DD-001, DD-003
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Adds hospitality warmth and shows guest-facing tone without Twilio/identity/PMS integration risk. Preview only — real send is explicitly out of scope.

## TREQ-009
- **Title:** ElevenLabs TTS "Play Briefing" reads a role card's briefing aloud
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-002
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Lowest-risk voice feature (TTS over already-generated text); sponsor (ElevenLabs) alignment and a memorable "Hospitality 2030" moment. ADR-001 keeps at least one card's TTS regardless of cuts.

## TREQ-010
- **Title:** Staff voice-note capture: browser mic → server-side ElevenLabs Scribe STT → classify → re-route → update affected role cards
- **Priority:** P1
- **Status:** LOCKED
- **Source:** DD-002
- **Relationship:** EXTENDS TREQ-011
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** "Staff as sensors, AI as coordinator" is the most differentiated workflow. Mic is the only live-audio risk → it EXTENDS the typed-text path (TREQ-011) and is cuttable to it.

## TREQ-011
- **Title:** Typed-text staff-observation input on the identical server code path (built before mic capture)
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-002, DD-004
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Mandatory resilience. If the judging-room mic fails, typing the observation keeps the demo moving with zero pause. Must exist before `getUserMedia` is wired.
- **Extended by:** TREQ-010

## TREQ-012
- **Title:** Implemented on Python 3.11 + FastAPI + Jinja2/HTMX + Anthropic SDK + ElevenLabs Python SDK + Pydantic v2; no Streamlit
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-004
- **Relationship:** NEW
- **Deliverable:** ADR → architect → _proj/deliverables/02-architecture/adr/ (ADR-001, Accepted)
- **Rationale:** Hard constraint. Single-process, no frontend build = one-command restart and no React hydration surface to break in a judging room. Streamlit is an explicitly banned anti-project.

## TREQ-013
- **Title:** Pluggable LLM backend with 3 resilience tiers, switchable by env/UI with no code change
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-004
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Tier 1 Anthropic Claude cloud (primary/showcased — robust + sponsor); Tier 2 Ollama local (dynamic re-plan with zero network); Tier 3 fixture-replay OFFLINE_MODE (deterministic last resort). Removes the single largest live-demo failure mode.

## TREQ-014
- **Title:** All model outputs pass through Pydantic models / Claude tool-use so malformed output cannot break the demo
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-004
- **Relationship:** REFINES TREQ-001
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Structured-output enforcement is the difference between a confident live render and a demo that dies on a stray token. Refines the orchestrator contract.

## TREQ-015
- **Title:** Public Git repo with README naming Problem Statement #1 and an explicit "built today" scope statement
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-003
- **Relationship:** NEW
- **Deliverable:** Guide → docs → _proj/deliverables/04-guides/
- **Rationale:** Public repo and clearly-isolated built-today work are disqualification-grade rules. Naming the exact problem statement also removes judge ambiguity.

## TREQ-016
- **Title:** Scope guard — single returning-guest persona (Ms. Chen), fixtures only, no live flight/weather APIs
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-003
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** A narrow deterministic slice beats a broad brittle one in a 3-min demo. External APIs are pure failure surface with no scoring upside here.

## TREQ-017
- **Title:** Demo-readiness & resilience playbook — 3-min script, cut order, backup screenshots/GIF, offline rehearsal
- **Priority:** P1
- **Status:** LOCKED
- **Source:** DD-003
- **Relationship:** NEW
- **Deliverable:** Guide → docs → _proj/deliverables/04-guides/
- **Rationale:** Live Demo is 45% and there is no post-5:00 PM hardening window. The script encodes the ADR-001 cut order (never cut TREQ-006) and a tested offline run before the room.

## TREQ-018
- **Title:** Room-legible dashboard UI (3-panel: inputs/triggers · mood + diff + suppression · role cards with Play Briefing)
- **Priority:** P1
- **Status:** LOCKED
- **Source:** DD-001
- **Relationship:** REFINES TREQ-002
- **Deliverable:** Design → design → _proj/deliverables/03-design/ (may be inlined into implementation under time pressure)
- **Rationale:** Visual clarity and pacing directly drive the 45% Live Demo score. High-contrast, large-font, one-click triggers; refines how role cards (TREQ-002) are presented.
