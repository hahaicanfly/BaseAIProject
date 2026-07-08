# AI Team Registry

> **Role**: This file is the complete registry of all agents and skills, generated verbatim from `.claude/agents/*.md` frontmatter and `.claude/skills/*/SKILL.md` description fields.
> **Canonical rule**: Model dispatch is governed by the `model` field in `.claude/agents/*.md` frontmatter (see CLAUDE.md canonical hierarchy).
> **This file was regenerated from frontmatter on 2026-07-08 (regenerated in English)**. If it conflicts with agent frontmatter, frontmatter wins. To update: re-generate per this section (re-read each file's frontmatter / SKILL.md description and overwrite the tables below) — do not hand-edit individual cells.

---

## Agents — 14

| Agent | model | Responsibility | tools |
|-------|-------|------|-------|
| `architect` | opus | Software Architect - system design, API design, data modeling, ADRs | Read, Grep, Glob |
| `code-reviewer` | sonnet | Automated Code Review specialist | Read, Bash, Grep, Glob |
| `competitive-analyst` | sonnet | Competitive Analyst - feature-by-feature competitor comparison, feature matrices, pricing comparison, SWOT. Not for market-size/consumer research (use market-researcher), not for quantitative KPI/metric design (use data-analyst) | Read, Grep, Glob, WebFetch, WebSearch |
| `data-analyst` | sonnet | Data Analyst - quantitative data analysis, KPI/metric design, statistical trend interpretation. Not for market qualitative research (use market-researcher), not for feature-by-feature competitor comparison (use competitive-analyst) | Read, WebSearch, WebFetch, Grep |
| `market-researcher` | sonnet | Market Researcher - market sizing (TAM/SAM/SOM), user research, consumer insights. Not for quantitative KPI/metric design (use data-analyst), not for feature-by-feature competitor comparison (use competitive-analyst) | Read, Grep, Glob, WebFetch, WebSearch |
| `plan-reviewer` | opus | Plan Reviewer - reviews execution plans for completeness, risk, and verification strategy | Read, Grep, Glob |
| `pm` | opus | Product Manager - requirements analysis, user stories, prioritization | Read, Grep, Glob, WebSearch, WebFetch |
| `qa-engineer` | sonnet | QA Engineer - unit tests, integration tests, bug analysis | Read, Bash, Grep, Glob |
| `security-reviewer` | opus | Security Reviewer - security audits, vulnerability detection, secret protection | Read, Grep, Glob |
| `tech-lead` | sonnet | Tech Lead - architectural refactoring, cross-module design review, tech-debt rulings | Read, Grep, Glob |
| `techdebt-scanner` | sonnet | Tech Debt Analyst - scans tech debt, code health analysis | Read, Bash, Grep, Glob |
| `ui-ux-designer` | sonnet | UI/UX Designer - high-fidelity design output (Phase 3 of the uiux-agent three-phase flow) | Read, Grep, Glob, WebFetch |
| `uiux-agent` | sonnet | UI/UX Design Agent - handles wireframing and critique, does not write production code | Read, Grep, Glob, Task |
| `workflow-optimizer` | sonnet | Workflow Optimizer - reviews Claude Code configuration and developer experience | Read, Grep, Glob |

> All agents also carry `verification_required: true`, `handoff_artifact: docs/plans/active/<task-id>.md`, `context_firewall: true` (omitted from the table above; consistent across every file).

---

## Skills — 17

| Skill | One-line description |
|-------|-----------|
| `beautiful-mermaid` | Generates beautiful, clear Mermaid diagrams (architecture, flowcharts, sequence, class, ER, state diagrams), output as terminal ASCII art or SVG files |
| `code-review` | Standard code review of a PR diff, covering security, quality, and architectural compliance. Standard single-PR review |
| `context-aggregator` | Aggregates multi-source information (MCP memory, git history, local files) into a structured summary for session handoff and work continuity |
| `feature-pipeline` | End-to-end development pipeline for large new features — requirements analysis, architecture design, UI/UX, through multi-agent review in one chain |
| `frontend-design` | Produces high-quality UI components and visual design guidance centered on typography, color, motion, and spatial-composition design philosophy |
| `gen-app-map` | Scans a project's entry points, routes, data layer, and state management to produce app-map.json (an AI-readable context primer) and app-map.html (a human-readable visualization), serving as a lightweight project map for new debug/refactor sessions. Tech-stack-agnostic template — fill in the scan-target table after forking to a specific project |
| `harness-eval` | Scans a target repo, evaluates Harness Engineering maturity, and outputs a 0–100 score, a gap list, and prioritized improvement recommendations |
| `multi-agent-review` | Launches code-reviewer, security-reviewer, and qa-engineer in parallel for an all-around review. Use for high-risk/core-logic changes needing three experts in parallel; use code-review for regular PRs |
| `pr-retro` | After every PR merge, automatically extracts lessons and writes them to ERRORS.md Pending Review, driving continuous improvement of skill docs |
| `pr-review-cycle-mob` | Uses a Cascade tiering strategy to balance cost, speed, and quality, running the optimal PR review flow after AI finishes writing code. Use when a cost-tiered cascade strategy is needed |
| `security-audit` | Full security review covering authentication, key leakage, dependency vulnerabilities, and OWASP standard checks |
| `skill-creator` | (Base version stub, superseded by skill-creator-plus) Use only when the user explicitly types the /skill-creator command; any create/optimize/evaluate-a-skill request should use skill-creator-plus instead |
| `skill-creator-plus` | Guides the complete skill-creation workflow — intent capture, overlap check, drafting, mechanical validation, trigger testing, through registry registration — including the eval iteration method. Supersedes the base skill-creator |
| `spectra-amplifier` | Strengthens a thin requirements description or PRD draft into a complete spec where every requirement carries verifiable acceptance criteria |
| `tdd-workflow` | Runs the Red → Green → Refactor test-driven development cycle, for core business logic and high-reliability requirements |
| `techdebt-scanner` | Systematically scans a project for technical debt (TODO/FIXME, complex functions, duplicated code, etc.) and produces a prioritized report |
| `ui-ux-pro-max` | Produces a complete design system covering color palettes, typography pairings, UI styles, and UX guidelines, across multiple frontend tech stacks |

---

## Commands (`.claude/commands/`)

| Command | File |
|------|------|
| `/last-word` | `.claude/commands/last-word.md` |
| `/techdebt` | `.claude/commands/techdebt.md` |

---

## Model Tiering Strategy

```
haiku  → repetitive tasks, formatting, fixed templates, simple lookups
sonnet → code generation, analysis, general review (default)
opus   → architecture design, complex reasoning, deep analysis
```

See `.claude/rules/cost-optimization.md` for details.

---

## Files that reference this registry

- `agent_docs/multi-agent-guide.md`
- `CLAUDE.md` rule pointer
