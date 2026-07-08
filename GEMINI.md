# BaseAIProject — Antigravity (agy) Operating Constitution

> **This file is the startup protocol for Antigravity agents.**
> Whenever an agy agent starts any task in this project, it **must fully read this file first, then read `CLAUDE.md`**.
> `CLAUDE.md` is the final authority for all work standards; this file is agy's bridging guide.

---

## Step 1: Read CLAUDE.md immediately

```
Required reading: CLAUDE.md (project root)
```

`CLAUDE.md` is this project's operations map, containing:
- Quick Commands
- Canon hierarchy and decision tree before acting (including hard guardrails, INV-* rule entry points)
- Standing rules, handoff, and session management
- Document map (Virtual Team / Multi-Agent Skills roster in `agent_docs/AI-TEAM-REGISTRY.md`)
- Tech Stack and Project Relations

**No file modification operations are allowed before `CLAUDE.md` has been fully read.**

---

## Antigravity Workflow Mapping

This project uses the **Harness Engineering** workflow. Antigravity agents map to it as follows:

### agy agents ↔ .claude/agents/

| agy invocation (invoke_subagent / direct use) | Corresponding role | Required reading |
|--------------------------------------|---------|---------|
| Requirements analysis | `.claude/agents/pm.md` | `CLAUDE.md` + `TECHNICAL-REFERENCE.md` |
| Architecture design | `.claude/agents/architect.md` | `CLAUDE.md` + `invariants.md` |
| Implementation | `.claude/agents/tech-lead.md` | `CLAUDE.md` + corresponding ExecPlan |
| Code review | `.claude/agents/code-reviewer.md` | `review-protocol.md` |
| Testing | `.claude/agents/qa-engineer.md` | `CLAUDE.md` + `invariants.md` |
| Security audit | `.claude/agents/security-reviewer.md` | `security-policy.md` |
| Plan review | `.claude/agents/plan-reviewer.md` | `execplan-lifecycle.md` |
| UI/UX task | `.claude/agents/uiux-agent.md` | `.claude/uiux/WORKFLOW.md` |

### agy skills ↔ .claude/skills/

Every agy skill executed in this project must first confirm the Harness workflow requirements:

| Skill type | Corresponding .claude/skills/ | Prerequisite |
|-----------|---------------------|---------|
| Feature development | `feature-pipeline/` | Create ExecPlan → human approval → open branch |
| Code review | `code-review/` | Read ExecPlan §3 + §5 |
| Security audit | `security-audit/` | Read `invariants.md` |
| Tech debt | `techdebt-scanner/` | Output report to `docs/learnings/` |
| UI/UX | `ui-ux-pro-max/` | Read `.claude/uiux/WORKFLOW.md` |

---

## Standard Procedure for Starting a Task

### 1. Reading phase (mandatory, cannot be skipped)
```
Step 1: Read GEMINI.md (this file)       <- you are reading this now
Step 2: Read CLAUDE.md                   <- operations map
Step 3: Read agent_docs/TECHNICAL-REFERENCE.md
Step 4: Read docs/architecture/invariants.md
Step 5: Read state/feature-list.json     <- check for any in_progress task
```

### 2. Determine task type
```
Simple Q&A / explanation      -> answer directly, no ExecPlan needed
Single-file small change      -> Read the file -> modify -> lint
Cross-module / API change     -> must create an ExecPlan first -> wait for human approval -> open branch
```

### 3. When an in_progress ExecPlan exists
```
Read docs/plans/active/F-NNN-*.md
Check the last line of §6 Progress Log
Check the Current state marker in §9 Handoff Manifest
Decide follow-up action based on the marker
```

---

## Handoff Markers (agy agents must comply)

When each agy subagent (invoke_subagent) completes a task, its final response must conform to one of the three markers defined by the canonical `.claude/protocols/handoff-protocol.md`. This is not just a Claude Code convention — it is a **hard requirement of this project**, applying to all AI agents operating in it.

---

## Git Rules (agy must self-enforce; no automatic hook interception)

The Antigravity environment has no Claude Code Python hooks to auto-intercept, so **agy agents must proactively confirm before every git operation**:

```bash
# Do this before every git commit
git branch --show-current   # confirm not on master/main
```

The full list of prohibited commands (INV-GIT-002/003/004) is in the canonical `docs/architecture/invariants.md`; hooks will not intercept them — compliance relies entirely on agy self-discipline.

---

## Output Language and Format

Output language, commit message conventions, and report format fully follow the Communication Style section of the canonical `CLAUDE.md`; no exceptions for agy.

---

## Quick Reference

| Need | Read |
|------|------|
| Work standards overview | `CLAUDE.md` |
| Current architecture | `agent_docs/TECHNICAL-REFERENCE.md` |
| INV hard rules | `docs/architecture/invariants.md` |
| Create a new ExecPlan | `docs/plans/PLANS.md` |
| Check in-progress tasks | `state/feature-list.json` |
| Handoff spec | `.claude/protocols/handoff-protocol.md` |
| ExecPlan lifecycle | `.claude/protocols/execplan-lifecycle.md` |
| Review standards | `.claude/protocols/review-protocol.md` |
| Virtual Team | `agent_docs/AI-TEAM-REGISTRY.md` |
| Multi-Agent guide | `agent_docs/multi-agent-guide.md` |
