# {{PROJECT_NAME}} — Docs Index

> This directory holds all design documents, architecture decisions, plans, and learning records.
> Every agent must check this INDEX before reading a document, to avoid reading the wrong version.

---

## Architecture Documents

| File | Purpose |
|------|------|
| [`architecture/invariants.md`](architecture/invariants.md) | Mechanically verifiable hard rules (INV-*), referenced directly by hooks |
| [`architecture/domains.md`](architecture/domains.md) | Domain boundaries and change-impact assessment table |

---

## Plan System

| File / Directory | Purpose |
|------------|------|
| [`plans/PLANS.md`](plans/PLANS.md) | ExecPlan spec and template |
| [`plans/active/`](plans/active/) | In-progress ExecPlan instances (version-controlled) |
| [`plans/completed/`](plans/completed/) | Completed ExecPlans (archived, version-controlled) |

---

## Architecture Decision Records (ADR)

| File | Status | Summary |
|------|------|------|
| [`decisions/ADR-template.md`](decisions/ADR-template.md) | Template | ADR authoring template |
| [`decisions/PDR-template.md`](decisions/PDR-template.md) | Template | Product Decision Record authoring template (product/feature decisions, not architecture — see file header for when PDR is mandatory) |

> When adding an ADR: `decisions/ADR-NNNN-<short-slug>.md`, and add a row to this table.
> When adding a PDR: `decisions/PDR-NNNN-<short-slug>.md`, and add a row to this table.

---

## Strategy & Market Research Reports

| File / Directory | Purpose |
|------------|------|
| [`research/README.md`](research/README.md) | Filing point + naming rule (`docs/research/<YYYY-MM-DD>-<slug>.md`) for pm / market-researcher / competitive-analyst / data-analyst output; every report requires a 假設-證據表 and a Sources section, reviewed via review-protocol.md's Document Reviewer Checklist |

---

## Accumulated Lessons

| File | Purpose |
|------|------|
| [`learnings/ERRORS.md`](learnings/ERRORS.md) | AI mistake log (Pending Review → Active Lessons) |

---

## Harness Institution Documents (established 2026-07-04)

| File | Purpose |
|------|------|
| [`harness/DIAGNOSIS.md`](harness/DIAGNOSIS.md) | Leak diagnosis: top-3 token leaks / focus loss / error-prone spots + fixes + capability limits |
| [`harness/LETTER-TO-FUTURE-SESSIONS.md`](harness/LETTER-TO-FUTURE-SESSIONS.md) | Letter to future sessions + outstanding handoff checklist |
| `../.claude/rules/model-dispatch.md` | Model dispatch rules (standing) |
| `../.claude/rules/judgment-rubrics.md` | Judgment externalization matrix (standing) |
| `../.claude/templates/delegation-templates.md` | 6 delegation prompt templates |
| `../.claude/protocols/harness-maintenance.md` | Harness file maintenance protocol (permission tiers / lesson format / pruning triggers) |

---

## Knowledge Map (who writes, who reads, when it flows)

| Layer | Location | Written by | Read by | Flow rule |
|----|------|------|------|----------|
| Lessons | `docs/learnings/ERRORS.md` | Auto-appended by hooks + manually by models; human weekly review promotes | All agents | Mechanizable ones get promoted to invariants |
| Hard rules | `docs/architecture/invariants.md` | Humans (red tier) | Hooks and all agents | Promoted from ERRORS |
| Architecture decisions | `docs/decisions/ADR-*.md` | Human-approved | Planning agents | Does not flow back |
| Session snapshots | `state/session-handoffs/` | Auto by pre-compact-snapshot.py | Continuing sessions | Read-only, does not flow back |
| Native memory | `~/.claude/projects/<proj>/memory/` | Auto by Claude Code | Next session's Claude | **Only cross-session metrics and personal preferences allowed; lessons always go through ERRORS.md — once promoted, delete the full text from memory and keep only the pointer** |

---

## Where This File Is Referenced

- `CLAUDE.md`: Document Map ("full document index")
- `docs/plans/PLANS.md` §5

---

## Chinese Mirror Convention

Human-readable Chinese versions of files in auto-discovered directories (agents/rules/commands) live under `agent_docs/zh/`. All other files use a same-directory `*_zh.md` suffix (e.g. `CLAUDE_zh.md`).
