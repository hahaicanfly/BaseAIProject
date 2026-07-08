---
name: multi-agent-review
description: Launches code-reviewer, security-reviewer, and qa-engineer in parallel for an all-around review; triggers when the user wants a comprehensive review of high-risk changes, core logic, or a PR, or mentions "高風險", "核心邏輯", "綜合審查". Use for high-risk/core-logic changes needing three experts in parallel; use code-review for regular PRs.
---

# Skill: multi-agent-review

> **Purpose**: Launch three reviewers in parallel (code-reviewer + security-reviewer + qa-engineer) for an all-around review, simulating a Code Review Swarm pattern.
> **Trigger**: `/multi-agent-review`
> **Applicable scenarios**: high-risk changes, auth/security-related, core business logic

## Usage

```
/multi-agent-review [file path or module name]
```

## Collaboration Pattern

This skill launches the following agents simultaneously for parallel review:

| Agent | Responsibility | Tools |
|------|------|------|
| **code-reviewer** | Code quality, architecture compliance, conventions | Read, Bash, Grep, Glob |
| **security-reviewer** | Security vulnerabilities, key leaks, auth/secret | Read, Grep, Glob |
| **qa-engineer** | Testability, test coverage, edge cases | Read, Bash, Grep, Glob |

## Execution Flow

### Phase 1: Fan-out Parallel Review

Use the Agent tool to launch all three expert agents simultaneously (see the parallel review fan-out diagram in `.claude/protocols/review-protocol.md`):

```
1. Launch code-reviewer agent → code quality review
2. Launch security-reviewer agent → security review
3. Launch qa-engineer agent → test review
```

Each reviewer must read the ExecPlan (`docs/plans/active/F-NNN-*.md`) and `docs/architecture/invariants.md` on its own — not just the diff — otherwise INV-ids referenced in Constraints will be missed.

### Phase 2: Result Aggregation

Collect all agents' review results, merge them into a unified report, and sync the Aggregated Decision into ExecPlan §7 Decision Log (one-line summary).

### Phase 3: Action Recommendations

Based on all review results, provide a prioritized action list.

## Parallelism Notes

- A sub-agent's `git checkout` may switch branches; the main conversation must re-check `git branch --show-current` before committing
- All three reports must be Pass before proceeding to human-pr-review

## Output Template

```markdown
## Multi-Agent Review Report: [Target]

### Review Summary

| Agent | Verdict | Issue Count |
|------|------|--------|
| code-reviewer | [Pass/Block] | [N] |
| security-reviewer | [Pass/Block] | [N] |
| qa-engineer | [Pass/Block] | [N] |

### Critical Issues (must fix)

#### [Source Agent] Issue Title
- **Location**: `path/file:line`
- **Description**: [issue]
- **Fix**: [suggestion]

### High Priority (should fix)
[same format as above]

### Medium Priority (suggested improvement)
[same format as above]

### Action Plan

1. [ ] [Highest priority task]
2. [ ] [Next priority task]
3. [ ] [General task]

### Aggregated Decision
[HANDOFF: dev | human-pr-review]

### Full Reports per Agent

<details>
<summary>code-reviewer Report</summary>
[full report]
</details>

<details>
<summary>security-reviewer Report</summary>
[full report]
</details>

<details>
<summary>qa-engineer Report</summary>
[full report]
</details>
```

## Use Cases

- **PR review**: full inspection before merge
- **Pre-release review**: final confirmation before important feature launches
- **Tech debt cleanup**: identify issues that need priority handling
- **New contributor code**: ensure conformance to team standards

## Cost Considerations

This skill launches multiple agents and consumes more resources. Recommended for:
- Core module changes
- Before important feature releases
- Periodic code health checks

For everyday small changes, use the single-reviewer `/code-review` instead.

## Verification Items

- **Output form**: 3 independent reviewer reports (code-reviewer + security-reviewer + qa-engineer) + a main-conversation aggregated summary.
- **Parallelism check**: each of the 3 sub-agents' final line must be a `[HANDOFF: <main>]` marker.
- **ExecPlan integration**: the aggregated summary paragraph is written into §7 Decision Log; individual details are handled by each reviewer per review-protocol.md.
- **Failure mode**: if any reviewer reports a Blocker → the main conversation outputs `[HANDOFF: dev]`, and must not proceed to PR.

## References

- `.claude/protocols/review-protocol.md`
- `.claude/agents/code-reviewer.md`
- `.claude/agents/security-reviewer.md`
- `.claude/agents/qa-engineer.md`
- `.claude/templates/delegation-templates.md`
