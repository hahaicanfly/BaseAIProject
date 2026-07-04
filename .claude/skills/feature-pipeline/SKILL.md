---
name: feature-pipeline
description: 大型新功能的端對端開發流水線，從需求分析、架構設計、UI/UX 到多代理審查一次串接；當使用者要開發新功能、跨模組變更或提及「新功能」「完整開發流程」時觸發。
---

# Skill: feature-pipeline

> **用途**：大型新功能的完整開發流程（PM → Architect → Plan Review → Dev → Code Review）。
> **觸發**：`/feature-pipeline`
> **適用場景**：新功能、架構變更、API 變動

## 執行步驟

1. **[PM]** 建立 ExecPlan，填 §1 Goal + §2 Context
2. **[Architect]** 補完 §3 Constraints + §4 Steps + §5 Verification
3. **[Plan-reviewer]** 審查 §1-§5，通過後輸出 `[HANDOFF: human-approval]`
4. **[Human gate]** 核可計劃，開 feat/branch
5. **[Tech-lead / Dev]** 執行 §4，每步 commit + §6 Progress Log
6. **[Code-reviewer]** VERIFYING，補 §7 Decision Log
7. **[Human gate]** PR review → merge

每次派工必須照 `.claude/templates/delegation-templates.md` 三件套（目標動機/驗收條件/回報格式）。

## ExecPlan 路徑

`docs/plans/active/F-NNN-<slug>.md`

## 參考

- `.claude/protocols/execplan-lifecycle.md`
- `docs/plans/PLANS.md`
