Proactive context wrap-up workflow. Before context usage approaches its limit, proactively perform a high-quality archival pass to ensure the next session can pick up work seamlessly.

Trigger points: context usage around 40%, the user is about to leave the session, or a major task phase has just completed.
**Hard gate (CLAUDE.md MUST: PHASE HANDOFF GATE)**: before moving to the next task after a phase completes (feature / Phase N / Mx), if context usage is >50%, you **must** run this command first to produce `SESSION-HANDOFF.md`, then `/clear`, then read that file to resume in a new session.

> **Phase D upgrade**: this command is now aligned with the harness architecture. Lessons are no longer written into CLAUDE.md — they are routed to `docs/learnings/ERRORS.md`, `docs/architecture/invariants.md`, and the active ExecPlan. Auto-memory may still hold **short-term session state**, but **long-term context lives in the ExecPlan**.

---

Execute the following 8 steps in order, briefly reporting after each one. **No skipping steps** — the auditability of a harness session wrap-up matters more than speed.

## Step 1: Review the conversation + identify markers

Review the entire session's conversation and extract four categories of information:

| Category | Example | Downstream destination |
|------|---------|---------|
| **Blocker / lesson** | "spent a whole morning fixing this before finding the bug" | `docs/learnings/ERRORS.md` or `invariants.md` |
| **Working approach / pattern** | "extracting a base fake solved all the stub issues at once" | same as above (tag as success pattern) |
| **Unfinished work** | "F-NNN ExecPlan §4 step 3 still not verified" | corresponding ExecPlan §6 + §9 |
| **In-session proactive markers** | `[VERIFY_FAILED:*]` / `[HUMAN_ATTENTION_REQUIRED:*]` records | wait for `stop-retro-logger.py` to auto-harvest (or supplement manually) |

## Step 2: Route lessons to the correct archive (replaces the old pattern of accumulating lessons in CLAUDE.md)

Route each Step 1 finding to the correct location per this table:

| Judgment condition | Archive location | Action |
|---------|---------|------|
| Mechanically verifiable (a grep / lint pattern can be written) | `docs/architecture/invariants.md` | add an INV-`<NS>`-`<NNN>` entry, tagged CHECK / HOOK / SOURCE (invariants.md is red-tier, see `harness-maintenance.md` §1 — confirm with the user before writing) |
| Not mechanically verifiable but general (design-level) | `docs/learnings/ERRORS.md` `## Pending Review` | wrap in `<!-- harvest:HASH -->`, awaiting promotion next week |
| Related to a **specific feature's design decision** | corresponding `docs/plans/active/F-NNN.md` §7 Decision Log | one-line summary, escalate to an ADR if warranted |
| Already tracked in a git commit / GitHub issue | **don't store** | avoid duplicate noise |
| One-off session state (e.g. "F-NNN reached step 3") | Auto-memory **or** ExecPlan §6 Progress Log | ExecPlan takes priority; memory only fills gaps where no ExecPlan exists |

**Actually perform the archiving** (edit `docs/learnings/ERRORS.md`, `docs/architecture/invariants.md`, the active ExecPlan section — **do not touch CLAUDE.md**).

> CLAUDE.md is "the map" (≤150 lines) — it is no longer where lessons pile up.

## Step 3: Sync ExecPlan progress

For every `docs/plans/active/F-NNN-*.md` touched during this session:

1. Append one summary line to §6 Progress Log (including timestamp + agent + one-sentence summary)
2. Update `Current state marker` in §9 Handoff Manifest:
   - fully complete → `[HANDOFF: code-reviewer]` / `[HANDOFF: human-pr-review]` / `[HANDOFF: done]`
   - an unfixed invariant violation exists → `[VERIFY_FAILED: <INV-id>]`
   - blocked on an external dependency → `[HUMAN_ATTENTION_REQUIRED: <reason>]`
3. If status changed, sync `state/feature-list.json` (if that file exists)

If the entire session falls outside ExecPlan scope (pure exploration / pure documentation / a hot-fix touching <3 files), skip this step.

## Step 4: Write the handoff prompt → into `SESSION-HANDOFF.md` (for the next session)

If work remains unfinished at the end of the session, **use the Write tool to write the following handoff prompt into `SESSION-HANDOFF.md` at the project root** (overwrite any prior content — this file is a single session's transient handoff zone, not a cumulative log). This is the concrete artifact of the "phase handoff gate" (CLAUDE.md MUST: PHASE HANDOFF GATE) — after the user runs `/clear`, they read this file directly to resume in a new session.

`SESSION-HANDOFF.md` content template:

```
# SESSION-HANDOFF — <YYYY-MM-DD HH:MM>

> Produced by /last-word. After `/clear`, read this file to resume; once resumption is complete this file may be deleted or will be overwritten by the next /last-word.

## Handoff prompt (paste directly to resume)

I'm working on [F-NNN — feature name] (ExecPlan: docs/plans/active/F-NNN-<slug>.md).

**Completed (latest entry in §6 Progress Log):**
- [...]

**Remaining (unchecked steps in §4):**
- [...]

**Current marker:** [HANDOFF: <next>] or [VERIFY_FAILED: <INV-id>]

**Pickup SOP:**
1. Read ExecPlan §3 Constraints + §9 Handoff Manifest
2. Confirm the git branch (should be `feat/<slug>`)
3. Start from §4 step <N>

**Related info:**
- Branch: `feat/<slug>` (latest commit: <hash>)
- Linked PR: #<NNN> or (no PR yet)
- Related invariants: INV-... / INV-...

## This session's archive summary
- invariants.md additions: INV-... × N
- ERRORS.md Pending Review additions: N entries
- ExecPlan updates: F-NNN (§6 + §9)
```

After writing the file, report the `SESSION-HANDOFF.md` path in the conversation. If all work is complete, skip this step, **do not generate** `SESSION-HANDOFF.md`, and instead output "nothing pending."

## Step 5: GitHub issue / PR cleanup

- Check the GitHub issues / PRs touched during this session
- Confirm issue status (open / closed) matches actual code progress
- If any issue is done but not yet closed, remind the user
- If an ExecPlan has been merged → move it from `docs/plans/active/` to `docs/plans/completed/` and update `state/feature-list.json`

## Step 6: Clean up stale content

Scan the following three locations:

| File | Cleanup focus |
|------|--------|
| `docs/learnings/ERRORS.md` `## Pending Review` section | promote validated, usable lessons to `## Active Lessons`; delete noise |
| `docs/plans/active/` | any ExecPlan stalled >4 weeks gets marked BLOCKED or moved to completed/ + a Rejection Reason added |
| Auto-memory | remove transient state already recorded in an ExecPlan / already tracked by git |
| Claude Code native memory (project memory directory) | content already promoted into ERRORS.md/invariants should be deleted from the memory file, leaving only a pointer |

**Forbidden**: cleaning up `docs/architecture/invariants.md` — once an INV is established, it stays.
**Forbidden**: touching CLAUDE.md — that file is already a compressed map, governed by the ADR process.
Conservative principle: if unsure whether something is stale, leave it.

## Step 7: Check for uncommitted changes + branch

Run:
```bash
git status
git branch --show-current
```

Confirm:
- no staged-but-uncommitted changes
- no important unstaged changes have been forgotten
- current branch is **not** master/main (INV-GIT-001 / INV-GIT-002)
- if uncommitted changes exist, **remind the user to commit before `/clear`**

## Step 8: Wrap-up report + safe `/clear` confirmation

After completing all steps, report to the user:

```
✓ Lessons archived:
  - invariants.md additions: INV-... × N
  - ERRORS.md Pending Review additions: N entries
  - ExecPlan updates: F-NNN (§6 + §9)

✓ Starter Prompt: [output / not needed]

✓ Git status:
  - Branch: feat/<slug>
  - Uncommitted: <file count> (needs commit / clean)

→ Safe to run /clear: [YES / NO (please resolve ... first)]
```

Close out with a harness marker:
- no issues throughout → `[HANDOFF: next-session]`
- unresolved issues remain → `[HUMAN_ATTENTION_REQUIRED: <reason>]`

---

## Relationship to stop-retro-logger.py

`/last-word` is **proactive, manual wrap-up**; `stop-retro-logger.py` (the Phase D sentinel) is **passive, automatic harvesting**. The two are **complementary, not redundant**:

| Observation | Handled by `/last-word` | Handled by `stop-retro-logger.py` |
|------|-------------------|------------------------------|
| `[VERIFY_FAILED:*]` appears in the conversation | structured classification + escalate to invariant if warranted | appended verbatim to Pending Review automatically |
| A lesson is evident in conversation but has no marker | identified and archived proactively by the agent | not handled (no marker to catch it) |
| ExecPlan §6 / §9 updates | must be done | not done |
| Auto-memory cleanup | evaluated and performed | not done |

> **Recommended order of use**: run `/last-word` first (structured wrap-up), then let the session end naturally (triggering stop-retro-logger's automatic harvest of any markers that slipped through).

---

## References

- `.claude/protocols/handoff-protocol.md` — spec for the three marker types
- `.claude/protocols/execplan-lifecycle.md` — the 10 ExecPlan phases
- `docs/plans/PLANS.md` — the 9-section ExecPlan spec
- `docs/learnings/ERRORS.md` — Pending Review section spec
- `docs/architecture/invariants.md` — INV-* entry format

### Division of labor: automatic snapshot vs. this command

- `pre-compact-snapshot.py` → `state/session-handoffs/`: **automatic snapshot**, triggered on PreCompact, machine-readable, requires no human involvement.
- `/last-word` → `SESSION-HANDOFF.md`: **manual handoff**, triggered proactively by a human, contains a paste-ready resume prompt for the next session's human/agent to read.
- The two are complementary: the automatic snapshot is the safety net (compaction can happen at any time), while the manual handoff is the only one with a structured resume prompt.
