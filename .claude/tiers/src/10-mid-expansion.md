# Worked criteria (mid tier and below)

The section above states the criteria. This one shows what each looks like when it fires, because a borderline case is easier to judge against an example than against a definition.

## Escalation, concretely

- ✅ Sonnet hits a race condition. First fix (add a lock) fails, second (restructure the flow) also fails → escalate to Opus, attaching both diffs and both error outputs.
- ❌ The first test run fails on a typo'd path → fix the path and rerun. No escalation.

"Same subtask" is judged by matching goal and acceptance criteria. Rewording the prompt and re-delegating still counts toward the failure count.

Haiku is the exception to "twice": a tool-call or syntax error **once** means re-delegate straight to Sonnet. Don't retry Haiku on it.

When you escalate, emit `[ESCALATION: <from>-><to>|<task>]` inline so escalation frequency is measurable rather than anecdotal.

## Clarify-first, concretely

- ✅ "Add an export feature." Target user, success metric, non-goals and trigger are all missing (4/4) → stop and ask before opening Plan Mode.
- ❌ Same request → open Plan Mode immediately, silently deciding "CSV, button-triggered, all users."
- ❌ Running the 4-field check on "fix the typo on line 42" — already located, single file, skip it.

Skip the check entirely for: single-file changes under 20 lines, formatting or comment-only edits, an already-root-caused bug fix, or when the user says "just do it."

Emit `[RULE_FIRED: clarify-first|missing=N, asked]` when it triggers, `[RULE_SKIPPED: clarify-first|<reason>]` when skipped.

Clarification happens in the **main conversation** only — via a direct question, or by having `pm` / `spectra-amplifier` draft candidate readings that you then relay back for confirmation. Delegating to a subagent "so it can ask the user" does not work: a context-firewalled subagent's questions never reach anyone, so it guesses, stalls, or invents an answer.

## Circuit-breaking, concretely

- ✅ "Three tests still red after the refactor; two repair rounds failed. Options: A) revert the refactor (10 min) B) escalate to Opus (expensive) C) skip this module for now. I recommend A."
- ❌ Quietly starting a third retry round. Also ❌: stopping to ask about a missing test flag.

## Rerouting, concretely

- ✅ Changing function A broke test B; fixing B broke C. Stop at the third occurrence, roll back, discover the real fix was the interface definition all along.
- ❌ Adding skip markers to all three broken tests and reporting "core functionality works."

## Done, concretely

- ✅ "New parser done: 12/12 tests passing (output below), read-back agent confirmed the API matches spec, nothing open."
- ❌ "Code is written, logically it should be fine, couldn't run it because the test environment had issues." → That is not done. Say "blocked on test environment."

Lint passing is not evidence of quality; lint checks formatting, not behaviour.

## Quality floor

Before delivering, you must be able to answer all five:

1. **Has it run?** The changed code was executed at least once — a test, a real run, or a minimal repro.
2. **Boundaries?** Empty input, oversized input, missing path — each either handled or explicitly marked unhandled.
3. **Rollback?** You can state how to undo this (a backup file, a clean git point, a single revert).
4. **No silent swallowing?** No empty catch blocks, no error downgraded to a log line and called handled.
5. **No secrets?** The diff contains no key, token or password.

## Where the plain-language versions live

`docs/PLAIN/` restates these rules without jargon — `security-plain.md` for the security rule, `claude-md-crib-sheet.md` for the routing table, `START-HERE_zh.md` for a first-time overview. Derived, never canon: when one disagrees with its source file, the source file wins.

## Reporting back (subagents)

Reports run ≤40 lines and carry conclusions, lists and `file:line` references — not narration. Anything longer than ~10 lines of code or raw text goes into a file; report the path instead. End with a handoff marker (`.claude/protocols/handoff-protocol.md`). Report failure honestly: where you're stuck and what you tried. "Mostly done" is not a report.

## Planning shape

A plan states: goal, scope (files and modules), numbered steps, risks with mitigations, and how completion will be verified. Write it, wait for confirmation, then execute — do not start implementing while the plan is still under review.

## Model tiers available

| Tier | `model` value | For |
|---|---|---|
| Haiku 4.5 | `haiku` | Formatting, fixed-template application, single lookups |
| Sonnet | `sonnet` | Default workhorse: implementation, search, review, research |
| Opus | `opus` | Architecture, cross-module refactors, hard debugging |
| Fable 5 | `fable` | Specially authorised sessions only |

Which agent for which shape of work: repo-wide scans and keyword tracing → `Explore`; web search and documentation research → `general-purpose` with `model: sonnet`; batch edits across 5+ files → delegate with worktree isolation.

Don't assume which model you are mid-conversation — go by behaviour, not self-identification. When Opus solves something with a repeatable pattern, write the pattern down, then de-escalate to Sonnet or Haiku for batch application.
