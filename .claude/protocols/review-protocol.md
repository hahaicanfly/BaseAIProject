# Protocol: PR Review

> **Role**: Defines the standard actions for code-reviewer / security-reviewer / qa-engineer during ExecPlan Phase 6 (VERIFYING).
> **Audience**: The above 3 reviewer agents + the main conversation before opening a PR.
> **Basis**: `docs/plans/PLANS.md` §3 + `.claude/protocols/execplan-lifecycle.md` Phase 6.

---

## Trigger

```
[HANDOFF: code-reviewer]    # required before any general PR
[HANDOFF: security-reviewer] # extra pass for anything touching auth/secret
[HANDOFF: qa-engineer]       # extra pass for core logic / high-reliability requirements
```

Or run manually from the main conversation:
```
@.claude/agents/code-reviewer.md
```

---

## Review Inputs

Every reviewer agent must read the following files first, **no skipping**:

1. The corresponding ExecPlan: `docs/plans/active/F-NNN-*.md` §3 Constraints + §5 Verification Strategy
2. `docs/architecture/invariants.md`: the INV-ids involved in this change
3. `docs/learnings/ERRORS.md`: related historical lessons
4. `agent_docs/TECHNICAL-REFERENCE.md`: relevant sections (find the path from ExecPlan §2 Context)
5. `git diff master...HEAD`: the full diff of this change

> **Executor note**: item 5's git command is run by the main conversation or an agent with Bash (code-reviewer / qa-engineer); agents without Bash (e.g. security-reviewer) do not run git commands themselves — they work from the diff/context provided by the main conversation.

---

## Severity Levels

Every finding must be tagged with a severity:

| Severity | Meaning | Fix Requirement |
|----------|------|-----------|
| **Blocker** | Invariant violation / security vulnerability / build failure / red test | **Must fix, or merge is blocked** |
| **Warning** | Convention violation / possible regression / missing verification | **Must fix** (per CLAUDE.md policy) |
| **Suggestion** | Optional improvement / style tweak / naming improvement | Handle at discretion |
| **Praise** | Something done well (worth remembering) | No action needed |

---

## Code Reviewer Checklist

```
□ Read ExecPlan §1 Goal and confirm the PR diff's scope matches it
□ Read ExecPlan §1 Non-Goals / Out of Scope; check the diff item by item for anything that IMPLEMENTS an excluded item — a hit is a Blocker tagged [SCOPE], citing the hunk and the violated Non-Goal line (the field is write-only otherwise)
□ Read ExecPlan §3 Constraints; verify each INV-id against the diff
□ Run `python3 scripts/acceptance-run.py <execplan-path>` — it executes §5's ```acceptance block and logs evidence to state/acceptance/; paste its summary line in the report. §5 Manual items are run by hand. (Legacy plans without an acceptance block: run §5's prose commands manually.)
□ git branch --show-current to confirm you're not on master
□ Is the commit message atomic and in type(scope) format?
□ Does each commit build independently?
□ Any hardcoded secrets (grep API_KEY / TOKEN / PASSWORD)?
□ Any leftover debug prints / logs?
□ Does new functionality have corresponding tests? (see INV-TEST-*, per the current invariants.md list)
□ Are all fakes/mocks updated for any new interface method?
□ Is documentation in sync (TECHNICAL-REFERENCE.md / diagrams)?
□ Are all cases covered for any new enum or sealed class?
□ New externally-imported symbols in the diff are greppable at their API-evidence-row location (spot-check ≥3; rows required by delegation-templates §2)
```

---

## Security Reviewer's Extra Checklist

```
□ All INV-SEC-* (Security/Auth/Secrets) rules checked
□ Sensitive data not written to logs
□ API keys / tokens not hardcoded
□ Do sensitive UI screens need protection (screenshot protection etc.)?
□ EncryptedStorage / Keychain keys not leaked
□ Third-party OAuth / JWT handling is correct
□ Certificate Pinning / App Integrity integrated (if applicable)
□ Input validation is complete
```

---

## QA Engineer's Extra Checklist

```
□ Unit tests cover core branches (including negative cases)
□ Test fakes/mocks are in sync with the production interface (INV-TEST-*, per the current invariants.md list)
□ Coroutine/async tests use the correct test dispatcher
□ Polling/timer tests can inject a time parameter
□ All loading/error/empty states have test coverage
□ Edge cases: empty values, overlong strings, extreme data volumes
```

---

## Document Reviewer Checklist

For non-code deliverables — PRD / market & competitive research / data analyses / strategy docs / ADR & PDR — executed by a fresh-context reviewer (general-purpose + Write for its single report file) or `plan-reviewer`. This is where product-strategy hallucinations get caught; "reads well" is not a review.

```
□ Run `python3 scripts/check-doc-refs.py --file <doc>` — 0 ERROR (dead paths/refs)
□ Every quantified claim (market size, %, price, benchmark, date) has a source (URL or file:line)
  OR an inline [UNCONFIRMED: <claim>] tag — having neither is a FAIL
□ Spot-fetch ≥3 cited URLs with WebFetch — the page must actually support the claim it backs;
  paste a one-line evidence quote for each
□ Re-read every file:line quote — content must match the citation
□ Facts (sourced) and inference (author judgment) are separated (delegation-templates §4 format)
□ Hypothesis-evidence table present with the confidence column filled (required for
  pm / market-researcher / competitive-analyst / data-analyst outputs)
□ If the doc feeds an architecture / security / irreversible decision (model-dispatch §5's
  second-opinion triggers): a second-opinion record is attached — this checklist item is the
  objective trigger; no record → FAIL
```

Verdict follows delegation-templates §6: full report to `docs/reviews/`, `VERDICT: PASS|FAIL <path>` line, ending marker.

---

## Output Format (required for every reviewer)

```markdown
# Review Report — F-NNN

**Reviewer**: code-reviewer | security-reviewer | qa-engineer
**Scope**: <git diff range or commit hash>
**Generated**: YYYY-MM-DD HH:mm

## Findings

### Blockers
- [SEC] <description>
  - File: `path/to/file:NN`
  - Violates: INV-SEC-001 (illustrative id; fill in per the project's current invariants.md)
  - Fix: <specific fix steps>

### Warnings
- [QA] <description>
  - ...

### Suggestions
- [STY] <description>
  - ...

### Praise
- Well done: <...>

## Verification Results

| Check | Result |
|-------|--------|
| Build | ✓ / ✗ |
| Lint  | ✓ / ✗ |
| Tests | ✓ / ✗ |
| Acceptance-run (§5 block) | ✓ / ✗ / n/a |

## Decision

- **Pass / Block / Conditional Pass**
- Linked ExecPlan: docs/plans/active/F-NNN-*.md

[HANDOFF: <dev to fix | human-pr-review | etc>]
```

The Decision section must also be **synced** into ExecPlan §7 Decision Log as a one-line summary.

---

## Three Reviewers Running in Parallel (multi-agent-review skill)

The `/multi-agent-review` skill's parallel review flow:

```
       ┌─────────────────┐
       │  Main session   │
       │  fan-out review │
       └────────┬────────┘
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Code   │ │ Security│ │   QA    │
│Reviewer │ │ Review  │ │Engineer │
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
     └───────────┼───────────┘
                 ▼
         Aggregated report
         to ExecPlan §7
```

When running in parallel, note: a subagent's internal `git checkout` may switch branches — the main conversation must re-check `git branch --show-current` before committing.

---

## Anti-Patterns

- ❌ Reviewer reviews the diff without reading the ExecPlan (misses INV-ids referenced in Constraints)
- ❌ Labeling a Suggestion as a Blocker (needlessly delays merge)
- ❌ Passing without running the §5 Verification Strategy
- ❌ Fixing an issue directly upon spotting it (a reviewer does not write production code — only reports and suggests)

---

## Where This File Is Referenced

- `.claude/agents/code-reviewer.md`
- `.claude/agents/security-reviewer.md`
- `.claude/agents/qa-engineer.md`
- `.claude/skills/code-review/SKILL.md`
- `.claude/skills/multi-agent-review/SKILL.md`
- `.claude/protocols/execplan-lifecycle.md` Phase 6
