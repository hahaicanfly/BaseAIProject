---
name: model-dispatch
description: Model dispatch, the delegation trio, escalation/de-escalation path, verification-not-self-certified (single source of truth)
always: true
---

# Model Dispatch Rules

> Always-on rule (auto-loaded every session); contains only criteria and hard rules.
> Full delegation prompt templates: `.claude/templates/delegation-templates.md`; judgment rubrics: `.claude/rules/judgment-rubrics.md`.

## 0. Actually Available Local Tiers (2026-07 inventory, facts not assumptions)

| Tier | Agent tool `model` value | Purpose |
|------|----------------------|------|
| Haiku 4.5 | `haiku` | Formatting, fixed-template application, single-point lookups |
| Sonnet | `sonnet` | Default workhorse: implementation, search, review, research |
| Opus 4.8 | `opus` | Architecture decisions, cross-module refactors, hard debugging |
| Fable 5 | `fable` | Special-authorization sessions only; do not assume availability day-to-day |

- The main conversation's model is set by `model` in `~/.claude/settings.json`; don't assume which model you are mid-conversation — go by behavioral rules, not self-identification.
- `effort` parameter: only the Workflow tool's `agent(prompt, {effort})` supports it (`low|medium|high|xhigh|max`); ignore this line if the environment has no Workflow tool. The Agent tool has no `effort` parameter — it inherits the session setting.
- When the Agent tool omits `model`, it inherits the main conversation's model — **lightweight delegated tasks must explicitly set `model: "haiku"` or `"sonnet"`, otherwise chores run on the main conversation's expensive model**.

## 1. The Commander Doesn't Do Fieldwork

The main conversation (commander) only does: deciding, decomposing, delegating, concluding acceptance review, and communicating with the user.

**Must delegate to a subagent** (any one condition triggers delegation — don't do it yourself):
- Estimated to require reading 3+ files, or a full read-through of a single file over 400 lines
- Full-repo scanning / keyword tracing (→ `Explore` agent)
- Web search or documentation research (→ `general-purpose`, `model: sonnet`)
- Batch-modifying 5+ files (→ delegate + worktree isolation, see parallel-worktree.md)
- Any analysis requiring "reading a lot before you can conclude anything"

**The main conversation may do directly**: editing a single known file (< 20-line diff), reading a specific section of a known file, running a single command and reading the result, writing the final deliverable text.

## 2. The Delegation Trio (every delegation prompt must contain these three sections — missing one, don't delegate)

1. **Goal and motivation**: what to achieve and why (lets the subagent make small decisions autonomously)
2. **Acceptance criteria**: a mechanically checkable definition of done (file exists, tests pass, report contains specific fields)
3. **Report format**: explicitly specify the report's structure and length cap

Copy the template directly from `.claude/templates/delegation-templates.md`; don't improvise.

## 3. The Reporting Contract (subagent side)

- Report ≤ 40 lines; return only conclusions, lists, and `file:line` references
- No pasting more than 10 lines of code or raw text into a report — long artifacts go to a file, report the path
- The last line of the report must be a handoff marker (see `.claude/protocols/handoff-protocol.md`)
- Report failures honestly: state where you're stuck and what you tried; "mostly done" is not an acceptable report

## 4. Escalation/De-escalation Path

| Situation | Action |
|------|------|
| Haiku hits a tool-call error or syntax error **once** | Re-delegate straight to Sonnet; don't retry Haiku |
| Sonnet fails the **same subtask twice in a row** | Escalate to Opus, with the prompt including the full failure trace: original instruction, both error outputs, expected result |
| Opus solves it with a repeatable, fixed pattern | Write the pattern down as a rule/example (persist it), then de-escalate to Sonnet/Haiku for batch application |
| After escalation (Opus) **fails once more** | Stop retrying → circuit-break, ask the user with the failure trace (see judgment-rubrics.md §3) |

Full sequence (the only valid reading): same model fails twice in a row → escalate once → fails once more after escalation → circuit-break and ask. The escalation attempt does not reset the failure counter or open a new budget.
"Same subtask" is determined by matching goal and acceptance criteria — rephrasing and re-delegating still counts toward the failure count.

## 5. Verification Is Never Self-Certified

- The implementer may not declare their own output as having passed acceptance.
- Acceptance review always goes to a **fresh-context subagent** (newly spawned, without the implementation-process context):
  - Document/config output → read-back: re-read the file, check it against acceptance criteria item by item
  - Code output → actually run tests or run the program, paste the actual output
  - High-risk judgment (architecture selection, security, irreversible operations) → second opinion: dispatch a second agent with a different model or a different angle to answer independently, then compare conclusions; escalate or ask the user on disagreement
- An acceptance agent's report can only be: `PASS` (list each acceptance criterion with evidence) or `FAIL` (list unmet items with evidence). "Looks fine" is not accepted.
- Acceptance review boundary: FAIL may only be based on acceptance criteria stated at delegation time that are mechanically checkable; style/writing/opinion-type feedback goes into a "Suggestions (non-blocking)" section and must not block delivery — this prevents reviewer overreach causing wasted rework cycles.
