# BaseAIProject — AI Harness Engineering Base Template

https://hahaicanfly.github.io/BaseAIProject/share/ai-journey-story/

> English | [繁體中文](README_zh.md)
> **Not a developer?** Start at [`docs/PLAIN/START-HERE.md`](docs/PLAIN/START-HERE.md) ([中文](docs/PLAIN/START-HERE_zh.md)) — same setup, no jargon, nothing to memorise.

## What This Is (30-Second Version)

A directly-forkable **Claude Code AI development governance template**. It turns "how to delegate, how to verify, how to guard against failure, how to accumulate lessons" into files the model actually reads and hooks that actually fire — so an AI assistant produces stable, verifiable, non-runaway output without a human watching every step.

What you get: **14 specialised agents**, **17 trigger-based skills**, **10 hooks across 8 events** (1 blocking, 9 observing), **3 model-tiered rule packs**, **7 scripts** that make claims checkable, **9 hard invariants**, and one lessons pipeline that turns mistakes into enforced rules.

**Three steps to get started:**

1. **Fork and fill in** — replace `{{PROJECT_NAME}}`-style placeholders and fill your build/test/lint commands into `CLAUDE.md` Quick Commands (bootstrap template: `.claude/templates/init.sh.template`). Executable verification commands are the single biggest lever on success rate.
2. **Activate the guardrails** — `chmod +x .claude/hooks/*.py`, then run the smoke tests in `.claude/protocols/harness-maintenance.md` §4. Test both the block *and* the pass scenario.
3. **Canary acceptance** — run one 30-minute task through the whole flow per `docs/harness/NEW-PROJECT-VALIDATION.md` (branch → plan → delegate → review → write the lesson back). When that passes, it is ready for real work.

Language convention: institutional files the AI reads are the **English canon**; the Traditional Chinese human-facing version lives in a `_zh`-suffixed file in the same directory, or mirrored under `agent_docs/zh/`.

---

## What Problem This Project Solves

AI-led development has three failure modes. Each gets a physical guardrail, not an exhortation.

| Failure mode | The guardrail |
|---|---|
| **Documented claims ≠ reality** — rules written but never executed, guardrails deployed but never actually triggered | Hooks smoke-tested black-box; every reference verified to exist; acceptance run by a fresh context |
| **Weak-model loss of focus** — documents contradict each other, and which one wins is arbitrary | Canonical hierarchy (one source of truth per fact, everything else may only reference it); mutually exclusive trigger words |
| **Knowledge evaporation** — lessons sink into chat history, the same pitfall gets hit three times | Lessons pipeline: hit it → `ERRORS.md` → human review promotes it → mechanised into an invariant + a guard |

## Core Design Philosophy

1. **The commander doesn't do fieldwork.** The main conversation decides, decomposes, delegates, judges acceptance, and talks to you. Heavy file-reading, repo scanning and research go to a subagent, whose report contains conclusions and `file:line` references — not pasted content.
2. **Verification is never self-verification.** An implementer may not declare its own output as passing. A fresh-context agent does the read-back, runs the tests for real, or gives an independent second opinion.
3. **The standing layer is a budget, and the budget is enforced.** What loads into every session is capped by `INV-ARC-001` and measured by `scripts/context-budget.py`. Adding a line to the standing layer now has a number attached to it.
4. **Judgment is externalised.** When to escalate a model, what counts as actually done, when to stop and ask, when you are on the wrong path — all written as *observable signal → action*, with worked examples, so a weak model can follow them by the book.
5. **Honesty clause.** Taste, ambiguous business judgment, and long reasoning chains with no ground truth are where weak models fail. The institution names the exit for each (offer candidates and let a human choose, tag it unconfirmed, get a second opinion) instead of pretending competence.

## Capability Overview

| Subsystem | Scale | One-liner |
|---|---|---|
| Rule delivery | 3 tier packs + 1 always-on rule | Rule weight is matched to the running model; `security.md` loads for everyone |
| Virtual team | 14 agents (4 opus + 10 sonnet) | Mutually exclusive responsibilities; model dispatch is canonically the frontmatter |
| Skills | 17 | Trigger-based workflows; the largest route through `references/` instead of loading whole |
| Hooks | 10 across 8 events + 2 shared modules | 1 enforce (exit 2, interception tested for real) + 9 sentinels |
| Protocols | 5 | ExecPlan lifecycle, handoff markers, review SOP, harness maintenance, 1 unwired draft |
| Mechanical gates | 7 scripts + 4-job CI | 6 checks + 1 read-only translator; `harness-gates.yml` re-checks every PR |
| Hard rules | 9 invariants | 5 git + 3 security + 1 architecture, each with a CHECK command and an owning hook |
| State ledgers | 8 JSONL + 2 JSON + 2 sub-dirs | Delegations, acceptance outcomes and rule hit-rates survive session context (`state/SCHEMA.md`) |
| Knowledge system | 5 layers | Lessons / hard rules / ADRs / session snapshots / native memory, each with its own permissions |

## The Subsystems

### 1. Command and Dispatch

- **`CLAUDE.md` (93-line routing hub)** — canonical hierarchy, hard-guardrail summary, document map. Past 100 lines, trimming is mandatory.
- **`.claude/rules/model-dispatch.md`** — available model tiers, the delegation trio (goal & motivation / acceptance criteria / report format — missing one means don't delegate), the escalation path (same model fails twice → escalate once → fails again → circuit-break and ask), the report contract (≤40 lines; long artifacts go to a file, the report returns the path), and the acceptance boundary (a FAIL may only cite mechanically checkable criteria; style opinions go in a non-blocking column).
- **`.claude/rules/judgment-rubrics.md`** — seven sections of observable criteria with positive/negative examples: when to escalate, what counts as done (including the gate-softening ban), when to circuit-break (including no-improvement detection — two rounds with an identical FAIL set stops the loop), wrong-path signals, quality floor, capability limits, and a Red Flags rationalisation phrasebook.
- **`.claude/templates/delegation-templates.md`** — six delegation templates, each carrying a scope declaration (may read / may write / off-limits / termination condition) and a destructive-command blacklist.
- **`.claude/commands/guided-start.md` + `scripts/translate-acceptance.py`** — a natural-language on-ramp for non-technical requests, plus a read-only script that restates acceptance evidence in plain language after the fact.

### 2. Tiered Rule Delivery

One template serves Haiku through Fable. A weak model needs explicit process; a strong one works better with criteria and room to judge. So the standing rules are built into three cumulative packs and the right one is injected at session start.

| Tier | Models | Carries |
|---|---|---|
| `strong` | Opus, Fable | Criteria only — signal → action, no worked examples |
| `mid` | Sonnet | strong + worked examples, quality floor, reporting contract |
| `light` | Haiku, anything unknown | mid + guardrails: rationalisation phrasebook, hard prohibitions, worktree isolation |

- **Packs are generated**, never hand-written — edit the fragments in `.claude/tiers/src/` and run `scripts/build-tier-packs.py`. Acceptance fails if a pack drifts from its sources.
- **The main conversation's tier is declared; a subagent's is detected.** No hook can see the model before the first response, so `HARNESS_TIER` in `.claude/settings.json` declares it (shipped as `auto`, meaning "guess"). A subagent's `SubagentStart` payload carries `agent_type`, so its tier comes from that agent's frontmatter. From the second turn, `tier-drift-check.py` compares the declaration against the real model id and corrects a mismatch.
- **Anything unknown resolves to `light`** — over-loading rules costs tokens, under-loading them costs correctness.
- **The six non-standing rule files stay in place** as full-text reference with worked examples. Read one when a borderline case needs the reasoning behind a criterion. Details: `.claude/tiers/README.md`.

### 3. Virtual Team (14 Agents)

**Opus ×4**, reserved for trade-offs with no standard answer: `architect` (system design, ADRs), `pm` (requirements, prioritisation), `security-reviewer` (audits), `plan-reviewer` (plan review).

**Sonnet ×10**, for checklists and templated work: `code-reviewer` (PR gating — the sole Decision exit point), `qa-engineer`, `tech-lead` (refactoring advisor, does *not* gate PRs), the research trio (`data-analyst` for quantitative KPIs, `market-researcher` for market and consumer work, `competitive-analyst` for feature-by-feature comparison — mutually exclusive triggers), `uiux-agent` (three-phase entry) and `ui-ux-designer` (Phase 3 output), `techdebt-scanner`, `workflow-optimizer`.

The four review-category agents share one output vocabulary via `review-protocol.md` (Blocker / Warning / Suggestion + Pass / Block / Conditional Pass). The roster is canonically `agent_docs/AI-TEAM-REGISTRY.md`, regenerated from frontmatter — editing individual cells by hand is forbidden.

### 4. Skills (17)

- **Development workflows** — `feature-pipeline` (end-to-end), `tdd-workflow`, `spectra-amplifier` (adds acceptance criteria to a thin PRD)
- **Review trio**, mutually exclusive triggers — `code-review` (standard single PR), `multi-agent-review` (three experts in parallel for high-risk changes), `pr-review-cycle-mob` (cost-tiered cascade)
- **Security and quality** — `security-audit` (OWASP), `techdebt-scanner`, `harness-eval` (harness maturity, scored 0–100)
- **Knowledge and handoff** — `pr-retro` (extracts lessons after a merge), `context-aggregator` (multi-source handoff summary), `gen-app-map` (tech-stack-agnostic project map)
- **Skill engineering** — `skill-creator-plus` (supersedes the base `skill-creator`): intent capture, overlap checks, the `validate_skill.py` mechanical validator, bidirectional trigger tests, eval iteration
- **UI and diagrams** — `beautiful-mermaid` (Mermaid → terminal ASCII / SVG), `ui-ux-pro-max` (design-system generator with retrieval scripts and design databases), `frontend-design` (design philosophy, Compose examples with cross-stack equivalents)

The four largest skills keep a short router in `SKILL.md` and hold their bulk in `references/`, loaded only when the task needs it. Follow that shape when a `SKILL.md` grows past ~150 lines — the body is not standing context, but it *is* paid for in full on every invocation.

### 5. Physical Guardrails (Hooks)

| Hook | Event | Mode | Responsibility |
|---|---|---|---|
| `pre-tool-use-guard.py` | PreToolUse(Bash) | **enforce** (exit 2) | Blocks direct commits to master/main, force-push, `reset --hard origin`, reading **and git-adding** secret files, every `curl\|sh` variant, `rm -rf /` |
| `post-edit-lint.py` | PostToolUse(write) | sentinel | Quick INV-pattern scan (fill in `QUICK_CHECKS` after forking) |
| `pre-compact-snapshot.py` | PreCompact | sentinel | Writes a session snapshot to `state/session-handoffs/` |
| `delegation-ledger.py` | PreToolUse(Task/Agent) | sentinel | Records every delegation, and whether acceptance criteria were attached |
| `post-bash-commit-ledger.py` | PostToolUse(Bash) | sentinel | Links every real commit back to its session |
| `session-activation-check.py` | SessionStart | sentinel | Warns while template activation slots remain unfilled |
| `session-tier-inject.py` | SessionStart | sentinel | Injects the tier pack for the declared tier |
| `subagent-tier-inject.py` | SubagentStart | sentinel | Injects the tier pack matching that agent's own frontmatter model |
| `tier-drift-check.py` | UserPromptSubmit | sentinel | From turn two, compares the declared tier against the real model id and corrects a mismatch |
| `stop-retro-logger.py` | Stop / SubagentStop | sentinel | Harvests `[VERIFY_FAILED:*]` into `ERRORS.md` and telemetry markers into `state/rule-events.jsonl`; markers quoted inside code spans are exempt; a tombstone ledger prevents duplicates |

Shared modules `_lib.py` and `tier_resolve.py` are imported by the hooks, not wired to events.

**Iron rule, learned the hard way:** any hook you add or change must be black-box smoke tested — block scenario expects exit 2, pass scenario expects 0 (commands in `harness-maintenance.md` §4). This project's guard once sat unnoticed for months as a paper guardrail, disabled twice over by a missing execute bit and a wrong exit code.

### 6. Mechanical Gates

Seven scripts make claims checkable on demand instead of on trust:

| Script | What it settles |
|---|---|
| `acceptance-run.py` | Executes an ExecPlan's acceptance block and stores the evidence |
| `execplan-lint.py` | Checks ExecPlan structure against the `PLANS.md` spec |
| `check-doc-refs.py` | Verifies every path and section reference in the canon exists (dead references are hallucination bait) |
| `context-budget.py` | Measures the standing layer against `.claude/tiers/budget.json` — the enforcement behind `INV-ARC-001` |
| `build-tier-packs.py` | Rebuilds the tier packs; `--check` fails when a pack has drifted from its sources |
| `retro-status.py` | Computes the trim-trigger numbers by their literal definitions |
| `translate-acceptance.py` | **Not a gate** — read-only, always exits 0, restates existing acceptance evidence in plain language |

`.github/workflows/harness-gates.yml` re-runs the checkable subset on every PR (py-compile, secret-scan, execplan-lint, placeholder-gate).

### 7. Knowledge Management (map at `docs/INDEX.md`)

```
Pitfall hit ──→ ERRORS.md (Pending; hook-harvested + manually appended)
              │ human weekly review promotes it
              ▼
         Active Lessons (with Why + How-to-apply)
              │ the mechanisable ones
              ▼
    invariants.md (INV-*) ──→ guard hook (physical interception)
```

Three further layers: `docs/decisions/ADR-*` (human-approved architectural decisions), `state/session-handoffs/` (automatic PreCompact snapshots), and Claude Code's native memory (**cross-session metrics only** — the full text of a lesson always goes through `ERRORS.md`).

Maintenance permissions are red/yellow/green (`harness-maintenance.md`): lessons may be appended any time, behavioural guidance may be changed after a backup, standing rules and guardrails require asking a human first.

`docs/PLAIN/` is a plain-language derived layer, not a sixth pipeline stage — a read-only translation of the rule files. If it ever disagrees with its source, the source governs.

### 8. UI/UX Three-Phase Flow (Optional)

Wireframe → Critique → Implementation, enforced as gates (`.claude/uiux/WORKFLOW.md`), with a style-spec template and six prompt templates. A project with no frontend can delete `.claude/uiux/` and both UI agents outright.

## Quick Start (Five Steps After Forking)

1. **Replace placeholders.** Search for `{{PROJECT_NAME}}` and `{{PROJECT_TAGLINE}}`; fill in `CLAUDE.md`'s Quick Commands and Tech Stack; bootstrap the environment from `.claude/templates/init.sh.template`. Files that still contain `{{}}` count as not activated and the model skips them.
2. **Minimum viable fill-in.** The header of `agent_docs/TECHNICAL-REFERENCE.md` lists 5 fields (core mission, tech-stack quadrant, top-level modules, API base URL, auth method). Filling those unlocks its "required reading" status; the rest can wait.
3. **Smoke-test the hooks.** `chmod +x .claude/hooks/*.py`, then test block and pass scenarios for real per `harness-maintenance.md` §4.
4. **Run the canary.** One 30-minute task through the full flow per `docs/harness/NEW-PROJECT-VALIDATION.md`, with an observable criterion at every step.
5. **Customise for your stack.** Add INV-SEC / INV-TEST / INV-API rules to `invariants.md`, fill `QUICK_CHECKS` in `post-edit-lint.py`, fill the scan-target table for `gen-app-map`, and — if you have a frontend — the uiux style spec. If you know which model you will mostly run, set `HARNESS_TIER` in `.claude/settings.json`; otherwise leave it on `auto`.

## Directory Structure

```
BaseAIProject/
├── CLAUDE.md                  # Routing hub: canon hierarchy, guardrails, document map (≤100 lines)
├── GEMINI.md                  # Antigravity (agy) agent bridging protocol
├── agent_docs/                # Detailed teaching layer
│   ├── AI-TEAM-REGISTRY.md    # Canonical roster (generated from frontmatter)
│   ├── TECHNICAL-REFERENCE.md # Technical encyclopedia (with a minimum-fill checklist)
│   └── multi-agent-guide / modularity / security-policy / cost-optimization / code-conventions
├── docs/
│   ├── INDEX.md               # Document index + five-layer knowledge map
│   ├── harness/               # Diagnosis, letter to future sessions, new-project validation
│   ├── architecture/          # invariants.md (INV-*), domains.md
│   ├── decisions/             # ADR-0001 + templates
│   ├── learnings/ERRORS.md    # Lessons pipeline (Pending → Active → invariants)
│   ├── PLAIN/                 # Plain-language layer: START-HERE, CLAUDE.md crib sheet
│   └── plans/                 # ExecPlan spec + active/ + completed/
├── scripts/                   # 6 mechanical gates + translate-acceptance (read-only, not a gate)
├── .github/workflows/         # harness-gates.yml CI (4 jobs)
├── state/                     # runtime, gitignored: 8 JSONL ledgers + acceptance/ + session-handoffs/
└── .claude/
    ├── settings.json          # Hook wiring (8 events) + HARNESS_TIER declaration
    ├── tiers/                 # 3 generated packs + src/ fragments + budget/model-map config
    ├── rules/                 # security.md (always-on) + 6 full-text reference files
    ├── agents/                # 14 virtual agents
    ├── skills/                # 17 skills
    ├── protocols/             # lifecycle / handoff / review / maintenance
    ├── templates/             # delegation templates, init.sh environment template
    ├── hooks/                 # 10 hooks + 2 shared modules
    ├── commands/              # /guided-start, /last-word, /techdebt
    └── uiux/                  # UI three-phase flow (optional)
```

## Core Concepts Quick Reference

| Concept | What it means | Canonical document |
|---|---|---|
| Canonical hierarchy | Order of trust when documents conflict: frontmatter > protocol > REGISTRY > invariants | `CLAUDE.md` |
| Tier pack | The standing rules, sized to the running model; declared for the main conversation, detected for subagents | `.claude/tiers/README.md` |
| Standing-layer budget | `CLAUDE.md` + `security.md` + the injected pack must fit the active mode's ceiling | `INV-ARC-001` |
| Delegation trio | Goal & motivation / acceptance criteria / report format — missing one means don't delegate | `model-dispatch.md` |
| Verification is never self-verification | A fresh-context agent reads it back, runs it, or reviews it | `model-dispatch.md` §5 |
| Circuit-break | Still failing after the full escalation path → ask a human, with the failure trace, in a fixed format | `judgment-rubrics.md` §3 |
| ExecPlan | A 9-section plan for cross-module / API changes, with a 10-stage lifecycle | `docs/plans/PLANS.md` |
| Handoff marker | An agent's final response must end with `[HANDOFF:]` / `[VERIFY_FAILED:]` / `[HUMAN_ATTENTION_REQUIRED:]` | `handoff-protocol.md` |
| Red / yellow / green tiers | Edit permissions and backup requirements for harness files | `harness-maintenance.md` §1 |
| Smoke test | Black-box test of both block and pass scenarios after any hook change | `harness-maintenance.md` §4 |
| Scope declaration | Every delegation states: may read / may write / off-limits / termination condition | `delegation-templates.md` |
| Quality gate | New agent or skill → overlap review + bidirectional trigger tests; new standing rule → evidence + telemetry + 90-day review | `harness-maintenance.md` §6 |
| Telemetry markers | Rules emit `RULE_FIRED` / `RULE_SKIPPED` / `ESCALATION` inline, harvested to `state/rule-events.jsonl` — a rule with no hits faces demotion | `handoff-protocol.md` |
| Five-dimension checkup | Instructions / Tools / Environment / State / Feedback — missing one means incomplete | `harness-maintenance.md` §7 |
| Red Flags | Rationalisation phrasebook; violating the letter is violating the spirit | `judgment-rubrics.md` §7 |

## Capability Limits (Honesty Clause)

Decomposition, isolated verification and multi-answer review can push a weak model's **execution quality** close to a high-tier model's. They cannot fix **whether the goal is right**. Taste, ambiguous business judgment, unverifiable long reasoning chains — the institution's answer is a named exit (offer candidates and let a human choose, state plainly that a human must decide, tag confidence and what is unconfirmed), not pretended competence. Full list in `docs/harness/DIAGNOSIS.md` §4.

## References

- [Anthropic — Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Anthropic — Official skills repo](https://github.com/anthropics/skills) (source of the skill-creator methodology)
- [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) (source of the five-dimension model)
- [obra/superpowers](https://github.com/obra/superpowers) (source of the Red Flags anti-rationalisation and skill-TDD patterns)
- [revfactory/harness](https://github.com/revfactory/harness) (source of quantified bidirectional trigger testing)
- Addy Osmani — Loop Engineering (maker/verifier separation, the gate-softening ban)
- Mitchell Hashimoto — Harness Engineering
- Andy Matuschak — Evergreen Notes (knowledge-pipeline design)
