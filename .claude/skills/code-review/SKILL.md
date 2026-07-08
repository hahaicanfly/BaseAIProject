---
name: code-review
description: Standard code review of a PR diff, covering security, quality, and architectural compliance; triggers when the user requests a code review, PR review, quality audit, or mentions "審查代碼", "PR review", "審查", "檢查代碼". Standard single-PR review.
---

# Skill: code-review

> **Purpose**: A single reviewer performs a standard code review on a PR diff.
> **Trigger**: `/code-review`
> **Agent**: code-reviewer (sonnet)

## Usage

```
/code-review [file path or feature name; if unspecified, reviews the full diff between the current branch and master]
```

## Execution Steps

1. **Scope confirmation**: Identify the files/directories under review; understand the purpose and background of the change
2. Read §3 Constraints + §5 Verification Strategy of the active ExecPlan (`docs/plans/active/F-NNN-*.md`); small changes without an ExecPlan may skip this
3. Read the relevant INV-id entries in `docs/architecture/invariants.md`
4. Run `git diff master...HEAD`
5. Verify item by item against the following dimensions (full rules live in their respective files; not repeated here):
   - **Security (priority)**: no hardcoded keys/passwords, no sensitive data logged, input validation, error handling doesn't leak internal details — details in `.claude/rules/security.md`
   - **Code quality**: naming conventions followed, single-responsibility functions, proper error handling, no obvious performance issues
   - **Architecture compliance**: correct module structure, correct dependency direction (depend on abstractions, not concrete implementations), reusable logic placed in shared modules — details in `agent_docs/modularity.md`
   - **Test coverage**: core logic has corresponding tests, clear test naming, tests are independent of each other
   - **Cost considerations** (if API calls are involved): calls are cached, resource usage is bounded, work that could be local isn't mistakenly sent to a cloud API — details in `.claude/rules/cost-optimization.md`
6. Output a Review Report (Blockers / Warnings / Suggestions / Praise, format below)
7. Sync a one-line summary into ExecPlan §7 Decision Log

## Output Format

```markdown
# Review Report — F-NNN

**Reviewer**: code-reviewer
**Scope**: <git range>
**Generated**: YYYY-MM-DD

## Findings
### Blockers
### Warnings
### Suggestions
### Praise

## Decision
Pass / Block / Conditional Pass

[HANDOFF: dev | human-pr-review]
```

## Pre-flight Checks

- CLAUDE.md (project conventions, Quick Commands)
- Whether the project has a separate coding standard or security policy document (per project structure; skip if none)

## Scope and Escalation Path

This skill is a **standard review of a single PR by a single reviewer**. Escalate to the `multi-agent-review` skill (parallel dispatch of code-reviewer / security-reviewer / qa-engineer) when:
- High-risk changes (auth, key handling, data migration)
- Large-scale refactoring of core business logic
- A single reviewer's Decision is Block and a second opinion is needed (see `.claude/rules/model-dispatch.md` §5, Verification is never self-certified)

## References

- `.claude/protocols/review-protocol.md` (full severity definitions and checklist, not repeated here)
- `docs/architecture/invariants.md`
- `.claude/rules/security.md`
- `agent_docs/modularity.md` (non-persistent design guidance)
- `.claude/rules/cost-optimization.md`
