# Discovery Queue

> Observations logged during execution. Normal DQs batch at next /discover; blocking DQs surface in /status and halt associated BL items until resolved. See TREQ-023.
>
> **DQ fields**: Status (first field), Title, Area, Observed, Description, Impact, Estimated scope, **Urgency** (normal|blocking, default normal), **Blocks** (BL-### required when Urgency=blocking).

<!-- DQ Format Reference
  Lifecycle state field (first body field, required on every DQ):
    Status  — pending (default) | promoted | resolved
             Canonical source of truth for lifecycle. Used by discovery-status.sh counts.

  Core fields (required on every DQ):
    Title, Area, Observed, Description, Impact, Estimated scope

  Urgency fields (required on new DQs, implicit normal on legacy entries):
    Urgency  — normal (default) | blocking
    Blocks   — BL-### (required when Urgency=blocking)

  Pointer fields (added when DQ is promoted or resolved):
    Promoted to   — DD-### reference when promoted to a Discussion Point
    Resolved via  — BL-###/TD-### reference when resolved directly

  Optional annotation fields:
    Note     — additional context or considerations
    Related  — cross-references to other DQs or TDs

  DQ heading format: plain "## DQ-###" (no suffix).
  Status is tracked in the body Status field, not in the heading.

  Example entry:
    ## DQ-001
    - **Status:** pending
    - **Title:** Short title of the observation
    - **Area:** Architecture
    - **Observed:** 2026-01-01
    - **Description:** What was observed and why it matters.
    - **Impact:** Non-blocking — triage quality improvement
    - **Estimated scope:** Low
    - **Urgency:** normal
    - **Blocks:** _none_
-->
