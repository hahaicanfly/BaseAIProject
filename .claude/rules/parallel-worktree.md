---
name: parallel-worktree
description: 多 agent 並行開發時的 git worktree 隔離規則
always: true
---

# Parallel Worktree Development Rules

## Overview

When multiple AI agents or sessions work on the same project simultaneously, each MUST use an isolated git worktree to prevent conflicts.

## General Rules

1. **Never modify files in the main project directory** when operating in worktree mode
2. Each task gets a unique `{TASK_ID}` and branch `agent/{TASK_ID}`
3. Never push without a passing build and tests
4. One worktree = one task = one branch = one PR

## Creating a Worktree

### Option A: Claude Code Built-in (Single Session)

Use `EnterWorktree` tool or Agent tool with `isolation: "worktree"`:
```
Agent(
  prompt: "implement feature X",
  isolation: "worktree"
)
```
Claude Code manages the worktree lifecycle automatically.

### Option B: Helper Script (Multi-Session / Manual)

```bash
./scripts/new-agent-worktree.sh <TASK_ID> [BASE_BRANCH]
```
Creates worktree at `../<project>-worktrees/<TASK_ID>/` with branch `agent/<TASK_ID>`.

## Code Modification Safety

- Confirm every file path starts with the current worktree directory
- Read before modify (same as main project rules)
- Only modify files related to the current task
- Do not touch files that belong to other agents' tasks

## Allowed Git Operations

```
git status / git diff / git log        # Read operations
git add / git commit                   # Stage and commit
git push -u origin <branch>           # Push your branch
git fetch / git rebase <base>         # Stay up to date
```

## Prohibited Git Operations

- `git reset --hard` (use `git stash` instead)
- Deleting branches that are not yours (`agent/other-task`)
- Modifying remote configuration
- Force push to shared branches
- Committing directly to `master`

## Build Verification Before Push

Adapt to your project's build system:

```bash
# Replace with your actual build/lint/test commands
# e.g. for Node.js: npm run build && npm test
# e.g. for Python:  python -m pytest
# e.g. for Go:      go build ./... && go test ./...
# e.g. for Rust:    cargo build && cargo test
[your build command]
[your lint command]
[your test command]
```

> See `docs/architecture/invariants.md` for project-specific build rules (INV-BLD-*).

## Cleanup

After PR is merged:
```bash
# Manual
git worktree remove ../<project>-worktrees/<TASK_ID>
git branch -d agent/<TASK_ID>

# Batch cleanup of all merged agent worktrees
./scripts/cleanup-agent-worktrees.sh
```

## When to Use Worktree Mode

| Scenario | Use Worktree? |
|----------|--------------|
| Multiple agents working simultaneously | Yes |
| Long-running feature alongside quick fixes | Yes |
| Single small change | No — work in main directory |
| Exploratory research (read-only) | No — no files modified |
