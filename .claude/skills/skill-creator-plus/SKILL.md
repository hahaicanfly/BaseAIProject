---
name: skill-creator-plus
description: Guides the complete skill-creation workflow — intent capture, overlap check, drafting, mechanical validation, trigger testing, through registry registration — including the eval iteration method. Triggers when the user wants to create a new skill, package a repeated workflow, or rewrite/optimize an existing skill's trigger accuracy, or mentions "做一個 skill", "skill 沒被觸發", "封裝這個流程". Supersedes the base skill-creator.
---

# Skill: skill-creator-plus

> Methodology base: Anthropic's official skill-creator (github.com/anthropics/skills, 2026-07 version) + this project's harness institution.
> The detailed eval iteration process lives in `references/eval-loop.md` (read on demand, not upfront).

## Step 0: Decide whether this should even be a skill

A skill is "trigger-loaded process knowledge." **Don't** make a skill for the following — use the matching mechanism instead:

| Situation | Correct mechanism | Why |
|------|---------|--------|
| A rule every session must follow | `.claude/rules/` (always-loaded) | A skill only loads when triggered; always-on rules can't gamble on triggering |
| A role that needs its own isolated context to run | `.claude/agents/` | A skill carries no context or tool allowlist of its own |
| Just a fixed text snippet | `.claude/templates/` | Turning content with no execution steps into a skill is wasted overhead |
| The operation has occurred < 3 times in a session | Don't package it yet | Official principle: skills get invoked millions of times — don't overfit to a one-off need |

## Step 1: Intent capture (4 questions, ask before you build)

1. What does this skill **do**? (one sentence)
2. **When** should it trigger? (list the actual phrases a user would say, including colloquial forms and typos)
3. What does the **output** look like? (format, where it lands)
4. Is the output **objectively verifiable**? (yes → build an eval later; subjective output like copy style → skip quantitative eval, use manual comparison instead)

## Step 2: Overlap and trigger-exclusivity check

Before writing anything, run:

```bash
grep -l "key trigger word" .claude/skills/*/SKILL.md   # who already claims these words
```

- If trigger words overlap with an existing skill, decide (criterion): if the new need is a subset or variant of an existing skill's purpose → **extend the existing skill**, don't open a new file; if it's genuinely a different purpose that merely shares vocabulary → add **mutual-exclusion qualifiers** to both descriptions (example: code-review "standard single-PR review" vs multi-agent-review "high-risk three-expert parallel review").
- Lesson learned: this project once had three review skills fighting over "review PR" trigger words, causing random misrouting — resolved in the 2026-07-04 third round using mutual-exclusion qualifiers; the same pathology (one fact scattered across multiple files → random source-of-truth selection) is logged under the single-canonical-source entry in ERRORS.md.

## Step 3: Structure and drafting

**Directory structure** (omit layers you don't need):

```
.claude/skills/<name>/
├── SKILL.md          # required. body ideally <150 lines, hard cap 500 lines
├── references/       # long content pulled out, loaded on demand (files >300 lines need a table of contents)
├── scripts/           # deterministic operations written as executable scripts (run without loading — zero context cost)
└── assets/             # templates/fonts/icons used for output
```

**Progressive disclosure, three layers** (official numbers): frontmatter is always in context (~100 words) → SKILL.md body loads on trigger → references and scripts load on demand. So: when-to-use information goes **entirely** in the description — none of it in the body.

**Frontmatter hard spec** (validated by `scripts/validate_skill.py`):
- `name`: kebab-case, ≤64 chars, **must equal the directory name** (mismatch means it will never trigger — this project has been bitten by this)
- `description`: ≤1024 chars, angle brackets `<>` forbidden; formula below
- Allowed fields only: name, description, license, allowed-tools, metadata, compatibility

**Description formula** (Claude tends to undertrigger, so write it pushy — the observable criterion for "pushy enough": every should-trigger test sentence in Step 4 hits):

```
[what it does, including a list of key capabilities]; triggers when [specific situation 1], [situation 2], or the user says "[verbatim trigger phrase × 3-5]". [mutual-exclusion qualifier vs. adjacent skills].
```

**Body writing rules**:
- Use imperative sentences that give direct instructions; write a draft first, then reread and rewrite it through the eyes of "a weak model reading this for the first time"
- Explain **why**, don't stack capitalized MUSTs — catching yourself writing ALWAYS/NEVER in all-caps is a signal the content lacks a stated reason (an official yellow flag)
- Give Input/Output paired examples rather than three paragraphs of abstract description
- Cited = verified: for every path, tool name, or agent name written in the body, `ls` to confirm it exists before writing it down (this project once had a protocol file with 5 references that were entirely fabricated)
- Don't duplicate canonical content: model dispatch belongs to model-dispatch.md, review format belongs to review-protocol.md — a skill may only reference these, never copy a duplicate

## Step 4: Mechanical validation + trigger testing (don't self-verify)

1. Run `python3 .claude/skills/skill-creator-plus/scripts/validate_skill.py .claude/skills/<name>`; proceed only once all checks pass.
2. Dispatch a **fresh-context subagent** (per `.claude/templates/delegation-templates.md` §6), giving it only "phrases a real user would say" — **8-10 items in each direction**: should-trigger (including colloquial forms and typo variants) + should-not (trigger phrases from adjacent skills, or sentences that look similar on the surface but serve a different purpose). Acceptance condition: it reports which skill it would pick and why — it must be correct in both directions to pass. Diagnosing failures: a should-trigger sentence misses → description lacks the verbatim trigger phrase, add it; a should-not sentence falsely triggers → missing a mutual-exclusion qualifier, add one. Retest after fixing.
3. If the output is objectively verifiable: run one minimal eval round — in the same turn, dispatch two subagents in parallel (one given the full skill text, one not) on the same task, and compare outputs. For the detailed method (assertions, near-miss negative cases, stopping conditions) see `references/eval-loop.md`.

## Step 5: Land and register

1. Register in `agent_docs/AI-TEAM-REGISTRY.md` (this file is regenerated from the directory — follow the instructions in its header, do not hand-edit individual cells)
2. Skill files are yellow-tier (`.claude/protocols/harness-maintenance.md` §1): make sure you have a git restore point before modifying an existing skill
3. One feature per commit; append pitfalls hit during creation to `docs/learnings/ERRORS.md`

## Anti-patterns (every one of these is a pitfall this project has actually hit)

- **Unmarked stub**: content isn't implemented yet but has a full description → append "(stub, not yet fully implemented)" to the end of the description
- **name ≠ directory name** → will never trigger
- **description only states what it does, not when to use it** → undertrigger, effectively invisible
- **when-to-use crammed into body** → nobody reads the body before it triggers in the first place
- **fabricated references** (claiming to be referenced by some file, or citing a paper that doesn't exist) → weak models will believe it and propagate the fabrication
- **cleaning up non-self-created files**: eval scratch files may only delete files created in the current round; destructive commands against any other file are always forbidden — the full blacklist is canonical in `.claude/templates/delegation-templates.md`'s general rules (see the 2026-07-04 accidental-deletion incident in ERRORS.md)
