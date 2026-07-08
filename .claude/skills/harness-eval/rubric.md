# Harness Eval — Scoring Matrix (Rubric)

> **Version**: v1.0 (first version after adding D8 from the SkillOpt paper)
> **Update policy**: bump the version and adjust weights once harness-eval has run against 3+ real repos and feedback has been collected.

---

## Scoring Matrix

### D1 — Constitutional Layer (max 15)

| Check | Points | Scoring logic |
|--------|------|---------|
| `CLAUDE.md` exists and is > 100 chars | 3 | present=3, empty shell=0 |
| Has a role definition section | 2 | present=2 |
| Has a token budget strategy (3-tier reading or equivalent) | 3 | present=3, mentioned but incomplete=1 |
| Has privacy / no-read rules | 2 | present=2 |
| Number in `.claude/rules/` | 5 | 0=0, 1-2=2, 3-4=3, 5+=5 |

### D2 — Agent Coverage (max 10)

| Check | Points | Scoring logic |
|--------|------|---------|
| `.claude/agents/` exists | 2 | present=2 |
| Number of agents | 4 | 0=0, 1-3=1, 4-7=2, 8-11=3, 12+=4 |
| Core 5 roles present (pm+architect+tech-lead+security+qa) | 4 | 0.8 pts each, rounded |

### D3 — Hook System (max 20, highest weight)

| Check | Points | Scoring logic |
|--------|------|---------|
| `pre-tool-use-guard.py` exists | 4 | present=4 |
| `post-edit-lint.py` exists | 3 | present=3 |
| `pre-compact-snapshot.py` exists | 2 | present=2 |
| `stop-retro-logger.py` exists | 2 | present=2 |
| All 4 hooks registered in `settings.json` | 3 | all=3, partial pro-rated |
| `QUICK_CHECKS` in `post-edit-lint.py` is non-empty | 3 | real patterns=3, empty array=0 |
| `pre-tool-use-guard.py` has enforce logic | 3 | actually blocks=3, pass-through=0 |

### D4 — Invariants INV-\* (max 15)

| Check | Points | Scoring logic |
|--------|------|---------|
| `docs/architecture/invariants.md` exists | 3 | present=3 |
| `INV-GIT-*` rules defined (≥2) | 3 | ≥2=3, 1=1, 0=0 |
| `INV-SEC-*` rules have real patterns (not TODO) | 4 | real grep pattern=4, TODO only=1, none=0 |
| Project-specific INV rules (non-GIT/generic) | 5 | ≥3=5, 1-2=2, 0=0 |

### D5 — ExecPlan System (max 10)

| Check | Points | Scoring logic |
|--------|------|---------|
| `docs/plans/PLANS.md` exists and isn't a pure template | 2 | present=2 |
| `docs/plans/active/` + `completed/` exist | 2 | both=2, one=1 |
| ≥1 completed ExecPlan exists (.md, not .gitkeep) | 4 | present=4, active-only=1, all empty=0 |
| `execplan-lifecycle.md` exists | 2 | present=2 |

### D6 — Memory & Retro Loop (max 15)

| Check | Points | Scoring logic |
|--------|------|---------|
| `docs/learnings/ERRORS.md` exists | 2 | present=2 |
| `ERRORS.md` Active Lessons is non-empty (real lessons) | 5 | ≥3=5, 1-2=2, empty=0 |
| `state/SCHEMA.md` exists | 2 | present=2 |
| `state/` has a `.gitignore` | 2 | present=2 |
| `state/` has real runtime data (jsonl or session-handoffs/) | 4 | has data=4, empty dir=0 |

### D7 — Skills & Commands (max 10)

| Check | Points | Scoring logic |
|--------|------|---------|
| `.claude/skills/` exists | 1 | present=1 |
| Number of skills | 3 | 0=0, 1-3=1, 4-7=2, 8+=3 |
| Skills with substantive content (not pure stub, > 100 chars with concrete steps) | 4 | ≥3=4, 1-2=2, 0=0 |
| `/last-word` command exists | 2 | present=2 |

### D8 — SkillOpt Loop Readiness (max 5)

| Check | Points | Scoring logic |
|--------|------|---------|
| Hook has a jsonl logging mechanism (rollout evidence) | 2 | `hook-events.jsonl` format present=2 |
| `ERRORS.md` has the dual-section structure (Pending Review + Active Lessons) | 2 | both sections=2, one only=1 |
| Skill update trigger is defined (when to change which file) | 1 | present=1 (explicit in a protocol or CLAUDE.md) |

---

## Level Calculation

| Total score | Level | Label |
|------|------|------|
| 0–20 | L0 | No Harness |
| 21–40 | L1 | Basic |
| 41–60 | L2 | Structured |
| 61–80 | L3 | Process-Aware |
| 81–95 | L4 | Self-Monitoring |
| 96–100 | L5 | SkillOpt-Ready |

---

## Rubric Change Log

| Version | Date | Summary of changes |
|------|------|---------|
| v1.0 | 2026-05-28 | Initial version, integrated the SkillOpt D8 dimension |
