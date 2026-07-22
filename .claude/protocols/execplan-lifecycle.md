# Protocol: ExecPlan Lifecycle

> **Role**: Defines the 10-phase state machine for an ExecPlan from creation through execution to archival.
> **Audience**: All sub-agents must read this file before executing a task; `code-reviewer` and `plan-reviewer` use this file to judge ExecPlan phase compliance.
> **Basis**: `docs/plans/PLANS.md` §3 + `docs/decisions/ADR-0001-adopt-harness-engineering.md` D8.

---

## State Machine

```
       ┌─────────────────────────────────────────────────────────┐
       │                                                          │
       ▼                                                          │
   [PROPOSED] ──► [PLANNED] ──► [APPROVED] ──► [IN_PROGRESS]      │
       │             │             │                 │             │
       │             │             │                 ▼             │
       │             │             │            [VERIFYING]        │
       │             │             │                 │             │
       │             │             │                 ▼             │
       │             │             │            [REVIEWING] ───┐   │
       │             │             │                 │          │   │
       │             │             │                 ▼          │   │
       │             ▼             ▼            [DONE]          │   │
       │        [REJECTED]    [REJECTED]            │            │   │
       │                                            │            │   │
       └────────[BLOCKED]────────────────────────  ─┘            │   │
                    │                                             │   │
                    └─────────────────────────────────────────────┘
```

### Phase Mapping to `state/feature-list.json`'s `status` field

| Lifecycle Phase | `status` value |
|---------------|----------------|
| PROPOSED, PLANNED, APPROVED | `todo` |
| IN_PROGRESS, VERIFYING, REVIEWING | `in_progress` |
| BLOCKED | `blocked` |
| REJECTED | `done` (marked cancelled) |
| DONE | `done` |

---

## 10 Phases

### Phase 1 — PROPOSED

**Trigger**: Human or PM agent raises a requirement.
**Owner**: `pm` agent (trigger words: requirement, planning, PRD, user story, feature).
**Action**: Create `docs/plans/active/F-NNN-<slug>.md`, fill in §1 Goal + §2 Context (partial).
**Exit**: Goal **and** §1's Non-Goals / Out of Scope line filled in (at least one explicit boundary, or a justified "none identified" — see PLANS.md §2), output `[HANDOFF: architect]`.

### Phase 2 — PLANNED

**Trigger**: `[HANDOFF: architect]` received.
**Owner**: `architect` agent (trigger words: architecture, design, planning).
**Action**: Complete §2 Context, §3 Constraints (incl. INV-id), §4 Step-by-step, §5 Verification Strategy.
**Exit**: Output `[HANDOFF: plan-reviewer]`.

### Phase 3 — APPROVED

**Trigger**: `[HANDOFF: plan-reviewer]` received.
**Owner**: `plan-reviewer` agent.
**Action**: Review §1-§5 completeness, verifiability, whether constraints are complete, whether Open Questions remain unresolved.
**Exit**:
- Passed → `[HANDOFF: <next-dev-or-feature-pipeline>]` + write to §7 Decision Log "Plan approved by plan-reviewer"
- Rejected → add questions to §8 Open Questions, return to Phase 2

> **Human reviewer gate**: after Phase 3 passes, you **must wait for human approval** before opening a branch and entering Phase 4 (PR-style review on `docs/plans/active/F-NNN.md`).

### Phase 4 — IN_PROGRESS (open branch)

**Trigger**: After human approval.
**Action**:
1. `git checkout master && git pull && git checkout -b feat/<slug>` (INV-GIT-005)
2. Add an entry with `status: in_progress` to `state/feature-list.json`
3. ExecPlan header: `Status: in_progress`, `Branch: feat/<slug>`
4. Begin executing §4 Step-by-step

### Phase 5 — IN_PROGRESS (execution)

**Owner**: `dev` (main conversation + implementation subagents with Bash). `tech-lead` handles review/spec-compliance only, and does not commit (tech-lead's frontmatter grants read-only tools, no Bash).
**Action**: After completing each step in §4 → commit immediately → append one line to §6 Progress Log.
**Iron rules**:
- Run `git branch --show-current` before every commit (INV-GIT-001)
- Run the corresponding lint/test after every edit (automatic via hook or manual)
- If an invariant violation is caught by a hook → fix it before committing; log the attempt in §6
**Exit**: All of §4 checked off → `[HANDOFF: code-reviewer]`

### Phase 6 — VERIFYING

**Owner**: `code-reviewer` agent (model: Sonnet).
**Action**:
1. Read ExecPlan §3 Constraints and §5 Verification Strategy
2. Run `git diff master...HEAD` and compare against §4
3. Check each INV-id one by one to confirm no violations
4. Run all verification commands from §5
5. Write to §7 Decision Log (Pass / Blocker / Warning / Suggestion)
**Exit**:
- All Pass → `[HANDOFF: human-pr-review]`
- Any Blocker / Warning → return to Phase 5 for fixes
- Missing invariant discovered → append to ERRORS.md Pending Review

### Phase 7 — REVIEWING (PR)

**Action**:
1. Open a PR (`gh pr create --base master`)
2. Add `Linked PR: #NNN` to the ExecPlan header
3. Wait for GitHub PR review

> **Human reviewer gate**: PR review must pass before entering Phase 8.

### Phase 8 — DONE (merge + archive)

**Trigger**: PR merged.
**Action**:
1. `git checkout master && git pull`
2. Move the ExecPlan from `docs/plans/active/` to `docs/plans/completed/`
3. ExecPlan header `Status: done`, add a final entry to §6
4. Update `state/feature-list.json`: `status: done`, `exec_plan` path changed to `completed/`
5. `verification.{build_ok, lint_ok, tests_passing}` all `true`

### Phase 9 — BLOCKED (reachable from any phase)

**Trigger**: An external dependency is found to be not ready (backend API not live, third-party SDK bug, design pending).
**Action**:
1. State the blocker in ExecPlan §8 Open Questions
2. `state/feature-list.json` `status: blocked`
3. Output `[HUMAN_ATTENTION_REQUIRED: <reason>]`
**Exit**: Blocker resolved → return to the original phase and continue.

### Phase 10 — REJECTED

**Trigger**: plan-reviewer rejects twice, or a human closes the PR.
**Action**:
1. Move the ExecPlan from `active/` to `completed/`, add a `## Rejection Reason` section
2. Remove the entry from `state/feature-list.json` or mark it cancelled
3. Append the rejection rationale to `docs/learnings/ERRORS.md` Pending Review

---

## SOP for Taking Over an ExecPlan Across Sessions

When a new session picks up an interrupted ExecPlan:

1. Read `state/feature-list.json` and find the task with `status: in_progress`
2. Read the full text of the corresponding `docs/plans/active/F-NNN-*.md`
3. Focus on the last line of §6 Progress Log + the `Current state marker` in §9 Handoff Manifest
4. If the marker is `[VERIFY_FAILED: <INV-id>]` → start from the fix corresponding to that INV-id
5. If the marker is `[HANDOFF: <agent>]` → take over that agent role
6. If the marker is `[HUMAN_ATTENTION_REQUIRED: ...]` → do not continue; consult a human first

---

## Trace Example

> The INV-ids below (INV-API-001, INV-TEST-001) are illustrative examples; use the current list in `docs/architecture/invariants.md` when citing real ids.

```
[2026-05-08 10:00] pm Created F-042-export-history.md, marked [HANDOFF: architect]
[2026-05-08 10:30] architect Filled Constraints (INV-API-001, INV-TEST-001) and Plan, [HANDOFF: plan-reviewer]
[2026-05-08 11:00] plan-reviewer Approved with note on §5 negative case, [HANDOFF: human-approval]
[2026-05-08 14:00] human Approved, branch feat/export-history created
[2026-05-08 14:30] dev Step 1 done, commit a1b2c3
[2026-05-08 15:00] dev Step 2 violated INV-API-001 (missing default for field), hook flagged, fixed in commit d4e5f6
[2026-05-08 15:30] dev Step 3-5 done, [HANDOFF: code-reviewer]
[2026-05-08 16:00] code-reviewer 1 Warning (missing test for negative case), [HANDOFF: dev]
[2026-05-08 16:30] dev Added test, commit 7890ab, [HANDOFF: code-reviewer]
[2026-05-08 17:00] code-reviewer All pass, [HANDOFF: human-pr-review]
[2026-05-08 17:30] human PR #142 opened
[2026-05-09 10:00] human PR #142 merged → moved to completed/
```

---

## Where This File Is Referenced

- `docs/plans/PLANS.md` §3
- `.claude/agents/*.md` (each agent's Harness handoff-protocol section)
- `.claude/protocols/handoff-protocol.md`
