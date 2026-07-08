---
name: feature-pipeline
description: 大型新功能的端對端開發流水線，從需求分析、架構設計、UI/UX 到多代理審查一次串接；當使用者要開發新功能、跨模組變更或提及「新功能」「完整開發流程」時觸發。
---

# Feature Pipeline Skill

模擬 Feature Factory 模式，按流水線順序執行完整的功能開發流程，對應 ExecPlan 10 階段生命週期（`.claude/protocols/execplan-lifecycle.md`）。

## 使用方式

```
/feature-pipeline [功能描述]
```

## 流水線階段

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│   PM    │ ─▶ │Architect│ ─▶ │UI/UX    │ ─▶ │開發實作 │ ─▶ │ Review  │
│需求分析 │    │架構設計 │    │界面設計 │    │         │    │多代理審查│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### Stage 1: 需求分析（pm agent）

**觸發條件**：收到功能請求
**輸出**：建立 ExecPlan `docs/plans/active/F-NNN-<slug>.md`，填 §1 Goal + §2 Context（部分）、用戶故事、驗收條件

```markdown
## 需求分析

### 用戶故事
作為 [角色]，我想要 [功能]，以便 [價值]

### 驗收條件
- [ ] AC1: [條件]
- [ ] AC2: [條件]

### 優先級
[P0/P1/P2]

### 範圍界定
- 包含: [範圍內的功能]
- 排除: [明確不做的事]
```

**Exit**：`[HANDOFF: architect]`

### Stage 2: 架構設計（architect agent）

**觸發條件**：需求分析完成
**輸出**：補完 ExecPlan §3 Constraints（含 INV-id）+ §4 Step-by-step + §5 Verification Strategy

```markdown
## 架構設計

### 技術方案
[設計概述]

### 影響範圍
- 檔案: [列表]
- 模組: [列表]

### API 設計 (如適用)
[介面定義]

### 資料模型變更 (如適用)
[模型變更]

### 風險評估
[潛在風險，引用 docs/architecture/invariants.md 相關 INV-id]
```

**Exit**：`[HANDOFF: plan-reviewer]` → `plan-reviewer` 審查通過後 `[HANDOFF: human-approval]`（人類核可 ExecPlan §1-§5，見 execplan-lifecycle.md Phase 3）

### Stage 3: UI 設計（uiux-agent，如涉及 UI）

**觸發條件**：架構設計完成且涉及 UI 變更
**執行**：進入 `.claude/uiux/WORKFLOW.md` 三階段流程（草圖 → 評審 → 實作），每階段須獲用戶「OK」才進下一階段，禁止跳階段
**輸出**：UI 規格、組件設計、互動流程

```markdown
## UI 設計

### 畫面規格
[規格描述]

### 組件設計
[使用/新增的組件]

### 互動流程
[用戶操作流程]
```

**跳過條件**：純後端 / 無 UI 變更的功能可跳過本階段，直接進 Stage 4

### Stage 4: 開發實作（dev = 主對話 + 具 Bash 的實作 subagent）

**觸發條件**：人類核可 ExecPlan（Stage 2 human-approval gate 通過），開 `feat/<slug>` 分支
**執行**：按 ExecPlan §4 逐步實作，每完成一步立即 commit 並 append 一行到 §6 Progress Log；`tech-lead` 僅負責 review / 規範檢查，不執行 commit
**鐵律**：每次 commit 前 `git branch --show-current`（不得在 master/main 上 commit）
**Exit**：§4 全打勾 → `[HANDOFF: code-reviewer]`

### Stage 5: 多代理審查

**觸發條件**：實作完成
**執行**：自動觸發 `/multi-agent-review` skill（code-reviewer + security-reviewer + qa-engineer 並行審查）
**Exit**：全 Pass → `[HANDOFF: human-pr-review]`；有 Blocker → 回 Stage 4 修復

## 中斷機制

任何階段發現阻礙問題時：
1. 暫停流水線，於 ExecPlan §8 Open Questions 寫明阻礙
2. 輸出 `[HUMAN_ATTENTION_REQUIRED: <reason>]`，回報問題給用戶
3. 等待用戶決策
4. 根據決策繼續或調整（見 execplan-lifecycle.md Phase 9 BLOCKED）

## 輸出範本

```markdown
## Feature Pipeline: [功能名稱]

### 進度追蹤

| 階段 | 狀態 | 負責 |
|------|------|------|
| 需求分析 | ✅ | pm |
| 架構設計 | ✅ | architect |
| UI 設計 | ⏳ | uiux-agent |
| 開發實作 | ⬜ | dev |
| 代碼審查 | ⬜ | multi-agent-review |

### 當前階段輸出
[當前階段的產出]

### 下一步
[接下來要做什麼]
```

## 適用場景

- 新功能開發
- 重大功能重構
- 跨模組變更

## 注意事項

- 每個階段完成後需用戶確認（人類 gate 見 execplan-lifecycle.md Phase 3、Phase 7）
- 可以跳過不適用的階段（如無 UI 變更可跳過 Stage 3）
- 保持階段產出簡潔，避免過度設計
- 每次派工必須照 `.claude/templates/delegation-templates.md` 三件套（目標動機 / 驗收條件 / 回報格式）

## ExecPlan 路徑

`docs/plans/active/F-NNN-<slug>.md`

## 驗證項目

- **產出形式**：完整 ExecPlan `docs/plans/active/F-NNN-*.md`（9 段齊全）+ commits 序列 + PR。
- **必經閘門**：pm → architect → plan-reviewer → human-approval → dev → code-reviewer → human-pr-review。
- **每階段 marker**：依 `.claude/protocols/handoff-protocol.md` 規範，逐步 `[HANDOFF: <next>]`。
- **完成判定**：PR merged → ExecPlan 移到 `docs/plans/completed/` + `state/feature-list.json` `status: done`。
- **失敗模式**：任一階段違反 invariant → `[VERIFY_FAILED: INV-id]` 退回上一階段。

## 參考

- `.claude/protocols/execplan-lifecycle.md`
- `docs/plans/PLANS.md`
- `.claude/uiux/WORKFLOW.md`
- `.claude/protocols/handoff-protocol.md`
