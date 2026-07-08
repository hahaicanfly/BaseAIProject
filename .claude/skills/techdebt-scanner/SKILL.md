---
name: techdebt-scanner
description: Systematically scans a project for technical debt (TODO/FIXME, complex functions, duplicated code, etc.) and produces a prioritized report; triggers when the user wants to analyze code health or mentions "技術債", "techdebt".
---

# Skill: techdebt-scanner

> **Purpose**: Systematically scan for technical debt and produce a prioritized report.
> **Trigger**: `/techdebt` (via `.claude/commands/techdebt.md`)
> **Agent**: techdebt-scanner (sonnet)

## Usage

```
/techdebt [scope: full | a specific path; if unspecified, scans the project source directory defined in CLAUDE.md Quick Commands]
```

## Scan Flow

### Step 1: Quick Overview
- Count the project's source files (extensions depend on tech stack, e.g. .ts/.py/.go/.kt)
- Scan for TODO/FIXME/HACK/WORKAROUND/XXX markers
- Count usage of suppress/ignore comments and deprecated markers (e.g. `@Deprecated`, `# noqa`, `eslint-disable`)
- Produce a preliminary numeric summary

### Step 2: Deep Analysis
- Identify functions over 50 lines, nesting over 4 levels deep, or with more than 5 parameters
- Check core modules for missing tests
- Scan for hardcoded URLs, paths, ports
- Check for unused imports / dead code
- Assess inter-module dependency direction (circular dependencies, direct cross-layer calls)

### Step 3: Produce Report
- Classify all findings by priority (P0/P1/P2)
- Tag each issue with a specific location (`file:line`)
- Provide remediation suggestions and effort estimates
- List a recommended action order

## Scan Scope

Default scan directory: the source directory defined in the project's CLAUDE.md Quick Commands; if undefined, scan the whole repo, excluding build output directories and package-manager caches (e.g. `build/`, `dist/`, `node_modules/`, `.gradle/`, `vendor/`).

## Scan Command Reference

```bash
# <SRC_DIR> = project source directory (fill in from CLAUDE.md, e.g. src/, app/, lib/)
# TODO/FIXME markers
grep -rn "TODO\|FIXME\|HACK\|WORKAROUND\|XXX" <SRC_DIR>

# Hardcoded values
grep -rn "http://\|localhost\|127.0.0.1" <SRC_DIR>
```

## Output Template

```markdown
## Technical Debt Report

### Scan Scope
- Directory: <SRC_DIR>
- File count: N
- Date: YYYY-MM-DD

### Summary
| Priority | Count |
|--------|------|
| P0 (High) | X |
| P1 (Medium) | X |
| P2 (Low) | X |

### Detailed Findings
[Listed by priority, with file:line and remediation suggestions]

### Recommended Actions
[Ordered remediation list]
```

## Reference Documents

Check before starting:
- CLAUDE.md (project conventions, Quick Commands)
- `agent_docs/TECHNICAL-REFERENCE.md` (architecture; applies once fully filled in — if it still has unfilled placeholders, skip it, per CLAUDE.md's "Activation Status" section)

## Verification Items

- **Output form**: technical debt report (with P0/P1/P2 priorities + impact scope + time estimate).
- **Integration**: each P0/P1 candidate → the PM agent starts a new ExecPlan under `docs/plans/active/`.
- **Deduplication**: cross-check against Active Lessons in `docs/learnings/ERRORS.md` to avoid opening duplicate items.
- **Trigger frequency**: recommended quarterly, not per PR.
- **Handoff marker**: `[HUMAN_ATTENTION_REQUIRED: technical debt scan complete, human decision needed on which items to prioritize]`
