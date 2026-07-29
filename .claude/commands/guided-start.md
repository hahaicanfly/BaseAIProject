Guided, natural-language entry point for non-technical users of BaseAIProject. Turns a plain-language ask into: (0) detect whether this continues in-progress work, (1) fill in the missing pieces of intent with a couple of targeted questions, (3) hand routing off to the routing table in the session's injected tier pack, and (4) once work is done, translate the acceptance evidence into plain language. This command adds **no new governance judgment of its own** — every routing decision and every acceptance criterion it reports comes from a file that already exists and is read fresh, every time, at the moment it is needed.

**Non-Goals (this reduced version deliberately does not do)**: there is no "confirm before executing" / error-recovery stage (the full six-stage guided flow this MVP is a slice of); this command is not wired into README/CLAUDE.md as a new canonical entry point — it is an alternate on-ramp that sits alongside the Decision Tree, never a replacement for it; it does not track a request's progress after handing off control in Step 3.

Run the following steps in order, briefly reporting after each one. **Do not skip Step 3** — it is the one guardrail keeping this command a translator of an existing decision tree rather than a second, competing source of judgment.

## Step 0: Detect whether this continues in-progress work

Before asking the user anything, check `docs/plans/active/` for `F-*.md` files.

- If the directory is empty or has no ExecPlan that looks in-progress (check its `Status` field and `state/feature-list.json` if present) → there is nothing to continue; go to Step 1.
- If there is an in-progress ExecPlan **and** the user's message reads like a continuation of it (references the same feature, says "continue", "keep going", picks up a thread from the ExecPlan's `## 6. Progress Log` or `## 9. Handoff Manifest`) → skip straight to Step 4 (the user is here for an acceptance/status read-out, not a new request).
- If it's unclear whether the message is a fresh request or a continuation → do **not** silently guess either way. Say one sentence naming the in-progress ExecPlan and ask directly: "Is this about `F-NNN-<slug>` that's already in progress, or something new?" Wait for the answer before proceeding.

## Step 1: Gather the request

1. Echo back, in one plain sentence, what you understood the user wants — so a misunderstanding surfaces immediately instead of after a plan is drafted.
2. Read `.claude/rules/clarify-first.md` §1 **right now** (its current text, not a memorized summary) and check the request against its 4-field checklist: target user, success metric, non-goals/boundaries, trigger condition. This command does not maintain its own copy of that checklist — it re-reads the rule file live so it can never drift out of sync with it.
3. Apply clarify-first.md §1's current signal for whether to stop and ask (this command holds no copy of that threshold — read it fresh each time). If it says to ask, batch the missing fields into 1-2 short questions per round (via `AskUserQuestion` if available, plain text otherwise), and never re-ask about something the user already told you in this conversation.
4. While gathering, also read `.claude/rules/plan-first.md`'s Exceptions list **live** (this command holds no copy of that list either). If the request already and obviously falls under one of its current Exceptions → skip Step 3 entirely and go straight to executing the task directly. Say so explicitly, one sentence, citing which Exception applies — quoting it from the file you just read, not from memory.
5. Otherwise, once the 4 fields are adequately covered (or the user has confirmed there's nothing more to add), move on to Step 3.

## Step 3: Route through the tier pack's routing table

This is the only judgment call this command makes, and it is not really this command's judgment — it is CLAUDE.md's.

1. Read the live text of the **"Before acting"** section of this session's tier pack right now, in full — `.claude/tiers/strong.md`, `mid.md` or `light.md`, whichever was injected (`.claude/tiers/README.md` explains which one that is). Read the file; do not paraphrase it and do not rely on a memory of the injected copy. Until F-003 this table lived in `CLAUDE.md` as "Decision Tree Before Acting"; it does not any more.
2. Apply its numbered criteria (0-5) to the gathered request exactly as written there. This command holds no routing table, no threshold list, and no shortcut copy of that tree — it only translates the tree's own output into a plain-language handoff for the user.
3. Hand control to whichever branch the Decision Tree names — draft an ExecPlan (`docs/plans/active/`, spec in `docs/plans/PLANS.md`, per `.claude/protocols/execplan-lifecycle.md`), enter Plan Mode, or execute the task directly — and say in one sentence which branch was chosen and why, quoting the matching criterion.
4. Once control is handed off, this command's job is done for this pass — it does not stay in the loop watching the work happen, and does not re-run this checklist mid-task (that is `judgment-rubrics.md` §3's job, not this command's).

## Step 4: Translate acceptance evidence into plain language

Once the handed-off work has actually run its verification (an ExecPlan's §5 Verification Strategy, a review report, or both):

1. Run `python3 scripts/translate-acceptance.py [plan.md] [--review <review-file>]` (omit `plan.md` to let it default to the newest ExecPlan in `docs/plans/active/`; add `--review` if a `docs/reviews/*.md` report exists for this work).
2. Read its output as-is — it is a read-only translator, not a second acceptance gate, and it says so plainly whenever it can't find evidence for something rather than guessing.
3. Fold that output into CLAUDE.md's existing three-line report template (`✓ Done / → Next / ⚠ Note`), and make sure every line that claims something passed or failed links to the real evidence file path the script reported (the `state/acceptance/<stem>.jsonl` it read, or the `docs/reviews/*.md` it translated) — never restate a result without the path behind it.
4. If the script reports it found no matching evidence (no jsonl, no review, ambiguous match), say that plainly in the `⚠ Note` line instead of inventing a status.

## References

- `.claude/rules/clarify-first.md` — the 4-field checklist Step 1 reads live
- `.claude/tiers/strong.md` / `mid.md` / `light.md` — the "Before acting" routing table Step 3 defers to; `.claude/tiers/README.md` explains which pack a session gets
- `.claude/rules/plan-first.md` — the Exceptions list Step 1 checks before deciding whether Step 3 is even needed
- `.claude/protocols/execplan-lifecycle.md` — the 10-phase ExecPlan lifecycle a Step 3 hand-off into ExecPlan territory enters
- `scripts/translate-acceptance.py` — the read-only acceptance/review translator Step 4 calls
- `.claude/protocols/review-protocol.md` — the review report format (`VERDICT:` line, traffic-light plain-language layer) `translate-acceptance.py` parses
