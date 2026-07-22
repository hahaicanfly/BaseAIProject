# Protocol: Agent Handoff Markers

> **Role**: Defines the structured handoff signals used between agents, and between agents and humans.
> **Audience**: All sub-agents must use this protocol's markers at the end of their output.
> **Basis**: `docs/decisions/ADR-0001-adopt-harness-engineering.md` D7.

---

## Marker Syntax

Every sub-agent's final response **must** end with one of the following three markers (single line, square brackets); for the main conversation the marker is required only at ExecPlan lifecycle exits and otherwise recommended within a task workflow (see "Where Markers Appear" and "Sentinel Coverage" below):

```
[HANDOFF: <next-agent-or-state>]
[VERIFY_FAILED: <INV-id-or-reason>]
[HUMAN_ATTENTION_REQUIRED: <reason>]
```

Any other ending from a sub-agent that did real work (at least one tool call) is treated as a protocol violation, flagged by `stop-retro-logger.py` and sent to `docs/learnings/ERRORS.md` Pending Review. The sentinel also validates marker *semantics*: a placeholder reason copied from docs (`<target>`), a `[HANDOFF:]` target outside the §1 table, or a `[VERIFY_FAILED:]`/`[HUMAN_ATTENTION_REQUIRED:]` reason over 80 chars are all flagged as violations. Markdown wrapping around the marker line (e.g. `**[HANDOFF: main]**`) is tolerated. This check only applies to `SubagentStop` events — the main conversation's ordinary turns (`Stop` events) are not required to end with a marker.

---

## 1. `[HANDOFF: <target>]`

**Purpose**: Normal completion of your own phase, handing off to the next role.
**Target must be one of the following** (sync source for `VALID_HANDOFF_TARGETS` in `stop-retro-logger.py` — change this table and that set together):

| Target | Meaning |
|--------|------|
| `architect` | Hand off to the architect agent |
| `plan-reviewer` | Hand off to the plan-reviewer agent to review the ExecPlan |
| `tech-lead` | Hand off to tech-lead to begin implementation |
| `dev` | Hand off to the development path (may be the main conversation + multiple sub-agents) |
| `code-reviewer` | Implementation done, awaiting review |
| `qa-engineer` | Hand off to the QA agent to write tests / run verification |
| `security-reviewer` | Final review for anything touching auth/secrets |
| `uiux-agent` | UI-related, entering the three-phase flow |
| `human-approval` | ExecPlan §1-§5 complete, awaiting human approval |
| `human-pr-review` | Code review passed, awaiting human PR review |
| `done` | Task fully complete (merged) |
| `main` | Report back to the main conversation (commander) — used when a delegated subagent (see `.claude/templates/delegation-templates.md`) completes its subtask |
| `pending` | Next step not yet determined (rarely used, usually paired with Open Questions) |

**Example** (INV ids are illustrative; use the current list in `docs/architecture/invariants.md`):
```
✓ Plan complete, §3 Constraints references INV-GIT-002 / INV-SEC-001
→ Next: waiting for plan-reviewer to review
[HANDOFF: plan-reviewer]
```

---

## 2. `[VERIFY_FAILED: <INV-id-or-reason>]`

**Purpose**: A verification failure discovered during execution (lint / test / hook block / invariant violation).
**Reason format**:
- If a specific invariant was violated: fill in that INV id (e.g. `INV-GIT-002`, per the current list in `docs/architecture/invariants.md`)
- For other reasons: a short sentence (≤80 characters)

**Rules**:
- On seeing `[VERIFY_FAILED:]` → do not continue, do not commit, must fix and retry
- 3 consecutive `[VERIFY_FAILED:]` → must escalate to `[HUMAN_ATTENTION_REQUIRED:]`
- `stop-retro-logger.py` (Phase D) harvests every `[VERIFY_FAILED:]` plus its preceding 5 lines of context into `docs/learnings/ERRORS.md` Pending Review

**Example** (INV id is illustrative; fill in per the project's actual invariants):
```
✗ post-edit-lint blocked: INV-SEC-001 — suspected hardcoded key detected in diff
→ Fix: read from an environment variable instead and update .env.example
[VERIFY_FAILED: INV-SEC-001]
```

---

## 3. `[HUMAN_ATTENTION_REQUIRED: <reason>]`

**Purpose**: Beyond what an agent may autonomously decide; requires human intervention.
**6 trigger situations** (any one is sufficient to mark):

1. **3 consecutive lint/test failures with the root cause still unidentified**
2. **Secret / hardcoded API key / password detected**
3. **An invariant conflict that cannot be resolved technically** (e.g., two INVs are mutually exclusive)
4. **ExecPlan §8 Open Questions unanswered and blocking progress**
5. **Cross-repo / cross-platform impact** (e.g., a frontend change requires backend coordination)
6. **Any destructive op** (rm -rf / git reset --hard / branch -D / force-push)

**Rules**:
- Must **stop immediately** after marking; do not attempt to resolve it yourself
- Must output a **structured question list** so a human can reply quickly
- Keep in sync with ExecPlan §8 Open Questions

**Example** (INV id is illustrative; fill in per the project's actual invariants):
```
⚠ Detected the Request data class missing a deviceId field, violating INV-SEC-002
   Two possible fixes:
   a) add a default null, compatible with old clients
   b) add a non-null required field → all call sites must be updated together

→ Outside the ExecPlan's expected scope, please choose a direction
[HUMAN_ATTENTION_REQUIRED: fix approach requires human choice between a or b]
```

---

## Where Markers Appear

| Location | Behavior |
|------|------|
| Sub-agent's final response | **Must** end with a single-line marker |
| ExecPlan §9 Handoff Manifest | Written into the `Current state marker:` field |
| ExecPlan §6 Progress Log | A marker may be appended to the end of each line |
| End of main conversation turn | Not required outside a task workflow; recommended within one; **required** at ExecPlan lifecycle exits (e.g. Phase 5 → `[HANDOFF: code-reviewer]`), where it is enforced by review, not by the hook |

---

## Sentinel Coverage

What `stop-retro-logger.py` mechanically checks vs. what remains honor-system — so nobody mistakes documented duty for enforced duty:

| Path | Coverage |
|------|----------|
| Sub-agent final response (`SubagentStop` with `agent_transcript_path`) | **Checked**: marker presence on the last non-empty line, valid `[HANDOFF:]` target (§1 table), non-placeholder reason, `[VERIFY_FAILED:]`/`[HUMAN_ATTENTION_REQUIRED:]` reason ≤80 chars |
| Sub-agent whose loop ends on a tool call (Workflow structured-output agents, interrupted agents) | Exempt — no final text report exists to hold to the marker rule |
| Main conversation turns (`Stop`) | Not checked by the hook; ExecPlan lifecycle exit markers are enforced by plan/code review |
| agy / Antigravity agents | Not checked — Python hooks do not run in that environment (CLAUDE.md Antigravity bridge); compliance is manual |

---

## Required Handoff Context

Every `[HANDOFF: <next>]` must be preceded by enough context for the next agent to cold-start:

| Info | Required? |
|------|---------|
| ExecPlan path (`docs/plans/active/F-NNN-*.md`) | **Required** |
| Current branch | **Required** |
| Last commit hash | **Required** |
| §4 Step progress (which steps done, which in progress) | **Required** |
| Known Open Questions | Required if any exist |
| Recommended execution order (for the next agent) | Recommended |

**Example handoff payload** (in the paragraph before the marker):

```
HANDOFF SUMMARY
- ExecPlan: docs/plans/active/F-042-export-history.md
- Branch: feat/export-history (commit 7890ab)
- Step status: §4.1-§4.4 done, §4.5 (test) pending
- Open Questions: none
- Suggested next: code-reviewer runs review, focus on whether §5 negative case is covered

[HANDOFF: code-reviewer]
```

---

## Anti-Patterns

- ❌ Ending with "done" / "ok" / "complete" without a marker
- ❌ Continuing to output after the marker (the marker must be the last line)
- ❌ `[HANDOFF: code-review]` (correct is `code-reviewer`, with the `-er`)
- ❌ `[VERIFY_FAILED: failed]` (reason must be specific: an INV-id or a sentence)
- ❌ `[HUMAN_ATTENTION_REQUIRED:]` followed by attempting your own workaround (on seeing this marker, you must stop)

---

## Where This File Is Referenced

- `.claude/agents/*.md` (each agent's Harness handoff-protocol section)
- `.claude/protocols/execplan-lifecycle.md`
- `.claude/hooks/stop-retro-logger.py` (Phase D)
