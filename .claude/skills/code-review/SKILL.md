---
name: code-review
description: 對 PR diff 進行標準代碼審查，涵蓋安全性、品質與架構合規；當使用者要求審查代碼、PR review、品質稽核或提及「審查」「檢查代碼」時觸發。單一 PR 的標準審查。
---

# Skill: code-review

> **用途**：單一 reviewer 對 PR diff 進行標準代碼審查。
> **觸發**：`/code-review`
> **Agent**：code-reviewer（sonnet）

## 使用方式

```
/code-review [檔案路徑或功能名稱；未指定則審查當前 branch 與 master 的完整 diff]
```

## 執行步驟

1. **範圍確認**：確認要審查的檔案/目錄，了解變更目的與背景
2. 讀 active ExecPlan（`docs/plans/active/F-NNN-*.md`）的 §3 Constraints + §5 Verification Strategy；無 ExecPlan 的小改動可跳過
3. 讀 `docs/architecture/invariants.md` 相關 INV-id
4. 執行 `git diff master...HEAD`
5. 逐條驗證，依下列面向檢查（規則全文見對應檔案，本節不重複列出）：
   - **安全（優先）**：無硬編碼金鑰/密碼、無敏感資訊寫入日誌、輸入驗證、錯誤處理不洩漏內部細節 —— 詳 `.claude/rules/security.md`
   - **代碼品質**：命名規範遵循、函數單一職責、適當錯誤處理、無明顯效能問題
   - **架構遵循**：模組結構正確、依賴方向正確（依賴抽象而非具體實作）、可復用邏輯放共享模組 —— 詳 `agent_docs/modularity.md`
   - **測試覆蓋**：核心邏輯有對應測試、測試命名清晰、測試彼此獨立
   - **成本考量**（如涉及 API 調用）：呼叫有快取、資源使用有上限、可本地化運算未誤發雲端 API —— 詳 `.claude/rules/cost-optimization.md`
6. 輸出 Review Report（Blockers / Warnings / Suggestions / Praise，格式見下）
7. 同步寫入 ExecPlan §7 Decision Log（一行 summary）

## 輸出格式

```markdown
# Review Report — F-NNN

**Reviewer**: code-reviewer
**Scope**: <git range>
**Generated**: YYYY-MM-DD

## Findings
### Blockers
### Warnings
### Suggestions
### Praise

## Decision
Pass / Block / Conditional Pass

[HANDOFF: dev | human-pr-review]
```

## 開始前檢查

- CLAUDE.md（專案規範、Quick Commands）
- 專案是否另有代碼規範文件或安全政策文件（依專案結構，若無則跳過）

## 適用範圍與升級路徑

本 skill 是**單一 reviewer 對單一 PR** 的標準審查。遇到以下情況改走 `multi-agent-review` skill（並行派 code-reviewer / security-reviewer / qa-engineer 三人）：
- 高風險變更（auth、金鑰處理、資料遷移）
- 核心業務邏輯的大範圍重構
- 單一 reviewer 的 Decision 為 Block 且需要第二意見（見 `.claude/rules/model-dispatch.md` §5 驗證不自驗）

## 參考

- `.claude/protocols/review-protocol.md`（完整 severity 定義與 checklist，本檔不重複）
- `docs/architecture/invariants.md`
- `.claude/rules/security.md`
- `agent_docs/modularity.md`（非常駐設計指引）
- `.claude/rules/cost-optimization.md`
