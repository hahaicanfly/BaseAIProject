# E. Delegation Prompt Templates

> Companion rule: `.claude/rules/model-dispatch.md` (when to delegate, escalation/de-escalation).
> **Don't paste standing rules into a delegation prompt.** Since F-003 the subagent receives the tier pack matching its own frontmatter `model` automatically, via the `SubagentStart` hook (`.claude/tiers/README.md`). Repeating those rules in the prompt wastes tokens and creates a second copy that will drift. Delegate task-specific context only.
> Usage: copy the matching template → fill in the `[…]` blanks → use as the Agent tool's prompt. **The trio (goal & motivation / acceptance criteria / report format) — missing any one, don't delegate.**
> Each template's closing "report format" section directly constrains the subagent — don't remove it.

## Common Conventions (shared by all templates, append to the end of the delegation prompt)

```
Report conventions:
- Report ≤ 40 lines; return only conclusions and file:line references — no pasting more than 10 lines of code/raw text
- Anything over 40 lines goes into a file; report only the path
- Report failures honestly: where you're stuck, what you tried; reporting "大致完成" (roughly done) is forbidden
- The last line must be [HANDOFF: main] or [VERIFY_FAILED: <reason>] or [HUMAN_ATTENTION_REQUIRED: <reason>] (`main` = report back to the main conversation, already whitelisted in handoff-protocol.md)
- Destructive-command blacklist: no rm, git checkout --, git restore, git clean, or overwriting mv on any "non-assigned file" — even for test cleanup. Untracked files aren't protected by git; deleting them is permanent (lesson: ERRORS.md 2026-07-04 accidental-deletion incident)
```

## Scope Declaration (required for every delegation, placed right after the prompt's "Goal")

The blacklist blocks destructive commands; this section is its positive complement — an allowlist defining the workable scope, and a termination condition defining when to stop.

```
Scope declaration:
- Allowed to read: [file/directory list, or "whole repo, read-only"]
- Allowed to write: [explicit list; any file not listed may not be modified/deleted/moved/created]
- Do not touch: [high-risk paths, e.g. .env*, state/, other tasks' worktrees]
- Termination condition: stop once all acceptance criteria are met; stop after 2 failed attempts on the same acceptance item and report [VERIFY_FAILED:*]; stop immediately if a file outside "allowed to write" needs changing and report [HUMAN_ATTENTION_REQUIRED:*]
```

---

## 1. Search & Locate (find files / symbols / usages)

- Recommended: `Explore` agent; use `quick` for narrow scope, `very thorough` for spanning multiple locations. No need to specify a model.

```
Locate [target: function/config/string/call site] in [repo/directory].
Motivation: [what you'll do once found, so you can judge which results are relevant].
Search hints: [known keywords/naming conventions/likely locations].
Acceptance criteria:
- Each result comes with file:line and a one-sentence reason it's relevant
- If nothing is found, list 3+ search approaches and keywords you tried
Report format: a result list (file:line — explanation), or "not found + search approaches tried."
```

**Filled-in example**: "Locate every call site in src/ that calls fetch() directly without going through the apiClient wrapper. Motivation: unifying retry and auth-header handling. Search hints: `fetch(`, `axios`. Acceptance criteria: each call site with file:line; if zero found, list the search approaches tried. Report format: a list."

## 2. Feature Implementation

- Recommended: `general-purpose`, `model: "sonnet"`; use `opus` only for architecture decisions. Add `isolation: "worktree"` when multiple people are editing files in parallel.

```
Implement [feature, one sentence].
Motivation & background: [why, user scenario, relevant ExecPlan/issue path].
Scope: only touch [file/module list]; do not touch [exclusion list].
Technical constraints: [interface signatures/dependency direction/naming, referencing the relevant section of docs/architecture/domains.md].
Acceptance criteria (all must be met to count as done):
- [test command] passes; paste the last 10 lines of actual output
- Every new/modified public function has [a test/usage example]
- The list of changed files matches the plan, with no out-of-plan changes
- API evidence table: every external API / third-party symbol used for the FIRST time gets a row
  `symbol → definition location (repo file:line, or official-doc URL + access date)`; an external
  symbol without an evidence row counts as guessed (CLAUDE.md: NEVER guess API signatures) → FAIL
Report format: list of changed files (file:line ranges) + tail of test output + API evidence table + open items (if any).
```

## 3. Code Refactoring

- Recommended: `general-purpose`, `model: "sonnet"`; behavior before and after the refactor must be provably unchanged.

```
Refactor [target scope], purpose: [eliminate duplication/extract an interface/reduce coupling, one sentence].
Motivation: [current pain point, with file:line].
Invariants (must hold after refactoring):
- External behavior unchanged: [existing test list/golden outputs] all pass
- Public API signature [unchanged / which changes are allowed]
Prohibited: don't change tests to accommodate the code; don't loosen types; don't comment out checks (judgment-rubrics §4).
Acceptance criteria: run tests once before refactoring to record a baseline; the same command's output must match after refactoring; diff line count [cap].
Report format: refactor summary (pattern, one sentence) + before/after test output comparison + changed files file:line list.
```

## 4. Research Investigation (web/documentation)

- Recommended: `general-purpose`, `model: "sonnet"`; for major technology-selection decisions, dispatch a second independent agent to cross-check the conclusion.

```
Research question: [one-sentence question].
Motivation: [what this answer will decide].
Required sources: [official docs/repo/specified URLs]; prefer primary sources.
Acceptance criteria:
- Every conclusion has a source (URL or file:line) and a date
- Separate "facts (sourced)" from "inference (your judgment)" into two sections
- Anything not found is tagged inline as `[UNCONFIRMED: <claim>]` (standard syntax, handoff-protocol.md "Inline Auxiliary Markers"; auto-harvested for weekly review) — fabrication is forbidden
Report format: conclusions (≤5 items, each with a source) + unconfirmed list + recommendation (≤3 lines).
```

## 5. Code Review

- Recommended: `code-reviewer` agent (frontmatter already sets sonnet); output format follows `.claude/protocols/review-protocol.md`.

```
Review [branch/PR/file list], change intent: [what this change is meant to achieve].
Focus dimensions: [correctness/security/performance/readability — at least one].
Acceptance criteria:
- Every finding has file:line, a severity (Blocker/Warning/Suggestion, per review-protocol.md's tiers), and a concrete failure scenario (what input breaks it)
- Even with no findings, list "dimensions checked and methods used"
- If unsure whether something is a bug, mark that finding "unconfirmed, needs human verification" — don't state it as fact
Report format: follow review-protocol.md's format; findings sorted by severity.
```

## 6. Fresh-Context Acceptance Review (verification-not-self-certified, pairs with model-dispatch §5)

- Recommended: spawn a new `general-purpose`, `model: "sonnet"`. **The prompt must not narrate the implementation process** — give only acceptance criteria and file paths, to prevent the reviewer from being biased by the implementer's self-report.

```
You are the reviewer, performing an independent verification of the following deliverable (you did not participate in the implementation — do not assume it is correct).
Deliverable under review: [file path list].
Acceptance criteria (check each one):
1. [criterion one, mechanically decidable]
2. [criterion two]
Verification method:
- Documents: re-read the file, check against each acceptance criterion, cite file:line as evidence
- Code: actually run [tests/commands], paste the last 10 lines of actual output
- API evidence table (if the deliverable has one): spot-check ≥3 rows — repo symbols must Grep at the
  cited file:line; URL rows must WebFetch and the page must contain the symbol
The acceptance report allows only two conclusions:
- PASS: list each "criterion → evidence (file:line or output)"
- FAIL: list unmet items → evidence → a one-sentence fix suggestion
FAIL may only be based on the mechanically checkable acceptance criteria listed above; style/writing/opinion-type
feedback goes into a separate "Suggestions (non-blocking, may be empty)" section and must not be used as a FAIL reason (model-dispatch §5).
Evidence-free conclusions such as "看起來沒問題" (looks fine) or "應該可以" (should be OK) are forbidden.
Verdict persistence (mandatory — acceptance outcomes must survive your ephemeral context):
- Write the FULL report (each criterion → evidence, actual command outputs) to docs/reviews/<YYYY-MM-DD>-<slug>.md
  with the Write tool. This is the ONLY file you may create; everything else stays read-only.
- Your final message must contain the line `VERDICT: PASS docs/reviews/<file>.md` (or `VERDICT: FAIL docs/reviews/<file>.md`)
  — stop-retro-logger harvests that line into state/verifications.jsonl, and a FAIL also lands in ERRORS.md Pending Review.
- Then end with the handoff marker as usual ([HANDOFF: main] on PASS, [VERIFY_FAILED: <reason>] on FAIL).
```

**Filled-in example**: "You are the reviewer. Deliverable under review: docs/harness/DIAGNOSIS.md. Acceptance criteria: 1) exactly 3 items in each of the three major pain-point categories, each with a fix 2) each item has at least one file:line piece of evidence 3) includes a Capability Limits section 4) no leftover `{{placeholders}}`. Verification method: re-read the file and check against each criterion. Output a PASS/FAIL report."

## 7. Strategy Research (file-first)

- Recommended: `pm` / `market-researcher` / `competitive-analyst` / `data-analyst` per topic
  (see each agent's frontmatter `description` for scope boundaries — market sizing vs.
  competitor comparison vs. quantitative KPI work are different agents, don't overlap them).
  This template is "file-first": the full report always lands in `docs/research/`; the chat
  reply is a bounded summary, never the deliverable itself.

```
Research question / strategy topic: [one-sentence question].
Motivation & background: [what decision this will inform, why now].
Required sources: [official docs/market reports/specified URLs]; prefer primary sources.
Scope declaration: (per the standard block above; the write scope is exactly one new file:
  docs/research/<YYYY-MM-DD>-<slug>.md — no other file may be modified/deleted/moved/created)
Acceptance criteria (all must be met to count as done):
- Full report has been written with the Write tool to docs/research/<YYYY-MM-DD>-<slug>.md
  (naming rule: docs/research/README.md)
- Report contains a `### 假設-證據表` with every row's confidence column filled
  (高/中/低 — an empty confidence cell is a FAIL, not a placeholder)
- Report contains a `### Sources` section with at least 3 verifiable URLs (or file:line for
  internal data); any claim without a source is tagged inline `[UNCONFIRMED: <claim>]`
- Chat reply is a summary ≤ 40 lines: key findings + open questions + the file path — full
  detail stays in the file, never pasted into the reply
Report format: ≤40-line chat summary (conclusions + path to the written report); the report
file itself follows the agent's Output Format template (assumption-evidence table + Sources
required — see agent frontmatter for the exact template).
```

Append **Common Conventions** (top of this file) to the end of every filled-in prompt, same as templates §1-6.
