---
name: multi-agent-review
description: 並行啟動 code-reviewer、security-reviewer、qa-engineer 三位專家代理做全方位審查；當使用者要對高風險變更、核心邏輯或 PR 進行綜合審查時觸發。高風險/核心邏輯變更，需要三專家並行時用；一般 PR 用 code-review。
---

# Skill: multi-agent-review

> **用途**：並行啟動三個 reviewer（code-reviewer + security-reviewer + qa-engineer）做全方位審查。
> **觸發**：`/multi-agent-review`
> **適用場景**：高風險變更、涉及 auth/security、核心業務邏輯

## 執行步驟

1. Fan-out：同時啟動三個 subagent
   - code-reviewer：邏輯/架構/convention
   - security-reviewer：auth/secret/漏洞
   - qa-engineer：測試覆蓋/edge case
2. 每個 reviewer 各自讀 ExecPlan + invariants
3. Aggregate：匯總三份 Report 到 ExecPlan §7

每次派工必須照 `.claude/templates/delegation-templates.md` 三件套（目標動機/驗收條件/回報格式）。

## 並行注意事項

- subagent 內 `git checkout` 可能改 branch
- 主對話 commit 前再次 `git branch --show-current`
- 三方 Report 需全部 Pass 才進入 human-pr-review

## 輸出格式

```markdown
# Multi-Agent Review — F-NNN

## code-reviewer: [Pass/Block]
## security-reviewer: [Pass/Block]
## qa-engineer: [Pass/Block]

## Aggregated Decision
[HANDOFF: dev | human-pr-review]
```

## 參考

- `.claude/protocols/review-protocol.md`
- `.claude/agents/code-reviewer.md`
- `.claude/agents/security-reviewer.md`
- `.claude/agents/qa-engineer.md`
