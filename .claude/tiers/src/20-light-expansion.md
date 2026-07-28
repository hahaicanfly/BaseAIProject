# Guardrails (light tier)

These exist because the failures below have actually happened in this repo, repeatedly. They are stated as hard rules rather than judgment calls on purpose.

## Rationalisation phrasebook

If you catch yourself — or a subagent's report — producing anything in the left column, a rule is being evaded. Take the right column instead.

| Phrase | What to do instead |
|---|---|
| "Small change, no need for the full process" | Grade by the routing table's objective criteria, not by how big it feels |
| "Test environment is broken, skip tests for now" | Not run = not done. Report honestly: "blocked on test environment" |
| "Should be fine / logically no issue" | That's a conclusion with no evidence. Go get the evidence |
| "Do it this way for now, fix it later" | A "later" with no date is never. Declare it as an open item |
| "The rule probably doesn't cover this case" | Violating the letter is violating the spirit. Ask a human before claiming an exception |
| "Tried many times, delivering the best version" | Not passing is not passing. Stop and ask |

**Literal-text clause**: hard rules bind by their literal text. "I think this matches the spirit" does not authorise a bypass.

**No gate-softening**: after several repair rounds it is forbidden to count a better earlier run as the pass. If the last run failed, it failed.

## Never

Hardcode secrets. Commit `.env`, keystores, or credential files. Guess an API signature instead of reading it. Add abstractions nobody requested. Skip lint or tests and report completion.

`git reset --hard` (use `git stash`). Force-push to a shared branch. Commit directly to master/main. Delete branches that aren't yours. Modify remote configuration.

`pre-tool-use-guard.py` blocks several of these with exit 2. A block is information, not an obstacle to route around.

## Before every commit

Run `git branch --show-current` and confirm you are not on master/main. Branch `feat/<slug>`, one feature per commit, English `type(scope)` messages, PR to merge.

## Parallel work isolation

When several agents or sessions work the same repo at once, each gets its own git worktree — one worktree, one task, one branch, one PR. Never edit the main project directory while operating in worktree mode, and never touch files belonging to another agent's task.

```bash
git worktree add ../<project>-worktrees/<TASK_ID> -b agent/<TASK_ID> [BASE_BRANCH]
```

Or `Agent(prompt: ..., isolation: "worktree")`, which manages the lifecycle for you. Skip worktrees entirely for a single small change or read-only exploration — they cost more than they save there.

After the PR merges: `git worktree remove <path>` then `git branch -d agent/<TASK_ID>`.

## Cost awareness

Don't call an API for what runs locally: OCR, language detection, basic text processing, image preprocessing, format validation. Don't repeat identical requests — cache. Batch small requests rather than firing them one at a time. Cap retries.

Flag to the user proactively: large volumes of repeated API calls, a cloud API doing something localisable, expensive operations with no caching, an over-tiered model on a simple task.

## Handing off

A subagent's final response must end with one of `[HANDOFF:*]`, `[VERIFY_FAILED:*]`, or `[HUMAN_ATTENTION_REQUIRED:*]` — spec in `.claude/protocols/handoff-protocol.md`.

When a phase completes and context is over half used, run `/last-word` to produce `SESSION-HANDOFF.md`, then `/clear`; the next session reads that file to continue.

Lessons go to `docs/learnings/ERRORS.md`. Before appending, search for an existing entry on the same topic and add `Recurred: <date>` to it rather than opening a duplicate.

## When documents disagree

1. Model and tool dispatch → `.claude/agents/*.md` frontmatter wins
2. Review process and output format → `.claude/protocols/review-protocol.md` wins
3. Agent / skill roster → `agent_docs/AI-TEAM-REGISTRY.md` wins
4. Git and security hard rules → `docs/architecture/invariants.md` wins

Log the conflict in `ERRORS.md` and move on. Do not stop to deliberate, and do not copy a canonical table into a second file — reference it.
