---
name: feature-pipeline
description: End-to-end development pipeline for large new features — requirements analysis, architecture design, UI/UX, through multi-agent review in one chain; triggers when the user wants to develop a new feature, make a cross-module change, or mentions "新功能", "完整開發流程".
---

# Feature Pipeline Skill

Simulates a Feature Factory pattern, executing the full feature-development flow in pipeline order, mapped to the ExecPlan 10-phase lifecycle (`.claude/protocols/execplan-lifecycle.md`).

## Usage

```
/feature-pipeline [feature description]
```

## Pipeline Stages

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│   PM    │ ─▶ │Architect│ ─▶ │ UI/UX   │ ─▶ │  Dev    │ ─▶ │ Review  │
│Requirements│ │Architecture│ │  Design │    │Implement│    │Multi-agent│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### Stage 1: Requirements Analysis (pm agent)

**Trigger condition**: a feature request is received
**Output**: create ExecPlan `docs/plans/active/F-NNN-<slug>.md`, filling in §1 Goal + §2 Context (partial), user stories, acceptance criteria

```markdown
## Requirements Analysis

### User Story
As a [role], I want [feature], so that [value]

### Acceptance Criteria
- [ ] AC1: [condition]
- [ ] AC2: [condition]

### Priority
[P0/P1/P2]

### Scope
- Included: [in-scope features]
- Excluded: [explicitly out of scope]
```

**Exit**: `[HANDOFF: architect]`

### Stage 2: Architecture Design (architect agent)

**Trigger condition**: requirements analysis complete
**Output**: complete ExecPlan §3 Constraints (with INV-ids) + §4 Step-by-step + §5 Verification Strategy

```markdown
## Architecture Design

### Technical Approach
[design overview]

### Impact Scope
- Files: [list]
- Modules: [list]

### API Design (if applicable)
[interface definitions]

### Data Model Changes (if applicable)
[model changes]

### Risk Assessment
[potential risks, referencing relevant INV-ids in docs/architecture/invariants.md]
```

**Exit**: `[HANDOFF: plan-reviewer]` → once `plan-reviewer` approves, `[HANDOFF: human-approval]` (human approval of ExecPlan §1-§5, see execplan-lifecycle.md Phase 3)

### Stage 3: UI Design (uiux-agent, if UI is involved)

**Trigger condition**: architecture design complete and UI changes are involved
**Execution**: enter the three-phase flow in `.claude/uiux/WORKFLOW.md` (sketch → review → implement); each phase requires the user's "OK" before proceeding — skipping phases is prohibited
**Output**: UI spec, component design, interaction flow

```markdown
## UI Design

### Screen Spec
[spec description]

### Component Design
[components used/added]

### Interaction Flow
[user interaction flow]
```

**Skip condition**: pure backend / no UI change features can skip this stage and go directly to Stage 4

### Stage 4: Development (dev = main conversation + implementation sub-agent with Bash)

**Trigger condition**: human approves the ExecPlan (Stage 2 human-approval gate passed), open a `feat/<slug>` branch
**Execution**: implement step by step per ExecPlan §4, committing immediately after each step and appending one line to §6 Progress Log; `tech-lead` only handles review / convention checks, and does not commit
**Hard rule**: `git branch --show-current` before every commit (must not commit on master/main)
**Exit**: all §4 items checked → `[HANDOFF: code-reviewer]`

### Stage 5: Multi-Agent Review

**Trigger condition**: implementation complete
**Execution**: auto-triggers the `/multi-agent-review` skill (parallel review by code-reviewer + security-reviewer + qa-engineer)
**Exit**: all Pass → `[HANDOFF: human-pr-review]`; if there's a Blocker → back to Stage 4 for fixes

## Interrupt Mechanism

If any stage encounters a blocking issue:
1. Pause the pipeline, document the blocker in ExecPlan §8 Open Questions
2. Output `[HUMAN_ATTENTION_REQUIRED: <reason>]`, report the issue to the user
3. Wait for the user's decision
4. Continue or adjust based on the decision (see execplan-lifecycle.md Phase 9 BLOCKED)

## Output Template

```markdown
## Feature Pipeline: [Feature Name]

### Progress Tracking

| Stage | Status | Owner |
|------|------|------|
| Requirements Analysis | ✅ | pm |
| Architecture Design | ✅ | architect |
| UI Design | ⏳ | uiux-agent |
| Development | ⬜ | dev |
| Code Review | ⬜ | multi-agent-review |

### Current Stage Output
[current stage's output]

### Next Step
[what comes next]
```

## Applicable Scenarios

- New feature development
- Major feature refactoring
- Cross-module changes

## Notes

- Each stage requires user confirmation before proceeding (human gates — see execplan-lifecycle.md Phase 3, Phase 7)
- Inapplicable stages can be skipped (e.g. skip Stage 3 if there's no UI change)
- Keep stage outputs concise; avoid over-engineering
- Every dispatch must follow the three-part template in `.claude/templates/delegation-templates.md` (goal & motivation / acceptance criteria / report format)

## ExecPlan Path

`docs/plans/active/F-NNN-<slug>.md`

## Verification Items

- **Output form**: a complete ExecPlan `docs/plans/active/F-NNN-*.md` (all 9 sections filled) + commit sequence + PR.
- **Required gates**: pm → architect → plan-reviewer → human-approval → dev → code-reviewer → human-pr-review.
- **Per-stage marker**: `[HANDOFF: <next>]` at each step, per `.claude/protocols/handoff-protocol.md`.
- **Completion criteria**: PR merged → ExecPlan moved to `docs/plans/completed/` + `state/feature-list.json` `status: done`.
- **Failure mode**: any stage violating an invariant → `[VERIFY_FAILED: INV-id]`, rolled back to the previous stage.

## References

- `.claude/protocols/execplan-lifecycle.md`
- `docs/plans/PLANS.md`
- `.claude/uiux/WORKFLOW.md`
- `.claude/protocols/handoff-protocol.md`
