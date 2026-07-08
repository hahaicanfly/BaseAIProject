---
name: multi-agent-review
description: 並行啟動 code-reviewer、security-reviewer、qa-engineer 三位專家代理做全方位審查；當使用者要對高風險變更、核心邏輯或 PR 進行綜合審查時觸發。高風險/核心邏輯變更，需要三專家並行時用；一般 PR 用 code-review。
---

# Skill: multi-agent-review

> **用途**：並行啟動三個 reviewer（code-reviewer + security-reviewer + qa-engineer）做全方位審查，模擬 Code Review Swarm 模式。
> **觸發**：`/multi-agent-review`
> **適用場景**：高風險變更、涉及 auth/security、核心業務邏輯

## 使用方式

```
/multi-agent-review [檔案路徑或模組名稱]
```

## 協作模式

本 skill 同時啟動以下代理進行並行審查：

| 代理 | 職責 | 工具 |
|------|------|------|
| **code-reviewer** | 代碼品質、架構遵循、convention | Read, Bash, Grep, Glob |
| **security-reviewer** | 安全漏洞、金鑰洩漏、auth/secret | Read, Grep, Glob |
| **qa-engineer** | 可測試性、測試覆蓋、edge case | Read, Bash, Grep, Glob |

## 執行流程

### Phase 1: Fan-out 並行審查

使用 Agent 工具同時啟動三個專家代理（見 `.claude/protocols/review-protocol.md` 並行 review fan-out 圖）：

```
1. 啟動 code-reviewer 代理 → 代碼品質審查
2. 啟動 security-reviewer 代理 → 安全審查
3. 啟動 qa-engineer 代理 → 測試審查
```

每個 reviewer 各自讀 ExecPlan（`docs/plans/active/F-NNN-*.md`）與 `docs/architecture/invariants.md`，不得只看 diff——否則會漏掉 Constraints 引用的 INV-id。

### Phase 2: 結果整合

收集所有代理的審查結果，整合成統一報告，並把 Aggregated Decision 同步寫入 ExecPlan §7 Decision Log（一行 summary）。

### Phase 3: 行動建議

根據所有審查結果，提供優先級排序的行動清單。

## 並行注意事項

- subagent 內 `git checkout` 可能改 branch，主對話 commit 前再次 `git branch --show-current`
- 三方 Report 需全部 Pass 才進入 human-pr-review

## 輸出範本

```markdown
## Multi-Agent Review Report: [目標]

### 審查摘要

| 代理 | 評價 | 問題數 |
|------|------|--------|
| code-reviewer | [Pass/Block] | [N] |
| security-reviewer | [Pass/Block] | [N] |
| qa-engineer | [Pass/Block] | [N] |

### Critical Issues (必須修復)

#### [來源代理] 問題標題
- **位置**: `path/file:line`
- **描述**: [問題]
- **修復**: [建議]

### High Priority (應該修復)
[同上格式]

### Medium Priority (建議改進)
[同上格式]

### 行動計劃

1. [ ] [最高優先級任務]
2. [ ] [次優先級任務]
3. [ ] [一般任務]

### Aggregated Decision
[HANDOFF: dev | human-pr-review]

### 各代理完整報告

<details>
<summary>code-reviewer Report</summary>
[完整報告]
</details>

<details>
<summary>security-reviewer Report</summary>
[完整報告]
</details>

<details>
<summary>qa-engineer Report</summary>
[完整報告]
</details>
```

## 使用場景

- **PR 審查**：在合併前進行全面檢查
- **上線前審查**：重要功能發布前的最終確認
- **技術債清理**：識別需要優先處理的問題
- **新成員代碼**：確保符合團隊標準

## 成本考量

此 skill 會啟動多個代理，消耗較多資源。建議用於：
- 核心模組變更
- 重要功能上線前
- 定期代碼健康檢查

日常小改動建議使用單一的 `/code-review`。

## 驗證項目

- **產出形式**：3 份獨立 reviewer 報告（code-reviewer + security-reviewer + qa-engineer）+ 主對話聚合 summary。
- **並行性檢查**：3 個 sub-agent 各自最末行必為 `[HANDOFF: <main>]` marker。
- **ExecPlan 整合**：聚合 summary 一段寫入 §7 Decision Log，個別細項各 reviewer 自行依 review-protocol.md 處理。
- **失敗模式**：任一 reviewer 報 Blocker → 主對話輸出 `[HANDOFF: dev]`，禁止繼續到 PR。

## 參考

- `.claude/protocols/review-protocol.md`
- `.claude/agents/code-reviewer.md`
- `.claude/agents/security-reviewer.md`
- `.claude/agents/qa-engineer.md`
- `.claude/templates/delegation-templates.md`
