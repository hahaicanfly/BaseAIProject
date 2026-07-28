---
name: judgment-rubrics
description: Executable criteria for model escalation, completion definition, circuit-breaking, and quality floor
always: false
---

> **Not auto-loaded.** Since F-003 this file is the full-text reference behind the
> tier packs (`.claude/tiers/`), which are what actually gets injected each session.
> Read this when a borderline case needs the reasoning or worked examples behind a criterion.

# Judgment Rubrics

*白話:遇到沒把握的決定,先照這裡的判斷準則停下來問你,不要硬做。*

> Each entry follows the format: **Signal (observable) → Action**, with a positive/negative example.
> A signal must be "a fact you can point to in the conversation transcript," not a feeling.

## 1. When to Escalate the Model

**Signal** (any one true → escalate per model-dispatch.md §4):
- The same error message appears a 2nd time, with two different fixes attempted, both failing
- Reasoning requires tracing causality across 3+ modules (A's change affects B, which affects C)
- The task involves a trade-off with no standard answer (architecture choice, API contract, security boundary)

- ✅ Good: Sonnet fixes a race condition(白話:兩個流程同時搶著改同一份資料,順序一亂就出錯的臭蟲) — first attempt (add lock) fails, second attempt (restructure flow) also fails → escalate to Opus with both diffs and error output attached.
- ❌ Bad: Sonnet's first test run fails because of a typo'd path → this is a typo, not a capability gap; fix the path and rerun, no escalation needed.

## 2. What Counts as "Actually Done" and Deliverable

**All of the following must hold** (missing even one means "in progress," not "done"):
1. Every acceptance criterion has evidence (test output, read-back result, actual run screenshot/output)
2. Verification was performed by a fresh-context agent or an actual execution — not the implementer's self-report
3. No leftover items marked "TODO / will handle later / should be fine"; if any exist, list them in the delivery notes
4. The list of changed files matches the acceptance report (no undisclosed changes)
5. The pass is against the **current version's full acceptance run** — after multiple repair rounds, it is forbidden to "count the best historical run as passing" (gate-softening); if the last round failed, it failed — go to §3 circuit-break

- ✅ Good: "New parser done: tests 12/12 passing (output below), read-back agent confirmed API matches spec, no open items."
- ❌ Bad: "Code is written, logically it should be fine, couldn't run it because the test environment had issues." → This is not done; you must say "blocked on test environment."

## 3. When to Circuit-Break and Ask the User

**Signal** (any one true → stop immediately, summarize the situation, and ask — do not burn more tokens):
- The full escalation/de-escalation sequence has been exhausted and still failed (same model fails twice in a row → escalate → fails once more after escalation, see model-dispatch.md §4)
- No improvement signal: after 2 consecutive repair rounds, the set of FAILing acceptance items is identical — don't wait for the full escalation sequence to finish; circuit-break immediately
- The next step is an irreversible operation without explicit authorization: push to a shared branch, delete files, send externally, high-volume paid API calls
- The requirement has two reasonable interpretations, and picking the wrong one would waste 30+ minutes of work
- An existing file/data contradicts the user's description (e.g., user says "this file is stale, delete it" but it contains unmerged new content)
- The task requires "taste / business judgment" with no existing spec (see §6 Capability Limits)

**Circuit-break question format**: one-sentence status + what's been tried + 2-3 options with their trade-offs + your recommendation.

- ✅ Good: "3 tests still red after refactor, two repair rounds failed. Options: A) revert the refactor (10 min) B) escalate to Opus for deep investigation (high cost) C) skip this module for now. Recommend A."
- ❌ Bad: silently starting a 3rd retry round — or the opposite extreme: stopping to ask over something trivial like a missing test-command flag.

## 4. Signals That You're on the Wrong Path — Reroute Instead of Retrying

**Signal** (any one true → stop patching the current approach, return to the last decision point, and choose a different path):
- Every fix produces a new error, 3 times in a row (whack-a-mole pattern)
- To make the approach work, you start changing things that shouldn't be touched (bending tests to fit the code, loosening types, commenting out checks)
- The patch code volume already exceeds half of the original change
- You've had to explain to yourself "why this is actually fine" more than once (a rationalization signal)

**Reroute action**: `git stash`(白話:先把目前的修改暫存起來,之後可以復原,不會丟掉) or roll back to the last clean point → write one sentence on why it failed → list at least 2 alternative paths before choosing.

- ✅ Good: changing function A broke test B, fixing B broke C — stop and roll back on the 3rd occurrence, discover the correct fix is to change the interface definition first.
- ❌ Bad: adding skip markers to all 3 broken tests and declaring "core functionality works."

## 5. How to Verify the Quality Floor (Minimum Acceptable Standard)

Check every item before delivery; if you can't answer any one of them, you haven't hit the floor:
1. **Has it run**: the changed code has been executed at least once (test, real run, or minimal repro script)
2. **Boundaries**: empty input / oversized input / nonexistent path — at least considered and either handled or explicitly marked as unhandled
3. **Rollback path**: you can state "if this change is wrong, how to revert" (backup file, clean git point)
4. **No silent error swallowing**: no empty catch blocks, no downgrading an error to a log line and calling it handled
5. **Secrets**: the diff contains no key/token/password (see security.md)

- ✅ Good: PR description includes "test output + boundary-case notes + rollback method: revert a single commit."
- ❌ Bad: treating "lint passed" as proof of quality — lint only checks formatting, not behavior.

## 6. Capability Limits (Honesty Clause)

The following tasks **a weak model is destined to do poorly — don't pretend otherwise**; hit one of these and take the designated exit:

| Limit Type | Signal | Exit |
|---------|------|------|
| Taste/aesthetic decisions | "Which design looks better/more premium" with no style spec | Produce 2-3 candidates + trade-offs each, hand to the user; don't decide unilaterally |
| Fuzzy business judgment | "Is it worth doing" "will users like this" | List verifiable assumptions and how to test them; state plainly "this needs a human decision" |
| Long inference chains with no ground truth | Conclusion can't be verified by test/run/documentation | Tag a confidence level and basis; escalate model or request a second opinion |
| Facts beyond the environment | Needs current external info that can't be searched | Tag inline as `[UNCONFIRMED: <claim>]` (syntax in handoff-protocol.md "Inline Auxiliary Markers"; auto-harvested to ERRORS.md Pending Review) — do not fabricate |

Decomposition, isolated verification, and multi-answer review can improve **execution quality** — they cannot fix **whether the goal is right**. Goal-level doubts always route to §3 circuit-break.

## 7. Red Flags: Rationalization Phrasebook

If you (or a subagent's report) produce a phrase in the left column, you're evading a rule — take the right-column action:

| Phrase | Countermeasure |
|------|---------|
| "This is a small change, no need for the full process" | Grade by the decision tree's objective criteria, not a subjective sense of size |
| "Test environment is broken, skip tests for now" | Not run = not done (§2); report honestly: "blocked on test environment" |
| "Should be fine / logically no issue" | An unsupported conclusion; go get evidence (§5.1) |
| "Do it this way for now, fix it later" | An "later" with no schedule = never; declare it as an open item |
| "The rule's intent probably doesn't cover this case" | **Violating the letter is violating the spirit**; ask a human before claiming an exception |
| "Tried many times, delivering the best version" | gate-softening (§2.5); not passing is not passing — circuit-break and ask |

**Literal-text clause**: all hard rules are binding by their literal text; "I think this matches the spirit" does not authorize bypassing the letter.
