# F. Harness Maintenance Protocol

> Audience: a long-running weak model. Defines how to **safely** update the harness's own files.
> Principle: lessons can be appended anytime; rules should be changed cautiously; defenses (hooks/invariants) require asking a human before touching.
> 人類讀者:這份是給 AI 看的安全改動流程,你不需要照著做;想了解 harness 怎麼分級保護的白話說明,目前(尚待撰寫,見 docs/research/2026-07-25-non-technical-accessibility.md Tier C)。

## 1. File Permission Tiers

| Tier | Scope | Rule |
|------|------|------|
| **Green: free to edit** | `docs/learnings/ERRORS.md` (append only), `docs/harness/LETTER-TO-FUTURE-SESSIONS.md` **only the §3 handoff-checklist entries (add/remove)** (other sections are Yellow tier), `state/`, your own ExecPlan under `docs/plans/active/`, `SESSION-HANDOFF.md` | Edit directly, following the §3 format |
| **Yellow: backup before edit + verify after** | `agent_docs/*.md`, `.claude/templates/`, `.claude/agents/*.md`, `.claude/skills/`, `docs/INDEX.md`, README | First `cp X X.bak` → edit → dispatch a fresh-context agent to read-back verify (template in delegation-templates.md §6) |
| **Red: must ask the user before touching** | `CLAUDE.md`, `.claude/rules/*.md`, `.claude/protocols/*.md`, `.claude/hooks/*.py`, `.claude/settings.json`, `docs/architecture/invariants.md` | Propose a diff with rationale, get agreement before editing; hook edits require a §4 smoke test |

- When in doubt about which tier applies, lean toward the stricter one. Deleting any file is always treated as Red tier.
- Red-tier exception: a modification explicitly instructed by the user in conversation is treated as already agreed, but still requires backup and verification.

## 2. Why the Tiering (so you can make boundary judgments yourself)

- Green tier is **factual record-keeping**: a mistake here is at worst noise that can be cleaned up later.
- Yellow tier is **behavioral guidance**: a mistake here causes future agents to act incorrectly, but the blast radius is bounded and reversible.
- Red tier is **always-on rules and physical safeguards**: auto-loaded or auto-executed every session; a mistake here systemically pollutes all subsequent work, and a weak model may not even notice.

## 3. Writing Back Lessons Learned (single write point: `docs/learnings/ERRORS.md`)

**When to write**: the same error occurs a 2nd time, or a single error wasted more than 10 minutes, or documentation is found to not match reality.

**Format** (append to the file-end Pending Review section):

```markdown
### [YYYY-MM-DD] [One-sentence title]
- Context: what task you were doing when this happened
- Error: what actually happened (include file:line or key error-message lines)
- Lesson: how to avoid it next time (one actionable instruction or check)
- Suggested destination: stay in ERRORS / promote to invariants / edit some file (path)
```

**Deduplication**: before appending, search ERRORS.md for an existing entry on the same topic; if found → add a line `Recurred: YYYY-MM-DD` to the existing entry rather than opening a new one. An entry that recurs 2+ times is a promotion candidate.

**Three-stage promotion pipeline** (from real-world Menu-Android experience):
1. Model appends to Pending Review (automatic/ad hoc)
2. Human weekly review: promote to a formal category or delete
3. Anything mechanizable (expressible as a regex/check) → propose adding it to `invariants.md` and a guard hook (Red tier, requires agreement)

When clearing Pending entries, there's no need to keep hash comments (`<!-- harvest:HASH -->`) — hashes for entries already processed are tracked in the `state/retro-hashes.jsonl` ledger and won't regenerate.

## 4. Safe Change Procedure

**Fixed workflow for editing any Yellow/Red tier file**:
1. Ensure a restore point exists (either): (a) the file is already committed and the working tree is clean → git itself is the backup, no `.bak` needed; (b) otherwise `cp file file.bak` (same directory; if `.bak` already exists, use `file.bak2` — don't overwrite an existing backup). `*.bak` is already in .gitignore and can be deleted once verification passes
2. Make the change
3. Verify:
   - Documents → fresh-context read-back (acceptance criteria must include at minimum: all referenced paths exist, no unintended leftover `{{placeholders}}`, no contradiction with the canonical hierarchy)
   - Hooks → **smoke test**, both block and pass scenarios must be tested (lesson source: a guard once double-failed silently, see DIAGNOSIS.md §3.1). Run from the **repo root** (`h` is a relative path):
     ```bash
     # Example: testing pre-tool-use-guard with a branch-independent static pattern (expected result is the same on any branch)
     python3 -c "import json,subprocess; h='.claude/hooks/pre-tool-use-guard.py'; \
     print(subprocess.run([h],input=json.dumps({'tool_name':'Bash','tool_input':{'command':'ca'+'t .e'+'nv'}}),capture_output=True,text=True).returncode)"
     # Expected: 2 (block, READ_DOTENV). Swap the command for 'ls -la' and expect: 0 (pass). Remember chmod +x on new hook files.
     # Note: don't use git commit as the test case — it only blocks on master/main and returns 0 on a feat branch, which would make you misdiagnose the hook as broken
     ```
4. Verification fails → restore from backup, log the failure to ERRORS.md

**Dump the real payload before writing hook logic.** Field names in the official docs have been wrong three times now (`SubagentStop`'s `transcript_path` is actually `agent_transcript_path`; `SessionStart` carries no `model` field at all despite the docs saying it may; `InstructionsLoaded`'s fields are named nothing like the documentation). A 20-line hook that writes `read_stdin_json()` to a file, plus one nested `claude -p` to trigger it, settles the question in minutes — far cheaper than discovering it after the logic is written.

**Declare a hook's dependency on a document's wording.** If a hook decides something by testing for a literal string inside a markdown file, add a `# COUPLING: <path> -- <what the needle means>` comment beside it, so whoever edits that document can find the dependency with `grep -rn "COUPLING:" .claude/hooks/`. `scripts/check-hook-doc-coupling.py` fails on an undeclared one. This exists because CI once proposed rewording the exact CLAUDE.md line an activation check keys off — which would have gone green while silently switching the check off.

**A content-scanning defense needs its exemptions designed alongside its rule.** Four times now a scanner has fired on content that merely *quoted* what it guards. When you add a pattern, ask immediately: what happens when this repo's own documentation describes this pattern? `pre-tool-use-guard.py` answers it by not scanning heredoc bodies bound for a data sink (`cat >`, `tee`, `git commit -F -`, `gh --body-file -`) while never exempting a body an interpreter will run. Exemptions follow security.md's allowlist rule, and each one ships with negative tests proving a real violation still blocks.

**Reference implies verification**: before writing any path/tool name/skill name into a harness file, confirm it exists (`ls` or Glob). If you find an existing dead reference: fix it directly for Green/Yellow tier; for Red tier, log it to ERRORS.md and wait for human review.

## 5. Trim Triggers (preventing unbounded document growth)

| File | Trigger Line | Action |
|------|--------|------|
| ERRORS.md | > 300 lines or Pending Review > 20 entries | Prompt the user for a weekly review; merge same-category entries into one abstracted lesson (keep the original dated list) |
| CLAUDE.md | > 100 lines | Move the excess to a referenced file, leave a one-line route in CLAUDE.md |
| `.claude/rules/*` total | All rules combined > 600 lines | Propose demoting the least-used rule to non-always-on (move to agent_docs/ or drop `always: true`); Red tier requires agreement |
| LETTER-TO-FUTURE-SESSIONS.md handoff checklist | Completed items | Remove completed items; don't leave "done" tombstones |

**The trimming method** is conceptual abstraction: 5 similar concrete lessons → 1 rule + 1 representative example; "delete the old ones" must never substitute for "merge same-category entries."

## 6. Quality Gates for Adding/Modifying an Agent, Skill, or Standing Rule

- **Skill** → go through the full `.claude/skills/skill-creator-plus/SKILL.md` process (overlap check, bidirectional trigger tests, baseline-comparison eval are all in there; not repeated here).
- **Agent** (`.claude/agents/*.md`) → three gates, with evidence attached to that commit/PR description:
  1. **Pre-check for duplication**: before starting, cross-reference `agent_docs/AI-TEAM-REGISTRY.md` and `.claude/agents/` — if responsibilities overlap, extend the existing file rather than creating a new one (prevents "same role, different name" pile-up, i.e., pre-empting the "canon re-fragmentation" decay pattern)
  2. **Bidirectional trigger test**: list 8-10 "should trigger" and 8-10 "should not trigger" scenarios and check each against the description/trigger words; conflicting trigger words with an existing agent is a FAIL — add a disambiguating qualifier and retest
  3. **Baseline comparison** (when changing behavioral guidance): run a representative task on the pre-change version first and record the failure mode, then rerun the same task post-change and compare item by item for improvement; any observed rationalization phrases go into judgment-rubrics §7 as candidates (via the ERRORS.md pipeline, not a direct edit to a Red-tier file)
- **Standing Rule** (`.claude/rules/*` — always-on, loaded into every session, so every line carries a permanent context cost) → three gates when adding a new rule or expanding an existing one, evidence attached to that commit/PR description (human-approved 2026-07-23; origin: F-001/O15 found that adding an always-on rule previously required zero evidence and had no exit mechanism):
  1. **Demand evidence**: cite ≥2 ERRORS.md entries or a harness-eval gap number that the rule addresses — "seems useful" with no recurring-failure evidence is a FAIL
  2. **Telemetry marker**: declare the rule's inline marker (syntax: handoff-protocol.md "Inline Auxiliary Markers", e.g. `[RULE_FIRED: <rule-name>|<detail>]`) and have the rule emit it wherever it fires, so hit-rate is measurable from `state/rule-events.jsonl` (live examples: clarify-first §1 `[RULE_FIRED:]`, model-dispatch §4 `[ESCALATION:]`)
  3. **90-day review date**: write the date (creation + 90 days) into the rule's header blockquote; at review, a rule with zero hits in `state/rule-events.jsonl` becomes a §5 demotion candidate (`.claude/rules/*` row: demote to non-always-on or move to `agent_docs/`)

## 7. The Five-Dimension Harness Checkup (framework for `/harness-eval` and quarterly audits)

All five subsystems must be present for the harness to be considered complete (source: walkinglabs/learn-harness-engineering; experiments show Feedback is the single biggest lever for success rate):

| Dimension | Check Question | This Project's Mapping |
|------|---------|-----------|
| Instructions | CLAUDE.md ≤100 lines, no dead references, no contradiction in the canon | CLAUDE.md + `.claude/rules/` |
| Tools | Agent permissions are minimal-but-sufficient, not disabling shell out of caution | agents frontmatter `tools` |
| Environment | Environment is self-describing and reproducible: init script runs, dependencies have a lockfile | `.claude/templates/init.sh.template` filled-in version |
| State | Long-running tasks have a progress file, session start/end read/write handoff | ExecPlan + SESSION-HANDOFF + `state/` |
| Feedback | Executable verification commands are filled in and actually get run | CLAUDE.md Quick Commands + verification-not-self-certified |

Locate weaknesses via **failure attribution** (was this failure due to unclear task, insufficient context, an unreproducible environment, missing verification, or corrupted state?) — vote for whichever dimension recurs most often; don't add rules by gut feel.

## 8. This Protocol Itself

This file is Red tier. If you find an error or a poor fit in this protocol: log it to ERRORS.md and raise it in your report — do not modify it yourself.
