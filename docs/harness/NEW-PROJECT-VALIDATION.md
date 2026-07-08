# New-Project Harness Acceptance Flow (Canary Walkthrough)

> **Role**: after forking this template, use a ~30-minute canary task with no real business value to walk through the harness's key links, proving that "hook/protocol files exist" ≠ "they actually work".
> **Basis**: adapted from a real project's 10-phase harness-migration dogfood log (which uncovered 2 hook bugs along the way). The project's tech-stack details have been stripped; only the reusable acceptance actions remain.
> **Principle**: every step must have an **observable** pass criterion (file contents, command output, exit code); verbal "it probably ran" confirmations are not accepted.

## When to run

After forking the template into a new repo, once `{{BUILD_CMD}}` runs clean, CLAUDE.md placeholders are filled, and `.claude/hooks/*.py` has `QUICK_CHECKS` filled in for the project's tech stack — run this flow once before real development starts. Also re-run the relevant steps after any later hooks/protocols change (yellow/red-tier changes).

## Preflight checks

- [ ] `{{BUILD_CMD}}` runs successfully (the project's own build/lint/test command, replacing this placeholder)
- [ ] `git branch --show-current` confirms you are not on master/main
- [ ] `.claude/hooks/settings.json` (or `.claude/settings.json`) has the hooks you'll use registered

---

## Step 1 — Hooks smoke test

**Action**: following the smoke-test procedure in `.claude/protocols/harness-maintenance.md` §4, run one block case and one pass case against `pre-tool-use-guard.py` (or the project's equivalent enforce hook):

```bash
python3 -c "import json,subprocess; h='.claude/hooks/pre-tool-use-guard.py'; \
print(subprocess.run([h],input=json.dumps({'tool_name':'Bash','tool_input':{'command':'ca'+'t .e'+'nv'}}),capture_output=True,text=True).returncode)"
```

**Pass criteria**:
- block case exits non-zero (per project definition, usually `2`)
- swapping the command for `ls -la` exits `0`
- do not use `git commit` as a test case (it only blocks on master/main and always exits 0 on a feat branch, which would falsely suggest the hook is broken)

---

## Step 2 — Open a feat branch and walk one minimal ExecPlan / Plan Mode

**Action**: branch `feat/canary-<date>` off master; per `docs/plans/PLANS.md` §2, create a minimal ExecPlan `docs/plans/active/F-CANARY-<date>.md` (a single harmless fake change is enough, e.g. adding one comment line), or walk the equivalent flow in Plan Mode instead.

**Pass criteria**:
- the ExecPlan file contains all 9 sections §1 Goal ~ §9 Handoff Manifest (order per `PLANS.md` §2)
- the `Status` field advances through the flow: `todo` → `in_progress` → `done`
- at least 1 commit references the ExecPlan filename or F-id

---

## Step 3 — Dispatch one subagent to verify handoff markers and the reporting contract

**Action**: use the Task/Agent tool to dispatch a sub-agent (any role, e.g. `code-reviewer` or a generic dev agent) to complete Step 2's fake change, requiring its final response to end per `.claude/protocols/handoff-protocol.md`.

**Pass criteria**:
- the **last line** of the sub-agent's final response is one of `[HANDOFF: <target>]` / `[VERIFY_FAILED: <reason>]` / `[HUMAN_ATTENTION_REQUIRED: <reason>]`
- `<target>` is one of the legal values tabled in handoff-protocol.md (not a fabricated role name)
- if no marker at all → treat as a protocol violation and go straight to Step 5 (no need to manufacture another error)

---

## Step 4 — Trigger one code-review skill run

**Action**: run `/code-review` on the diff produced by Steps 2/3 (or manually walk the steps in `.claude/skills/code-review/SKILL.md`).

**Pass criteria**:
- output matches the format defined in SKILL.md: the four sections `Blockers / Warnings / Suggestions / Praise` plus a `Decision`
- likewise ends with a legal `[HANDOFF: ...]` marker
- the review cites at least 1 INV-id from `docs/architecture/invariants.md` (proving the reviewer actually read the constraints rather than commenting generically)

---

## Step 5 — Deliberately make one small mistake to verify the ERRORS.md pipeline

**Action**: deliberately violate one known invariant (e.g. run an operation on master that should be blocked, or write a file you know a hook will flag), and observe whether the error actually gets recorded.

**Pass criteria**:
- `docs/learnings/ERRORS.md` gains a new entry under `## Pending Review`, formatted with the four fields "situation / error / lesson / suggested destination" (per `harness-maintenance.md` §3)
- if the project has a sentinel hook (e.g. a stop-retro-logger equivalent), the corresponding `state/*.jsonl` should also show this event
- manually confirm the new entry is **not** a duplicate of an existing topic; if the topic already exists, instead append `再犯：YYYY-MM-DD` (recurrence: date) to the old entry

---

## Step 6 — Check roster consistency with frontmatter

**Action**: compare the agents/models/tools tabled in `agent_docs/AI-TEAM-REGISTRY.md` against each `.claude/agents/*.md` file's frontmatter (`model` / `tools` fields).

**Pass criteria**:
- every agent's `model` field matches the REGISTRY table, 0 contradictions
- the canon source declared in the REGISTRY header (frontmatter is authoritative) is not overridden in reverse by table contents
- agent count matches the REGISTRY heading count (e.g. "Agents — N")
- on contradiction → follow the file tiering in `harness-maintenance.md`: REGISTRY.md is yellow-tier and may be fixed and regenerated directly; changing frontmatter itself follows that agent file's own tier rules

---

## Summary acceptance table

| # | Link | Criterion (observable) |
|---|------|---------------|
| 1 | Hooks smoke test | block case non-zero, pass case 0 |
| 2 | ExecPlan / Plan Mode | all 9 sections present, Status advanced, matching commit exists |
| 3 | Subagent handoff | ends with one of the three legal markers |
| 4 | code-review skill | four-section output + INV-id citation + legal marker |
| 5 | ERRORS.md pipeline | Pending Review gains a well-formed entry (or jsonl event) |
| 6 | REGISTRY consistency | agent count / model fields vs frontmatter, 0 contradictions |

## Cleanup

After the canary: revert the fake change, or keep it archived in `docs/plans/completed/` as this acceptance run's evidence; the feat branch may be deleted if unneeded (it is not master, not force-retained).

`[HANDOFF: human-approval]`
