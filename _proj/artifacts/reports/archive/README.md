# Archived Reports

**Category**: `archive`

## What Goes Here

Reports older than 7 days are automatically moved here by the archive script.

Archived reports are organized by original category:
```
archive/
├── analysis/
├── arch/
├── review/
└── ...
```

## Searching Archives

```bash
# Search all archives for a keyword
grep -r "keyword" artifacts/reports/archive/

# Search specific category
grep -r "keyword" artifacts/reports/archive/review/
```

## Archive Policy

- Reports auto-archived after 7 days
- Archived reports kept for 90 days
- After 90 days, reports may be deleted (configurable)
