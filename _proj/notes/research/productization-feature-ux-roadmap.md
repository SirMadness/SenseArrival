# Red Thread 紅線 — Productization Feature & UX Roadmap

**Document type:** Research / product analysis
**Date:** 2026-05-16
**Author:** Analyst (⚪)
**Audience:** Founding team, product leads, technical co-founder, seed investors
**Scope:** Everything needed to move from the current hackathon-grade demo into a real, operating luxury-hospitality product. Hackathon-locked scope treated as already-specced baseline; this doc surfaces the delta.

---

## 1. Executive Summary

Red Thread 紅線 is a genuinely original product concept: an **arrival choreography engine** that treats luxury hospitality personalization as a choreography problem rather than a data-retrieval problem, with guest-controlled privacy as a first-class design primitive rather than a compliance checkbox. The live site at `app.redthread.boutique` demonstrates that framing compellingly — the "Hold the Thread" discretion slider, the Movement IV lifecycle, and the three-zone staff brief are all coherent. The underlying SenseArrival engine delivers structured, schema-validated arrival plans with a "what changed & why" diff across a simulated delay scenario.

The core gap is categorical: **everything that makes a demo feel credible is not what makes a product operable.** The demo works because inputs are fixtures and state is in-memory. A product works because identity, persistence, integrations, compliance, and reliability are real. Red Thread has the concept and the UI language; it needs the infrastructure and operational depth that turns concept into system.

**The five biggest bets to become real:**

1. **Persistent identity + consent ledger.** The "Hold the Thread" discretion dial is the product's originality spine. It must become a real, portable, auditable consent record — not a UI slider that resets on page reload. This is also the regulatory moat.
2. **PMS integration as the forcing function.** Nothing else in the integration stack matters before Opera Cloud (or equivalent). Reservation context is the trigger for everything; without it the system is always manually bootstrapped.
3. **Staff mobile surface (Zone II + Zone III as real tools).** The concierge brief and actuator panel are currently described text. Floor staff won't adopt a desktop web app in a hotel operation; the brief must be a thumb-operable surface with push notifications and a sub-30-second read.
4. **LLM-mediated Discretion Layer as an auditable subsystem.** The pitch says Claude Haiku 4.5 audits each data signal against the privacy score. That must be a real, logged, contestable process — not a demo narrative. This is both the privacy moat and the trust story for HNW/VIP guests.
5. **Cross-property guest graph as a real datastore.** The dual-card model (portable guest profile + local sense of place) validated with Radha Arora only works at scale if prior-stay data is durably stored, structured, and retrievable across properties. Fixtures cannot scale.

---

## 2. Current-State Assessment

### What genuinely works

| Element | Status | Notes |
|---|---|---|
| Brand narrative and visual language | Working | "Red Thread" metaphor, Movement IV lifecycle, three-zone architecture are coherent and distinctive |
| Discretion slider UI at `/profile` | Functional (front-end) | Renders tier descriptions per level; "Save change" button present; no backend persistence confirmed |
| Intake form at `/intake` | Partially functional | Three question cards (Room, Food, Privacy) render; voice channel and demo playback buttons present; ElevenLabs/Claude attribution visible |
| Arrival choreography engine (SenseArrival) | Working for one scenario | Ms. Chen @ Rosewood Sand Hill produces a validated ArrivalPlan; delay re-plan + diff work; suppression panel works; TTS works |
| Six role cards + mood banner | Working | Schema-validated via Pydantic; rendered in Jinja2 grid |
| "What changed & why" diff panel | Working | The never-cut spine is delivered |
| Staff voice/typed observation path | Working | Keyword-classify → OOB card swap via HTMX |
| 3-tier backend resilience | Working | Claude → Ollama → fixture-replay switchable via env var |

### What is scripted / aspirational

| Element | Gap | What's Missing |
|---|---|---|
| Zone I "Research Streams" | Described, not implemented | No real flight API, CRM, or web search calls; placeholders show "Awaiting briefing/reservation" |
| Zone III "Actuators" | Described, not implemented | "+Room service", "+Spa", etc. are UI controls with no backend write to PMS/POS/spa systems |
| Guest submission flow | Partial | Form renders; no confirmed real submission path, no session persistence, no confirmation state |
| `/profile` preference persistence | Front-end only | "Save change" has no backend; slider resets |
| Multi-guest, multi-property | Fixture stub | 3 hand-authored dossiers, 3 property cards; no real multi-tenancy |
| Voice intake (STT) | Demo-optional | Mic access requested; full STT→Scribe pipeline not hardened |
| "Auditable removals" and contest flow | Narrative only | No real audit log; no contestation UI or backend |
| Login / identity | Absent | No auth flow for guest or staff; no session management |
| Mobile / responsive | Not present | Desktop-first; no responsive treatment |

### Demo ↔ engine gap

The live site (`app.redthread.boutique`) is a more advanced UI concept than the SenseArrival engine — it describes a system (PMS pushes, CRM reads, Haiku audits, guest contest flow) that the engine does not yet implement. The engine is a structured prompt → structured output pipeline with fixtures in. The site is the product vision. The gap between them is the roadmap.

---

## 3. Demo → Production Gap Analysis

Each pillar below represents a categorical capability that a real product requires but a demo does not.

### 3.1 Persistence & State Management

**What the demo does:** In-memory Python dict (`app.state`). Restarts wipe everything. One guest, one session, one property.

**What a product requires:** A durable datastore (relational + document hybrid) holding: guest dossiers (versioned), per-visit ArrivalPlans, consent records, staff observations, audit logs, plan diffs, actuator action history. Session state must survive process restarts and scale to concurrent properties. Schema migrations as the data model evolves.

**Key decisions:** PostgreSQL (structured guest/property data) + object store (dossier Markdown, plan artifacts); Redis for session/queue; event log (append-only) for audit trail.

---

### 3.2 Identity, Auth & Multi-Tenancy

**What the demo does:** No auth. One hardcoded guest. One property context.

**What a product requires:**
- **Staff identity:** SSO/SAML integration with hotel HR systems (or standalone IdP); role-based access (valet sees their card, MOD sees all six, GM sees analytics); MFA for PII access.
- **Guest identity:** Lightweight — email/SMS OTP or existing loyalty ID link; no password burden for HNW guests; identity must be portable across properties.
- **Property tenancy:** Each property is a tenant with its own sense-of-place card, service policies, role mappings, staff roster, and branding. Plans, dossiers, and actuator actions must be tenant-scoped. A portfolio operator (Rosewood) sees across tenants.

---

### 3.3 Real Integrations

**What the demo does:** Fixtures only. No live APIs.

**What a product requires:** See Section 4.5 (Integrations catalog). The integration stack is the operational nervous system. Nothing in the AI layer matters until the system knows what reservation exists (PMS), who the guest is (CRM/loyalty), where the flight is (flight feed), and can act (PMS/POS/spa write-back). Each integration requires: an adapter layer, auth credential management, error handling + retry, rate limiting, and a fallback (graceful degradation to manual briefing if an integration is down).

---

### 3.4 Security, PII & Compliance

**What the demo does:** No security surface at all. Guest names are hardcoded strings.

**What a product requires:** HNW/VIP guest data is among the most sensitive PII in existence. Encryption at rest and in transit, field-level encryption for dossier contents, RBAC with least-privilege, GDPR/CCPA consent management with a real deletable consent record, audit log of every data access, penetration testing before any pilot, staff NDA/data handling policies enforced by system controls (not just policy). The Discretion Layer's "auditable removals" must be a real, tamper-evident log.

---

### 3.5 Reliability & Observability

**What the demo does:** Single process, no monitoring, offline replay as the fallback.

**What a product requires:** Uptime SLA (99.9%+ for a hospitality critical path); LLM call latency budgets (arrival briefing must complete before the car arrives — typically 15–45 min window); cost controls on LLM API calls (per-plan budget, caching, model routing); structured logging; distributed tracing for multi-step agentic flows; alerting on plan failures; graceful degradation (if Claude is unavailable, surface last cached plan, flag as stale, notify MOD). Incident response playbook for the hotel ops team.

---

### 3.6 Real Communications & Guest Channels

**What the demo does:** Guest message preview only ("what we'd send" — no real send).

**What a product requires:** Real outbound guest messaging (SMS/WhatsApp for HNW guests, email, Apple Wallet / Google Wallet passes for digital key + itinerary, in-app push if a guest app exists). Inbound guest reply handling. Pre-arrival communication sequencing (T-72h, T-24h, T-2h cadence). Opt-out management per channel. Message templates tied to mood/role-card content, not generic confirmations.

---

### 3.7 Mobile & Operational Surfaces

**What the demo does:** Desktop-first web app; no responsive treatment.

**What a product requires:** Floor staff (valet, front desk, dining, housekeeping, concierge, MOD) do not sit at desks. The brief must be: a PWA or native mobile app surfacing the relevant role card; readable in a glance (< 30 seconds); push-notified when a plan updates (e.g., delay re-plan fires); thumb-operable for observation capture ("what I noticed" → staff sensor loop). Tablet kiosk mode for front desk. MOD dashboard on desktop.

---

### 3.8 Dossier Authoring & Maintenance

**What the demo does:** Three hand-authored Markdown files. Humans edit them manually.

**What a product requires:** A structured dossier authoring tool for CRM/concierge staff — a form-driven UI that produces the structured Markdown (or structured schema) the engine consumes. Versioned dossiers with edit history. Merge/conflict resolution when two staff members add observations for the same guest concurrently. A "freshness" system — preferences stale after N visits without confirmation.

---

## 4. Feature & UX Catalog

This is the exhaustive catalog. Each item includes: what it is, why it matters, key UX considerations, dependencies, effort, and risk level.

Effort tiers: **S** = days, **M** = 1–3 weeks, **L** = 1–2 months, **XL** = 3+ months
Risk tiers: **Low / Medium / High / Critical** (Critical = blocks pilot or creates legal exposure)

---

### 4.1 Guest-Facing Experience & UX

#### 4.1.1 Persistent "Hold the Thread" Consent Profile

| | |
|---|---|
| **What** | The discretion slider at `/profile` backed by a real, portable, durable consent record. Persists across properties and stays. Guest can update at any time; each change is timestamped and acknowledged. |
| **Why** | The originality spine. Without persistence it is decoration. With persistence it is a genuine privacy moat and the foundation for all downstream data-access decisions. For HNW guests, knowing their preference is remembered and enforced is a trust signal stronger than any amenity. |
| **UX** | The current UI is good — three-tier descriptions (Loosely/Held/Fully) are clear. Add: confirmation toast on save ("Thread updated — applies from your next pre-arrival"), a history log ("You changed this on May 12 at The Carlyle"), and a one-click "reset to default" for post-stay cleanup. |
| **Dependencies** | Auth/identity (3.2), persistent DB (3.1), consent ledger subsystem (4.6.2) |
| **Effort** | M |
| **Risk** | High (PII, must be GDPR-compliant) |

---

#### 4.1.2 Pre-Arrival Guest Communication Sequence

| | |
|---|---|
| **What** | Automated, choreographed pre-arrival touchpoints: T-72h "We're preparing for your arrival" (confirms details, links to intake), T-24h "Your arrival brief is ready" (links to profile, surfaces mood theme), T-2h "Your team is ready" (car/valet logistics, final ETA). Content is drawn from the role cards — not generic. |
| **Why** | Luxury guests expect proactive communication. The current engine produces a plan but nothing reaches the guest. The communication sequence is where the "choreography" becomes experiential, not just operational. |
| **UX** | Channel-adaptive: SMS-first for HNW guests (shorter, more personal), email for detail-seekers, Apple Wallet pass for itinerary. Each message should feel like a note from a person, not a system. Voice/tone tied to property's sense-of-place card. Opt-down (not opt-out) — guest controls granularity, not channel presence. |
| **Dependencies** | Messaging integration (SMS/email/WhatsApp — 4.5.5), consent profile (4.1.1), reservation trigger (PMS — 4.5.1), mood banner content from engine |
| **Effort** | L |
| **Risk** | Medium (channel compliance — SMS opt-in, CAN-SPAM for email) |

---

#### 4.1.3 Guest Intake Flow — Real Submission & Confirmation

| | |
|---|---|
| **What** | The `/intake` three-question flow (Room, Food, Privacy) completed and persisted. Submission triggers plan generation. Confirmation state shown ("Your arrival is being prepared"). Voice intake (ElevenLabs → STT → structured answers) as the premium path; typed fallback. |
| **Why** | Currently the form renders but has no confirmed real submission path. This is the primary guest interaction surface; without a real submit it is a prototype. |
| **UX** | The three-question card design is elegant — keep it. Add: progress indicator (3 steps), graceful mic-permission denial fallback (auto-switch to typed), conversational confirmation ("Got it — we'll have your room at 68°F, no shellfish, and standard discretion"), edit/review before submit, post-submit animation that reinforces the "thread being woven" metaphor. |
| **Dependencies** | Auth/identity (guest token or reservation lookup), persistence (3.1), STT pipeline (4.2.5), plan generation engine |
| **Effort** | M |
| **Risk** | Medium (voice channel needs mic permission UX care) |

---

#### 4.1.4 Guest Profile Portal — Full Self-Service

| | |
|---|---|
| **What** | A richer `/profile` beyond the discretion slider: view what the property knows about you (your dossier, filtered to your privacy tier), edit preferences (dietary, room, rituals, communication channels), see upcoming stay details, access past-stay summaries, manage consent (what signals are used, what has been removed, decline future use of specific data points). |
| **Why** | Transparency builds trust. HNW guests who know they can see and edit their own dossier are more likely to share preferences, which makes the choreography better. This is also the GDPR/CCPA "right of access and erasure" interface — it must exist. |
| **UX** | Not a settings dump — make it feel like a personal concierge record. "Here's what we remember" (preferences). "Here's what we used for your last arrival" (plan summary). "Here's what we chose not to surface" (suppression log). Each section collapsible, expandable for detail. Mobile-first (guests will check this on their phone before arriving). |
| **Dependencies** | Auth/identity (4.1.1), consent ledger (4.6.2), dossier datastore, suppression log |
| **Effort** | L |
| **Risk** | High (PII display — careful with what tier of data each privacy level exposes) |

---

#### 4.1.5 Digital Key & Arrival Wallet Pass

| | |
|---|---|
| **What** | Apple Wallet / Google Wallet pass delivered pre-arrival, containing: room number (when assigned), check-in time, parking/valet instructions, a condensed "Your arrival" summary, and digital key (if property supports BLE/NFC). |
| **Why** | Reduces friction at check-in; the pass is also a pre-arrival brand touchpoint that signals "we are ready for you." Luxury guests increasingly expect mobile key; it also reduces front-desk congestion. |
| **UX** | Pass design must be on-brand (property-specific). Include the guest's mood theme language ("A quiet, restorative evening awaits") — turns a functional pass into an experiential one. Update the pass dynamically if ETA changes (Wallet supports push updates). |
| **Dependencies** | Apple Wallet / Google Wallet API, PMS integration (room assignment), plan engine (mood language), messaging integration |
| **Effort** | M |
| **Risk** | Low–Medium (Wallet pass generation is well-documented; digital key requires PMS/hardware support) |

---

#### 4.1.6 Post-Stay Memory Confirmation & Ritual Preservation

| | |
|---|---|
| **What** | 24–48h post-checkout touchpoint: "We've updated your thread" — a brief summary of what was noted (with consent), what will carry forward to future stays, and an invitation to correct or add. Prevents dossier drift. |
| **Why** | The cross-visit guest graph only improves if feedback loops exist. Without post-stay confirmation, stale preferences accumulate (e.g., a dietary restriction that was temporary, a room preference that changed). |
| **UX** | Short, personal, text-forward. "Your team noted you prefer the garden-facing suite and asked for extra pillows on the third night — shall we carry that forward?" Binary answers (carry forward / clear) with an optional free-text addition. Not a survey; a thread-maintenance ritual. |
| **Dependencies** | Messaging (4.5.5), dossier versioning, consent (4.1.1), plan history |
| **Effort** | M |
| **Risk** | Low (post-stay, lower sensitivity than pre-arrival data) |

---

#### 4.1.7 Accessibility & Internationalization

| | |
|---|---|
| **What** | WCAG 2.1 AA compliance (screen reader labels, contrast ratios, keyboard navigation, focus management). Multi-language support for guest-facing surfaces (at minimum: English, Mandarin, Japanese, Arabic — covering Rosewood's core feeder markets). RTL layout support. |
| **Why** | Rosewood operates globally. A guest-facing surface that is English-only or inaccessible is a product gap, not a nice-to-have. The brand "紅線" already signals bilingual intent. |
| **UX** | Language auto-detect from browser/reservation locale. In-app language switcher. Property-specific language defaults (Hong Kong → Cantonese/English; Sand Hill → English/Mandarin). Sense-of-place card and mood banner language must match. |
| **Dependencies** | i18n framework, translation pipeline (human review for luxury language register — machine translation alone will not meet brand standards), property config |
| **Effort** | L–XL (ongoing) |
| **Risk** | Medium (translation quality risk for luxury copy is high — wrong register damages brand) |

---

#### 4.1.8 In-Stay Guest Interaction Surface

| | |
|---|---|
| **What** | A lightweight in-stay guest channel: the ability to send a preference update mid-stay ("I'd prefer the air conditioning off tonight"), receive a "how is your stay?" prompt tied to a specific service moment (not a generic survey), and surface contextual suggestions ("Your reservation at Madera is at 7:30 PM — here's what your team has prepared"). |
| **Why** | The current system is arrival-only. Luxury hospitality value extends through the entire stay; a system that goes silent after check-in misses 80% of the relationship. |
| **UX** | Not a chatbot. Short, specific, triggered by events (check-in complete, day 2, pre-dinner). SMS-native for HNW guests; optional in-app. Each interaction should feel like a note from the concierge, not an automated prompt. |
| **Dependencies** | Messaging (4.5.5), PMS events (checkout trigger, dinner booking trigger), plan engine extension (generalized triggers — delay is just one) |
| **Effort** | L |
| **Risk** | Medium (over-messaging risk — frequency controls are critical) |

---

### 4.2 Staff & Operations Console UX

#### 4.2.1 Mobile-First Role Card Brief

| | |
|---|---|
| **What** | Each of the six role cards surfaced as a thumb-operable mobile view, specific to the logged-in staff member's role. Valet sees only the valet card. MOD sees all six. Cards show: guest name, arrival ETA, the three-line action brief, suppression note ("we chose not to offer X"), and a one-tap observation capture. |
| **Why** | Floor staff operate on phones or small tablets. A desktop grid is useless in a parking structure, at a door, or in a service corridor. The brief must be consumable in a 15-second glance before the car pulls up. |
| **UX** | Card-native layout: large guest name + photo (if available and consented), arrival countdown ("Arriving in ~12 min"), three action bullets, one "I noticed something" button. Swipe between cards for MOD. Color-coded by role for multi-card views. Offline-capable (cached brief) for areas with poor connectivity. |
| **Dependencies** | Auth/RBAC (role-to-card mapping), mobile PWA or native app, push notifications (4.2.2), persistence (3.1) |
| **Effort** | L |
| **Risk** | Medium (role mis-assignment exposes wrong guest data to wrong staff — RBAC must be correct) |

---

#### 4.2.2 Real-Time Plan Update Push Notifications

| | |
|---|---|
| **What** | When a re-plan fires (flight delay, early arrival, room change, weather), all relevant role-card holders receive a push notification: "Benjamin Shyong's arrival updated — now 2:45 PM. Valet brief refreshed." Notification links directly to updated card. |
| **Why** | The delay re-plan + diff is the "creative proof" of the system. Without real push delivery to staff, the re-plan fires in a vacuum. Push is what makes the re-plan operationally real. |
| **UX** | Notification copy must be role-specific (valet gets logistics; dining gets dietary + timing; housekeeping gets room-state note). Notification grouping if multiple guests update simultaneously (MOD sees a count, not a flood). Acknowledged-read receipt so MOD can confirm the team has seen the update. |
| **Dependencies** | Mobile surface (4.2.1), WebSocket or SSE for live updates, push notification service (FCM/APNs for native; web push for PWA), re-plan trigger pipeline |
| **Effort** | M |
| **Risk** | Medium (notification fatigue — frequency and priority controls needed) |

---

#### 4.2.3 Staff-as-Sensors Observation Capture Loop

| | |
|---|---|
| **What** | A formalized, quick-capture UI for staff to add observations to a guest's live thread: typed text (current), voice (STT path), or structured quick-picks ("Guest mentioned: [dietary change / preferred something / sensitive topic / positive reaction]"). Observations are: classified (LLM or keyword), gated through the Discretion Layer, and either added to the live dossier or flagged as ephemeral (this stay only). |
| **Why** | The current typed-text path works but is unstructured and informal. Real product needs: structured capture (for queryability), ephemeral vs. persistent distinction, and a clear signal to staff that the observation has been received and acted on (closing the loop). |
| **UX** | One-tap quick-picks for common observations (reduces friction; increases capture rate). Voice as the premium path (staff narrate while walking). Confirmation feedback ("Added to Benjamin's thread — classified as Dietary / marked ephemeral"). Staff should never feel like they are doing data entry; the metaphor is "passing a note." |
| **Dependencies** | STT (4.2.5), Discretion Layer (4.4.2), dossier write path, persistence |
| **Effort** | M |
| **Risk** | High (staff capture of sensitive guest observations is a PII risk — all captures must flow through Discretion Layer before write) |

---

#### 4.2.4 Shift Handoff & MOD Briefing

| | |
|---|---|
| **What** | An end-of-shift summary for outgoing staff and a start-of-shift brief for incoming staff, generated from the current guest thread state. MOD-specific: a live-arrival board showing all guests arriving in the next N hours, their thread status (plan ready / pending / re-planned), and any flags (VIP tier, unresolved suppression, open observation). |
| **Why** | In a real hotel, shifts change. The current system assumes a single session; in production, a valet who captured an observation at 2 PM needs that to be visible to the evening team. Without shift handoff, the thread breaks at every staff rotation. |
| **UX** | Handoff summary: 1 page, auto-generated, printable and/or pushable to shift-start notification. MOD board: arrival timeline with status chips (green = ready, amber = re-planned, red = issue). Quick-tap to drill into any guest's full brief. |
| **Dependencies** | Persistence, shift/roster integration or manual shift input, MOD role in RBAC |
| **Effort** | M |
| **Risk** | Low–Medium |

---

#### 4.2.5 Voice STT — Production Hardening

| | |
|---|---|
| **What** | The mic → STT → Scribe → plan-update path hardened for real operational use: background noise robustness (hotel lobbies are loud), speaker diarization for multi-person briefings, confidence scoring with fallback to typed confirmation, and a playback-and-confirm UI before committing the observation. |
| **Why** | The current path is demo-optional. For floor staff, voice is the only viable input method at speed. Without production-quality STT, the observation loop reverts to typed-only and adoption drops. |
| **UX** | Visual waveform during capture (confirms mic is live). Transcription preview before confirm. One-tap correction. Auto-punctuation and luxury-vocabulary tuning (guest names, hotel terms, cuisine). "Did you mean...?" recovery for misheard proper nouns. |
| **Dependencies** | ElevenLabs STT or Whisper, noise-cancellation preprocessing, Discretion Layer |
| **Effort** | M |
| **Risk** | Medium (STT accuracy in hospitality settings; proper noun handling) |

---

#### 4.2.6 Suppression Panel — Staff Override & Escalation

| | |
|---|---|
| **What** | The current suppression panel shows "tasteful restraint" choices (what the engine chose not to offer and why). Add: staff override capability (with a reason field, logged), GM/MOD escalation for overrides above a threshold, and a per-guest suppression history visible to the MOD. |
| **Why** | Staff instincts are often right. If the engine suppresses an offer but the concierge knows this specific guest always wants it regardless of context, they need an override path. The override itself is valuable training signal. |
| **UX** | Override button on each suppressed item. Reason dropdown (common reasons) + free text. Override logged with staff ID and reason. MOD sees a daily suppression-override summary. Repeated overrides on the same item for the same guest flag a preference update. |
| **Dependencies** | Auth/RBAC (who can override), audit log, preference feedback loop |
| **Effort** | S–M |
| **Risk** | Medium (override without logging is a compliance gap) |

---

#### 4.2.7 Actuator Panel — Real PMS/POS Write-Back

| | |
|---|---|
| **What** | The Zone III "Actuators" controls (+Room service, +Spa, +Front desk, +Late checkout, +Push) connected to real systems. Each action: creates a work order or reservation in the relevant system, logs the Red Thread action ID (for auditability), and updates the live brief with a "committed" status indicator. |
| **Why** | Currently these are UI buttons with no backend action. Real operational value is zero without write-back. The actuator panel is the product's "outcome" layer — without it, Red Thread is a read-only briefing tool, not an orchestration engine. |
| **UX** | Each actuator button shows its committed state (pending → confirmed → delivered). Failed actions surface immediately with a clear error and a manual fallback ("Call spa directly at ext. 42"). Staff see a "committed actions" log for each guest arrival. |
| **Dependencies** | PMS integration (4.5.1), POS integration (4.5.2), spa booking integration (4.5.4), staff auth for each downstream system |
| **Effort** | XL (integration-heavy) |
| **Risk** | High (writes to live operational systems; incorrect writes cause real service failures) |

---

### 4.3 Admin / Property Configuration / Onboarding

#### 4.3.1 Property "Sense of Place" Card Authoring Tool

| | |
|---|---|
| **What** | A structured, form-driven UI for property managers to author and update the sense-of-place card that feeds the arrival plan: local activities, cultural notes, seasonal highlights, signature rituals, service style descriptors. Currently: hand-authored Markdown. Should become: a structured form with rich text, media attachment, and version history. |
| **Why** | Sense-of-place cards require ongoing maintenance (seasonal updates, new service launches, changing local events). Manual Markdown editing does not scale beyond three properties. |
| **UX** | Section-by-section form (culture / activities / rituals / signature services / seasonal notes). Preview pane showing how the card feeds into a sample plan prompt. Publish/draft workflow — edits go to draft until a property manager approves. Version diff ("what changed since last season"). |
| **Dependencies** | Admin role in RBAC, property tenancy model (3.2), persistence |
| **Effort** | M |
| **Risk** | Low |

---

#### 4.3.2 Service Policy & Suppression Rule Configuration

| | |
|---|---|
| **What** | Property-level rules that govern the Discretion Layer beyond the guest's privacy dial: categories of offers that are always suppressed for this property (e.g., no upsells in first 30 min of check-in), categories that are always offered (e.g., welcome drink regardless of tier), and custom suppression rationale templates ("We chose not to mention the spa because..."). |
| **Why** | Different luxury properties have different service philosophies. A blanket AI suppression rule does not capture brand nuance. Property managers need authoring control over what the system considers "tasteful restraint" for their property. |
| **UX** | Rule builder: category (offer type) + condition (always / never / if guest tier ≥ X / if privacy ≤ Y) + rationale template. Rule test: "How would this rule affect Benjamin Shyong's next arrival?" Preview suppression log with and without the rule. |
| **Dependencies** | Property config model, Discretion Layer (4.4.2), admin RBAC |
| **Effort** | M |
| **Risk** | Medium (misconfigured rules could suppress critical safety information — validation needed) |

---

#### 4.3.3 Role & Permission Management

| | |
|---|---|
| **What** | RBAC console: map staff members to roles (valet, front desk, dining, housekeeping, concierge, MOD, GM, property admin); configure which role cards each role can see; set override permissions; manage API access for integrations. |
| **Why** | Without RBAC, any staff member can see any guest's full dossier, which is both a privacy risk and a compliance gap. Role mapping is also how the six role cards become operationally meaningful — each card only surfaces to the relevant team. |
| **UX** | Spreadsheet-like role matrix (staff × permission). Bulk import from hotel HR system (CSV or SCIM). Role templates ("Standard valet" defaults). Audit log of permission changes. |
| **Dependencies** | Auth/identity (3.2), HR system integration or manual roster |
| **Effort** | M |
| **Risk** | High (permission misconfiguration exposes PII) |

---

#### 4.3.4 White-Label & Property Branding

| | |
|---|---|
| **What** | Per-property branding configuration: logo, color palette, typography tokens, email/SMS sender identity, Wallet pass design, the voice tone of guest-facing messages. "Red Thread" is the platform brand; each property expression should feel like it comes from that property, not a generic SaaS tool. |
| **Why** | Rosewood's brand equity is in individual property identity. A Rosewood Sand Hill communication should feel like Rosewood Sand Hill, not a generic hotel tech product. |
| **UX** | Branding config panel: upload logo, set hex values, preview against guest-facing surfaces (email template, Wallet pass, SMS header). Staff console can remain platform-branded (operational tool vs. guest-facing experience). |
| **Dependencies** | Property tenancy model (3.2), white-label email/SMS setup |
| **Effort** | M |
| **Risk** | Low |

---

#### 4.3.5 Dossier Authoring & CRM Staff Tool

| | |
|---|---|
| **What** | A structured UI for concierge/CRM staff to create, edit, and annotate guest dossiers: biographical context, past-stay highlights, preferences (room, F&B, communication, rituals), sensitivities (family situation, health context, known aversions), and cross-property notes. Currently: hand-authored Markdown files. |
| **Why** | The dossier is the primary input to the choreography engine. Markdown authoring does not scale, is error-prone, and creates an unqueryable data surface. A structured dossier tool is the data foundation for everything. |
| **UX** | Form-driven with rich text for narrative sections. "Freshness" indicator per field (when was this last confirmed?). Merge UI when two staff members edit concurrently. "What the engine will see" preview — shows how a dossier field maps to a prompt element. Flag for "carry forward" vs "this stay only." |
| **Dependencies** | Persistence, auth/RBAC (concierge role), dossier schema, engine input format |
| **Effort** | L |
| **Risk** | High (staff entering sensitive guest data — audit log of who authored/edited what is required) |

---

#### 4.3.6 Multi-Property Portfolio Onboarding Flow

| | |
|---|---|
| **What** | A structured onboarding path for adding a new property to the platform: sense-of-place card setup, PMS credential configuration, staff roster import, role mapping, integration testing, pilot guest selection, and a "go live" checklist. |
| **Why** | Scaling from 2 properties (demo) to 10+ requires a repeatable onboarding process. Ad-hoc setup creates configuration drift and support burden. |
| **UX** | Wizard-style onboarding (8–10 steps, progress indicator). Each step has a validation gate before proceeding. "Test with a sample guest" step before go-live. Onboarding completion dashboard for the portfolio operator. |
| **Dependencies** | All of 4.3.1–4.3.5, integration config (4.5), RBAC |
| **Effort** | M |
| **Risk** | Medium (onboarding errors compound — a misconfigured PMS integration on day 1 is hard to untangle later) |

---

### 4.4 AI / Agentic Capabilities

#### 4.4.1 Generalized Trigger Engine (Beyond Delay)

| | |
|---|---|
| **What** | The current re-plan fires on a single trigger: a 120-minute flight delay. A real product needs a generalized trigger framework: early arrival (> 30 min), missed/cancelled inbound flight, weather event at property (hurricane warning, storm front), room not ready at ETA, spa appointment missed due to delay, key staff absence (concierge out sick), cross-property guest transfer (checking out of one property, arriving at another same day). Each trigger maps to a re-plan with a specific diff. |
| **Why** | The diff panel is the creative proof. One trigger demonstrates the concept; a library of triggers demonstrates the system. Each trigger also represents a real operational scenario where current hotel systems produce no automatic re-plan — staff scramble manually. |
| **UX** | Trigger configuration UI (admin): define trigger type, conditions, and re-plan instructions. Trigger history log (what fired, when, what plan change resulted). Staff notification templates per trigger type. |
| **Dependencies** | PMS events (4.5.1), flight feed (4.5.3), weather feed (future), re-plan pipeline |
| **Effort** | M (framework) + S per trigger type |
| **Risk** | Medium (trigger false-positives cause unnecessary re-plans and staff disruption) |

---

#### 4.4.2 Discretion Layer — Real Auditable Subsystem

| | |
|---|---|
| **What** | The described Claude Haiku 4.5 Discretion Layer as a real, logged, contestable system. Each data signal used in plan generation is: (a) evaluated against the guest's privacy score, (b) either passed or removed with a logged rationale, (c) removals surfaced in the suppression panel with an audit trail, (d) guest-contestable via the `/profile` view. The layer is not just a narrative — it is a tamper-evident log that the privacy-conscious guest can inspect. |
| **Why** | Without this being real, the "auditable removals" copy on the live site is misleading. With it, Red Thread has a defensible privacy story that no competitor in hotel tech can match: the system that shows its work and lets the guest contest it. |
| **UX** | Suppression log entry format: signal description (what data) + privacy score at time of decision + decision (pass/remove) + rationale (one sentence, generated by Haiku) + "Contest this removal" button. Guest view of the log is read-only; staff view includes the raw signal. MOD can see all removals across all guests in current arrival window. |
| **Dependencies** | Claude Haiku integration (real, not replay), consent/privacy score persistence, audit log datastore, guest `/profile` portal (4.1.4) |
| **Effort** | L |
| **Risk** | Critical (if audit log is tampered with or incomplete, the privacy claim collapses; this must be append-only) |

---

#### 4.4.3 Arrival-Memory Reconciliation

| | |
|---|---|
| **What** | Before generating a plan, the engine compares the current dossier against the prior-stay plan and observed outcomes to detect: stale preferences (dietary restriction removed post-stay), conflicting signals (dossier says prefers quiet room but last observation was "loved the bar noise"), and escalating patterns (third consecutive stay requesting same upgrade — suggest formalizing). Surfaces conflicts to the concierge for resolution before the plan is committed. |
| **Why** | Dossiers accumulate over time. Without reconciliation, the engine confidently acts on stale data. A guest who had a surgery and changed their dietary needs two stays ago will still get a plan referencing their old preference if no reconciliation pass happens. In luxury hospitality, this is not a minor error — it is a relationship failure. |
| **UX** | Pre-plan "reconciliation brief" for the concierge: "Three things to confirm before we generate the brief" (each conflict or stale item listed, with "confirm," "update," or "clear" actions). Takes 60 seconds to complete; can be skipped with a "use last known" default. |
| **Dependencies** | Dossier versioning, plan history, cross-visit graph (4.5.6), LLM call for conflict detection |
| **Effort** | M |
| **Risk** | Medium (reconciliation that surfaces wrong conflicts is worse than no reconciliation — evaluation needed) |

---

#### 4.4.4 Arrival Ritual Composer

| | |
|---|---|
| **What** | A structured sub-component of the plan that composes a specific arrival ritual sequence for this guest at this property: the exact sequence of moments from valet approach to room key delivery, with timing, sensory details (scent, music, lighting state), and staff script fragments for each moment. Generated from the intersection of guest profile + sense-of-place card. |
| **Why** | The current role cards are briefing cards (what each role should know). The ritual composer adds a choreographic layer (the sequence of moments the guest experiences). This is the "arrival choreography" framing made explicit — a literal sequence of choreographed steps, not just parallel briefings. |
| **UX** | Staff view: a timeline with expandable moments (T-0 valet → T+2 lobby greeting → T+8 room tour → T+15 amenity reveal). Each moment: who is responsible, what they say/do, what the guest should feel. Printable for shift briefing. Guest view (optional, premium): a stripped-down version ("what to expect when you arrive") surfaced T-1h before arrival. |
| **Dependencies** | Plan engine extension, sense-of-place card schema (must include ritual/sequence fields), role card schema extension |
| **Effort** | M |
| **Risk** | Low |

---

#### 4.4.5 Evaluation & Quality Guardrails

| | |
|---|---|
| **What** | A systematic evaluation layer for plan quality: (a) automated evals — does the plan pass schema validation, does the mood banner have an internal contradiction, are all six role cards internally consistent, does the suppression panel correctly reference the guest's privacy tier; (b) human-in-the-loop — concierge reviews and approves the plan before it is pushed to staff; (c) A/B tracking — over time, do plans with higher suppression scores produce better or worse guest satisfaction outcomes? |
| **Why** | LLMs produce plausible-sounding output that can be subtly wrong (wrong name, wrong dietary note, confused property references). In a luxury context, a plan that has the guest's name spelled wrong or references a meal preference from a different guest is a catastrophic failure. Schema validation (already present via Pydantic) catches structural errors; content evals are needed to catch semantic errors. |
| **UX** | Concierge approval flow: "Review before pushing to team" — shows the full plan with a flag for any auto-eval warnings. One-click approve or edit-and-approve. Approval is logged (who approved, when). Dashboard of eval pass rates over time for GM. |
| **Dependencies** | Eval framework (LLM-as-judge or custom rubric), plan approval workflow, logging |
| **Effort** | M |
| **Risk** | High (without evals, a single bad plan reaching staff is a guest-relationship failure; with evals, failures are caught before they propagate) |

---

#### 4.4.6 Research Streams — Real Tool Orchestration

| | |
|---|---|
| **What** | The Zone I "Research Streams" (parallel tool calls — flight APIs, CRM, web search) implemented as a real agentic pipeline: structured tool definitions, parallel execution, result synthesis, and Discretion Layer filtering before results feed the plan. Flight: current status + gate + ETA. CRM: prior-stay notes, spend history, loyalty tier. Web search: recent public news about the guest (for VIP/celebrity — privacy-gated). |
| **Why** | Currently these are described/aspirational. Real research streams are what allows the system to be responsive to context without human manual input (the concierge shouldn't have to look up the flight and then type it in). |
| **UX** | Zone I as a real-time panel: each stream shows status (queued → running → complete → filtered). Results visible to authorized staff (concierge, MOD) with their privacy filter tier shown. Streams that returned no useful data are shown as "clear" (not hidden — the absence of data is also information). |
| **Dependencies** | Flight API (4.5.3), CRM integration (4.5.2), web search tool, Claude tool-use framework, Discretion Layer (4.4.2) |
| **Effort** | L |
| **Risk** | High (web search for VIP guests is a high-sensitivity PII operation — Discretion Layer must gate this correctly) |

---

#### 4.4.7 Model Routing & Cost Controls

| | |
|---|---|
| **What** | A production model routing layer: Claude Sonnet for full plan generation (quality-critical), Claude Haiku for Discretion Layer evaluations (latency-critical, high-volume), local model (Ollama) for dev/testing. Per-plan cost budget with hard ceiling. Prompt caching for sense-of-place cards and property policy rules (stable across many plans). |
| **Why** | At production scale (100 arrivals/day across 10 properties = 1000+ LLM calls/day), uncontrolled model usage becomes a significant cost line. Model routing and caching are not optimizations — they are operational necessities. |
| **UX** | No guest/staff-facing UX. GM/admin: per-property daily LLM cost dashboard. Alerts when cost exceeds budget. |
| **Dependencies** | Anthropic SDK, Ollama (local fallback), cost tracking instrumentation |
| **Effort** | M |
| **Risk** | Medium (cost overrun risk; also, routing the wrong model tier to a quality-critical path produces bad plans) |

---

### 4.5 Integrations & Data Platform

#### 4.5.1 PMS Integration (Opera Cloud / Maestro / Mews)

| | |
|---|---|
| **What** | Bidirectional PMS integration: inbound — reservation trigger (new booking → initiate pre-arrival sequence), ETA updates, room assignment, check-in event, checkout event; outbound — write room-state preferences (temperature, lighting if smart room), create work orders (amenity delivery, housekeeping instructions), update guest profile with stay notes. |
| **Why** | The PMS is the operational source of truth for hotel arrivals. Without it, the system has no way to know a guest is arriving without manual input. This is the highest-priority integration — nothing else is automatable without it. |
| **UX** | No staff-facing config UX beyond credential entry. Inbound events appear automatically as plan-generation triggers. Outbound writes show as "committed" in the actuator panel (4.2.7). |
| **Dependencies** | PMS vendor API (Opera Cloud REST API, or equivalent; Mews Open API), auth credential vault, event processing queue |
| **Effort** | XL |
| **Risk** | Critical (PMS writes to live operational systems; integration errors can cause incorrect charges, wrong room assignments, or lost work orders) |

---

#### 4.5.2 CRM / Loyalty Integration

| | |
|---|---|
| **What** | Read access to the hotel group's CRM or loyalty platform: guest lifetime value, loyalty tier, prior-property history, staff-entered preference notes, known sensitivities. This is the structured complement to the Red Thread dossier — CRM is the system of record for operational history; dossier is the system of record for arrival context. |
| **Why** | Rosewood already has guest preference data in their CRM (staff collect it manually across visits). Red Thread should augment this, not replace it. CRM integration means the engine has a richer prior-visit signal without requiring manual re-entry into a new system. |
| **UX** | CRM data surfaces in Zone I Research Streams. Concierge sees "from CRM" vs "from thread observation" source labels. Discrepancies between CRM and dossier are flagged for reconciliation (4.4.3). |
| **Dependencies** | CRM vendor API (Salesforce, Amadeus, or property-specific), data normalization layer |
| **Effort** | L–XL (varies by CRM) |
| **Risk** | High (CRM data access is politically sensitive in hotel tech — IT/GM sign-off required; data model normalization is complex) |

---

#### 4.5.3 Flight & Travel Feed Integration

| | |
|---|---|
| **What** | Real-time flight status for the guest's inbound flight: status, ETA update, gate, baggage claim, delay notification. Triggers automatic re-plan if delay exceeds threshold. Source: AeroAPI (FlightAware), Cirium, or similar. |
| **Why** | The 120-min delay re-plan is the demo's centerpiece. Making it automatic — the system detects the delay, fires the re-plan, and pushes updated briefs to staff — is what turns a demo scenario into a real operational capability. |
| **UX** | No staff action required for flight tracking. Zone I shows flight status live. Delay re-plan fires automatically; staff are notified via push (4.2.2). If flight is on time, Zone I shows "On schedule — no re-plan needed." |
| **Dependencies** | Flight data API subscription, reservation data (flight number), re-plan trigger engine (4.4.1) |
| **Effort** | M |
| **Risk** | Medium (flight data can be wrong or delayed; incorrect delay triggers cause unnecessary re-plans) |

---

#### 4.5.4 Spa, Dining & Activity Booking Integration

| | |
|---|---|
| **What** | Read/write integration with property booking systems: spa (Book4Time, SpaSoft), dining (SevenRooms, OpenTable), activities. Read: what reservations the guest already has, to inform the plan ("Guest has a 7 PM dinner reservation — do not offer alternatives that conflict"). Write: pre-book a welcome treatment based on plan recommendation (with guest consent). |
| **Why** | The "+Spa" actuator in Zone III requires write access to the spa booking system. Without it, the actuator is a button that emails someone. With it, the actuator is an automated booking — the concierge action is compressed from minutes to seconds. |
| **UX** | Read: existing bookings surface in concierge brief context. Write: actuator confirms booking with reference number. Guest receives confirmation via their preferred channel. Cancellation path (if re-plan fires and timing changes, cancel and rebook). |
| **Dependencies** | Spa/dining API access (property-specific), guest consent for pre-booking, PMS room charge integration |
| **Effort** | L–XL (varies by system) |
| **Risk** | High (incorrect bookings are guest-facing failures; requires robust cancel/rebook handling) |

---

#### 4.5.5 Guest Messaging Integration (SMS / WhatsApp / Email)

| | |
|---|---|
| **What** | Outbound messaging to guests via their preferred channel: Twilio (SMS/WhatsApp), SendGrid/Postmark (email), Apple Wallet push. Inbound reply handling (guest responds to pre-arrival SMS — response is routed to concierge and optionally to the intake flow). |
| **Why** | Currently all guest messaging is a preview ("what we would send") with no real send. Without real messaging, the guest-facing choreography is invisible to the guest. |
| **UX** | Message preview in the staff console (concierge approves before send). Delivery status (delivered, read — where available). Reply handling: replies surface in the staff console flagged as "Guest replied." Opt-out management per channel stored in consent ledger. |
| **Dependencies** | Twilio / SendGrid accounts, consent (opt-in per channel), phone/email from PMS or intake form |
| **Effort** | M |
| **Risk** | Medium (messaging compliance — SMS opt-in, unsubscribe handling; WhatsApp business API approval) |

---

#### 4.5.6 Cross-Property Guest Graph (Persistent Datastore)

| | |
|---|---|
| **What** | The portfolio guest graph — structured, durable storage of the cross-visit signal: which properties visited, in what order, what preferences were confirmed at each, what the mood/ritual was, what was suppressed and why, staff observation history. Queryable for: "What did we do for this guest at The Carlyle that worked?" "What is this guest's preference drift over 5 stays?" |
| **Why** | The dual-card model (portable profile + local sense of place) validated by Rosewood leadership only works if the portable profile is actually portable — i.e., stored and accessible cross-property. Without this, every property starts from scratch, and the cross-visit synthesis panel in the demo is always fixture data. |
| **UX** | Concierge view: "Guest history" timeline — properties visited, dates, key plan highlights, outcomes (positive/negative notes). "Carry-forward" panel: what are the persistent preferences this guest has confirmed across ≥ 3 stays? These are the high-confidence signals that should always be in the plan. |
| **Dependencies** | Persistent DB (3.1), dossier schema (must be property-agnostic for portable fields, property-specific for local fields), cross-property RBAC (a concierge at Sand Hill can see that a guest stayed at Carlyle, but not the Carlyle staff's private notes) |
| **Effort** | L |
| **Risk** | High (cross-property data sharing requires careful RBAC and guest consent — guest may not consent to their data crossing property boundaries) |

---

#### 4.5.7 Data Abstraction & Adapter Layer

| | |
|---|---|
| **What** | An integration abstraction layer that decouples the Red Thread engine from specific vendor implementations: a PMS adapter interface (Opera Cloud, Mews, Maestro all implement the same interface), a CRM adapter, a messaging adapter. New integrations are plugins; the engine code does not change. |
| **Why** | Hotel tech is deeply fragmented. No two properties use exactly the same PMS/CRM stack. Without an adapter layer, adding a new property requires new integration code in the core engine — a scaling disaster. |
| **UX** | Admin: integration marketplace listing available adapters. Property onboarding: select your PMS from a list, enter credentials, test connection. |
| **Dependencies** | Architecture decision (adapter pattern vs. iPaaS like Boomi or Mulesoft), each specific integration (4.5.1–4.5.5) |
| **Effort** | L |
| **Risk** | Medium (over-engineered abstraction can slow early integrations; under-engineered abstraction requires rewrites later) |

---

### 4.6 Privacy, Security, Compliance & Trust

#### 4.6.1 PII Data Classification & Field-Level Encryption

| | |
|---|---|
| **What** | A formal PII data classification schema (tier 1: name/contact; tier 2: preferences/history; tier 3: financial/health/family/relationship context). Field-level encryption for tier 2 and tier 3 fields at rest. TLS everywhere in transit. Key management (AWS KMS or similar). |
| **Why** | HNW/VIP guest data is a high-value target. A data breach affecting a roster of Rosewood guests (diplomats, executives, celebrities, HNWIs) is a catastrophic brand and legal event. Field-level encryption means a database compromise does not expose the most sensitive dossier content in plaintext. |
| **UX** | No user-facing UX; entirely infrastructure. Operational cost: slightly slower read/write on encrypted fields; manageable with key caching. |
| **Dependencies** | DB design (3.1), key management service, data classification schema |
| **Effort** | M |
| **Risk** | Critical (non-negotiable before any pilot with real guest data) |

---

#### 4.6.2 Consent Ledger & Auditable Removals

| | |
|---|---|
| **What** | An append-only consent ledger: every consent grant, update, withdrawal, and Discretion Layer removal is a signed, timestamped record. Records are: immutable (append-only), exportable per guest (GDPR right of access), deletable per guest (GDPR right to erasure — deletion of the consent record AND all associated PII in scope). The guest `/profile` portal exposes a human-readable view of this ledger. |
| **Why** | GDPR Article 7 (conditions for consent) and Article 17 (right to erasure) require a demonstrable consent record. For HNW guests and VIP privacy concerns, this ledger is also a trust artifact — showing it exists (and is inspectable) is a differentiating feature, not just a compliance checkbox. |
| **UX** | Guest view: "Your consent history" — a chronological list of what was consented to, what was updated, what was removed by the Discretion Layer, and any guest-initiated contests. One-click "Erase my thread" — triggers GDPR erasure workflow, sends confirmation. Staff view: read-only ledger per guest (concierge/MOD) + write-only (Discretion Layer). |
| **Dependencies** | Append-only DB design, encryption (4.6.1), guest portal (4.1.4), Discretion Layer (4.4.2) |
| **Effort** | L |
| **Risk** | Critical (GDPR non-compliance; also, if the ledger can be retroactively altered, the "auditable" claim is false) |

---

#### 4.6.3 RBAC & Least-Privilege Access Controls

| | |
|---|---|
| **What** | Role-based access control enforced at the API layer (not just the UI): each staff role can only read the data their role card contains, plus operational metadata relevant to their function. Cross-property data access is consent-gated. Admin access to raw PII requires a separate elevated-privilege auth step (break-glass pattern). |
| **Why** | A valet who can see a guest's family situation and financial history is both a privacy failure and an insider-threat risk. Least-privilege is the policy that makes "Hold the Thread" operationally real — the guest's privacy preference is enforced not just by the Discretion Layer but by the access control layer. |
| **UX** | Staff see only what their role card contains. Attempts to access out-of-scope data return a permission-denied response (not a redirect to login — staff need to know access was denied, not assume they are logged out). Admin break-glass: requires secondary auth factor + written justification + triggers an alert to GM. |
| **Dependencies** | Auth/identity (3.2), role management (4.3.3), API gateway |
| **Effort** | M |
| **Risk** | Critical |

---

#### 4.6.4 Audit Log — Complete Data Access Trail

| | |
|---|---|
| **What** | An append-only audit log of every data access and mutation: who accessed which guest's data, what operation (read/write/delete), from which surface (staff mobile, admin console, API), at what time, with what justification (if write). Retained per regulatory requirement (typically 2–7 years). Queryable by GM and compliance team. Alerts on anomalous access patterns (one staff member accessing all guest dossiers in 5 minutes). |
| **Why** | In a hotel context, insider threat (staff leaking VIP guest information to tabloids or extracting financial information) is a real risk. An audit log is the primary deterrent and the investigation tool when incidents occur. |
| **UX** | Not guest-facing (separate from the consent ledger, which is guest-visible). GM/compliance console: searchable log. Pre-built queries ("Show me all accesses to guest X's record in the last 30 days"). Anomaly alerts delivered via email/Slack to GM. |
| **Dependencies** | Append-only event log datastore, RBAC (4.6.3), alerting |
| **Effort** | M |
| **Risk** | High |

---

#### 4.6.5 GDPR / CCPA / Global Privacy Compliance

| | |
|---|---|
| **What** | Formal compliance program: data processing agreements with third-party vendors (Anthropic, ElevenLabs, flight APIs), data residency configuration (EU guests' data stays in EU), cookie/tracking consent for the guest-facing web surface, privacy policy published and linked, incident response plan for breach notification (GDPR 72-hour notification requirement). |
| **Why** | Rosewood operates in the EU (GDPR) and California (CCPA). A hotel tech platform handling guest PII without these in place is not a partner any major hotel group can adopt — legal review will block it. |
| **UX** | Cookie consent banner on guest-facing web (minimal — preference-cookie only, no advertising). Privacy policy linked in footer of every guest-facing surface. "Data residency" selector in property onboarding admin. |
| **Dependencies** | Legal counsel, vendor DPAs, data residency infrastructure config, consent ledger (4.6.2) |
| **Effort** | M (framework) + ongoing |
| **Risk** | Critical (non-compliance blocks pilot with any regulated hotel group) |

---

#### 4.6.6 Security Review & Penetration Testing

| | |
|---|---|
| **What** | A formal security review before any pilot: OWASP Top 10 scan, penetration test (external red team), dependency vulnerability scan, secrets management audit (no credentials in code or logs), LLM prompt injection testing (can a malicious guest intake submission exfiltrate another guest's data via the LLM call?). |
| **Why** | LLM prompt injection is a novel attack surface specific to this product. A guest who submits a crafted intake response designed to manipulate the plan generation could potentially exfiltrate data from the system prompt (which contains the dossier). This must be tested before real guest data is in scope. |
| **UX** | No user-facing UX. Process: engage a security firm with hotel-tech + LLM experience; findings must be remediated before pilot. |
| **Dependencies** | All of 4.6.1–4.6.5 in place first; stable API surface |
| **Effort** | M |
| **Risk** | Critical (especially prompt injection given the LLM-mediated pipeline) |

---

### 4.7 Reliability, Observability & Operations

#### 4.7.1 Structured Logging & Distributed Tracing

| | |
|---|---|
| **What** | Replace ad-hoc print/log statements with structured logging (JSON logs, per-request trace ID). Distributed tracing across the multi-step agentic flow: intake → research streams → Discretion Layer → plan generation → actuator pushes → staff notification. Each step emits a span. Trace ID propagated to LLM call metadata for cost attribution. |
| **Why** | When a plan fails or is wrong, the current system offers no way to diagnose which step failed. Tracing makes every plan generation reproducible and debuggable. Also enables cost attribution (which plan consumed how many LLM tokens). |
| **UX** | Engineering/ops only. Recommend OpenTelemetry → Honeycomb or Datadog. |
| **Dependencies** | OTel SDK, trace backend |
| **Effort** | M |
| **Risk** | Medium (without this, production incidents are undiagnosable) |

---

#### 4.7.2 LLM Fallback & Graceful Degradation

| | |
|---|---|
| **What** | Production version of the current 3-tier backend: if Claude API is unavailable, route to local Ollama (if property has local compute), or surface the last cached plan (with "using last known brief — verify with concierge" flag), or fall back to a manual briefing template. Degradation must be automatic, logged, and visible to the MOD. Under no circumstances should the system show a blank brief to staff before an arrival. |
| **Why** | A hotel operation cannot tolerate a tool that goes blank when the LLM API has an outage. The current offline-replay mode is a demo fallback; production needs a real tiered degradation policy with SLA expectations per tier. |
| **UX** | System status indicator visible to concierge and MOD ("Live AI / Cached plan / Manual mode" badge). Alert to MOD when degradation fires. Auto-recovery when Claude API returns. |
| **Dependencies** | 3-tier backend (already exists in code), health-check integration, notification to MOD |
| **Effort** | S–M |
| **Risk** | High (undetected degradation to a stale plan causes operational failures) |

---

#### 4.7.3 Uptime SLA & Deployment Architecture

| | |
|---|---|
| **What** | Move from single-process FastAPI to a production deployment: containerized (Docker), orchestrated (Kubernetes or ECS), with: health checks, automatic restart, horizontal scaling for concurrent arrival processing, a CDN for static assets, managed database (RDS or Cloud SQL), secrets management (AWS Secrets Manager or Vault). |
| **Why** | A single Python process cannot support multiple concurrent properties, has no automatic recovery from crashes, and provides no path to the 99.9% uptime that a hospitality-critical system requires. |
| **UX** | No user-facing UX. Operational: zero-downtime deploys (rolling update), blue/green deployment for major releases, database migration automation. |
| **Dependencies** | Cloud provider selection, containerization, CI/CD pipeline |
| **Effort** | L |
| **Risk** | High (single process is a single point of failure; this is not optional for production) |

---

#### 4.7.4 Incident Response Playbook

| | |
|---|---|
| **What** | A documented and rehearsed incident response process: severity tiers (P0 = arrival failure for in-progress VIP arrival; P1 = system degraded; P2 = non-critical feature failure), escalation paths (on-call engineer, property GM, hotel IT), communication templates (what to tell the hotel when the system is down), and a post-incident review process. |
| **Why** | When a VIP guest is in a car 20 minutes from the property and the system fails, the hotel needs a clear manual fallback and a clear escalation path. Without a playbook, chaos ensues and the hotel blames the product. |
| **UX** | Internal process document; not user-facing. |
| **Dependencies** | On-call rotation, alerting (4.7.1), contacts from each pilot property |
| **Effort** | S |
| **Risk** | High (absence of playbook means first incident is also a learning experience in front of a paying pilot customer) |

---

### 4.8 Analytics, Feedback & Continuous Improvement

#### 4.8.1 Arrival Outcome Tracking

| | |
|---|---|
| **What** | Post-arrival outcome data: did the guest comment on the arrival? (captured via staff observation loop), was there a service recovery event?, did the guest modify their room state after arrival? (PMS signal), did the guest use the spa/dining booking the plan recommended? (booking system feedback). Outcomes linked to the plan that generated them. |
| **Why** | Without outcome data, there is no way to know if the plan was good. Plan quality is currently judged by schema validation and human review — a necessary but insufficient bar. Outcome data enables: model prompt improvement, suppression calibration, and the GM ROI story ("arrivals with Red Thread plans had 23% higher satisfaction scores"). |
| **UX** | GM dashboard: arrival cohort analysis (with plan / without plan), outcome metrics per arrival trigger type, top-suppressed items and their outcomes when staff override vs. follow. |
| **Dependencies** | PMS integration (4.5.1), spa/dining integration (4.5.4), staff observation loop (4.2.3), persistence |
| **Effort** | M |
| **Risk** | Medium (outcome attribution is noisy; causality claims require care) |

---

#### 4.8.2 Staff Plan Feedback

| | |
|---|---|
| **What** | After each arrival, a lightweight staff feedback prompt for the relevant concierge/MOD: "Was the brief accurate?" (yes/mostly/no), "Which cards were most useful?" (multi-select), "Anything the plan missed?" (free text). Feedback stored against the plan; recurring misses flag a prompt or dossier improvement. |
| **Why** | Staff are the closest observers of plan quality. A concierge who knows the plan got the guest's room preference wrong is the fastest feedback loop available. Without capturing this, the system never learns from its errors. |
| **UX** | Post-arrival notification (push) to concierge: "Quick debrief on [Guest Name]'s arrival?" — 3 questions, < 60 seconds. Optional free text. Not a survey; framed as "help us improve the brief." |
| **Dependencies** | Staff mobile surface (4.2.1), push notifications (4.2.2), feedback datastore |
| **Effort** | S |
| **Risk** | Low |

---

#### 4.8.3 GM & Portfolio Analytics Dashboard

| | |
|---|---|
| **What** | A GM-facing analytics surface: arrivals processed (vs. total arrivals), plan generation success rate, most common triggers, suppression analysis (what is suppressed most, what is overridden most), staff adoption metrics (what % of staff opened their role card before the arrival), and eventually guest satisfaction correlation. For portfolio operators: cross-property comparisons. |
| **Why** | GMs need to justify the system to ownership. "We used AI for X% of arrivals and saw Y% higher service quality scores" is the ROI story. Without an analytics layer, the ROI is anecdotal. |
| **UX** | Executive-friendly dashboard: KPI tiles at top, trend charts below, drilldown to individual arrivals. Exportable as PDF for ownership reports. |
| **Dependencies** | Analytics datastore (time-series), outcome tracking (4.8.1), GM role in RBAC |
| **Effort** | M |
| **Risk** | Low (analytics are read-only; no guest-facing impact) |

---

#### 4.8.4 A/B Testing — Suppression Calibration

| | |
|---|---|
| **What** | A controlled framework for testing different Discretion Layer policies: for a sample of arrivals, vary the suppression threshold or the model used for evaluation, and track whether outcomes differ. Also applicable to: plan prompt variants (does a more poetic mood banner drive better guest comments?), ritual sequence variants. |
| **Why** | The "tasteful restraint" thesis is a hypothesis. A/B testing is how it becomes evidence. At scale, small improvements in suppression calibration (getting the "creepy vs. magic" line right more often) compound into significant guest satisfaction and staff adoption gains. |
| **UX** | Admin: A/B experiment configuration (variant definition, traffic split, measurement period, success metric). Dashboard of live and completed experiments. Auto-stop on statistical significance. |
| **Dependencies** | Outcome tracking (4.8.1), analytics infrastructure, sufficient arrival volume (A/B requires volume to be meaningful — relevant at Phase 2+) |
| **Effort** | M |
| **Risk** | Low (experiments are read-only on guest experience; suppression policy changes are the only guest-facing variable) |

---

### 4.9 Commercialization & Platform

#### 4.9.1 Pricing & Packaging Model

| | |
|---|---|
| **What** | A defined commercial model: per-property SaaS subscription (likely tiered by arrival volume), a per-arrival API pricing tier for high-volume chains, an enterprise-agreement path for portfolio operators (Rosewood, Four Seasons, Mandarin Oriental). Includes: what is included in each tier (which integrations, which AI features, which analytics), and a pilot/proof-of-concept pricing path. |
| **Why** | Without a commercial model, even a successful pilot cannot convert to revenue. Hotel tech buyers expect annual contracts, ROI projections, and a clear path from pilot to enterprise agreement. |
| **UX** | Pricing page (marketing site, separate from the app). Pilot agreement templates. Usage-based billing dashboard for the hotel operator. |
| **Dependencies** | Legal (contract templates), billing infrastructure (Stripe or similar), usage tracking (4.7.1) |
| **Effort** | M |
| **Risk** | Medium (hotel tech procurement cycles are long — 6–18 months for enterprise; pilot pricing must be low enough to bypass lengthy procurement) |

---

#### 4.9.2 Pilot-to-Scale Rollout Framework

| | |
|---|---|
| **What** | A defined path from single-property pilot (1 property, limited arrival volume, manual onboarding) to portfolio scale (10+ properties, automated onboarding, full integration stack). Includes: pilot evaluation criteria, go/no-go checkpoints, escalation path for integration issues, and a success playbook for the GM to champion internal rollout. |
| **Why** | The first pilot property is a reference customer. The framework for how the pilot runs determines whether it produces a case study or an incident report. |
| **UX** | Internal process + GM-facing pilot dashboard (progress against rollout milestones). |
| **Dependencies** | Property onboarding flow (4.3.6), all pilot-required integrations, incident response playbook (4.7.4) |
| **Effort** | M |
| **Risk** | High (pilot failure is a reference-customer failure; the first pilot must succeed) |

---

#### 4.9.3 API for Hotel Tech Ecosystem

| | |
|---|---|
| **What** | A documented, versioned REST/webhook API that allows hotel tech ecosystem partners to: receive arrival plan events (PMS vendors, revenue management systems, housekeeping apps), push signals into the research stream (concierge apps, guest-facing hotel apps), and subscribe to actuator actions (spa systems, dining systems receiving booking events). |
| **Why** | Hotel tech is an ecosystem play. The properties that will buy Red Thread already use 5–10 other systems. Positioning Red Thread as an orchestration layer that other systems plug into (rather than a replacement for those systems) requires an open API. |
| **UX** | Developer portal: API reference docs, webhook configuration UI, sandbox environment, API keys per integration partner. |
| **Dependencies** | Stable API design, auth (API key + OAuth), rate limiting, versioning policy |
| **Effort** | L |
| **Risk** | Medium (public API surface is an attack surface — security review required; versioning must be disciplined) |

---

#### 4.9.4 Partner / Marketplace Model

| | |
|---|---|
| **What** | A marketplace for integration adapters (4.5.7): certified PMS/CRM/spa/dining adapters built by Red Thread or by third-party integration partners. Hotel operators can browse and install certified adapters. Partners can build and certify adapters for revenue share or flat fee. |
| **Why** | At scale, Red Thread cannot build every integration. A partner marketplace distributes the integration burden while maintaining quality control (certification gate). |
| **UX** | Marketplace UI in admin console: browse adapters by category, read reviews from other properties, install with one click (credentials entered separately). Partner portal for adapter developers. |
| **Dependencies** | API (4.9.3), adapter layer architecture (4.5.7), legal (partner agreements, revenue share) |
| **Effort** | XL |
| **Risk** | Medium (marketplace governance is complex; a bad adapter damages the platform reputation) |

---

## 5. Prioritized Phased Roadmap

### Phase 0 — "Make the Demo Honest & Hardened"
**Theme:** Close the gap between what the live site claims and what the system actually does. No new features; fix the lies.
**Timeline:** Weeks 1–4 post-hackathon

| Item | Catalog Ref | Why Now |
|---|---|---|
| Persistent consent profile (backend) | 4.1.1 | The slide literally exists; without backend it is false advertising |
| Real intake submission + confirmation state | 4.1.3 | Core guest flow has no real submit path |
| Auth (basic — staff login, guest token from reservation) | 3.2 | Prerequisite for everything; can be minimal (JWT + simple IdP) |
| SQLite → PostgreSQL with schema | 3.1 | In-memory state is a demo artifact; persistence is a product prerequisite |
| Suppress overlay — staff override + logging | 4.2.6 | Already has UI; needs backend log |
| Structured logging + trace IDs | 4.7.1 | Can't debug production without this; 1 day of eng work |
| LLM fallback hardening (from demo offline to real degradation policy) | 4.7.2 | Current 3-tier is demo-mode; production degradation must be auto-detected |
| Secrets management (no credentials in env or code) | 4.6.1 partial | Before any real guest data enters the system |

**Entry criteria:** Hackathon demo complete.
**Exit criteria:** The system can: accept a real guest submission, persist it, generate a plan, and show a staff brief — with real auth and a real database. No demo fixtures required for the happy path. Security audit of Phase 0 completed.

---

### Phase 1 — "Single-Property Pilot-Ready MVP"
**Theme:** One property (Rosewood Sand Hill), real guests, real integrations, real staff workflow. Compliant, observable, reliable.
**Timeline:** Months 2–6 post-hackathon

| Item | Catalog Ref | Why Now |
|---|---|---|
| PMS integration (Opera Cloud or Mews) | 4.5.1 | Unlocks automatic arrival trigger; foundational |
| Flight feed integration (AeroAPI) | 4.5.3 | Enables automatic delay re-plan (the product's core differentiator in production) |
| Mobile role-card brief (PWA) | 4.2.1 | Staff adoption depends on mobile surface |
| Push notifications for re-plan | 4.2.2 | Re-plan is useless if staff don't receive it |
| Dossier authoring tool | 4.3.5 | Concierge staff need a UI; Markdown is not an ongoing solution |
| Sense-of-place card authoring | 4.3.1 | Property manager must be able to maintain this without engineering |
| PII encryption + consent ledger | 4.6.1, 4.6.2 | Non-negotiable before real guest data in production |
| RBAC (role → card mapping, enforced at API) | 4.6.3 | Must be in before pilot; role misassignment is a compliance failure |
| GDPR/CCPA compliance framework | 4.6.5 | Required for any EU or CA guest |
| Discretion Layer — real (Haiku, logged) | 4.4.2 | The privacy story is only real when the audit log is real |
| Pre-arrival guest communication (T-24h SMS/email) | 4.1.2 | Guest-facing choreography requires at least one real communication |
| Staff observation capture — formalized | 4.2.3 | Staff-as-sensors loop; foundational for dossier improvement |
| Deployment: containerized + managed DB | 4.7.3 | Single process cannot support a pilot |
| Arrival outcome tracking (basic) | 4.8.1 | Need this from day 1 to build ROI story |
| Staff plan feedback (lightweight) | 4.8.2 | Fastest quality feedback loop available |
| Penetration test + security review | 4.6.6 | Must pass before pilot go-live |

**Entry criteria:** Phase 0 complete; pilot property agreement signed; PMS vendor API access granted.
**Exit criteria:** ≥ 20 arrivals processed end-to-end (real reservations, real staff, real guests), ≥ 80% staff card-open rate before arrival, zero security incidents, GDPR compliance documentation complete. GM debrief positive.

---

### Phase 2 — "Multi-Property / Portfolio"
**Theme:** Scale the single-property MVP to a portfolio. Onboarding automation, cross-property graph, richer guest experience, generalized triggers.
**Timeline:** Months 7–18 post-hackathon

| Item | Catalog Ref | Why Now |
|---|---|---|
| Multi-property tenancy model | 3.2 | Prerequisite for every item in this phase |
| Property onboarding wizard | 4.3.6 | Manual onboarding doesn't scale past 2–3 properties |
| Cross-property guest graph (persistent) | 4.5.6 | The dual-card model's value compounds across properties |
| Arrival-memory reconciliation | 4.4.3 | Dossiers will drift; reconciliation becomes critical at scale |
| CRM / loyalty integration | 4.5.2 | Prior-visit history at scale requires CRM read |
| Generalized trigger engine | 4.4.1 | Early arrival, weather, room-not-ready, missed-appointment triggers |
| Actuator panel — real PMS/POS write-back | 4.2.7 | Zone III becomes real at Phase 2; write-back per-property integration |
| Messaging — full sequence (T-72h, T-24h, T-2h) | 4.1.2 extended | Full pre-arrival choreography for guests |
| Guest profile portal — full self-service | 4.1.4 | Guest dossier transparency and GDPR erasure interface |
| Post-stay memory confirmation | 4.1.6 | Dossier quality improvement loop |
| Digital key + Wallet pass | 4.1.5 | Premium arrival surface; reduces friction |
| Shift handoff + MOD board | 4.2.4 | Required when multiple properties have staggered arrivals |
| Research streams — real tool orchestration | 4.4.6 | Zone I becomes real; flight/CRM/web search live |
| GM analytics dashboard | 4.8.3 | Portfolio operators need cross-property analytics |
| RBAC — cross-property (consent-gated) | 4.6.3 extended | Cross-property data sharing requires explicit guest consent |
| White-label / property branding | 4.3.4 | Each property needs its own brand expression |
| Pricing model + billing infrastructure | 4.9.1 | Revenue starts; billing must be automated |

**Entry criteria:** Phase 1 pilot successful; ≥ 1 additional property committed; cross-property guest consent model finalized with legal.
**Exit criteria:** ≥ 3 properties live, ≥ 200 arrivals/month processed, self-service onboarding operational, cross-property guest graph queryable by authorized concierge staff, ARR target defined and on track.

---

### Phase 3 — "Platform & Ecosystem"
**Theme:** Red Thread as a platform other hotel tech systems plug into. Marketplace, API, A/B calibration, global scale.
**Timeline:** Month 18+ post-hackathon

| Item | Catalog Ref | Why Now |
|---|---|---|
| API for hotel tech ecosystem | 4.9.3 | Partner integrations require a stable, documented API |
| Data abstraction / adapter marketplace | 4.5.7, 4.9.4 | Integration burden distributed to partners |
| In-stay guest interaction surface | 4.1.8 | Extends beyond arrival; full stay choreography |
| Arrival ritual composer | 4.4.4 | Full choreographic layer; differentiator at luxury tier |
| A/B testing — suppression calibration | 4.8.4 | Requires scale; validates the restraint thesis empirically |
| Accessibility + i18n | 4.1.7 | Global scale requires multilingual, accessible surfaces |
| Model routing + cost controls | 4.4.7 | LLM cost optimization at platform scale |
| Evaluation + quality guardrails | 4.4.5 | Automated evals + human-in-the-loop at volume |
| Pilot-to-scale rollout framework (codified) | 4.9.2 | Self-service pilot program |
| Pricing tier — per-arrival API | 4.9.1 extended | High-volume chains prefer consumption pricing |

**Entry criteria:** Phase 2 at ≥ 5 properties; stable API surface; at least one external integration partner.
**Exit criteria:** External integrations via marketplace account for ≥ 20% of integration surface; product can be onboarded by a new property without direct engineering involvement.

---

## 6. Cross-Cutting Principles & Open Questions

### The Restraint/Consent Principle — Enforced Product Law

The "they just knew vs. that's creepy" tension is not a marketing narrative — it must be the organizing principle of every product decision:

1. **Default to less.** The default privacy dial is "Held" (6/10). Features should require opt-in to access more data, not opt-out to restrict it.
2. **Show the work.** Every suppression must be explainable in one sentence the guest can read. "We chose not to offer the spa because your privacy preference is Standard and the spa interest signal came from a public source" is the standard. Opaque suppression is not acceptable.
3. **Guest contest is not a support ticket.** The `/profile` "contest this removal" flow must be a first-class product interaction — resolved within minutes by the concierge, not routed to a help desk.
4. **Staff override is logged, always.** No override should be untracked. Every departure from the plan is data for improvement.
5. **The absence of data is data.** A "clear" zone in the research stream (no signal found) should be surfaced to staff, not hidden. A guest with no digital footprint deserves the same quality of arrival as one with a rich profile — the system should gracefully handle sparse dossiers without defaulting to generic plans.

### What Must Be Validated With Rosewood / Operators Before Building

The following are open product questions that require operator validation — building without this validation risks building the wrong thing:

| Question | Why It Matters | Validated? |
|---|---|---|
| What is the actual CRM/dossier workflow today, and where does Red Thread fit in vs. replace? | Dual-card model was validated at concept level; the operational workflow integration has not been mapped. Building a dossier tool that conflicts with existing concierge workflows will cause rejection. | No |
| Which staff roles have smartphones / tablets available on the floor, and what are the connectivity conditions? | Mobile-first brief design depends on actual device availability and network quality in hotel service areas. | No |
| Is the PMS Opera Cloud, and do we have API access committed? | Entire Phase 1 integration stack depends on PMS vendor. The answer changes the effort by 1–3 months. | No |
| What is the guest consent model for cross-property data sharing? | The cross-property graph is only buildable if guests consent to their data crossing property boundaries. Legal/privacy team must define this before architecture is committed. | No |
| What is the privacy/legal stance on web-search signals for VIP/celebrity guests? | The research-stream web-search tool is high-value and high-risk. Hotel group legal must sign off on what public signals are permissible inputs before this is built. | No |
| What is the acceptable LLM latency budget for the pre-arrival brief? (i.e., how far in advance does the concierge need the plan?) | This determines whether prompt caching and Haiku routing are required from Phase 1 or can wait. | No |
| What does "arrival outcome" mean to a GM? (Is it satisfaction score, repeat booking, upsell conversion, or something else?) | Outcome tracking (4.8.1) is only useful if it measures what GMs care about. | No |

### Key Open Product & Architecture Questions

| Question | Implication |
|---|---|
| Should the guest-facing surface be a web portal, SMS-only, or a hotel-branded native app? | Determines mobile dev stack and distribution strategy; native app implies App Store approval cycle and hotel IT involvement. |
| Is the dossier the source of truth, or is the CRM? | Data ownership and conflict resolution model depends on this. Getting it wrong creates a political problem with hotel CRM teams. |
| What is the minimum viable integration stack for Phase 1? (PMS only? PMS + flight? PMS + messaging?) | Determines pilot timeline and integration risk. |
| Should the Discretion Layer model (Haiku) be replaceable by the hotel operator (e.g., with a local/private model for ultra-sensitive properties)? | Ultra-privacy-conscious properties (heads of state, high-profile executives) may require that no guest data leaves their network. This requires a local LLM path for the Discretion Layer specifically. |
| How does the product handle a guest who has no dossier yet (first-time guest)? | The engine is optimized for returning guests. A first-time guest arrival should be graceful — the system should surface a minimal but useful plan, not fail. The "sparse dossier" case must be designed, not inherited. |
| What is the licensing and data-processing agreement with Anthropic and ElevenLabs for use in a commercial hotel context with real PII? | Standard API terms may not cover commercial PII processing at scale. DPA negotiation timeline could affect Phase 1 date. |

---

## Reasoning

**Decision chain:**
1. Grounded analysis in four WebFetch probes of the live site (home, `/profile`, `/intake`, `/dashboard`-404) to establish what is actually present vs. aspirational.
2. Cross-referenced against the SenseArrival engine codebase characterization (CONTEXT 2) to identify the demo↔engine gap accurately.
3. Organized the feature catalog by operational domain (guest, staff, admin, AI, integrations, privacy/security, reliability, analytics, commercial) to match how a founding team would actually allocate work.
4. Phased the roadmap by risk and dependency order: Phase 0 (honesty), Phase 1 (one real thing working), Phase 2 (scale), Phase 3 (platform) — a standard SaaS maturation arc adapted to hotel tech's long procurement and integration cycles.
5. The restraint/consent thesis was treated as a non-negotiable cross-cutting constraint, not a feature to be scheduled.

**Constraints applied:**
- Hackathon-locked items treated as already-specced baseline (not re-listed as gaps, but noted where productization changes/hardens them).
- Explicitly out-of-scope items from hackathon (persistent DB, real auth, real integrations, real comms, real STT at scale, production deployment) treated as the primary productization frontier.
- No code changes; research only.

**Confidence:** High on the gap analysis and feature catalog (grounded in live site observation + codebase characterization). Medium on effort estimates (hotel tech integration timelines are highly variable; PMS integration in particular can range from weeks to quarters depending on vendor cooperation). Medium on Phase 2+ roadmap (sequencing will shift based on operator validation findings in Phase 1).
