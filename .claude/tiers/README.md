# Tier packs — how the harness sizes itself to the model

One template serves Haiku through Fable. A weak model needs explicit process; a strong one works better with criteria and room to judge. So the standing rules are split into three cumulative packs and the right one is injected per session.

| Tier | Models | Pack | What it carries |
|---|---|---|---|
| `strong` | Opus, Fable | `strong.md` | Criteria only — signal → action, no worked examples |
| `mid` | Sonnet | `mid.md` | strong + worked examples, quality floor, reporting contract |
| `light` | Haiku, anything unknown | `light.md` | mid + guardrails: rationalisation phrasebook, hard prohibitions, worktree isolation |

Packs are **generated**. Edit the fragments in `src/`, then run `python3 scripts/build-tier-packs.py`. Never edit `strong.md` / `mid.md` / `light.md` directly — the next build overwrites them, and `--check` fails acceptance if they drift from their sources.

## How a tier gets chosen

**Main conversation — declared.** No hook can see the model before the first response: `SessionStart`, `InstructionsLoaded` and `UserPromptSubmit` payloads all lack a `model` field, and the environment is identical across models (verified on Claude Code 2.1.220; the docs claim SessionStart *may* carry one — it does not). So the tier is declared, in this order:

1. `HARNESS_TIER` in this project's `.claude/settings.json` `env` block — explicit, wins
2. the `model` field in `~/.claude/settings.json` — a guess; right for `/model`, wrong for a `--model` CLI override
3. `light` — anything unknown, invalid or unreadable

The template ships `"HARNESS_TIER": "auto"`, which declares nothing: `auto`, empty and any non-tier value all fall through to the guess. The knob is in settings.json so a forked project can see it exists; set it to `strong` / `mid` / `light` to pin a tier and skip the guess. Because it is an environment variable, a change lands on the next config load, and clearing it needs a new session (see the caveat below).

**Subagent — detected.** `SubagentStart` carries `agent_type`, so the tier comes from that agent's frontmatter `model`. An agent that declares no model inherits the main conversation's tier; a built-in agent with no definition file gets `light`.

**Everything unknown resolves to `light`.** Over-loading rules costs tokens; under-loading them costs correctness.

## When the declaration is wrong

From the second turn onward the transcript carries the true model id — including `--model` overrides that `~/.claude/settings.json` never sees. `tier-drift-check.py` compares the two and, on a mismatch, tells the session to load the correct pack instead. Without that, a session declared `strong` while actually running Haiku would silently operate on condensed rules.

**Operational caveat**: setting `HARNESS_TIER` takes effect on the next config load, but *removing* it does not clear the variable from an already-running session — start a new session to unset it.

## Files

| Path | Role |
|---|---|
| `src/00-core-criteria.md` | Fragment: the criteria. In every tier |
| `src/10-mid-expansion.md` | Fragment: worked examples. mid and below |
| `src/20-light-expansion.md` | Fragment: guardrails. light only |
| `manifest.json` | Which fragments compose which pack |
| `budget.json` | Per-tier size ceilings, with switchable modes |
| `model-map.json` | Model id → tier, plus the fallback |
| `{strong,mid,light}.md` | **Generated.** Do not edit |

Related: `../hooks/tier_resolve.py` (shared resolution), `session-tier-inject.py`, `subagent-tier-inject.py`, `tier-drift-check.py`. Design record: `docs/plans/completed/F-003-tiered-harness.md`.
