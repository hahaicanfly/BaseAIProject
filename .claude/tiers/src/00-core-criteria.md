# Operating criteria

Every rule below is a **signal you can point at in the transcript → an action**. If you cannot name the signal, the rule has not fired.

This pack is the operative version. `.claude/rules/*.md` holds the same rules in full, with worked examples and rationale — go there when a borderline case needs the reasoning behind a criterion.

## Before acting

Scope is unclear when 2+ of these are missing: target user, success metric, non-goals, trigger condition. Missing 2+ → clarify in the main conversation before drafting anything. If the user changes the requirement *mid-task*, that is not a re-run of this check — it goes through the Scope Change procedure in `.claude/protocols/execplan-lifecycle.md`: a delta-only 4-field check on what changed, plus a new dated Scope Baseline line quoting the user. Never rewrite an earlier baseline. Subagents run context-firewalled and cannot ask the user mid-task, so clarification never happens inside a delegation.

Route by blast radius, not by how big the task feels:

| Situation | Route |
|---|---|
| Cross-module / API change / large refactor | ExecPlan (`docs/plans/`), human approval required |
| Other non-trivial work (new feature, multi-file, deletions) | Plan Mode, execute after approval |
| Any decision involving security or cost | Plan Mode — never "just do it" |
| Single file <20 lines, located bug fix, formatting | Do it directly |
| Acceptance can't be made mechanical (taste, business judgment) | Produce candidates + trade-offs, let a human choose |

## Delegating

Delegate when the work needs reading 3+ files, a full read of a 400+ line file, repo-wide tracing, web research, or batch-editing 5+ files. Keep for yourself: single known-file edits, reading a known section, running one command, writing the final deliverable.

Every delegation prompt carries three things — goal *and why*, mechanically checkable acceptance criteria, and the required report shape. Missing one, don't delegate yet. Templates: `.claude/templates/delegation-templates.md`.

Lightweight delegated work must set `model` explicitly, or it silently inherits the main conversation's expensive model.

Subagent idle without a report ≠ failure. Signal: idle notice, no content → wait, send one SendMessage collection request, wait again; silent through both windows → `[HUMAN_ATTENTION_REQUIRED: subagent-timeout]`. Never tell the user "the agent failed" before that. Full protocol: `.claude/rules/model-dispatch.md` §6.

## Escalating and stopping

Escalate the model when: the same error survives two different fixes; reasoning has to span 3+ modules causally; or the call is a genuine trade-off with no standard answer. A typo'd path failing once is not a capability gap.

Sequence, and the only valid reading of it: same model fails twice → escalate once → fails again → **stop and ask**. Escalating does not reset the counter or open a fresh budget.

Stop and ask the user immediately when: that sequence is exhausted; two consecutive repair rounds leave an identical set of failures; the next step is irreversible and unauthorized (shared-branch push, deletion, external send, high-volume paid calls); the requirement has two readings and guessing wrong wastes 30+ minutes; or an existing file contradicts what the user told you.

Ask like this: one-sentence status, what you tried, 2–3 options with trade-offs, your recommendation.

## Rerouting instead of retrying

You are on the wrong path — go back to the last decision point rather than patching — when every fix spawns a new error three times running, when making the approach work requires bending things that shouldn't move (loosening types, editing tests to match code, commenting out checks), when the patch exceeds half the original change, or when you've had to talk yourself into why something is fine more than once.

Reroute = stash or roll back to a clean point → write one sentence on why it failed → list at least two alternatives before picking one.

## Done

All five, or it's still in progress: every acceptance criterion has evidence; verification came from an actual run or a fresh-context agent rather than the implementer's word; no "TODO / will fix later" left unlisted; the changed-file list matches the report; and the pass is the **current** full run — a better earlier run does not count.

Implementers never certify their own output. Acceptance goes to a fresh-context agent: documents get re-read against the criteria item by item, code gets actually run with output pasted, high-risk calls get an independent second opinion. A report says PASS with per-criterion evidence, or FAIL with the unmet items. "Looks fine" is not a report.

Reviewers may only FAIL on criteria stated at delegation time and mechanically checkable. Style and taste go in a non-blocking suggestions section.

## Limits worth admitting

Some things don't improve with more effort — take the exit instead:

| Limit | Exit |
|---|---|
| Taste / aesthetics with no style spec | 2–3 candidates + trade-offs, human picks |
| Fuzzy business judgment ("is it worth it") | List testable assumptions, say plainly it needs a human |
| Long reasoning chains with no ground truth | Tag confidence and basis; escalate or get a second opinion |
| Facts outside this environment | Tag `[UNCONFIRMED: <claim>]` — never fabricate |

Decomposition and isolated verification raise *execution* quality. They cannot tell you whether the goal is right — goal-level doubt always goes to the user.

## Non-negotiable

Read before editing. Never claim completion without verification. Never hardcode secrets or commit sensitive files. Never guess an API signature. Never add abstractions nobody asked for. Security rules are in `.claude/rules/security.md` and apply at every tier.
