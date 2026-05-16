# CLAUDE.md
## Session Startup

At the start of every session, determine the active project phase:

1. Read `_proj/artifacts/_phase.md` to get current phase
2. **If phase is `discovery`**: Load the `discover` skill. Read `_proj/artifacts/drafts/` files (DISCUSSION_POINTS.md, Requirements_Draft.md, Features_Draft.md, User_Stories_Draft.md). Report open DD count and active requirement count. Check `_proj/deliverables/01-requirements/` for locked requirements from prior discovery cycles.
3. **If phase is `execution`** (or no phase file exists): Load the `execute` skill and follow its steps (this loads `agent-coordination`, reads registries/deliverables, and syncs requirements to backlog).

### Phase Commands
| Command | Effect |
|---------|--------|
| `/discover` | Switch to Discovery phase (requirements gathering) |
| `/execute` | Switch to Execution phase (planning + implementation) |
| `/discover reconcile` | Run reconciliation checklist before transitioning to Execution |

New projects start in Discovery. Use `/discover` and `/execute` to switch between phases as needed. Discovery produces requirements; Execution consumes them.

### Project Structure

| Directory | Purpose | When Used |
|-----------|---------|-----------|
| `_proj/artifacts/drafts/` | Working space — discussion points, draft requirements, notes | During Discovery phase |
| `_proj/artifacts/` | State files — phase, backlog, registry, action plan, tech debt | Throughout execution |
| `_proj/artifacts/reports/` | Agent work reports in category subdirectories | Throughout execution |
| `_proj/deliverables/01-requirements/` | Locked requirements (`requirements.md`, `features.md`, `user-stories.md`) | Graduated during reconciliation |
| `_proj/deliverables/02-architecture/` | Architecture docs and ADRs (`adr/ADR-NNN-*.md`) | Written directly by architect agent |
| `_proj/deliverables/03-design/` | Finalized design documents | Graduated or written directly |
| `_proj/deliverables/04-guides/` | Setup guides, onboarding docs | Written directly |

**Discovery phase**: Work in `_proj/artifacts/drafts/`. Finalize into `_proj/deliverables/` during reconciliation.
**Execution phase**: Reference `_proj/deliverables/` for specs. `_proj/artifacts/drafts/` contains working drafts only.

---

## Hard Rules (Execution Phase)

1. **NEVER use Edit/Write/Bash for code changes directly.** Delegate via Agent tool to the appropriate specialized agent.
2. **ALL implementation work happens on a working branch — never on main.**
3. **Before ANY task**, check registries: `grep -i "[keyword]" _proj/artifacts/_registry.md` and `_proj/artifacts/_tech-debt.md`
4. **After task completion**, follow the 5-step post-delegation protocol:
   1. Verify — `.claude/scripts/verify.sh [category] [report-name] [date]`
   2. Review — delegate to `code-quality` if 3+ files changed
   3. Fix — if review finds critical issues, delegate fixes, re-review
   4. Record — `.claude/scripts/update-registry.sh [cat] [name] [date] [agent] Completed "[summary]"`
   5. Update tracking — complete backlog item, update action plan, log tech debt
   Steps 4-5 are **MANDATORY** — do NOT proceed to next backlog item until done.
5. **Subagents NEVER read registries directly** — Main injects context via Agent tool prompts.
6. **All agents MUST prefix every response** with their emoji identifier.
7. **Main is the sole orchestrator** — it decides what to build, in what order, and who leads. Main prescribes the objective, constraints, and interfaces to preserve. Agents decide how to implement within those boundaries. Main never prescribes specific files to modify or implementation patterns unless they are hard constraints.

## Available Scripts

> **Rule:** Check `.claude/scripts/` before writing inline `awk`/`sed`/`grep` on state files — project scripts encode correct parsing and filter template/example rows automatically. Inline shell only when no existing script fits the query.

<!-- BEGIN auto-generated scripts table -->
| Script | Purpose |
|--------|---------|
| `add-dq.sh` | Add entry to the Discovery Queue |
| `add-tech-debt.sh` | Add entry to the tech debt registry |
| `add-to-backlog.sh` | Manage backlog items |
| `analyze-agents.sh` | Analyze agent activity logs |
| `analyze-patterns.sh` | Analyze outcome log for delegation patterns |
| `archive-old.sh` | Move old reports to archive |
| `bump-version.sh` | Bump the framework version number |
| `cascade-unblock.sh` | Identify backlog items blocked on a completed BL item |
| `compact-state.sh` | State compaction: move old entries from active files to archive files |
| `context-digest.sh` | Assemble delegation context in one command |
| `discovery-status.sh` | Discovery phase status summary and item extraction |
| `export-learnings.sh` | Export portable learnings from project state |
| `index-reports.sh` | Tag-based registry index lookup |
| `list-backlog.sh` | List backlog items from state file |
| `list-discussions.sh` | List decisions from action plan state file |
| `list-registry.sh` | List registry entries from state file |
| `list-tech-debt.sh` | List tech debt items from state file |
| `log-outcome.sh` | Log the outcome of a delegation for pattern analysis |
| `migrate.sh` | Post-install migration checker |
| `new-report.sh` | Create a new report from template |
| `plan-health.sh` | Plan health and outcome monitoring |
| `query-state.sh` | Structured state query interface |
| `resolve-tech-debt.sh` | Mark a tech debt item as resolved |
| `restore-from-backup.sh` | Restore project data from a .claude backup |
| `session-retrospective.sh` | Session retrospective and learning extraction |
| `state-integrity.sh` | Cross-reference validation for state files |
| `state-recover.sh` | Recover from incomplete state transactions |
| `state-transaction.sh` | Atomic state transaction management |
| `status-summary.sh` | Generate quick project status |
| `sync-check.sh` | Verify .claude/ installation health |
| `track-template-delta.sh` | Compare installed files against framework source |
| `update-action-plan.sh` | Manage the action plan |
| `update-dd.sh` | Create and manage Discussion Point (DD) lifecycle |
| `update-registry.sh` | Add entry to the report registry |
| `verify.sh` | Verify report exists and has content; or validate state file integrity |
| `lib/run-python-tool.sh` | Shared helper for resolving and running Python CLI tools (sourced, not executed) |
| `lib/tx-journal.sh` | Shared transaction journal support library (sourced by state-transaction.sh participants) |
<!-- END auto-generated scripts table -->

---

## Agent Identification

| Agent | Prefix |
|-------|--------|
| Main | 🔴 **Main** |
| Engineer | 🟢 **Engineer** |
| Code-Quality | 🟡 **Code-Quality** |
| Architect | 🔵 **Architect** |
| Security | 🛡️ **Security** |
| Infrastructure | 🔷 **Infrastructure** |
| Data | 🟣 **Data** |
| Analyst | ⚪ **Analyst** |
| Design | 🟠 **Design** |
| Docs | ⚫ **Docs** |

## Available Agents

| Agent | Modes | Use For |
|-------|-------|---------|
| `architect` | system, pipeline | System design, ADRs, API contracts |
| `code-quality` | review, debug, qa-strategy, report-review | Code review, debugging, test planning, report quality |
| `engineer` | backend, frontend, fullstack | Implementation |
| `infrastructure` | devops, database, cloud | DevOps, databases, cloud resources |
| `data` | pipeline, ml, analytics | Data pipelines, ML, analytics |
| `analyst` | research, deep-dive | Parallel research during discovery/execution |
| `security` | audit, scan, threat-model | Security audits, scans |
| `design` | wireframe, visual, review | UI/UX design |
| `docs` | api, readme, guide | Documentation |

## Slash Commands

| Command | When to Use |
|---------|-------------|
| `/discover` | Enter Discovery phase (requirements gathering) |
| `/execute` | Enter Execution phase (planning + implementation) |
| `/phase` | Show current project phase |
| `/status` | Project status overview |
| `/review` | Quick code review |
| `/review-full` | Comprehensive L1-L4 review before PRs |
| `/test` | Execute tests |
| `/ci` | Run local CI pipeline |
| `/security` | Security scanning |
| `/debt` | Manage tech debt |
| `/rfc` | Design document workflow |
| `/postmortem` | Incident analysis |

## Project Context

> **Customize this section for your project.** Describe what this repo does, the
> primary technologies, and any conventions developers should follow. Reference
> the locked requirements in `_proj/deliverables/01-requirements/` for canonical
> scope.

### Key Directories
- `_proj/deliverables/` — Finalized specs (requirements, architecture, design, guides)
- `_proj/artifacts/` — Live state files (registry, backlog, action plan, tech debt)
- `_proj/artifacts/drafts/` — Working space for discovery (discussion points, draft requirements)
- `_proj/artifacts/reports/` — Agent work reports
- `.claude/scripts/` — Deployed (symlinked) automation scripts
- `_proj/notes/research/` — Durable research and analysis documents
