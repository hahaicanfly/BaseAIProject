# AI Cost Optimization Guide

> Standing hard rules live in `.claude/rules/cost-optimization.md` and `.claude/rules/model-dispatch.md`; this file only holds extended notes and examples.
> **Audience**: all agents (reference when choosing a model or deciding whether to make an API call).

---

## Model Selection

The tier table, escalation/de-escalation path, and dispatch rules use `.claude/rules/model-dispatch.md` as the single source of truth; this file does not duplicate the table.

---

## Prompt Cache Strategy

### Maximizing Cache Hits

- Put long system prompts (CLAUDE.md, invariants.md) at the **front** of the message; don't reorder them each time
- Put static context (architecture docs, rules) before dynamic context (the current task)
- 5-minute TTL: if a session is idle for more than 5 minutes, the cache expires

### Choosing a ScheduleWakeup Interval

| Scenario | Recommended interval | Reason |
|------|---------|------|
| Waiting on external CI/CD | 60–270s | Keeps cache warm while polling external status |
| Waiting on a longer operation | 1200–1800s | Exceeds cache TTL anyway, so save a cache-miss cycle |
| Avoid 300s | — | Just past cache expiry but too short a wait — worst case |

---

## Context Engineering (Token Budget Strategy)

### Three-Tier Reading Principle

```
Tier 1: Read the index file (lightweight, ~KB) → locate the relevant page
Tier 2: Read 2-3 core documents (medium weight) → compose the answer
Tier 3: Only read raw source code (heavyweight) if the first two tiers are insufficient
```

### Preventing Context Flooding

- Prefer reading summary pages over raw large files
- Use `grep` for targeted reads instead of `cat`-ing an entire large file
- Have sub-agents handle heavyweight tasks to protect the main context

---

## Edge AI Integration (Extended)

See `.claude/rules/cost-optimization.md` "Edge AI First" for the list of tasks that can be done locally. Additional notes — tasks that need a cloud model:

- Deep semantic understanding
- Complex reasoning and analysis
- Cross-document synthesis

---

## Monitoring and Analysis

### `state/token-usage.jsonl` Tracking

`pre-compact-snapshot.py` automatically logs token usage on every PreCompact event.

**Metrics to track**:
- Cost per API call
- Cache hit rate (`cache_read` / `input_tokens`)
- Average session token consumption

### Warning Signs

- `cache_read` staying at 0 → prompt ordering issue or session gaps too long
- `input_tokens` spiking → context flooding, consider splitting into sub-agents
- The same task called repeatedly → missing a caching layer

---

## Extended Priorities

- Sub-agent isolation: run heavyweight tasks in a sub-agent to avoid polluting the main context
- Periodic review: analyze cost distribution from `state/token-usage.jsonl` monthly
