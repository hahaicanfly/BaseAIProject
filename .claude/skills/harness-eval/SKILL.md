---
name: harness-eval
description: Scans a target repo, evaluates Harness Engineering maturity, and outputs a 0-100 score, a gap list, and prioritized improvement recommendations; triggers when the user wants to assess engineering infrastructure maturity or mentions "harness eval".
---

# Skill: harness-eval

> **Purpose**: Scan a target repo and output a Harness Engineering maturity score (0-100), a per-dimension gap list, and prioritized improvement recommendations.
> **Trigger**: `/harness-eval [repo_path]` (omit path to default to the current working directory)
> **Output**: Maturity Report — score card + improvement roadmap

---

## Execution Steps

### Step 0: Locate the Target Repo

Confirm the following path exists, otherwise error and abort:
- `CLAUDE.md` or `.claude/` (either counts as harness intent)

### Step 1: Read the Rubric

Read `.claude/skills/harness-eval/rubric.md` to get the scoring standard for the 8 dimensions.

### Step 2: Scan Dimension by Dimension

**D1 — Constitutional Layer (CLAUDE.md + rules/)**
- [ ] Does `CLAUDE.md` exist and is non-empty
- [ ] Is there a role definition section (`## 角色` or `## Role`)
- [ ] Is there a token budget strategy (3-tier reading or equivalent)
- [ ] Are there privacy rules / no-read zones
- [ ] Number of rules in `.claude/rules/` (0/1-2/3-5/5+)

**D2 — Agent Coverage**
- [ ] `.claude/agents/` exists
- [ ] Number of agents (0/1-3/4-7/8-11/12+)
- [ ] Are the core 5 roles present: pm, architect, tech-lead, security-reviewer, qa-engineer

**D3 — Hook System (highest weight)**
- [ ] `pre-tool-use-guard.py` exists
- [ ] `post-edit-lint.py` exists
- [ ] `pre-compact-snapshot.py` exists
- [ ] `stop-retro-logger.py` exists
- [ ] Do the hooks in `.claude/settings.json` map to `PreToolUse`, `PostToolUse`, `PreCompact`, `Stop`
- [ ] Is `QUICK_CHECKS` in `post-edit-lint.py` actually populated (non-empty array)
- [ ] Does `pre-tool-use-guard.py` have real enforce logic (not pass-through)

**D4 — Invariants (INV-\*)**
- [ ] `docs/architecture/invariants.md` exists
- [ ] `INV-GIT-*` rules are defined
- [ ] `INV-SEC-*` rules are defined (with real patterns, not template TODOs)
- [ ] Number of project-specific INV rules (0/1-2/3+)
- [ ] Does `post-edit-lint.py` reference an INV-id

**D5 — ExecPlan System**
- [ ] `docs/plans/PLANS.md` exists
- [ ] `docs/plans/active/` + `docs/plans/completed/` directories exist
- [ ] At least 1 completed ExecPlan exists (otherwise "never activated")
- [ ] `.claude/protocols/execplan-lifecycle.md` exists

**D6 — Memory & Retro Loop**
- [ ] `docs/learnings/ERRORS.md` exists
- [ ] `ERRORS.md`'s Active Lessons section is non-empty (has real lessons)
- [ ] `state/SCHEMA.md` exists
- [ ] `state/` has a `.gitignore` (to keep jsonl out of version control)
- [ ] `state/hook-events.jsonl` or `session-handoffs/` has real data (indicating the system has actually run)

**D7 — Skills & Commands**
- [ ] `.claude/skills/` directory exists
- [ ] Number of skills (0/1-3/4-7/8+)
- [ ] Do key skills have substantive content (not pure stubs): either code-review or multi-agent-review
- [ ] `.claude/commands/last-word.md` exists (session hygiene)

**D8 — SkillOpt Loop Readiness** (SkillOpt paper standard)
- [ ] Is there a rollout evidence collection mechanism (hook logging execution results to jsonl)
- [ ] Is there a validation gate concept (can compare before/after effects of skill changes)
- [ ] Does `ERRORS.md`'s structure match: Pending Review → Active Lessons dual sections (rejected-edit buffer + epoch update)
- [ ] Are skill update trigger conditions defined (when to update which agent/skill file)

### Step 3: Calculate the Score

Refer to the scoring matrix in `rubric.md`, sum the per-dimension scores, normalize to 0-100.

### Step 4: Produce the Report

Output format:

```
## Harness Maturity Report — [repo_path]
**Date**: [today]
**Total score**: XX / 100 → Level N [level name]

### Score Card
| Dimension | Score | Max | Comment |
|------|------|------|------|
| D1 Constitutional | X | 15 | ... |
| D2 Agents         | X | 10 | ... |
| D3 Hooks          | X | 20 | ... |
| D4 Invariants     | X | 15 | ... |
| D5 ExecPlan       | X | 10 | ... |
| D6 Memory/Retro   | X | 15 | ... |
| D7 Skills/Cmds    | X | 10 | ... |
| D8 SkillOpt Ready | X |  5 | ... |

### Gap List (priority-ordered)
1. [HIGH] ...
2. [MED] ...
3. [LOW] ...

### Minimum Improvement Path (3 steps)
1. ...
2. ...
3. ...

### SkillOpt Readiness Index
[analysis of whether the preconditions for automatic self-improvement are met]
```

### Step 5: Write Back to External Knowledge Base or to docs/

- (If the project has an external knowledge base, write there; otherwise skip)
- Otherwise → output to `docs/harness-eval-[date].md`

---

## Maturity Level Definitions

| Level | Score | Name | Characteristics |
|------|------|------|------|
| 0 | 0–20 | No Harness | No CLAUDE.md, or an empty shell only |
| 1 | 21–40 | Basic | Has CLAUDE.md + a few rules, no hooks |
| 2 | 41–60 | Structured | Has agents + hooks (at least a guard), has INV-GIT-* |
| 3 | 61–80 | Process-Aware | ExecPlan actually used, ERRORS.md has lessons |
| 4 | 81–95 | Self-Monitoring | All 8 hooks running, INV-* has project rules, retro loop active |
| 5 | 96–100 | SkillOpt-Ready | D8 complete, skill docs have version history, validation gate fully defined |

---

## Notes

- Scanning is read-only (except for the final report output)
- Scan time should stay under 2 minutes (don't read large source files)
- Focus on structure and configuration, not skill/agent content quality (that's the job of skill-quality-review)
