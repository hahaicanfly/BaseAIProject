---
name: pr-retro
description: After every PR merge, automatically extracts lessons and writes them to ERRORS.md Pending Review, driving continuous improvement of skill docs; triggers after a PR is merged or when the user mentions "複盤" "retro".
---

# Skill: pr-retro

> **Purpose**: After every PR merge, automatically extract lessons and write them into ERRORS.md Pending Review, driving SkillOpt-style continuous improvement of skill documents.
> **Trigger**: `/pr-retro [PR description / review log / diff summary]` (or auto-invoked by stop-retro-logger)
> **Role**: The "minibatch reflection + rejected-edit buffer writer" from the SkillOpt paper

---

## Core Concept: A PR Is the Best Training Signal

Every PR is a complete rollout:
- **A successful PR** = positive example (know what works)
- **A problem caught by review** = negative example (know what not to do)
- **A PR that needed multiple revisions to pass** = high-signal training data

pr-retro's job: turn these signals into candidate lessons for ERRORS.md.

---

## Execution Steps

### Step 1: Collect PR Context

Requires any of the following inputs:
- git diff (`git diff main...HEAD` or PR diff)
- PR review comments (if code review output exists)
- The Cascade report from `pr-review-cycle-mob`
- `[VERIFY_FAILED:*]` entries from ExecPlan §6 Progress Log

If no input is available, read the most recent N entries from `state/hook-events.jsonl`.

### Step 2: Analyze Failure Patterns

For every entry Flagged / Blocked / VERIFY_FAILED, analyze:

```
Problem description: [what happened]
Root cause: [why it happened]
Triggered INV: [which INV-* it maps to, or a candidate new one]
Fix applied: [how it was resolved]
Prevention: [how to avoid it next time]
```

### Step 3: Classify

**Case A: Matches an existing ERRORS.md lesson (recurrence)**
- Append to the matching lesson in ERRORS.md: `  ↩ [date] recurred in [PR slug]`
- Consider whether to promote this lesson to an INV-* rule

**Case B: New pattern (unseen failure)**
- Produce a candidate lesson:
  ```
  - [YYYY-MM-DD] [category] problem description → correct approach
  ```
- Append to `## Pending Review` in `docs/learnings/ERRORS.md`

**Case C: Requires a skill doc update**
- If the root cause is insufficient or incorrect guidance in an agent/skill
- Produce a concrete skill doc edit suggestion:
  ```
  [SKILL_EDIT_CANDIDATE]
  Target file: .claude/agents/xxx.md
  Action: replace
  Location: [describe which section of the file]
  Original text: [excerpt]
  Suggested replacement: [revised version]
  Reason: [why]
  ```
- Write into ERRORS.md Pending Review (human decides during weekly review whether to apply)

**Case D: Requires a new INV-* rule**
- If the problem can be expressed as a grep pattern for mechanical verification
- Produce a candidate INV:
  ```
  INV-[NS]-[NNN]  [one-sentence rule]
    CHECK    [grep command]
    HOOK     post-edit-lint.py
    SOURCE   [origin date]
  ```
- Write into ERRORS.md Pending Review; human promotes to invariants.md after weekly review

### Step 4: Produce the Retro Report

```
## PR Retro Report — [PR slug / date]

### PR Stats
- Files changed: N
- Review rounds: N
- L1 Flags: N, L2 Blocks: N, L3 Criticals: N

### New Candidate Lessons (Case B)
[list]

### Recurring Lessons (Case A)
[list]

### Skill Doc Edit Candidates (Case C)
[list SKILL_EDIT_CANDIDATE]

### New INV-* Candidates (Case D)
[list]

### PR Quality Score (0-10)
[simple calculation based on review rounds and flag count]
```

### Step 5: Auto-Update Tracking

- Append to `## Pending Review` in `docs/learnings/ERRORS.md`: `## [date] retro | [PR slug]`
- If Case B/C/D produced content → remind the human at the end of the session: "N pending items in ERRORS.md need weekly review"

---

## Mapping to SkillOpt

| pr-retro action | SkillOpt component |
|--------------|---------------|
| Collect Flag/Block | rollout evidence |
| Case B → Pending Review | rejected-edit buffer |
| Human weekly review promote | epoch-wise slow update |
| Case C → skill edit | bounded text edit (human-approved) |
| Case D → INV candidate | validation gate reinforcement |

---

## Relationship to stop-retro-logger

`stop-retro-logger.py` only appends a plain-text reminder at session end and does **not** run the Case A/B/C/D classification analysis. Classification analysis only happens when this skill is manually triggered (`/pr-retro`).

See the `# PR_RETRO_HOOK` marker in `.claude/hooks/stop-retro-logger.py`.
