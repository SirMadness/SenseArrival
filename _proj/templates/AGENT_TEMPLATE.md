# Claude Agent Template & Best Practices

> **Purpose**: Standardized format for creating effective Claude Code agents based on analysis of CACM patterns, TeamOfAgents agents, and Claude documentation best practices.

---

## Template

```markdown
---
name: agent-name
description: [One-sentence summary]. Modes - mode1: [brief description] | mode2: [brief description]. [When to use this agent].
tools: Read, Write, Edit, Grep, Glob, Bash, TodoWrite
model: sonnet
---

# [Agent Name]

## Role
[1-2 sentences defining the agent's expertise and responsibility]

## Modes

**mode1** - [Mode purpose]
- [Key activity 1]
- [Key activity 2]
- [Key activity 3]

**mode2** - [Mode purpose]
- [Key activity 1]
- [Key activity 2]

## Context Required

- [What the orchestrator should provide]
- [Specific data or constraints needed]
- [References to prior work]

## Deliverables

### mode1
- [Primary output]
- [Secondary output]
- [Report location]

### mode2
- [Primary output]
- [Report location]

## Output Location

Reports go to: `_proj/artifacts/reports/[category]/`
Naming: `[category]-[topic]-YYYYMMDD.md`

## Key Principles

1. **[Principle]** - [Brief explanation]
2. **[Principle]** - [Brief explanation]
3. **[Principle]** - [Brief explanation]

## Constraints

- [What this agent should NOT do]
- [Boundaries of responsibility]
- [Escalation triggers]
```

---

## Format Rules & Reasoning

### 1. Frontmatter (YAML)

| Field | Required | Format | Notes |
|-------|----------|--------|-------|
| `name` | Yes | lowercase-kebab | Must be unique, used for Agent tool calls |
| `description` | Yes | 1-3 sentences | **Critical for auto-delegation** |
| `tools` | Yes | Array or `*` | Only include tools the agent needs |
| `model` | No | `sonnet`, `opus`, `haiku` | Default: inherit from parent |
| `mode` | No | `mode1 \| mode2` | Document available modes |
| `color` | No | CSS color name | Visual distinction in UI |

**Reasoning: Description Field**

The `description` field is the **most important field** for agent selection. Claude Code parses descriptions to auto-delegate tasks. Structure it as:

```
[Primary capability]. Modes - [mode1]: [what] | [mode2]: [what]. [When to use].
```

✅ **Good**: `"Code review, debugging, and QA strategy. Modes - review: security/correctness/performance review | debug: root cause analysis. Use for code quality assessment."`

❌ **Bad**: `"This agent is responsible for reviewing code and can help with debugging too."`

**Why**: Concise, keyword-rich descriptions enable accurate auto-delegation. Listing modes in the description helps Claude Code understand the agent's full capabilities without reading the entire system prompt.

**Agent Identification (Emoji Prefix)**

All agents must prefix their responses with an emoji identifier for visual distinction. The prefix assignments and spawning instructions are defined in the **agent-coordination** skill (`SKILL.md` → Agent Identification section). When spawning subagents, include the prefix instruction in the Agent tool prompt.

---

### 2. System Prompt Length

| Length | When to Use |
|--------|-------------|
| 20-50 lines | Simple, single-purpose agents |
| 50-150 lines | Agents with 2-3 modes, need deliverable templates |
| 150-300 lines | Complex agents with detailed templates (SRE, Security) |
| 300+ lines | **Avoid** - split into multiple agents or use skills |

**Reasoning**:
- Long prompts consume context that agents need for actual work
- Detailed code examples belong in **skills**, not agent definitions
- If an agent needs 500+ lines, it's doing too much

✅ **Good**: SRE agent at 221 lines with mode-specific deliverable templates

❌ **Bad**: Code reviewer at 750 lines with embedded Python/TypeScript examples

---

### 3. Structure Sections

#### Required Sections

| Section | Purpose |
|---------|---------|
| **Role** | 1-2 sentence identity statement |
| **Modes** | What each mode does (if multi-mode) |
| **Deliverables** | What the agent produces |
| **Key Principles** | 3-5 guiding rules |

#### Optional Sections

| Section | When to Include |
|---------|-----------------|
| **Context Required** | When agent needs specific inputs from orchestrator |
| **Output Location** | When agent writes reports |
| **Constraints** | When boundaries need explicit definition |
| **Deliverable Templates** | For complex outputs (postmortems, SLOs) |

#### Sections to Avoid

| Section | Why to Avoid |
|---------|--------------|
| **Detailed Code Examples** | Move to skills system |
| **Technology Stack Preferences** | Move to skills system |
| **Interaction with Other Agents** | Handled by orchestrator |
| **Communication Style** | Unnecessary verbosity |
| **Anti-patterns** | Move to skills system |

**Reasoning**: Keep agent definitions focused on **what** and **when**, not **how**. Detailed implementation guidance belongs in the skills system which can be loaded on-demand.

---

### 4. Mode Definition

Structure modes consistently:

```markdown
## Modes

**mode-name** - [One-line purpose]
- [Activity 1]
- [Activity 2]
- [Activity 3]
```

**Reasoning**: Modes let one agent handle related tasks without creating many similar agents. The orchestrator specifies the mode in the Agent tool call.

✅ **Good**: `code-quality` agent with `review`, `debug`, `qa-strategy` modes

❌ **Bad**: Separate `code-reviewer`, `debugger`, `qa-strategist` agents that share 80% of their logic

---

### 5. Tools Specification

| Approach | When to Use |
|----------|-------------|
| `tools: *` | Agent needs all available tools |
| `tools: [list]` | Agent has specific needs (recommended) |
| `allowed-tools: [list]` | Same as tools (alternative syntax) |

**Recommended Tool Sets by Agent Type**:

```yaml
# Read-only analysis
tools: Read, Grep, Glob, TodoWrite

# Code implementation
tools: Read, Write, Edit, Grep, Glob, Bash, TodoWrite

# Full access (orchestrator)
tools: Read, Write, Edit, Grep, Glob, Bash, Task, TodoWrite

# Infrastructure/DevOps
tools: Read, Write, Edit, Grep, Glob, Bash, TodoWrite, WebFetch

# Data/notebook work
tools: Read, Write, Edit, Grep, Glob, Bash, NotebookEdit, TodoWrite, WebFetch
```

`NotebookEdit` is available for agents that work with Jupyter notebooks (e.g., data agent).

**Reasoning**: Limiting tools reduces accidental actions and clarifies agent scope.

---

### 6. Context Injection Pattern

Agents should **never** read registries or search for prior work themselves. The orchestrator provides context:

```markdown
## Context Required

- Relevant prior reports (summaries, not full text)
- Tech debt items that may be impacted
- Constraints from project requirements
- Specific files or components to focus on
```

**Reasoning**: This separation of concerns keeps subagents focused and prevents duplicate registry reads.

---

### 7. Deliverable Templates

Include templates for complex, structured outputs:

```markdown
### incident mode
\`\`\`markdown
# Postmortem: [Incident Title]

## Incident Summary
- **Severity:** SEV1 | SEV2 | SEV3 | SEV4
- **Duration:** [start] to [end]
- **Impact:** [description]

## Timeline
| Time | Event |
|------|-------|

## Root Cause
[Description]

## Action Items
| Priority | Action | Owner | Due Date |
\`\`\`
```

**Reasoning**: Templates ensure consistent output format, making reports easier to parse and compare across time.

---

## Comparison: CACM vs TeamOfAgents

| Aspect | CACM (Recommended) | TeamOfAgents (Legacy) |
|--------|--------------------|-----------------------|
| Length | 20-220 lines | 300-750 lines |
| Description | Modes inline, concise | Examples in frontmatter |
| Code Examples | None (use skills) | Embedded throughout |
| Deliverables | Per-mode with templates | Generic lists |
| Output Location | Explicit | Often missing |
| Notebook Protocol | Not used (registry) | Included |

---

## Migration Checklist

When consolidating agents to the new format:

- [ ] Shorten description to 1-3 sentences with modes inline
- [ ] Remove embedded code examples (move to skills)
- [ ] Remove Notebook Protocol section (replaced by registry)
- [ ] Remove "Interaction with Other Agents" (orchestrator handles)
- [ ] Add explicit output location
- [ ] Add mode-specific deliverables
- [ ] Keep total length under 300 lines
- [ ] Remove technology stack details (move to skills)

---

## Example: Consolidated Agent

### Before (TeamOfAgents style - 500+ lines)

```markdown
---
name: code-reviewer
description: Use this agent when you need to review code for quality, best practices, potential bugs, maintainability issues, or architectural concerns. This agent excels at conducting thorough code reviews, identifying code smells, suggesting improvements, ensuring coding standards compliance, and providing constructive feedback. Examples: <example>Context: User needs code review...
model: sonnet
---

## Role Identity
You are an expert Code Reviewer...

[200 lines of review checklists]
[150 lines of code examples]
[100 lines of notebook protocol]
[50 lines of interaction patterns]
```

### After (CACM style - 80 lines)

```markdown
---
name: code-quality
description: Code review, debugging, and QA strategy. Modes - review: security/correctness/performance review | debug: root cause analysis | qa-strategy: test planning. Use for code quality assessment.
tools: Read, Write, Edit, Grep, Glob, Bash, TodoWrite
model: sonnet
---

# Code Quality Agent

## Role
Code quality specialist focused on reviews, debugging, and QA planning.

## Modes

**review** - Code review
- Security analysis
- Correctness verification
- Performance assessment
- Style and maintainability

**debug** - Root cause analysis
- Bug reproduction
- Cause identification
- Fix verification

**qa-strategy** - Test planning
- Test coverage analysis
- Acceptance criteria
- Test case design

## Context Required

- Files or PR to review
- Relevant prior review findings
- Applicable tech debt items
- Coding standards (if project-specific)

## Deliverables

### review mode
- Review report with severity-ranked findings
- Location: `_proj/artifacts/reports/review/review-[component]-YYYYMMDD.md`

### debug mode
- Root cause analysis with fix recommendation
- Location: `_proj/artifacts/reports/bugs/bug-[issue]-YYYYMMDD.md`

### qa-strategy mode
- Test plan with coverage mapping
- Location: `_proj/artifacts/reports/tests/testplan-[feature]-YYYYMMDD.md`

## Key Principles

1. **Constructive** - Focus on improvement, not criticism
2. **Specific** - Point to exact code, provide examples
3. **Prioritized** - Rank by severity (Critical > High > Medium > Low)
4. **Actionable** - Clear next steps for author
```

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT TEMPLATE                           │
├─────────────────────────────────────────────────────────────┤
│  FRONTMATTER (5-7 lines)                                    │
│  ├── name: lowercase-kebab                                  │
│  ├── description: [capability]. Modes - [x] | [y]. [when]   │
│  ├── tools: [specific list]                                 │
│  └── model: sonnet                                          │
├─────────────────────────────────────────────────────────────┤
│  SYSTEM PROMPT (50-200 lines)                               │
│  ├── Role (2 lines)                                         │
│  ├── Modes (10-20 lines)                                    │
│  ├── Context Required (5-10 lines)                          │
│  ├── Deliverables (20-50 lines)                             │
│  ├── Output Location (3 lines)                              │
│  ├── Key Principles (5-10 lines)                            │
│  └── [Templates if needed] (50-100 lines)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Version

- **Created**: 2026-02-02
- **Based on**: CACM repo analysis, Claude Code best practices
- **Supersedes**: TeamOfAgents verbose format
