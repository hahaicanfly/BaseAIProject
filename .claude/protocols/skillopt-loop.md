# SkillOpt Loop Protocol

> ⚠ Status: unwired design draft. No hook/cron actually executes this loop; no other document may cite it as an effective rule. Whether to wire it in or delete it is pending human decision.

> **Role**: Defines the Harness system's "self-improvement loop" — how failure signals from PRs get turned into better skill documents.
> **Theoretical basis**: SkillOpt: Optimizing Agent Skills as External Text State (Microsoft Research et al., 2026-05) [Unconfirmed: unable to verify this source exists].
> **Core insight**: An agent skill document = a frozen model's trainable external state; apply MLOps discipline to training text rather than model weights.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     SkillOpt Loop                               │
│                                                                 │
│  ┌────────────┐   rollout    ┌──────────────────────────────┐   │
│  │  PR / Task │─evidence──▶  │  pr-review-cycle-mob         │   │
│  │  execution │             │  (scored trajectories)       │   │
│  └────────────┘             └──────────────┬───────────────┘   │
│                                            │ fail signals       │
│                                            ▼                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  pr-retro  (minibatch reflection)                        │    │
│  │  ・Case A: re-triggers an existing lesson                │    │
│  │  ・Case B: new lesson → Pending Review                   │    │
│  │  ・Case C: skill doc edit candidate                     │    │
│  │  ・Case D: INV-* candidate                              │    │
│  └────────────────────────────┬────────────────────────────┘    │
│                               │ candidates                      │
│                               ▼                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ERRORS.md Pending Review  (rejected-edit buffer)         │    │
│  └────────────────────────────┬────────────────────────────┘    │
│                               │ human weekly review (validation gate) │
│                               ▼                                 │
│  ┌──────────────┐    ┌────────────────────┐                     │
│  │ ERRORS.md    │    │ .claude/agents/    │                     │
│  │ Active       │    │ .claude/skills/    │  (epoch-wise update) │
│  │ Lessons      │    │ invariants.md      │                     │
│  └──────────────┘    └────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Loop Participants and Responsibilities

| Role | Tool/Skill | SkillOpt Component |
|------|-----------|--------------|
| PR execution + hooks | `pre-tool-use-guard` / `post-edit-lint` | rollout + scoring |
| Cascade review | `pr-review-cycle-mob` | scored trajectories |
| Lesson extraction | `pr-retro` | minibatch reflection |
| Candidate collection | `ERRORS.md Pending Review` | rejected-edit buffer |
| Human weekly review | Every Sunday evening, manual promotion | validation gate |
| Document update | Direct edits to `.claude/agents/*.md` / `invariants.md` | bounded text edit |

---

## Learning Rate (Textual Learning Rate)

At each weekly review, promote **at most** this many lessons:

| Lessons this week | Max promoted | Analogy |
|-------------|-------------|------|
| 1–3 | All of them | learning rate = 1.0 |
| 4–7 | 3–4 | learning rate = 0.5 |
| 8+ | 3 | learning rate = 0.3 (prevents catastrophic forgetting) |

**Principle**: better to learn slowly than to make one big edit to the skill docs and destabilize the system.
**Priority**: promote Case D lessons first (mechanically verifiable), then Case C, then Case B.

---

## Validation Gate (how to decide whether a lesson is worth promoting)

Ask these 3 questions before promoting:

1. **Reproducibility**: has this error occurred in ≥2 different PRs/sessions?
   - Yes → promote, priority HIGH
   - No (occurred only once) → leave in Pending Review, observe for another week

2. **Preventability**: would adding this lesson/INV let pre-tool-use-guard or post-edit-lint catch it next time?
   - Yes → update `invariants.md` + the hook's `QUICK_CHECKS` together
   - No → only add it to ERRORS.md Active Lessons (as an LLM review reference)

3. **No side effects**: could this lesson cause false positives that block normal workflow?
   - Possible false positives → don't promote yet; narrow the pattern and re-evaluate

---

## Protected Regions (epoch-wise slow update)

The following sections of the following files are **protected** and may not be modified except through the weekly review:

| File | Protected Section | Reason |
|------|--------------|------|
| `CLAUDE.md` | `## Hard Guardrails` | Core safety constraints; must not change frequently |
| `docs/architecture/invariants.md` | `INV-GIT-*` | Git rules are stable; casual changes carry high risk |
| `.claude/hooks/pre-tool-use-guard.py` | enforce logic | A mistaken edit could open a security hole |

Modifying a protected region requires an ADR (`docs/decisions/ADR-NNNN-*.md`).

---

## Rejected-Edit Buffer Format (ERRORS.md Pending Review)

Every Pending Review entry must use this format, for fast decisions during weekly review:

```
### [YYYY-MM-DD] [Category] [Case B/C/D]
**Triggering PR**: feat/xxx or session date
**Problem**: [one-sentence description]
**Root cause**: [why it happened]
**Candidate action**:
  Case B: - [date] [category] description → correct approach
  Case C: [SKILL_EDIT_CANDIDATE] file + section + how to change it
  Case D: INV-[NS]-[NNN] CHECK: [grep] HOOK: [hook name]
**Reproduction count**: 1 (first occurrence)
**Weekly review decision**: □ Promote  □ Reject  □ Keep observing
```

---

## SkillOpt Readiness Checklist

When `/harness-eval`'s D8 score is < 5, fill these in, in order:

- [ ] `state/hook-events.jsonl` has rollout evidence (hooks are actually logging)
- [ ] `ERRORS.md` has both a Pending Review and an Active Lessons section
- [ ] `pr-review-cycle-mob` has defined cascade scoring criteria
- [ ] `pr-retro` can trigger automatically (integrated with stop-retro-logger)
- [ ] At least 1 human weekly review has been recorded (confirms the process actually runs)

D8 = 5 → Harness reaches Level 5 SkillOpt-Ready.

---

## Where This File Is Referenced

(No file references this protocol yet.)
