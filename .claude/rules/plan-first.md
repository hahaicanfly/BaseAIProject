---
name: plan-first
description: Non-trivial tasks must enter Plan Mode first (except ExecPlan scope — see CLAUDE.md decision tree)
always: true
---

# Plan First Rule

*白話:不是芝麻小事的任務,先讓 Claude 寫一份計畫給你看過、你同意了才會動手做,不會沒說一聲就直接改東西。*

## Principle

**Before executing any non-trivial task, you must first enter Plan Mode(白話:先寫一份計畫給你看過、你同意後才開始做,不是立刻動手改檔案) and write a plan for the user to review.**

> Entry point follows CLAUDE.md's "Decision Tree Before Acting": cross-module / API changes / large-scale refactors go through **ExecPlan**(白話:規模較大、跨檔案或跨模組的正式計畫文件,一樣要你同意才會執行,只是流程比 Plan Mode 更完整) (`docs/plans/PLANS.md`, requires human approval) and are not covered by this file; this file covers all other non-trivial tasks.

## Applicable Situations

The following situations require a plan first (situations already covered by ExecPlan scope go through ExecPlan, not duplicated here):
- New feature implementation
- Changes affecting multiple files
- Decisions involving security or cost
- Deleting or moving files

## Exceptions

The following can be executed directly:
- Small single-file changes (< 20 lines)
- Formatting adjustments
- Comment updates
- A clearly identified bug fix (root cause already located)
- User explicitly instructs "just do it"

## Plan Content

```markdown
## Execution Plan: [Task Name]

### Goal
[What to achieve]

### Scope
- Files: [list]
- Modules: [list]

### Execution Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Risk Assessment
- [Potential risks and mitigations]

### Verification Method
- [How to confirm completion]
```

## Workflow

1. Analyze task requirements
2. Enter Plan Mode
3. Write the execution plan
4. **Wait for user confirmation**
5. Begin implementation only after user agrees
6. Execute per the plan
7. Report results on completion

## Why This Matters

- Ensures the direction of development matches user expectations
- Avoids large amounts of wasted work
- Provides an opportunity for review and correction
- Establishes a traceable decision record
