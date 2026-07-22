# {{PROJECT_NAME}} — Agent Operations Map

> {{PROJECT_TAGLINE}}
> This file is the **routing hub** (≤100 lines): only trust order, decision tree, and highest-frequency hard rules live here — details are referenced elsewhere.
> Rewritten 2026-07-04 from 503→125→this version; the old version is in `CLAUDE.md.bak`; rationale in `docs/harness/DIAGNOSIS.md`.

## Activation Status (new projects forked from this template: read this section first)

- If any file still contains `{{placeholder}}` = **not activated**: skip it — do not follow it literally, do not invent content to fill the gap.
- Once `agent_docs/TECHNICAL-REFERENCE.md` is filled in (no placeholders) → it regains "must-read before any task" status; if not filled in → skip it.

## Quick Commands

```bash
# {{fill in project build/test/lint commands}} ← first must-fill after forking (executable verification commands are the biggest lever on success rate); env bootstrap template: .claude/templates/init.sh.template
git branch --show-current   # confirm not on master/main before making changes
```

## Canon Hierarchy (trust order when documents conflict)

1. Model and tool dispatch → `.claude/agents/*.md` frontmatter is authoritative
2. Review process and output format → `.claude/protocols/review-protocol.md` is authoritative
3. Agent / Skill roster → `agent_docs/AI-TEAM-REGISTRY.md` is authoritative (generated from frontmatter; regeneration method in that file's header)
4. Git / security hard rules → `docs/architecture/invariants.md` is authoritative

On conflict: trust per the table above, log the conflict in `docs/learnings/ERRORS.md`, and don't stop to deliberate.

## Decision Tree Before Acting (single entry point)

0. Scope/requirements unclear (2+ of: target user, success metric, non-goals/boundaries, trigger condition are missing) → clarify first in the main conversation before drafting an ExecPlan or Plan Mode plan (`.claude/rules/clarify-first.md`)
1. Cross-module / API changes / large-scale refactors → create an ExecPlan (`docs/plans/active/`, spec in `docs/plans/PLANS.md`), **wait for human approval**
2. Other non-trivial tasks (new features, multi-file changes, file deletion) → propose a plan in Plan Mode, execute after approval
3. Single file < 20 lines, already-located bug fix, formatting change → do it directly
4. Acceptance criteria cannot be made mechanical (taste/business judgment) → produce candidates + trade-offs for a human to choose (judgment-rubrics §6); do not enter an implementation loop
5. Always applies: Read before editing; do not claim completion without verification

## Standing Rules (auto-loaded from `.claude/rules/`, no need to re-read)

security / model-dispatch (model dispatch & delegation) / judgment-rubrics (escalation·completion·circuit-breaker·path-switch criteria) / clarify-first (proactive scope check before ExecPlan/Plan Mode) / plan-first / parallel-worktree / cost-optimization (modularity demoted from standing → `agent_docs/modularity.md`)

- Delegation prompt templates: `.claude/templates/delegation-templates.md`
- How to safely edit harness files: `.claude/protocols/harness-maintenance.md`

## Hard Guardrails

`pre-tool-use-guard.py` (enforce, field-tested) blocks via exit 2: commits on master/main, force-push to master/main, `reset --hard origin/master|main`, reading `.env` or other secret files, `curl|sh`. Full text in `docs/architecture/invariants.md`.

NEVER: hardcode secrets / commit sensitive files (`.env`, `*.keystore`, …) / guess API signatures / add unrequested feature abstractions / skip lint/test and claim completion.

## Handoff & Session Management

- Sub-agent final responses must include `[HANDOFF:*]` / `[VERIFY_FAILED:*]` / `[HUMAN_ATTENTION_REQUIRED:*]` (spec: `.claude/protocols/handoff-protocol.md`)
- Phase complete and context usage >50% → run `/last-word` to produce `SESSION-HANDOFF.md` → `/clear` → new session reads the file to continue
- Append lessons learned to `docs/learnings/ERRORS.md` (format in harness-maintenance.md); recurring, mechanizable ones get promoted into `invariants.md`

## Document Map

| Need | Where |
|---------|--------|
| Full document index | `docs/INDEX.md` |
| Current architecture (must-read once filled in) | `agent_docs/TECHNICAL-REFERENCE.md` |
| Team roster, model dispatch, skills | `agent_docs/AI-TEAM-REGISTRY.md` |
| Multi-agent collaboration patterns | `agent_docs/multi-agent-guide.md` |
| ExecPlan 10-stage lifecycle | `.claude/protocols/execplan-lifecycle.md` |
| Harness diagnosis / letter to future sessions | `docs/harness/` |
| UI three-phase workflow | `.claude/uiux/WORKFLOW.md` |
| Mechanical verification tools | `scripts/` (acceptance-run / execplan-lint / check-doc-refs / retro-status) |
| Runtime state format | `state/SCHEMA.md` |
| Chinese human-readable mirrors | auto-discovered dirs (agents/rules/commands) → `agent_docs/zh/`; everything else → same-dir `*_zh.md` |

## Communication Style

Respond to the user in Traditional Chinese; code comments may be in English; commit messages in English, `type(scope)` format, one feature per commit, never commit directly to master (branch `feat/<slug>` + PR). Concise, technically accurate, no emoji (unless the user requests them).

```
✓ Done: [what was specifically done]
→ Next: [what happens next]
⚠ Note: [risks or issues the user should know]
```

## Tech Stack / Project Relations

{{unfilled = not activated, skip this section}}

## Antigravity (agy) Bridge

agy agent: read `GEMINI.md` first. Rules in `.claude/agents/*.md` and `.claude/skills/*/SKILL.md` apply fully to agy; Python hooks do not auto-run in the agy environment, so equivalent rules must be followed manually (especially invariants' INV-GIT-*).
