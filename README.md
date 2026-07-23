# BaseAIProject — AI Harness Engineering Base Template

https://hahaicanfly.github.io/BaseAIProject/share/ai-journey-story/

> English | [繁體中文](README_zh.md)

## What This Is (30-Second Version)

BaseAIProject is a directly-forkable **Claude Code AI development governance template**: it turns "how to delegate, how to verify, how to guard against failure, how to accumulate lessons" into institutional files — 7 always-on rules, 14 specialized agents, 17 trigger-based skills, 7 guard hooks, 4 mechanical gate scripts with a matching CI workflow, and one lessons pipeline — so AI can produce stable, verifiable, non-runaway output with minimal human intervention.

**Three steps to get started**:

1. **Fork and fill in**: Globally replace placeholders like `{{PROJECT_NAME}}`, and fill in your project's build/test/lint commands (`CLAUDE.md` Quick Commands; environment bootstrap template at `.claude/templates/init.sh.template`) — executable verification commands are the single biggest lever for success rate
2. **Activate the guardrails**: `chmod +x .claude/hooks/*.py`, then run the smoke tests per `.claude/protocols/harness-maintenance.md` §4 (test both the block and pass scenarios)
3. **Canary acceptance**: Run a 30-minute small task through the full flow per `docs/harness/NEW-PROJECT-VALIDATION.md` (branch → plan → delegate → review → write lessons back); once it all passes, it's ready for real use

Language convention: institutional files that AI reads are always the **English canon**; the Traditional Chinese human-facing version lives in a `_zh`-suffixed file in the same directory, or mirrored under `agent_docs/zh/`. The full introduction follows below.

---

> A directly-forkable **AI development governance skeleton**: it lets Sonnet/Haiku-tier models produce stable, verifiable, non-runaway output autonomously, even without step-by-step human direction. Extracted from the MaiNeu production project, institutionalized through three deep rounds during the 2026-07 Fable 5 architecture session, then strengthened in a fourth round that absorbed external harness-ecosystem research (7 sources including superpowers, learn-harness-engineering, revfactory/harness — star counts and content field-verified).

## What Problem This Project Solves

AI-led development has three major failure modes, each with a corresponding physical guardrail:

| Failure Mode | This Project's Solution |
|----------|------------|
| **Documented claims ≠ reality** (rules written but never executed, guardrails deployed but never actually triggered) | Enforce hooks tested for real (black-box smoke tests), verify-on-reference, isolated acceptance |
| **Weak-model loss of focus** (multiple documents contradict each other, arbitrary which one gets trusted) | Canonical hierarchy (one single source of truth per fact category, everything else may only reference it), mutually exclusive trigger-word design |
| **Knowledge evaporation** (lessons sink into chat history, the same pitfall gets hit three times) | Lessons pipeline: hit a pitfall → ERRORS.md → human review promotes it → mechanized into invariants + guard |

## Core Design Philosophy (Five Principles)

1. **The commander doesn't get their hands dirty**: The main conversation only decides, decomposes, delegates, judges acceptance, and communicates with the user; any heavy file-reading/repo-scanning/research is always delegated to a subagent, whose report contains only conclusions and `file:line` references.
2. **Verification is never self-verification**: The implementer may not declare their own output as passing acceptance; a fresh-context agent is always delegated to do read-back, run tests for real, or perform multi-answer review.
3. **The always-loaded surface is the budget**: Content auto-loaded every session (CLAUDE.md + rules) is a tax on all future work, with an explicit line-count ceiling and a trigger line for trimming.
4. **Judgment externalized**: When to escalate models, how to determine "actually done," when to circuit-break and ask, signals for changing course — all written as observable criteria with positive/negative examples, so weak models can execute by the book.
5. **Honesty clause**: Taste decisions, ambiguous business judgment, and reasoning chains with no ground truth are the limits of weak models — the institution specifies clear exits when these are hit (offer multiple candidates for human choice, flag as unconfirmed, get a second opinion), rather than pretending to be capable.

## Capability Overview

| Subsystem | Scale | One-Liner |
|--------|------|--------|
| Virtual Team | 14 agents (4 opus + 10 sonnet) | Mutually exclusive responsibilities, professional division of labor; model dispatch is canonically defined by frontmatter |
| Skills | 17 | Trigger-based workflows, mutually exclusive description design + mechanical validators |
| Hooks | 7 + shared library | 1 enforce (exit 2, tested for real interception) + 6 sentinels |
| Always-on Rules | 7 (`always: true`) | Dispatch, judgment criteria, clarify-first, security, cost, worktree, plan-first (modularity has been demoted to non-always-on → `agent_docs/`) |
| Protocols | 5 | ExecPlan lifecycle, handoff markers, review SOP, harness maintenance, (1 unwired draft) |
| Mechanical Gates | 4 scripts + 4-job CI | `scripts/` acceptance-run / execplan-lint / check-doc-refs / retro-status; `harness-gates.yml` re-checks every PR (py-compile, secret-scan, execplan-lint, placeholder-gate) |
| State Ledgers | 5 JSONL ledgers | commits / delegations / verifications / rule-events / metrics-monthly — delegations, acceptance outcomes, and rule hit-rates survive session context (schema: `state/SCHEMA.md`) |
| Knowledge System | 5 layers | Lessons / hard rules / ADRs / session snapshots / native memory, each with its own write/read permissions and flow rules |

## The Six Subsystems

### 1. Command and Dispatch Layer

- **`CLAUDE.md` (87-line routing hub)**: Canonical hierarchy (order of trust when documents conflict), pre-action decision tree (ExecPlan vs. Plan Mode vs. do it directly vs. acceptance criteria can't be mechanized → hand to human choice), hard-guardrail summary, document map. Exceeding 100 lines triggers mandatory trimming.
- **`.claude/rules/model-dispatch.md`**: The actually-available model tiers on this machine, the delegation trio (goal & motivation / acceptance criteria / report format — missing any one means don't delegate), escalation/de-escalation path (same model fails twice in a row → escalate once → fails again → circuit-break and ask a human), report contract (≤40 lines, large artifacts get written to file with the path returned), acceptance boundary (FAIL may only be based on mechanically checkable criteria; style opinions go into a non-blocking suggestions column).
- **`.claude/rules/judgment-rubrics.md`**: Seven sections of observable criteria, each with positive/negative examples — when to escalate, when something actually counts as done (including a gate-softening ban), when to circuit-break and ask (including no-improvement detection: two consecutive rounds with an identical FAIL set triggers a circuit-break), what signals mean you should change course, quality floor, capability limits, a Red Flags rationalization-phrase lookup table ("violating the letter is violating the spirit").
- **`.claude/templates/delegation-templates.md`**: Six delegation templates — search / implementation / refactor / research / review / fresh-context acceptance — each including a scope declaration (allowed to read / allowed to write / off-limits / termination condition) and a blacklist of destructive commands (no rm / checkout / restore / clean on files outside the assignment).

### 2. Virtual Team (14 Agents)

Opus ×4 reserved for trade-offs with no standard answer: `architect` (system design/ADRs), `pm` (requirements/prioritization), `security-reviewer` (security audits), `plan-reviewer` (plan review).
Sonnet ×10 execute checklists and templated work: `code-reviewer` (PR gating, the sole Decision exit point), `qa-engineer`, `tech-lead` (architectural refactoring advisor, does not do PR gating), the research trio (`data-analyst` for quantitative KPIs / `market-researcher` for market and consumer research / `competitive-analyst` for competitor comparison, mutually exclusive triggers), `uiux-agent` (three-phase entry point) and `ui-ux-designer` (Phase 3 output), `techdebt-scanner`, `workflow-optimizer`.

The four review-category agents share a unified output format via the `review-protocol.md` canonical vocabulary (Blocker/Warning/Suggestion + Pass/Block/Conditional Pass). The roster and dispatch are canonically defined by `agent_docs/AI-TEAM-REGISTRY.md` (regenerated from frontmatter; manual edits to individual cells are forbidden).

### 3. Skills (17)

- **Development workflows**: `feature-pipeline` (end-to-end pipeline), `tdd-workflow`, `spectra-amplifier` (adds acceptance criteria to PRDs)
- **Review trio** (mutually exclusive triggers): `code-review` (standard single-PR review), `multi-agent-review` (three experts in parallel for high-risk changes), `pr-review-cycle-mob` (cost-tiered cascade)
- **Security and quality**: `security-audit` (OWASP), `techdebt-scanner`, `harness-eval` (harness maturity, scored 0-100)
- **Knowledge and handoff**: `pr-retro` (extracts lessons after merge), `context-aggregator` (multi-source handoff summary), `gen-app-map` (tech-stack-agnostic project map generator)
- **Skill engineering**: `skill-creator-plus` (supersedes the base `skill-creator`; official Anthropic methodology × local institution: intent capture, overlap checks, pushy descriptions, the mechanical validator `validate_skill.py`, 8-10 fresh-context bidirectional trigger tests each way, eval iteration)
- **UI and diagrams**: `beautiful-mermaid` (Mermaid → terminal ASCII/SVG), `ui-ux-pro-max` (design-system generator, with 3 retrieval scripts + 24 design databases across 13 tech stacks), `frontend-design` (design-philosophy guidance, with Compose examples annotated with equivalents)

> As of 2026-07-07, all skills have had their full content restored from the parent project and been de-project-specific-ized (10 of them had been silently outlined-down during extraction — this incident itself was also fed into the lessons pipeline).

### 4. Physical Guardrails (Hooks)

| Hook | Event | Mode | Responsibility |
|------|------|------|------|
| `pre-tool-use-guard.py` | PreToolUse(Bash) | **enforce** (exit 2) | Blocks: direct commits to master/main, force-push, reset --hard origin, reading **and git-adding** sensitive files (.env/keystore/credential…), all variants of `curl\|sh`, rm -rf / |
| `post-edit-lint.py` | PostToolUse(write) | sentinel | Quick INV-pattern scan (fill in QUICK_CHECKS after forking) |
| `pre-compact-snapshot.py` | PreCompact | sentinel | Automatically writes a session snapshot to `state/session-handoffs/` |
| `delegation-ledger.py` | PreToolUse(Task/Agent) | sentinel | Records every subagent delegation (and whether acceptance criteria were attached) to `state/delegations.jsonl` |
| `post-bash-commit-ledger.py` | PostToolUse(Bash) | sentinel | Links every real git commit back to its session in `state/commits.jsonl` |
| `session-activation-check.py` | SessionStart | sentinel | Warns while template activation slots (build/test commands, placeholders) remain unfilled |
| `stop-retro-logger.py` | Stop/SubagentStop | sentinel | Harvests `[VERIFY_FAILED:*]` into ERRORS.md and telemetry markers into `state/rule-events.jsonl` (markers quoted in code spans/fences are exempt); tombstone ledger prevents duplicates; 30/90-day state rotation |

Iron rule (from a real production lesson): **any hook addition or modification must be black-box smoke tested** (block scenario expects exit 2, pass scenario expects 0; commands in `harness-maintenance.md` §4) — this project's guard once went unnoticed for months as a "paper guardrail," doubly disabled by missing execute permission and a wrong exit code.

Beyond runtime hooks, four **mechanical gate scripts** (`scripts/`) make claims checkable on demand: `acceptance-run.py` executes an ExecPlan's §5 acceptance block and stores the evidence, `execplan-lint.py` checks ExecPlan structure against the PLANS.md spec, `check-doc-refs.py` verifies every path/section reference in the canon actually exists (dead references are hallucination bait), and `retro-status.py` computes the §5 trim-trigger numbers by their literal definitions. The same checks run on every PR via `.github/workflows/harness-gates.yml` (4 jobs: py-compile, secret-scan, execplan-lint, placeholder-gate).

### 5. Knowledge Management (Five Layers; map at `docs/INDEX.md`)

```
Pitfall hit ──→ ERRORS.md (Pending, auto-harvested by hook + manual append)
              │ human weekly review promotes it
              ▼
         Active Lessons (with Why + How-to-apply)
              │ mechanizable ones
              ▼
    invariants.md (INV-* hard rules) ──→ guard hook (physical interception)
```

Three more layers: `docs/decisions/ADR-*` (architectural decisions, human-approved), `state/session-handoffs/` (automatic PreCompact snapshots), Claude Code's native memory (**only cross-session metrics allowed**; the full text of lessons always goes through ERRORS.md). Maintenance permissions use a red/yellow/green tier system (`harness-maintenance.md`): lessons may be appended anytime, behavioral guidance may be changed after backup, always-on rules and guardrails require asking a human before touching.

### 6. UI/UX Three-Phase Flow (Optional)

Wireframe → Critique → Implementation, enforced as gates (`.claude/uiux/WORKFLOW.md`), with a style-spec template and six prompt templates. Projects without a frontend can delete `.claude/uiux/` and the two UI agents entirely.

## Quick Start (Five Steps After Forking)

1. **Replace placeholders**: Globally search for `{{PROJECT_NAME}}`, `{{PROJECT_TAGLINE}}`; fill in CLAUDE.md's Quick Commands and Tech Stack (executable verification commands are the single biggest lever for success rate — the Feedback subsystem); fill in environment bootstrap per `.claude/templates/init.sh.template`. Files still containing `{{}}` are treated as not yet activated, and the model will automatically skip them.
2. **Minimum viable fill-in**: The header of `agent_docs/TECHNICAL-REFERENCE.md` lists 5 fields (core mission, tech-stack quadrant, top-level modules, API base URL, auth method) — filling these unlocks "required reading before any task" status; the remaining 28 placeholders can be filled in later.
3. **Hooks smoke test**: `chmod +x .claude/hooks/*.py`, then test both the block/pass scenarios for real per `harness-maintenance.md` §4.
4. **Run canary acceptance**: Use one 30-minute small task to walk the full flow per `docs/harness/NEW-PROJECT-VALIDATION.md` (branch → plan → delegate → review → lessons pipeline), with observable criteria at every step.
5. **Customize by tech stack**: Add INV-SEC/TEST/API rules to `invariants.md`, fill in QUICK_CHECKS in `post-edit-lint.py`, fill in the scan-target table for `gen-app-map`, and (if you have a frontend) fill in the uiux style-spec.

## Directory Structure

```
BaseAIProject/
├── CLAUDE.md                  # Routing hub: canonical hierarchy, decision tree, document map (≤100 lines)
├── GEMINI.md                  # Antigravity (agy) agent bridging protocol
├── agent_docs/                # Detailed teaching layer (extended content for always-on rules)
│   ├── AI-TEAM-REGISTRY.md    # Canonical roster of agents/skills (generated from frontmatter)
│   ├── TECHNICAL-REFERENCE.md # Technical encyclopedia (with a minimum-fill checklist)
│   └── multi-agent-guide / modularity / security-policy / cost-optimization / code-conventions
├── docs/
│   ├── INDEX.md               # Document index + five-layer knowledge map
│   ├── harness/                # Institutional documents: diagnosis report, letter to the future, new-project validation flow
│   ├── architecture/          # invariants.md (INV-* hard rules), domains.md
│   ├── decisions/             # ADR-0001 + template
│   ├── learnings/ERRORS.md    # Lessons pipeline (Pending → Active → invariants)
│   └── plans/                 # ExecPlan spec + active/ + completed/
├── scripts/                   # Mechanical gates: acceptance-run / execplan-lint / check-doc-refs / retro-status
├── .github/workflows/         # harness-gates.yml CI (py-compile, secret-scan, execplan-lint, placeholder-gate)
├── state/                     # runtime (gitignored): snapshots, hook events, 5 JSONL ledgers (schema: SCHEMA.md)
└── .claude/
    ├── settings.json          # Hook wiring (6 events)
    ├── rules/                 # 7 always-on rules (always: true)
    ├── agents/                # 14 virtual agents
    ├── skills/                # 17 skills
    ├── protocols/             # lifecycle / handoff / review / maintenance
    ├── templates/             # delegation templates, init.sh environment template
    ├── hooks/                 # 7 hooks + _lib
    ├── commands/               # /last-word, /techdebt
    └── uiux/                   # UI three-phase flow (optional)
```

## Core Concepts Quick Reference

| Concept | Description | Canonical Document |
|------|------|---------|
| Canonical hierarchy | Order of trust when documents conflict: frontmatter > each protocol > REGISTRY > invariants | `CLAUDE.md` |
| Delegation trio | Goal & motivation / acceptance criteria / report format — missing any one means don't delegate | `.claude/rules/model-dispatch.md` |
| Verification is never self-verification | A fresh-context agent does read-back / runs it for real / reviews it | `model-dispatch.md` §5 |
| Circuit-break | Still failing after the full escalation/de-escalation path → ask a human with the failure trace, in a fixed format | `.claude/rules/judgment-rubrics.md` §3 |
| ExecPlan | A 9-section plan for cross-module/API changes, with a 10-stage lifecycle | `docs/plans/PLANS.md` |
| Handoff marker | An agent's final response must end with `[HANDOFF:]`/`[VERIFY_FAILED:]`/`[HUMAN_ATTENTION_REQUIRED:]` | `.claude/protocols/handoff-protocol.md` |
| Red/yellow/green tiers | Modification permissions and backup-verification requirements for harness files | `.claude/protocols/harness-maintenance.md` |
| Smoke test | Black-box testing of both block/pass scenarios for real, after any hook change | `harness-maintenance.md` §4 |
| Scope declaration | Every delegation must include: allowed to read / write / off-limits / termination condition | `delegation-templates.md` general spec |
| Quality gate | Adding/changing an agent or skill: overlap review + bidirectional trigger tests + baseline comparison; adding/expanding a standing rule: demand evidence + telemetry marker + 90-day review | `harness-maintenance.md` §6 |
| Telemetry markers | Rules emit inline markers (`RULE_FIRED` / `RULE_SKIPPED` / `ESCALATION`) at the moment they fire, harvested to `state/rule-events.jsonl` — hit-rate becomes measurable, zero-hit rules face demotion | `handoff-protocol.md` "Inline Auxiliary Markers" |
| Five-dimension checkup | Instructions/Tools/Environment/State/Feedback — missing any one is incomplete | `harness-maintenance.md` §7 |
| Red Flags | Rationalization-phrase lookup table; violating the letter is violating the spirit | `judgment-rubrics.md` §7 |

## Capability Limits (Honesty Clause)

Decomposition, isolated verification, and multi-answer review can push a weak model's **execution quality** close to that of a high-tier model; they cannot fix **whether the goal itself is right**. Taste and aesthetic decisions, ambiguous business judgment, unverifiable long reasoning chains — the institution's answer is a clear exit (offer multiple candidates for human choice, explicitly state that human judgment is needed, flag confidence level and what's unconfirmed), not pretending to be capable. Full list in `docs/harness/DIAGNOSIS.md` §4.

## References

- [Anthropic — Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Anthropic — Official skills repo (source of the skill-creator methodology)](https://github.com/anthropics/skills)
- [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) (source of the five-subsystem model)
- [obra/superpowers](https://github.com/obra/superpowers) (source of the Red Flags anti-rationalization and skill-TDD patterns)
- [revfactory/harness](https://github.com/revfactory/harness) (source of quantified bidirectional trigger testing)
- Addy Osmani — Loop Engineering (theoretical origin of maker/verifier separation and the gate-softening ban)
- Mitchell Hashimoto — Harness Engineering
- Andy Matuschak — Evergreen Notes (reference for knowledge-pipeline design)
