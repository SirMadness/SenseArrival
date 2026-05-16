# ADR-002: Portfolio Guest Graph — Cycle-2 Architecture Deltas

## Status
Accepted

## Context

ADR-001 established the fixed stack (Python 3.11 + FastAPI + Jinja2/HTMX + Anthropic SDK + ElevenLabs SDK + Pydantic v2) and the core domain model (GuestProfile, ArrivalPlan, RoleCard, PlanDiff) around a single guest persona (Ms. Chen) and a single property fixture. Discovery cycle 2 locked five requirements that widen the domain without changing the stack: TREQ-019 (3 dossiers × 3 properties), TREQ-020 (dossier + sense-of-place card format), TREQ-021 (cross-visit synthesis), TREQ-022 (fixture selector), TREQ-023 (staff-note → dossier loop, in-memory). This ADR resolves each delta as a concrete decision so BL-001 (foundation) and BL-002 (orchestrator) are built once on the correct model — no mid-build refactor.

Stack is fixed. No new dependencies are introduced.

---

## Delta 1 — Domain Model (TREQ-019, TREQ-020, TREQ-021)

### Decision

Introduce four new Pydantic models and rename/extend one existing model. ADR-001's GuestProfile is **replaced** by GuestDossier. ArrivalPlan, RoleCard, and PlanDiff are **unchanged**.

```python
# models.py  (additions / replacements from ADR-001)

class PriorStay(BaseModel):
    property_id: str                  # matches PropertyCard.property_id, e.g. "rosewood-london"
    dates: str                        # human-readable, e.g. "March 2024"
    staff_observations: list[str]     # raw notes from that property's staff, 1–5 bullet strings

class GuestDossier(BaseModel):
    guest_id: str                     # slug, e.g. "ms-chen"
    name: str
    nationality: str
    arrival_property_id: str          # which PropertyCard is "deep" for this visit
    profile_summary: str              # stable persona summary (dietary, accessibility, style)
    prior_stays: list[PriorStay]      # ordered newest-first; may be empty for first-visit guests

class PropertyCard(BaseModel):
    property_id: str                  # slug, e.g. "rosewood-sand-hill"
    name: str
    location: str                     # city/region
    depth: Literal["arrival", "provenance"]   # arrival = full render; provenance = context only
    sense_of_place: str               # raw Markdown blob (local culture, landmarks, activities)
    signature_anchors: list[str]      # 3–6 specific named anchors used for grounding prompts

class GuestSynthesis(BaseModel):
    unified_understanding: str        # 2–4 sentence prose: what the system infers cross-visit
    inferred_preferences: list[str]   # bullet list surfaced in the UI ("inferred from prior stays")
    provenance_properties: list[str]  # property_id list that contributed observations

# Unchanged from ADR-001 — do not modify these signatures:
# class ArrivalPlan(BaseModel): ...
# class RoleCard(BaseModel): ...
# class PlanDiff(BaseModel): ...
```

**Rationale:** GuestProfile had no prior-stay structure; a clean rename to GuestDossier with added `prior_stays` avoids a partial-extension anti-pattern. PropertyCard replaces the implicit `sand_hill_context.json` blob with an explicit, typed model — the `sense_of_place` field carries the raw Markdown content loaded at startup. GuestSynthesis is a discrete, addable field on the orchestrator's internal context object (not a top-level API response field), keeping ArrivalPlan unchanged. `depth` on PropertyCard makes the arrival-vs-provenance distinction machine-readable without adding a separate type hierarchy.

---

## Delta 2 — Fixture Format and Directory Layout (TREQ-020)

### Decision

Markdown files are the source for dossiers and property cards. JSON files are used exclusively for offline-replay plans. No parser is written — files are loaded with `open().read()` and injected directly into the prompt as a labeled block.

**Directory layout (under `sense_arrival/fixtures/`):**

```
sense_arrival/
  fixtures/
    dossiers/
      ms-chen.md                   # GuestDossier: returning guest, cross-property history
      mr-okafor.md                 # GuestDossier: second demo persona
      dr-reyes.md                  # GuestDossier: third demo persona
    properties/
      rosewood-sand-hill.md        # PropertyCard: arrival property, depth=arrival
      rosewood-london.md           # PropertyCard: provenance property 1
      rosewood-beijing.md          # PropertyCard: provenance property 2
    plans/
      baseline_plan.json           # Offline-replay: ArrivalPlan for canonical path
      replanned_plan.json          # Offline-replay: re-planned ArrivalPlan for canonical path
      synthesis_fixture.json       # Offline-replay: GuestSynthesis for canonical path
    delay_event.json               # Injected delay payload (unchanged from ADR-001)
```

**Markdown template — Guest Dossier (`dossiers/[guest-id].md`):**

```markdown
# Guest Dossier: [Full Name]

## Profile
- **Guest ID:** [slug, e.g. ms-chen]
- **Nationality:** [Country]
- **Dietary:** [e.g. vegetarian, gluten-free, none noted]
- **Accessibility:** [e.g. prefers ground floor, none noted]
- **Style:** [2–3 words, e.g. quiet / restorative / understated]
- **Summary:** [2–3 sentence persona — tone, priorities, what matters to this guest]

## Prior Stays

### [Property Name] — [Month Year]
**Property ID:** [rosewood-property-slug]
**Staff Observations:**
- [Verbatim or paraphrased note from that property's staff]
- [Another observation — specific behaviors, preferences, requests]
- [Third observation if available]

### [Next Property Name] — [Month Year]
**Property ID:** [rosewood-property-slug]
**Staff Observations:**
- [Observation]
- [Observation]

<!-- Add or remove Prior Stay sections as needed. Newest stay first. -->
<!-- If no prior stays: omit the Prior Stays section entirely. -->
```

**Markdown template — Property Card (`properties/[property-id].md`):**

```markdown
# Property Card: [Full Property Name]

## Identity
- **Property ID:** [slug, e.g. rosewood-sand-hill]
- **Location:** [City, Region/Country]
- **Depth:** [arrival | provenance]

## Sense of Place
[3–5 paragraph prose about the destination's local culture and activities —
theatre, landmarks, regional food scene, outdoor activities, seasonal experiences.
Focus on what a discerning traveler would want to know about THIS DESTINATION,
not just on-property amenities. Be specific: name venues, districts, experiences.]

## Signature Anchors
Specific named experiences and places grounded in this location:
- [Named anchor 1, e.g. "Stanford Shopping District"]
- [Named anchor 2, e.g. "Ridge Winery rosé tasting"]
- [Named anchor 3, e.g. "Bluejay Bikes — Portola Valley trail loop"]
- [Named anchor 4]
- [Named anchor 5]
- [Named anchor 6, optional]

## On-Property Highlights
[1–2 sentences on the hotel itself — what makes this Rosewood location distinct.
Keep brief; the Sense of Place section above is the primary grounding source.]
```

**Loading convention (in `orchestrator.py`):**

```python
def load_dossier(guest_id: str) -> str:
    path = Path("fixtures/dossiers") / f"{guest_id}.md"
    return path.read_text()

def load_property_card(property_id: str) -> str:
    path = Path("fixtures/properties") / f"{property_id}.md"
    return path.read_text()
```

Raw strings are injected into the Claude prompt between labeled delimiters (`--- GUEST DOSSIER ---` / `--- PROPERTY CARD: ARRIVAL ---` / `--- PROPERTY CARD: PROVENANCE ---`). The LLM does the parsing; no Python parser is written.

**Rationale:** Markdown is human-readable, judge-visible, and trivially editable by the analyst filling content (BL-010). JSON is retained only for offline-replay plans because plans are machine-generated structured data. The flat file naming (slug.md) makes the selector (TREQ-022) trivial: `os.listdir("fixtures/dossiers")`.

---

## Delta 3 — Orchestrator Synthesis Contract (TREQ-021)

### Decision

Synthesis is **folded into the existing `plan()` / `replan()` Claude tool-use call** as a prompt prefix + one additional Pydantic output field. It is NOT a discrete step, NOT a separate API call, and NOT a separate endpoint.

**Mechanism:**

`plan()` in `orchestrator.py` constructs the prompt in this order:

```
[System prompt]
--- GUEST DOSSIER ---
{dossier_markdown}
--- PROPERTY CARD: ARRIVAL ---
{arrival_property_markdown}
--- PROPERTY CARD: PROVENANCE: rosewood-london ---
{provenance_1_markdown}
--- PROPERTY CARD: PROVENANCE: rosewood-beijing ---
{provenance_2_markdown}
--- ARRIVAL EVENT ---
{delay_event or base event JSON}
```

The Claude tool schema (response_format / tool-use) returns a single object:

```json
{
  "synthesis": {
    "unified_understanding": "...",
    "inferred_preferences": ["...", "..."],
    "provenance_properties": ["rosewood-london", "rosewood-beijing"]
  },
  "arrival_plan": {
    "mood": "...",
    "role_cards": [...],
    "suppression": [...],
    "guest_message": "..."
  }
}
```

The outer response Pydantic model is:

```python
class OrchestratorResponse(BaseModel):
    synthesis: GuestSynthesis
    arrival_plan: ArrivalPlan
```

`replan()` accepts the same prompt structure with the delay event added; it returns the same `OrchestratorResponse`. The diff step compares `arrival_plan` fields only — synthesis does not participate in PlanDiff. This means synthesis never delays or displaces the diff panel.

**Spine safety:** The diff panel (TREQ-006) operates on `OrchestratorResponse.arrival_plan`, which is the identical field as in ADR-001's `ArrivalPlan`. Synthesis is additive context for the UI; it never blocks the `GET /diff` route.

**OFFLINE_MODE behavior:** When `OFFLINE_MODE=true`, `orchestrator.py` loads `fixtures/plans/synthesis_fixture.json` and `fixtures/plans/baseline_plan.json` (or `replanned_plan.json`) directly. It constructs an `OrchestratorResponse` from these files without calling Claude. The synthesis fixture is a hand-authored `GuestSynthesis` JSON that matches the canonical guest (Ms. Chen at Rosewood Sand Hill — see Delta 5).

**Rationale:** A discrete synthesis step would add latency (~3–8s) before plan generation and introduce a second failure surface. Folding into one call costs one extra prompt paragraph and one extra output field — negligible under the hackathon time budget and actually more coherent (the LLM synthesizes and plans in one reasoning pass). The single-call pattern matches ADR-001's existing tool-loop design.

---

## Delta 4 — Routes Addendum (TREQ-022, TREQ-023)

### Decision

Add two routes. All existing ADR-001 routes are unchanged.

**TREQ-022 — Guest/Property Selector**

| Method | Path | HTMX Target | Purpose |
|--------|------|-------------|---------|
| GET | `/select` | `#dashboard-root` (full swap) | Return HTML `<select>` dropdowns populated from `os.listdir("fixtures/dossiers")` and `os.listdir("fixtures/properties")` |
| POST | `/select` | `#dashboard-root` (full swap) | Accept `guest_id` + `property_id` form fields; call `plan()` with the selected fixtures; return the full `dashboard.html` fragment with the new plan |

Signature:

```python
@app.post("/select")
async def select_guest(
    guest_id: str = Form(...),
    property_id: str = Form(...),
) -> HTMLResponse:
    dossier_md = load_dossier(guest_id)
    property_md = load_property_card(property_id)
    provenance_mds = load_provenance_cards(guest_id, exclude=property_id)
    response = await orchestrator.plan(dossier_md, property_md, provenance_mds)
    return templates.TemplateResponse("dashboard.html", {"response": response})
```

`load_provenance_cards()` reads all `.md` files in `fixtures/properties/` except the selected arrival property; filters to only those referenced in the guest dossier's prior stays. This reuses the `load_property_card()` helper.

HTMX on the selector form: `hx-post="/select" hx-target="#dashboard-root" hx-swap="innerHTML"`. The selector panel itself is rendered in the left column of the existing 3-panel layout.

This route is **demo-optional** (P1). If cut, the app boots with the canonical guest pre-loaded and the selector is hidden. No behavior depends on it.

**TREQ-023 — Staff Note → Dossier → Re-synthesis Loop**

This route **reuses `POST /voice/transcribe`** from ADR-001 — no new route required. The existing transcribe endpoint already classifies the transcript and routes to a role card. The extension is purely in `orchestrator.py`:

After transcription + classification, if the classified category is `dossier_observation` (a new classification bucket):

1. Append the note text to an **in-memory session list** (`app.state.session_observations: list[str]`). No disk write.
2. Re-call `plan()` with the accumulated session observations appended to the dossier Markdown prompt under a labeled section `--- LIVE STAFF OBSERVATIONS (THIS VISIT) ---`.
3. Return an HTMX response that swaps `#synthesis-panel` (the inferred-from-prior-stays UI block) and `#role-cards` (the full role card grid).

HTMX targets: `hx-target="#synthesis-panel"` for the synthesis text update; a second `hx-swap-oob="true"` swap on `#role-cards` for card updates. Both are returned in a single multipart HTMX response using `HX-Trigger` or an OOB swap body.

**In-memory only:** `app.state.session_observations` is a plain Python list initialized to `[]` at startup. It is never written to disk. Session resets on server restart. This is confirmed as a demo-shim, not a persistence feature.

**Rationale:** Reusing `/voice/transcribe` avoids a new endpoint and keeps the FEAT-004 code path single. The only new surface is a classification bucket, an in-memory list, and a prompt injection — all contained in `orchestrator.py`. The OOB swap pattern is a standard HTMX idiom and requires no new JavaScript.

---

## Delta 5 — Offline-Replay Canonical Path (TREQ-019, TREQ-013)

### Decision

**Canonical offline demo path: Ms. Chen (guest_id: `ms-chen`) arriving at Rosewood Sand Hill (property_id: `rosewood-sand-hill`).**

Provenance properties: Rosewood London + Rosewood Beijing (loaded as provenance depth).

Fixture files covering this path:

| File | Content |
|------|---------|
| `fixtures/dossiers/ms-chen.md` | Full dossier with prior stays at London + Beijing |
| `fixtures/properties/rosewood-sand-hill.md` | Arrival property, depth=arrival |
| `fixtures/properties/rosewood-london.md` | Provenance property 1 |
| `fixtures/properties/rosewood-beijing.md` | Provenance property 2 |
| `fixtures/plans/baseline_plan.json` | Pre-computed ArrivalPlan for Ms. Chen at Sand Hill, no delay |
| `fixtures/plans/replanned_plan.json` | Pre-computed ArrivalPlan for Ms. Chen at Sand Hill, with delay injected |
| `fixtures/plans/synthesis_fixture.json` | Pre-computed GuestSynthesis for Ms. Chen cross-property observations |
| `fixtures/delay_event.json` | Injected delay payload (unchanged from ADR-001) |

When `OFFLINE_MODE=true`:
- `GET /` loads `ms-chen.md` + `rosewood-sand-hill.md` + provenance cards; constructs `OrchestratorResponse` from `baseline_plan.json` + `synthesis_fixture.json`. No Claude call.
- `POST /replan` returns `OrchestratorResponse` from `replanned_plan.json` + `synthesis_fixture.json`. No Claude call.
- `GET /diff` diffs `baseline_plan.json` vs `replanned_plan.json`. No Claude call. Returns `PlanDiff` as in ADR-001.
- `POST /voice/transcribe` returns a hardcoded transcript string. No ElevenLabs call. (Unchanged from ADR-001.)
- `GET /voice/tts/{card_id}` returns `static/audio/briefing_cached.mp3`. No ElevenLabs call. (Unchanged from ADR-001.)
- `POST /select` is disabled in offline mode (returns 503 with a banner). The selector is hidden in the UI when `OFFLINE_MODE=true`.
- Staff-note loop (TREQ-023): appends to `app.state.session_observations` normally but re-synthesis returns the `synthesis_fixture.json` contents unchanged (deterministic replay). The note still appears in the dossier panel.

The other two dossiers (`mr-okafor.md`, `dr-reyes.md`) and their respective property cards are fully authored for live-mode use and for the `POST /select` path. They are NOT covered by offline fixture files — offline mode is strictly Ms. Chen at Sand Hill.

**Rationale:** Deterministic zero-network replay requires pre-computed fixtures for every Claude call in the demo path. Covering all three guests would require six plan fixtures (baseline + replan × 3) and three synthesis fixtures, adding ~2 hours of content generation with no demo payoff — the rehearsed path is always Ms. Chen. The other dossiers provide live-mode richness and the "show multi-property on request" option for judges who ask.

---

## Consequences

**What becomes easier:**
- Engineer can implement `models.py` and `orchestrator.py` from the model sketches above with no ambiguity about field names or prompt structure.
- Analyst filling fixture content (BL-010) has a copy-paste Markdown template with no interpretation required.
- The diff panel (TREQ-006 / never-cut spine) is unaffected — it still operates on `ArrivalPlan` only.
- Offline mode remains zero-network deterministic for the rehearsed path.

**Trade-offs accepted:**
- `GuestProfile` is renamed `GuestDossier` — any code started before this ADR using the old name requires a one-time rename. (No code written yet — zero cost.)
- `PropertyCard` as a Pydantic model carries a `sense_of_place` field that is the raw Markdown blob; this is redundant with the `.md` file. The field is populated at load time by `load_property_card()` parsing the Markdown into the model so orchestrator code can pass typed objects without re-reading disk. The file remains the source of truth for human editing.
- OOB HTMX swap (TREQ-023) is slightly more complex than a single-target swap; the engineer must test it early. Mitigation: test the OOB pattern against the role-card swap in BL-002.
- Three dossiers × three property cards = 6 Markdown files needed before first demo run. The analyst (BL-010) owns content; engineer owns the template validation. These are parallel workstreams.

**Never-cut spine preserved:** `POST /replan` → `GET /diff` → `PlanDiff` rendering is structurally unchanged from ADR-001. Synthesis adds a new UI panel but does not sit in the replan→diff critical path.

---

## Alternatives Considered

**Synthesis as a discrete pre-call:** A separate Claude call synthesizing cross-visit data before `plan()` is cleaner conceptually but adds 3–8 seconds of latency and a second failure surface. Rejected under hackathon time constraints.

**JSON dossier files (not Markdown):** JSON would be Pydantic-parseable directly but is harder for the analyst to author and for judges to read in the repo. The "Markdown loaded as raw context" pattern is explicitly called out in TREQ-020 as a feature. Rejected.

**Persistent staff observations (disk write-back):** Would require a write path, error handling, and a reset mechanism. Out of scope per TREQ-023 and the 5PM deadline. Rejected.

**Separate selector endpoint + separate plan endpoint:** Two routes instead of one `POST /select` that does both. More REST-correct but adds an extra HTMX round trip and a transient state problem (which guest is selected between calls). Rejected in favor of one form-submit that selects and plans atomically.

---

## Flagged Items

- DQ: normal — `PropertyCard.sense_of_place` carries the full Markdown blob as a string field. If any property card exceeds ~4,000 tokens, it may push the combined prompt over Claude's practical structured-output limit. Mitigation: keep Sense of Place sections under ~600 words per card. Analyst (BL-010) should be informed of this limit.
- DQ: normal — The three guest dossiers (`mr-okafor`, `dr-reyes`) and their provenance properties need enough prior-stay content to make synthesis meaningful. If analyst time is short, Mr. Okafor and Dr. Reyes can have minimal prior-stay sections (one property each) — synthesis still works, it just produces thinner inferences. This is acceptable for live-mode demo; canonical path is Ms. Chen.

---

## Reasoning

**Decision chain:**
1. Cycle-2 requirements widen the guest/property model but impose no new dependencies and no changes to the demo's narrative spine. The clean path is additive extension of ADR-001 models.
2. Markdown-as-context (no parser) is explicitly locked in TREQ-020 and matches the "raw prompt context" pattern Claude handles fluently — no engineering cost for a parser that adds zero value.
3. Folding synthesis into the single plan() call is the only approach that preserves sub-10-second re-plan latency while keeping the never-cut spine intact.
4. In-memory staff observations (TREQ-023) are the minimum viable demo-shim — disk persistence would require a reset/cleanup mechanism that consumes build time with no demo payoff.
5. Canonical offline path = Ms. Chen only — covering all three guests in offline fixtures is a 2-hour content task with zero scoring upside.

**Constraints applied:** Solo builder, hard 5PM deadline, no new deps, never-cut TREQ-006 spine, fixtures-only / no-live-API, single rehearsed demo path.

**Confidence:** High on Deltas 1–3 and 5. Medium on Delta 4 (OOB HTMX swap for TREQ-023) — the pattern is correct but engineer should prototype the OOB swap early in BL-002 to catch any HTMX version quirk before it blocks the demo.
