# First Five Minutes by SenseArrival

## Consolidated Hackathon Concept

**Product thesis:** The first five minutes of arrival define the guest’s emotional experience. SenseArrival helps hotel staff choreograph those first five minutes in real time by combining pre-arrival intelligence, live staff observations, role-specific service cards, and voice-enabled updates.

**Demoable workflow:** Start with the broad **First Five Minutes** arrival orchestration concept, then show **Delay-to-Delight** as a high-drama branch when the guest is arriving late. Add **TTS staff briefing playback** and **staff voice note capture** to make the system feel live, operational, and differentiated.

**One-line pitch:**

> SenseArrival turns every guest arrival into a coordinated service moment: staff speak what they notice, AI updates every role’s next best action, and the guest receives just the right level of care before they ask.

---

## Why this concept works

### It is broader than Delay-to-Delight

Delay-to-Delight is a compelling demo path, but by itself it can look like a late-arrival recovery bot. First Five Minutes makes it a broader arrival intelligence system.

Delay-to-Delight becomes one trigger inside the system:

- guest arrival is late
- restaurant hours are at risk
- guest may be tired or hungry
- staff need updated instructions
- guest may need reassurance, food, and low-friction check-in

### It is less obvious than a concierge chatbot

The product does not primarily chat with guests. It coordinates staff actions. It focuses on tone, restraint, timing, and role-specific execution.

### It is feasible in 6.5 hours

The MVP can use synthetic guest profiles, mocked flight / delay status, a simple staff dashboard, text-to-speech playback, and optionally voice note capture. Real PMS, POS, hotel app, and kitchen integrations can be described as future extensions.

### It is strong for judging

- **Live Demo:** Visible state change from guest context → role cards → delay trigger → staff voice note → updated cards → spoken briefing.
- **Creativity / Originality:** Human-in-the-loop service choreography, not a generic RAG app or chatbot.
- **Impact Potential:** The pattern can expand to early arrivals, VIP privacy, room-readiness issues, guest complaints, dietary changes, spa timing, and post-stay memory.

---

## Core components

## 1. First Five Minutes Orchestrator

The central agent generates the service plan for the first five minutes after arrival.

### Inputs

- guest profile
- prior stay preferences
- trip purpose
- arrival time
- delay status
- dining availability
- room readiness
- privacy / personalization level
- staff observations
- property context

### Outputs

- arrival mood
- role-based staff cards
- suppressed recommendations
- optional guest text
- audit trail explaining what changed and why

### Example arrival mood labels

- Quiet Arrival
- Efficient Arrival
- Restorative Arrival
- Celebratory Arrival
- Family Landing
- Work-Mode Arrival
- Recovery Arrival

---

## 2. Delay-to-Delight Branch

This is the main demo branch because it creates a clear before / after moment.

### Scenario

A returning guest is delayed and will arrive near or after restaurant hours.

### Agent behavior

The AI detects the risk and revises the plan:

- prepares a late-arrival reassurance message
- offers in-room dining or light supper options
- updates front desk to keep check-in brief
- updates dining to prepare realistic late options
- updates housekeeping to avoid interruption
- suppresses irrelevant spa / activity suggestions

### Example guest SMS

> Welcome back, Ms. Chen — we see your arrival is now closer to 10:45 PM. Madera may be closed by then, so we can have a light late supper waiting in-room. Based on your last stay, would you prefer: 1) seasonal soup + salad, 2) grilled chicken + vegetables, or 3) a quiet tea service with fruit?

### Example confirmation SMS

> Of course. We’ll have a light supper waiting in-room and keep your arrival quiet and efficient. No need to rush — the team will be ready when you arrive.

---

## 3. Role-Based Staff Cards

Each staff role receives only the information needed for their part of the arrival.

### Valet card

**Arrival mode:** Quiet / efficient arrival  
**Action:** Greet by name, avoid asking about the delay, notify front desk when guest exits vehicle.  
**Do not:** Start extended conversation unless guest initiates.

### Front Desk card

**Arrival mode:** Low-friction check-in  
**Action:** Keep check-in brief, confirm that in-room dining can be arranged immediately, offer hotel app handoff if needed.  
**Do not:** Upsell activities or ask unnecessary travel questions.

### Dining card

**Arrival mode:** Late supper recovery  
**Action:** Prepare light in-room dining options. Prioritize soup, salad, tea service, fruit, or a simple protein.  
**Do not:** Suggest full tasting menu tonight.

### Housekeeping card

**Arrival mode:** Quiet room readiness  
**Action:** Confirm room temperature, extra pillows if known, quiet setup.  
**Do not:** Schedule turndown interruption unless requested.

### Concierge card

**Arrival mode:** Suppressed recommendation mode  
**Action:** Hold spa, activity, and excursion suggestions until tomorrow unless guest asks.  
**Do not:** Push itinerary planning tonight.

### Manager on Duty card

**Arrival mode:** Recovery oversight  
**Action:** Monitor arrival handoff, confirm dining and front desk alignment, intervene only if delay causes service risk.

---

## 4. TTS Staff Briefing Playback

Each role card has a **Play Briefing** button. ElevenLabs reads the staff briefing aloud.

### Why this matters

This is the safest voice feature because it uses generated text the app already has. It adds polish and makes the demo feel more like a future hotel operating system without depending on a live conversation.

### Example spoken briefing

> Valet: quiet arrival. Greet Ms. Chen by name, avoid asking about the flight delay, and notify front desk when she exits the vehicle.

### Demo use

1. Generate role cards.
2. Click **Play Briefing** on Valet.
3. Trigger the delay branch.
4. Click **Play Briefing** again on Dining or Front Desk to show the updated service plan.

---

## 5. Staff Voice Note Capture

Staff can speak real-time observations into the app. The AI updates the service plan and role cards.

### Example staff voice note

> Ms. Chen seemed exhausted, skipped lunch, and asked if food could go straight to the room.

### AI interpretation

- mood: exhausted
- need: light food
- service mode: minimize friction
- memory type: temporary context for this stay
- routing: front desk, dining, housekeeping, concierge

### Updated cards

**Front Desk**

> Keep check-in brief. Mention that in-room dining can be arranged immediately.

**Dining**

> Prepare light in-room dining options. Avoid tasting menu suggestions tonight.

**Housekeeping**

> Quiet arrival setup. No turndown interruption unless requested.

**Concierge**

> Suppress activity and spa suggestions tonight unless guest asks.

### Why this is powerful

This makes staff the sensors and AI the coordinator. It shows that the system learns from human hospitality rather than replacing it.

---

## Demo narrative

### Opening line

> Most hotel AI demos start with a chatbot. We started with the moment luxury service actually begins: the first five minutes after arrival.

### Demo sequence

1. **Show guest profile**
   - returning guest
   - prefers quiet arrival
   - previously enjoyed light seasonal dining
   - privacy setting: helpful but not intrusive

2. **Generate initial First Five Minutes plan**
   - arrival mood
   - role-based staff cards
   - suppressed suggestions
   - optional guest message

3. **Play a staff briefing**
   - click Valet or Front Desk TTS playback

4. **Trigger Delay-to-Delight**
   - arrival changes from 7:30 PM to 10:45 PM
   - restaurant hours now at risk

5. **Show revised plan**
   - dining options added
   - check-in shortened
   - housekeeping interruption suppressed
   - concierge suggestions paused

6. **Guest receives SMS**
   - late supper offer
   - reassurance that arrival is prepared
   - option to ask for anything else

7. **Staff voice note arrives**
   - valet or front desk says: “Guest seemed exhausted and asked if food could go straight to the room.”

8. **AI updates role cards**
   - dining, front desk, housekeeping, concierge update in real time
   - UI shows “what changed and why”

9. **Play revised briefing**
   - click Dining or Front Desk TTS playback

10. **Close with platform vision**
   - same loop works for early arrival, VIP privacy, family arrival, wellness stays, complaints, post-stay memory, and cross-property preference continuity

---

## MVP build scope

### Must build

- guest profile fixture
- arrival context fixture
- delay trigger
- role-card generator
- staff note input box
- role-card update logic
- “what changed and why” diff
- TTS playback for at least one role card

### Should build if time allows

- voice note capture from microphone
- guest SMS simulation
- multiple staff roles
- privacy / personalization level selector
- suppression panel showing recommendations the AI chose not to make

### Cut if time is tight

- real flight API
- real SMS send
- full guest voice agent
- real hotel app handoff
- real PMS / POS / dining integration
- persistent long-term memory database

---

## Suggested technical design

### Simple data model

```json
{
  "guest": {
    "name": "Ms. Chen",
    "returning_guest": true,
    "preferences": ["quiet arrival", "light seasonal dining", "minimal check-in friction"],
    "privacy_level": "helpful_not_intrusive"
  },
  "arrival_context": {
    "scheduled_arrival": "7:30 PM",
    "updated_arrival": "10:45 PM",
    "delay_status": true,
    "restaurant_risk": true,
    "room_ready": true
  },
  "staff_signal": {
    "source_role": "Valet",
    "note": "Guest seemed exhausted, skipped lunch, and asked if food could go straight to the room."
  }
}
```

### Agent outputs

```json
{
  "arrival_mood": "Quiet Recovery Arrival",
  "role_cards": {
    "valet": "...",
    "front_desk": "...",
    "dining": "...",
    "housekeeping": "...",
    "concierge": "..."
  },
  "guest_message": "...",
  "suppressed_suggestions": [
    {
      "suggestion": "Promote spa availability tonight",
      "reason": "Guest appears exhausted and requested low-friction arrival."
    }
  ],
  "change_log": [
    {
      "trigger": "late arrival",
      "change": "Dining card updated with late supper options."
    },
    {
      "trigger": "staff voice note",
      "change": "Concierge activity suggestions suppressed tonight."
    }
  ]
}
```

---

## Demo UI layout

### Left panel

- guest profile
- arrival context
- delay trigger button
- staff voice note input

### Center panel

- arrival mood
- what changed and why
- suppressed suggestions

### Right panel

- role-based staff cards
- Play Briefing buttons
- updated timestamp per card

### Optional bottom panel

- guest SMS preview
- staff note history
- audit log

---

## Judging hooks

### Live Demo

The demo has clear action:

- initial cards generated
- voice briefing played
- delay trigger changes the plan
- staff voice note updates the cards
- revised briefing plays back

### Creativity / Originality

This is not a chatbot and not a basic RAG app. It is a live service choreography system where human observations continuously update coordinated staff actions.

### Impact Potential

The pattern generalizes beyond late arrivals:

- early arrivals
- room not ready
- VIP privacy
- family travel
- wellness stays
- missed meal windows
- transportation changes
- service recovery
- post-stay memory
- cross-property preference continuity

---

## Final positioning

**Name:** First Five Minutes by SenseArrival  
**Demo branch:** Delay-to-Delight  
**Voice layer:** TTS staff briefing playback + staff voice note capture  
**Core insight:** Luxury hospitality is not just knowing the guest. It is coordinating the team around the latest human signal.

**Closing line:**

> SenseArrival does not replace the intuition of great hotel staff. It captures it, coordinates it, and turns it into the next best action for every role before the guest has to ask.
