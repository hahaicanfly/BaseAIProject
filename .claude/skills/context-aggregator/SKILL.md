---
name: context-aggregator
description: Aggregates multi-source information (MCP memory, git history, local files) into a structured summary for session handoff and work continuity; triggers when the user wants to aggregate context, write a handoff report, or mentions "聚合" "摘要" "交接".
---

# Skill: context-aggregator

> **Purpose**: When picking up someone else's work, quickly aggregate all necessary context for a seamless cold-start handoff.
> **Trigger**: `/context`

## Usage

```
/context [scope: session | recent | full]
```

- `session` — summary of the current session's work
- `recent` — summary of activity over the last 3 days (default)
- `full` — full project context

## Information Sources

### 1. Claude Code Memory
- Read the project memory index (`~/.claude/projects/<project>/memory/MEMORY.md` or equivalent path)
- If the project has an MCP memory server configured, query it too (check `.claude/settings.json` for `mcpServers`)
- Extract key decisions and findings; identify unfinished tasks

### 2. Git History
- Recent commit log (`git log --oneline -10`)
- Current branch state (`git branch --show-current`)
- Uncommitted changes (`git status`)
- List of active branches (`git worktree list` / `git branch -a`)

### 3. Harness State
- Look for in_progress tasks in `state/feature-list.json` (if the file doesn't exist, no active harness state — skip)
- The corresponding full ExecPlan (focus: last line of §6 Progress Log + §9 Handoff Manifest)
- Relevant INV-ids in `docs/architecture/invariants.md`
- TODO/FIXME marker counts, failing tests (if any), unresolved lint warnings

## Aggregation Flow

### Step 1: Collect
- Gather raw information from each source, filter noise, keep valuable data

### Step 2: Classify
- Group by topic (feature development, bug fixes, infrastructure)
- Tag status (in progress, completed, pending)

### Step 3: Synthesize
- Produce a structured summary, flag items needing attention
- Suggest next actions based on the current `[HANDOFF:*]` marker

## Output Format

```markdown
# Context Aggregation

## Active Tasks
- F-NNN: [title] | status: in_progress | marker: [HANDOFF: xxx]

## Recent Commits
[git log output]

## Pending Open Questions
[pulled from ExecPlan §8]

## Next Action
Based on current state marker: [HANDOFF: xxx]
→ Enter role: xxx
→ Start from: §4 step N
```

## References

- `.claude/protocols/execplan-lifecycle.md` — cross-session handoff SOP
- `.claude/protocols/handoff-protocol.md` — the three marker types
- `state/SCHEMA.md`
- `.claude/settings.json` (check for MCP memory config)

## Verification Checklist

- **Output form**: a handoff document (markdown) with four sections — done / pending / blocked / next-step suggestions.
- **ExecPlan integration**: write into the corresponding `docs/plans/active/F-NNN-*.md` §9 Handoff Manifest.
- **State integration**: trigger `pre-compact-snapshot.py` (manual PreCompact) to write `state/session-handoffs/<ts>.json` when needed.
- **Distinction from `/last-word`**: context-aggregator proactively aggregates multi-source context; `/last-word` is the structured dispatch for session wrap-up — the two are complementary, not overlapping.
- **Handoff marker**: `[HANDOFF: next-session]` or `[HANDOFF: <specific-agent>]`.
