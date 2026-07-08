---
name: skill-creator
description: (Base version, superseded by skill-creator-plus) Use only when the user explicitly types the /skill-creator command; any "create/optimize/evaluate a skill" request should use skill-creator-plus instead.
---

# Skill: skill-creator

> ⚠ This file is a base-version stub: the full workflow (intent capture, overlap check, mechanical validation, trigger testing, eval iteration) lives in `.claude/skills/skill-creator-plus/SKILL.md` — use that version instead.
> **Trigger**: `/skill-creator` (explicit command only)
> **Agent**: workflow-optimizer (sonnet)

## Trigger Conditions

Proactively suggest this skill when you notice:
- The same operation occurring ≥3 times in a session
- A complex process that needs a fixed multi-step prompt
- A task that needs a specific output format

## Execution Steps

1. Identify the pattern of the repeated operation
2. Extract the core steps
3. Design the SKILL.md structure:
   - Purpose (one sentence)
   - Trigger command
   - Execution steps
   - Output format
   - Reference documents
4. Create `.claude/skills/<name>/SKILL.md`
5. Register in `agent_docs/AI-TEAM-REGISTRY.md`

## Skill Format Template

```markdown
# Skill: <name>

> **Purpose**: <one sentence>
> **Trigger**: `/<command>`
> **Agent**: <agent> (<model>)

## Execution Steps
1. ...

## Output Format
...

## References
- ...
```
