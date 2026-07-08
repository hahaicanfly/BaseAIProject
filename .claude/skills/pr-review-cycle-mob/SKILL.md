---
name: pr-review-cycle-mob
description: Uses a Cascade tiering strategy to balance cost, speed, and quality, running the optimal PR review flow after AI finishes writing code; triggers when the user wants to review a PR or mentions "review cycle" "cascade review". Use when a cost-tiered cascade strategy is needed.
---

# Skill: pr-review-cycle-mob

> **Purpose**: The optimal PR review flow after AI finishes writing code — using a Cascade (tiered) strategy to balance cost / speed / quality.
> **Trigger**: `/pr-review-cycle-mob [PR description or diff path]`
> **Core insight**: not about finding "one sweet spot," but three layers of filtering — run the cheap check first, only escalate when necessary.

---

> This is a risk-tiering cascade, a separate mechanism from the failure-escalation path in `model-dispatch.md` — do not conflate the two.

## Cascade Architecture

```
[Level 1] haiku — Mechanical scan (<10s, lowest cost)
     │ pass → DONE (60-70% of PRs end here)
     │ flag →
[Level 2] sonnet — Logic & design review (<60s, medium cost)
     │ pass → DONE
     │ flag HIGH_RISK →
[Level 3] opus — Deep arbitration (<3min, high cost)
     │ Only used for: auth changes, DB schema, public APIs, security vulnerabilities
```

**Principle**: Level N's input must include Level N-1's complete output — no duplicated work.

---

## Level 1 — Mechanical Scan (haiku)

**Good for**: formatting, security antipatterns, INV-* rules

### Checklist

**1.1 Security Antipatterns** (against `docs/architecture/invariants.md` INV-SEC-*)
- [ ] No hardcoded API key / token / password
- [ ] No sensitive files added (`.env`, `*.pem`, `*.keystore`)
- [ ] No secret strings in logs (grep `console.log.*key|log.*password|print.*token`)

**1.2 Git Hygiene** (INV-GIT-*)
- [ ] No direct commits to main/master
- [ ] Branch naming follows `feat/*` / `fix/*` / `refactor/*`

**1.3 Code Structure** (INV-ARC-* / INV-API-*, if defined)
- [ ] Checked against every pattern in `QUICK_CHECKS` in `post-edit-lint.py`

**1.4 File Footprint**
- [ ] Number of files changed (> 15 warns, > 30 escalates to Level 2)
- [ ] Any unintended changes (`.gitignore`, `package-lock.json`, `*.lock`)

**Output format**:
```
L1 Result: PASS / FLAG
- [SEC] ...
- [GIT] ...
- [ARC] ...
Escalation reason (if FLAG): ...
```

---

## Level 2 — Logic & Design Review (sonnet)

**Trigger condition**: L1 FLAG, or the PR involves any of the following:
- New function/class/interface definitions
- Changed behavior of an existing API
- State management changes
- Test coverage changes

### Checklist

**2.1 Logical Correctness**
- [ ] Does function behavior match the intent described in the PR
- [ ] Are edge cases handled (null/empty/boundary)
- [ ] Is async/concurrent logic safe

**2.2 Design Consistency**
- [ ] Does naming follow `agent_docs/code-conventions.md`
- [ ] Does it violate module dependency rules in `docs/architecture/domains.md`
- [ ] Do new interfaces maintain single responsibility

**2.3 Test Quality**
- [ ] Does the new functionality have corresponding tests
- [ ] Do tests follow Given/When/Then structure
- [ ] Was a real DB/external API replaced with a mock (flag if it shouldn't be mocked)

**2.4 Documentation Updates**
- [ ] Does `TECHNICAL-REFERENCE.md` need updating
- [ ] Has ExecPlan §6 Progress Log been updated
- [ ] Is a new ADR needed (if there's an architectural decision)

**High-risk trigger conditions** (escalate to Level 3):
- Involves auth / token / session logic
- DB schema change (migration)
- Public API interface change (potential breaking change)
- A change type marked `multi-agent review: yes` in `docs/architecture/invariants.md`

**Output format**:
```
L2 Result: PASS / FLAG / HIGH_RISK
Blockers:
  - [BLOCK] ...
Suggestions:
  - [SUGGEST] ...
Escalation reason (if HIGH_RISK): ...
```

---

## Level 3 — Deep Arbitration (opus)

**Trigger condition**: L2 HIGH_RISK
**Usage limit**: no more than 5 times per week (cost control)

### Checklist

**3.1 Deep Security Audit**
- [ ] Can auth logic be bypassed
- [ ] Is the token/session lifecycle correct
- [ ] Is input validation complete (injection, XSS, SSRF, etc.)

**3.2 Data Consistency**
- [ ] Does the migration have a rollback plan
- [ ] Are there race conditions in concurrent writes
- [ ] Are foreign keys/constraints correct

**3.3 Breaking Change Assessment**
- [ ] Do existing clients need a coordinated update
- [ ] Is the version compatibility strategy appropriate

**3.4 Architecture Impact Assessment**
- [ ] Should this change be escalated to an ADR
- [ ] Does it affect boundary definitions in `docs/architecture/domains.md`

**Output format**:
```
L3 Result: APPROVED / CHANGES_REQUIRED / ESCALATE_HUMAN
Critical Issues:
  - [CRITICAL] ...
Architecture Impact:
  - [ADR_NEEDED] ...
Final Verdict: ...
```

---

## Mob Review Mode (extra option for high-risk PRs)

When L3 result is `CHANGES_REQUIRED` or has a `CRITICAL`, launch a parallel review:

```
Launch simultaneously (multiple Agent calls in a single message):
Agent(tech-lead, "review code quality and design consistency", background=true)
Agent(security-reviewer, "review security", background=true)
Agent(qa-engineer, "review testability and test coverage", background=true)
```

Every dispatch must follow the three-part template (goal/motivation, acceptance criteria, report format) in `.claude/templates/delegation-templates.md`.

Merge the three results, sort by severity, and output a unified Mob Review report.

**Final output must map to `review-protocol.md` terminology**: `PASS` → `Pass`, `FLAG` → `Conditional Pass`, `HIGH_RISK` / `CRITICAL` → `Block`.

---

## Cost Estimation Guide

| PR Type | Expected Level Reached | Estimated Cost |
|---------|-------------|---------|
| Simple bug fix (1-3 files) | L1 | < $0.01 |
| General feature (5-15 files) | L2 | $0.05–0.20 |
| Involves auth/schema (any size) | L3 | $0.20–1.00 |
| Mob Review triggered | L3 + 3 agents | $1.00–3.00 |

**Principle**: L3 + Mob totaling under $20/month is very healthy review spend.

---

## Interface with pr-retro

After every Cascade completes, the `pr-retro` skill should:
1. Collect all Flag/Block/Critical entries
2. Check whether they match an existing lesson in ERRORS.md (if matched → the lesson recurred)
3. If it's a new pattern → write into ERRORS.md Pending Review

See `.claude/skills/pr-retro/SKILL.md`.
