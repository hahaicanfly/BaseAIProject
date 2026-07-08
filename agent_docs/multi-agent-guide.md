# Multi-Agent Collaboration Guide

> Multi-agent collaboration guide — using Claude Code's Agent tool to implement team-collaboration patterns

## Overview

This guide explains how to use Claude Code's **Agent tool** for multi-agent collaboration, emulating patterns such as Code Review Swarm and Feature Factory.

## Available Collaboration Patterns

### 1. Swarm Pattern (Parallel Review)

Multiple expert agents review the same target simultaneously, each focused on a different dimension.

```
                    ┌─────────────────┐
                    │  Target Code    │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ Tech Lead   │   │  Security   │   │     QA      │
    │ Code Quality│   │Vulnerability│   │Testability  │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Integrated Report│
                    └─────────────────┘
```

**Usage**: `/multi-agent-review [target]`

### 2. Pipeline Pattern (Sequential Development)

Agents hand off in sequence; each stage's output is the next stage's input.

```
┌────┐    ┌──────────┐    ┌────────┐    ┌──────┐    ┌────────┐
│ PM │ ─▶ │ Architect│ ─▶ │ UI/UX  │ ─▶ │ Dev  │ ─▶ │ Review │
└────┘    └──────────┘    └────────┘    └──────┘    └────────┘
Requirements  Architecture  UI Design    Implementation  Review
```

**Usage**: `/feature-pipeline [feature description]`

### 3. Council Pattern (Technical Decisions)

Multiple agents provide different-angle analyses of the same question to help the user decide.

**Manual invocation**:
```
Launch simultaneously:
- Architect: architectural feasibility analysis
- Tech Lead: technical-debt assessment
- PM: business-value analysis
```

### 4. Watchdog Pattern (Guard Checks)

Automatically runs safety checks before/after critical operations.

**Automatic trigger points**:
- Before git commit: security scan (`pre-tool-use-guard.py`)
- API changes: backward-compatibility check
- Dependency updates: vulnerability scan

### 5. Worktree Pattern (Parallel Development)

Multiple agents each work in an isolated git worktree, enabling true parallel development.

```
┌──────────────────────────────────────────┐
│              Orchestrator                │
│         (human or managing agent)        │
└────────┬──────────┬──────────┬───────────┘
         │          │          │
    ┌────▼────┐ ┌───▼────┐ ┌──▼─────┐
    │ Agent A │ │Agent B │ │Agent C │
    │ WT: T-1 │ │WT: T-2 │ │WT: T-3 │
    │ feat/x  │ │fix/y   │ │refact/z│
    └────┬────┘ └───┬────┘ └──┬─────┘
         │          │          │
         └──────────┼──────────┘
                    ▼
              PR → Merge
```

**Use cases**:
- Multiple independent tasks need to run at once
- Long-running feature work shouldn't block quick fixes
- Physical isolation is needed to avoid workspace conflicts

**Agent tool usage**:
```
Agent(
  isolation: "worktree",     # automatically creates a git worktree
  prompt: "implement F-NNN ...",
  mode: "auto"
)
```

**See**: `.claude/rules/parallel-worktree.md`

## Agent Role Overview

> See `agent_docs/AI-TEAM-REGISTRY.md` for the full agent roster and trigger words.

## Implementation Mechanics

### Agent Tool Usage

```
Agent(
  subagent_type: "tech-lead",     # use a project-defined agent
  prompt: "review the code quality of xxx",
  model: "sonnet",                # optional: haiku, sonnet, opus
  run_in_background: true         # run in parallel
)
```

### Parallel Execution

Launch multiple agents simultaneously for parallel review (multiple Agent calls in a single message):

```
Agent(tech-lead, "review code quality", background=true)
Agent(security-reviewer, "review security", background=true)
Agent(qa-engineer, "review testability", background=true)
```

### Result Integration

Collect results from all background agents and merge them into a unified report, ordered by severity.

## Cost Optimization

> See `.claude/rules/model-dispatch.md` for the model-selection table.

## Best Practices

### DO

- Use multi-agent review for significant changes
- Set `run_in_background: true` in parallel mode
- Dedupe and sort findings when integrating reports
- Order issues by severity

### DON'T

- Overuse multi-agent review for simple changes
- Launch too many agents at once (recommended ≤ 3)
- Ignore conflicting opinions between agents
- Integrate results before all agents have finished

## Related Documents

- Skills: `.claude/skills/multi-agent-review/`, `.claude/skills/feature-pipeline/`
- Agents: `.claude/agents/`
- Worktree Rules: `.claude/rules/parallel-worktree.md`
- Security Policy: `agent_docs/security-policy.md`
- Cost Optimization: `agent_docs/cost-optimization.md`
