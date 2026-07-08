# A. Harness Leak Diagnosis

> Produced: 2026-07-04 one-off architecture session by Fable 5. Audience: long-running models such as Sonnet / Opus / Haiku.
> Basis: 3 parallel audits (full 68-file BaseAIProject sweep, global ~/.claude environment, comparison with the MaiNeu parent project) + live verification in the main conversation.
> This file is the basis for all subsequent harness files. Fix-status markers: [已修] (fixed) / [未修] (not fixed).

## Diagnostic method

- Full inventory of 68 files (~8,760 lines), tagged DUP (duplicate) / STALE (outdated) / HEAVY (too heavy for always-on load)
- Black-box testing of hooks (feed JSON payloads, observe exit codes) — never trust a document's self-description
- Compared evolutionary drift against the MaiNeu parent project (Menu-Android, the longest battle-tuned)
- Criterion for "token leak": loaded on every session or every spawn, with low information density or duplication

## I. Top 3 token leaks

### 1. The "must-read" empty shell: agent_docs/TECHNICAL-REFERENCE.md (257 lines, all 33 {{placeholders}} empty) [已修 fixed]
CLAUDE.md's first MUST was "read this file before any task", yet the entire file was an unfilled template — every task paid a mandatory 257 lines of tokens for zero information, and it trained weak models into the bad intuition that "must-read files can contain no information".
**Blocking fix**: CLAUDE.md now says "if TECHNICAL-REFERENCE.md still contains {{placeholders}}, treat it as not activated and skip it"; an activation-switch note was added at the top of the template. It regains must-read status only after a new project fills it in.

### 2. All standing rules loaded in full + the same rule copied three times (~420 lines per session, more than half duplicated) [已修 fixed]
All of `.claude/rules/*.md` is auto-injected into every session. The security rule existed in three copies (rules/security.md ≈ agent_docs/security-policy.md ≈ invariants.md INV-SEC-*), the cost rule in two, differing only in wording.
**Blocking fix**: layered single source of truth — rules/ holds only the "standing condensed version" (criteria and hard rules); full versions and tutorial content live in agent_docs/ and are referenced from rules; duplicate passages deleted. Any new rule file must first answer "does this need to be standing?"

### 3. Verbatim boilerplate across 14 agent files (~15–20 lines × 14 files ≈ 250 lines repaid on every spawn) [未修 not fixed → handed to the maintenance protocol]
The three-marker handoff explanation, the `git branch --show-current` self-check, and the "read invariants, list INV-ids" passage were copied verbatim across 14 agent files (source: handoff-protocol.md:13-17).
**Blocking fix**: collapse each agent file's tail section to one line: "Handoff and self-check rules: see `.claude/protocols/handoff-protocol.md`; final response must include a marker." The batch edit is mechanical application, well suited to dispatching Haiku/Sonnet in batch (exactly the example downgrade-batch task in model-dispatch.md §4).

## II. Top 3 focus-loss risks

### 1. Fractured single source of truth: multiple mutually contradictory canons for the same thing [部分已修 partially fixed]
- Model dispatch table contradicted in 9 places (agent frontmatter vs the CLAUDE.md table vs AI-TEAM-REGISTRY.md — e.g. pm marked haiku in one and opus in another)
- Three mutually exclusive review output formats (code-reviewer vs review-protocol vs tech-lead)
- Two agent/skill rosters, both with wrong counts (REGISTRY missing code-reviewer; skill list missing 4 later-added skills)
A weak model that hits a contradiction will not stop to verify — it adopts one at random, making behavior unpredictable.
**Blocking fix**: declare a canon hierarchy (now written into the new CLAUDE.md): model dispatch follows **agent frontmatter**; review format follows **review-protocol.md**; rosters follow **AI-TEAM-REGISTRY.md**; other files may only reference, never re-list. Until contradictions are fully cleaned, weak models resolve inconsistencies by this hierarchy.

### 2. Dead references and ghost paths: what can't be traced makes weak models fabricate [部分已修 partially fixed]
`ADR-0001` (referenced 7 times, file doesn't exist), `/harness-workflow` skill (referenced in CLAUDE.md, doesn't exist), `scripts/*.sh` (referenced in parallel-worktree.md, doesn't exist), `src/` (referenced twice by techdebt, doesn't exist), the `always_read` frontmatter claimed by docs/INDEX.md (0 agents have it).
**Blocking fix**: the new CLAUDE.md drops the dead references; the maintenance protocol (harness-maintenance.md) mandates "reference = verify": confirm any path exists before writing it down; log discovered dead references in ERRORS.md. The remaining dead-reference list is in the LETTER-TO-FUTURE-SESSIONS.md handoff checklist.

### 3. Two parallel pre-work processes with no defined precedence: plan-first.md (Plan Mode) vs ExecPlan (PLANS.md) [已修 fixed]
Two "plan before acting" mechanisms coexisted with no defined relationship; a weak model would either do both (duplicated labor) or neither (each assumed the other covered it).
**Blocking fix**: the new CLAUDE.md defines a single decision tree: cross-module / API / refactor → ExecPlan (heavyweight, version-controlled, needs human approval); other non-trivial tasks → Plan Mode (lightweight, in-conversation); single-file < 20-line changes → do directly.

## III. Top 3 error sources (tool/hook/skill invocation)

### 1. All 4 hooks (+1 shared lib `_lib.py`) had never executed: double failure [已修 fixed, verified by live test]
(a) Files lacked execute permission (`-rw-r--r--`) and settings.json invoked `.py` directly → Permission denied on every trigger;
(b) even with (a) fixed, the guard tried to block with `exit 1` — in the Claude Code hook protocol **only exit 2 blocks; exit 1 is a warning and the command runs anyway**.
In other words, the "enforce mode interception" claimed by CLAUDE.md had been a paper defense since deployment.
**Fix**: `chmod +x` all hooks; two `return 1` → `return 2` in the guard (backup at pre-tool-use-guard.py.bak). Live-tested: block scenarios exit 2 with reason on stderr; normal commands exit 0.
**Lesson (now a rule)**: every hook must be black-box tested once after deployment, covering both a block and a pass scenario — written into harness-maintenance.md.

### 2. stop-retro-logger dedup broken, continuously polluting ERRORS.md [未修 not fixed → handed off]
The dedup hash included the timestamp → nothing ever deduplicates → ERRORS.md was flooded with 7 duplicate PR_RETRO noise entries. Once the lessons file is diluted by noise, weak models stop trusting it and stop reading it — the whole "mistake → lesson → rule" pipeline dies.
**Blocking fix**: fix `_hash` to drop the timestamp field (stop-retro-logger.py, exact line numbers in the handoff checklist); purge existing duplicate entries from ERRORS.md.

### 3. Agent tool permissions contradict duties + skill triggering broken [未修 not fixed → handed off]
- pm and security-reviewer have no Bash, yet review-protocol.md requires them to run `git branch --show-current`; tech-lead is read-only (Read/Grep/Glob), yet execplan-lifecycle.md:82 assigns it to "implement, commit" → the agent discovers mid-run it lacks tools, then reports failure or takes wild detours
- Some SKILL.md files (e.g. skill-creator) lack YAML frontmatter → may never trigger at all
**Blocking fix**: re-audit all 14 agent frontmatters on the principle "duties determine tools"; every action a SOP demands of an agent must be backed by a corresponding tool. The batch fix suits dispatching Sonnet against a checklist.

## IV. Harness capability limits (honesty clause)

Decomposition, isolated verification, and multi-answer adjudication can push a weak model's **execution quality** toward that of a stronger model; the following three categories **cannot be compensated** — take the designated exit (details in `.claude/rules/judgment-rubrics.md` §6):

1. **Taste and aesthetic decisions** (whether a UI looks good, copywriting tone): the weak model produces 2–3 candidates + trade-offs for a human to choose; it does not decide on its own.
2. **Ambiguous business judgment** (is it worth doing, what do users want): list verifiable hypotheses and state plainly that a human decision is required.
3. **Long-chain reasoning without ground truth** (conclusions unverifiable by tests / live runs / documents): mark confidence level, escalate the model or seek a second opinion; if it can't be found, write "unverified" — do not fabricate.

Additionally, this diagnosis has its own limits: "unverified" items include the line-by-line content of commands/last-word.md and the 5 uiux/ files, and the actual behavior of the agy (Gemini) side — none were live-tested.

## Appendix: physical fixes completed this session

| Item | Action | Verification |
|------|------|------|
| hooks lacked execute permission | `chmod +x .claude/hooks/*.py` | live-tested guard is executable |
| guard exit code | `return 1` → `return 2` ×2 places + docstring | block→exit 2 / pass→exit 0 live-tested |
| backups | pre-tool-use-guard.py.bak, CLAUDE.md.bak | exist |
