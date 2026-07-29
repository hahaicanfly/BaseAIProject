# {{PROJECT_NAME}} — Agent Operations Map

> {{PROJECT_TAGLINE}}
> This file is the **routing hub** (≤100 lines): only trust order, decision tree, and highest-frequency hard rules live here — details are referenced elsewhere.
> Rewritten 2026-07-04 from 503→125→this version; the old version is in `CLAUDE.md.bak`; rationale in `docs/harness/DIAGNOSIS.md`.

## Activation Status (new projects forked from this template: read this section first)

- If any file still contains `{{placeholder}}` = **not activated**: skip it — do not follow it literally, do not invent content to fill the gap.
- Once `agent_docs/TECHNICAL-REFERENCE.md` is filled in (no placeholders) → it regains "must-read before any task" status; if not filled in → skip it.
- 不會打指令?直接把這句貼給 Claude Code:「幫我完成專案初始化,交給它做前兩步」

## Quick Commands

```bash
# --- Harness self-check (this template's own gates; always available) ---
python3 scripts/context-budget.py --tier strong      # always-on context budget (thresholds: .claude/tiers/budget.json)
python3 scripts/execplan-lint.py docs/plans/active/*.md   # ExecPlan structure
python3 scripts/check-doc-refs.py                    # dead-reference sweep
python3 scripts/acceptance-run.py <plan.md>          # run an ExecPlan's acceptance block

# --- Product build/test/lint: {{fill in after forking}} ---
# Executable verification commands are the biggest lever on success rate.
# Env bootstrap template: .claude/templates/init.sh.template
git branch --show-current   # confirm not on master/main before making changes
```

## Canon Hierarchy (trust order when documents conflict)

1. Model and tool dispatch → `.claude/agents/*.md` frontmatter is authoritative
2. Review process and output format → `.claude/protocols/review-protocol.md` is authoritative
3. Agent / Skill roster → `agent_docs/AI-TEAM-REGISTRY.md` is authoritative (generated from frontmatter; regeneration method in that file's header)
4. Git / security hard rules → `docs/architecture/invariants.md` is authoritative

On conflict: trust per the table above, log the conflict in `docs/learnings/ERRORS.md`, and don't stop to deliberate.

## Operating Rules (tier pack, injected each session)

The criteria you work by — routing, delegation, escalation, when to stop, what counts as done — arrive as a **tier pack** matched to the running model — `strong.md`, `mid.md` or `light.md` under `.claude/tiers/`. Follow the pack; it is the operative version.

`.claude/rules/*.md` holds the same rules in full with worked examples. Only `security.md` is auto-loaded (every tier); the rest are reference — read one when a borderline case needs the reasoning behind a criterion.

Tier is **declared, not detected** (no hook can see the model before the first response). `HARNESS_TIER` in this project's `.claude/settings.json` `env` block decides it; the shipped value `auto` declares nothing, so the tier is guessed from `~/.claude/settings.json`, and anything unknown falls back to `light` (full SOP). A mismatch against the real model is caught from the second turn and announced. **Tier is fixed once per session** — switching models mid-session with `/model` does not re-inject; it takes effect in the next session. Details: `.claude/tiers/README.md`.

- Delegation prompt templates: `.claude/templates/delegation-templates.md`
- How to safely edit harness files: `.claude/protocols/harness-maintenance.md`
- 不熟悉 ExecPlan / Plan Mode 是什麼?→ `docs/PLAIN/claude-md-crib-sheet.md` 一頁對照卡

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
| Tier packs: how the harness sizes itself | `.claude/tiers/README.md` |
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
