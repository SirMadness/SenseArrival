> **Version:** v001.02
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
- **Extended by:** TREQ-020
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
- **Refined by:** TREQ-024
- **Source:** DD-003
- **Relationship:** NEW
- **Deliverable:** Guide → docs → _proj/deliverables/04-guides/
- **Rationale:** Public repo and clearly-isolated built-today work are disqualification-grade rules. Naming the exact problem statement also removes judge ambiguity.

## TREQ-016
- **Title:** Scope guard — single returning-guest persona (Ms. Chen), fixtures only, no live flight/weather APIs
- **Priority:** P0
- **Status:** DEPRECATED
- **Replaced by:** TREQ-019
- **Deprecated on:** 2026-05-16
- **Source:** DD-003
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** A narrow deterministic slice beats a broad brittle one in a 3-min demo. External APIs are pure failure surface with no scoring upside here. _[Superseded by TREQ-019 in v001.02 — scope widened to a fixed 3-dossier/3-property library per Radha Arora validation; fixtures-only / no-live-API / single-rehearsed-path constraints retained. Never implemented — no completed BL.]_

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

## TREQ-019
- **Title:** Scope guard (widened) — fixed fixture library of 3 guest dossiers + 3 Rosewood property cards (1 deep arrival property + 2 provenance), expandable only after the 3/3 scenario tests clean; fixtures only, no live APIs; single rehearsed demo path preserved
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-005
- **Relationship:** REPLACES TREQ-016
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Preserves ADR-001's narrow-deterministic-slice spirit (fixtures only, no live-API demo risk, one rehearsed path) while enabling the portfolio guest-graph creativity hook. Caps breadth at 3/3 so build cost stays bounded; any expansion is gated on a passing 3/3 test. Supersedes the single-Ms.-Chen-persona constraint in TREQ-016 only — the fixtures-only / no-live-API / single-rehearsed-path constraints are retained. Belongs to the Foundation runtime (FEAT-005): the fixture library must load before orchestration.

## TREQ-020
- **Title:** Portfolio-aware grounding — guest dossier = profile + prior stays (each tagged with a Rosewood property + that site's staff observations); per-property "sense of place" card library that captures the **local culture & activities of the hotel's destination** (theatre, landmarks, regional experiences — not just on-property amenities); arrival property rendered deep, others as provenance; Markdown card format + templates
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-006
- **Relationship:** EXTENDS TREQ-004
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/ (property "sense of place" content: Research → analyst → _proj/artifacts/reports/analysis/)
- **Rationale:** TREQ-004 grounds outputs in Sand Hill anchors. This adds the portfolio dimension: grounding spans a per-property card library and the arrival is informed by where the guest stayed before. Markdown source keeps cards human-editable and judge-visible (loaded as raw prompt context — no parser). Property "sense of place" content is researched at build time by an analyst (parallel to engineering, no live-demo API risk). Per Rosewood president Radha Arora: tailor to BOTH the guest profile AND the local culture/activities of the hotel's location — so the hotel card is destination-culture-centric, broader than amenities.

## TREQ-021
- **Title:** Cross-visit guest synthesis — orchestrator infers a unified guest understanding from cross-property prior-stay observations before choreographing the arrival, surfaced as an explicit "inferred from prior stays" element
- **Priority:** P0
- **Status:** LOCKED
- **Source:** DD-006
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** The headline creativity hook for the 35% Creativity weight and the event's "they just knew vs. that's creepy" theme. STRICTLY behind the never-cut spine (BL-001→002→003) — must not displace or delay the re-plan diff. Implemented as a synthesis step folded into the existing Claude tool-use call (a prompt + Pydantic field), not a new subsystem.

## TREQ-022
- **Title:** Thin interactive guest/property selector — swaps the active dossier/property and re-runs plan() via the existing render path; demo-optional (rehearsed script stays single-path); NOT a CRUD/authoring/chat-edit subsystem
- **Priority:** P1
- **Status:** LOCKED
- **Source:** DD-007
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Lets the builder tune and pick the final demo profile and show multi-property on request at minimal cost (HTMX fixture swap reusing the render path). P1/cuttable — the rehearsed single-path demo never depends on it. Scope-creep guard: explicitly excludes any LLM card-authoring or chat-edit feature; "new guest" = add a Markdown card.

## TREQ-023
- **Title:** Live staff-observation → dossier loop (demo-shim) — a staff voice/typed note captured during the visit is appended to the on-screen guest dossier and feeds the current cross-visit re-synthesis & re-plan; in-memory session persistence (no disk write-back)
- **Priority:** P1
- **Status:** LOCKED
- **Source:** DD-006
- **Relationship:** NEW
- **Deliverable:** Implementation → engineer → _proj/artifacts/reports/implementation/
- **Rationale:** Radha Arora (Rosewood president) emphasized staff *manually collect* customer data *into a profile*. This makes that loop visible: staff voice note (reuses existing TREQ-010 STT / TREQ-011 typed path) → appended to the guest dossier panel → triggers TREQ-021 re-synthesis → arrival plan + role cards update → TREQ-006 diff shows what changed & why. Demo-shim only (in-memory, no disk persistence) to stay spine-safe under the 5PM deadline. Strictly behind the never-cut spine; reuses the FEAT-004 capture path so new surface is minimal.

## TREQ-024
- **Title:** README frames the dual-card model (guest dossier + destination-culture hotel card) as the answer to Problem Statement #1, noting validation with Rosewood's president
- **Priority:** P1
- **Status:** LOCKED
- **Source:** DD-005
- **Relationship:** REFINES TREQ-015
- **Deliverable:** Guide → docs → _proj/deliverables/04-guides/
- **Rationale:** TREQ-015 requires the README name PS#1 + built-today scope. This specifies the framing: explicitly present the dual-card (customer card + hotel card) architecture as the PS#1 answer, validated in conversation with Radha Arora (President, Rosewood Hotels & Resorts). Cheap to write, direct lift to the 20% Impact score and judge credibility; no behavior change to TREQ-015.
