# Feature Reports

Per-BL collaborative reports grouped by feature. See FEAT-035/TREQ-062.

## Structure

```
artifacts/reports/features/
  FEAT-###-name/
    BL-###-name.md    # Collaborative per-BL report
    BL-###-name.md    # Another BL under the same feature
```

## Usage

Create a new per-BL collaborative report:

```bash
.claude/scripts/new-report.sh --feat FEAT-###-name BL-###-name
```

Verify an existing per-BL report:

```bash
.claude/scripts/verify.sh --feat FEAT-###-name BL-###-name --quality --criteria
```

## When to Use

Use this directory for BL items where one or more agents contribute sections. The lead agent creates the report, contributing agents append their sections during message passing, and the lead agent finalizes the Summary, Flagged Items, and Contributors table.

For standalone specialty reports (security audits, architecture reviews, code reviews not tied to a BL), use the standard category directories instead.
