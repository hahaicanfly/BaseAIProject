---
name: clarify-first
description: Proactive scope/requirement check before entering ExecPlan or Plan Mode — objective signal, not vibes
always: true
---

# Clarify First

> Always-on rule. Complements `judgment-rubrics.md` §3 (reactive circuit-break, fires mid-task) — this rule is **proactive**: it runs *before* you start drafting an ExecPlan or a Plan Mode plan, not after ambiguity is hit while executing. Format follows the `judgment-rubrics.md` convention: **Signal (observable) → Action**, with positive/negative examples.

## 1. When to Stop and Clarify Before Drafting a Plan

**Signal** (count how many of the following 4 are missing from the request; 2 or more missing → clarify before drafting anything):
1. **Target user** — who uses this / who is affected
2. **Success metric** — how you'd know it's done / working
3. **Explicit boundaries or non-goals** — what is deliberately excluded
4. **Concrete trigger condition** — when this runs / what invokes it

- ✅ Good: User says "add an export feature." Missing: target user, success metric, non-goals, trigger condition (4/4 missing) → stop, ask before opening Plan Mode or an ExecPlan.
- ❌ Bad: Same request → immediately start Plan Mode, silently deciding "export to CSV, triggered by a button, for all users" without confirming any of it.

When this gate runs, emit the telemetry marker inline — `[RULE_FIRED: clarify-first|missing=N, asked]` when it triggers clarification, `[RULE_SKIPPED: clarify-first|<§4 exception>]` when skipped — so the rule's hit-rate is measurable (syntax: handoff-protocol.md "Inline Auxiliary Markers"; harvested to state/rule-events.jsonl).

## 2. Where Clarification Happens (context_firewall constraint)

All agents in `.claude/agents/` run with `context_firewall: true` — non-interactive subagents that cannot pause mid-task to ask the user something live. Clarification must therefore happen in the **main conversation**, never inside a delegated subagent:

- Ask directly in the main conversation (`AskUserQuestion` or plain text), or
- Invoke `pm` or `spectra-amplifier` to draft candidate interpretations, then relay their output back to the user **in the main conversation** for confirmation before handing off to ExecPlan/Plan Mode.

- ✅ Good: Main conversation asks "which of these two did you mean?" before delegating to `architect`.
- ❌ Bad: Delegate straight to a subagent hoping it will "ask the user" — a context-firewalled subagent's questions never reach the user; it will silently guess, stall, or fabricate an answer.

## 3. Relationship to judgment-rubrics.md §3

§3 is the **reactive** exit: it fires *during* execution, once "two reasonable interpretations exist and picking the wrong one would waste 30+ minutes." This rule is the **proactive** gate: it fires *before* drafting starts, using the objective 4-field checklist in §1 above. Passing this gate does not exempt you from §3 later — if ambiguity surfaces mid-task anyway, handle it there; don't re-run this checklist mid-task. One exception: a **user-initiated requirement change** mid-task is not covered by this don't-re-run clause — it goes through execplan-lifecycle.md's "Scope Change" procedure (delta-only 4-field check + Scope Baseline version line).

## 4. When to Skip

Skip this check for anything already covered by `plan-first.md`'s Exceptions list — those tasks never enter Plan Mode or an ExecPlan in the first place, so there's no plan to clarify scope for:
- Single-file changes < 20 lines
- Formatting or comment-only updates
- An already-located bug fix (root cause confirmed)
- User explicitly says "just do it"

- ✅ Good: "Fix the typo in line 42" → root cause already located, single file, skip clarify-first entirely.
- ❌ Bad: Running the 4-field checklist on a one-line formatting fix, wasting a clarification round-trip on a task with no real ambiguity.
