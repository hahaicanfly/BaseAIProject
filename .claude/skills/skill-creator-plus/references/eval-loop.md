# Skill Eval Iteration Process (detailed)

> Condensed from Anthropic's official skill-creator eval methodology (github.com/anthropics/skills/tree/main/skills/skill-creator, 2026-07 version), adapted to this project's environment: dispatch via the Agent tool in place of the official Python infrastructure. If you need the full official automation infrastructure (run_eval.py, run_loop.py, viewer), pull it directly from the official repo.

## Core loop

Define intent → draft → 2-3 test prompts → qualitative + quantitative evaluation → rewrite based on feedback → repeat, until: the user is satisfied, feedback comes back empty, or two consecutive rounds show no substantive progress.

## I. Qualitative evaluation (do this for every skill)

1. Write 2-3 prompts "a real user would actually type" — concrete filenames, colloquial phrasing, even typos; not textbook-style questions.
2. **Dispatch two subagents in parallel in the same turn** (using the delegation-templates.md three-part dispatch format):
   - with-skill: prompt prefixed with the full skill text
   - baseline: prompt only (when modifying an existing skill, give baseline the old version's full text)
3. Compare the outputs. Read the **entire process**, not just the result — which sections of the skill actually influenced behavior? Delete sections that had no effect (keep it lean).
4. Watch for duplicated work across tests: if multiple subagents each rewrite the same script snippet or look up the same data → fold it into the skill's `scripts/` or `references/`.

## II. Trigger evaluation (dedicated test for the description)

1. Write 16-20 queries: 8-10 should-trigger, 8-10 should-not-trigger.
2. The value of negative cases is in the **near-miss** — situations that share keywords with the skill but shouldn't trigger it (example: for the code-review skill, "can you take a look at how this code is written" is a near-miss; "what's the weather today" tests nothing meaningful).
3. Dispatch one fresh-context subagent per query: give it this project's full skill list (name + description) plus the query, and ask "which skill would you pick?" Recommend testing the same query 2-3 times to take the majority (triggering has randomness; the official threshold is a trigger rate ≥0.5 to pass).
4. should-trigger misses → add the verbatim trigger phrase and situational examples to the description (push it further toward pushy); should-not falsely triggers → add a mutual-exclusion qualifier.
5. After editing the description, rerun the same query set. To prevent overfitting: hold back 40% of queries from the rewrite decision, using them only for final verification (in the spirit of the official train/test split).

## III. Quantitative assertions (objectively verifiable output only)

- Each assertion must be **objectively, programmatically verifiable** and have a readable name ("output contains frontmatter and name equals the directory name" rather than "good quality").
- When dispatching a grader, give it dual responsibility (in the spirit of the official grader.md): (a) grade the assertion — a PASS must be genuine completion, not surface compliance and (b) **critique the assertion itself** — an assertion with no discriminative power (both groups fully pass or fully fail) is worse than no assertion at all; report a recommendation to remove it.
- Don't force assertions onto subjective output (copy style, visual taste) — this is a weak-model judgment limit (judgment-rubrics.md §6); instead: produce 2-3 candidates → blind comparison (de-identified, judged by an independent agent with reasoning) → hand off to the user for the final call.

## IV. Workspace discipline

- Put eval artifacts in a `<name>-workspace/` sibling of the skill, organized as `iteration-N/`; this directory is not version-controlled (gitignored).
- You may only delete scratch files created in the current round; `rm` / `git checkout` / `git restore` against any non-self-created file is forbidden (destructive blacklist, general rule in delegation-templates.md).
- Log one line per iteration: what changed, how the trigger rate shifted, the next hypothesis — this becomes the handoff record if work is interrupted.
