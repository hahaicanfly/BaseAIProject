---
name: context-aggregator
description: 聚合 MCP 記憶、Git 歷史、本地檔案等多來源資訊，產出結構化摘要以利 session 交接與工作延續；當使用者要整理上下文、寫交接報告或提及「聚合」「摘要」「交接」時觸發。
---

# Skill: context-aggregator

> **用途**：接手他人工作時，快速聚合所有必要 context，冷啟動無縫銜接。
> **觸發**：`/context`

## 使用方式

```
/context [範圍: session | recent | full]
```

- `session` — 本次 session 的工作摘要
- `recent` — 最近 3 天的活動摘要（預設）
- `full` — 完整專案上下文

## 資訊來源

### 1. Claude Code 記憶
- 讀專案 memory 索引（`~/.claude/projects/<project>/memory/MEMORY.md` 或等效路徑）
- 若專案另外設定 MCP 記憶伺服器，一併查詢（見 `.claude/settings.json` 是否有 `mcpServers`）
- 提取關鍵決策和發現，識別未完成的任務

### 2. Git 歷史
- 最近的 commit 記錄（`git log --oneline -10`）
- 當前分支狀態（`git branch --show-current`）
- 未提交的變更（`git status`）
- 活躍分支列表（`git worktree list` / `git branch -a`）

### 3. Harness 狀態
- `state/feature-list.json` 找 in_progress tasks（若檔案不存在代表尚無 active harness 狀態，可跳過）
- 對應 ExecPlan 全文（重點：§6 Progress Log 最後一行 + §9 Handoff Manifest）
- `docs/architecture/invariants.md` 相關 INV-id
- TODO/FIXME 標記統計、失敗的測試（如有）、未解決的 lint 警告

## 聚合流程

### Step 1: 收集
- 從各來源收集原始資訊，過濾雜訊，保留有價值的資料

### Step 2: 分類
- 按主題分組（功能開發、bug 修復、基礎設施）
- 標記狀態（進行中、已完成、待處理）

### Step 3: 合成
- 產出結構化摘要，標記需要注意的項目
- 依當前 `[HANDOFF:*]` marker 建議下一步行動

## 輸出格式

```markdown
# Context Aggregation

## Active Tasks
- F-NNN: [title] | status: in_progress | marker: [HANDOFF: xxx]

## Recent Commits
[git log output]

## Pending Open Questions
[從 ExecPlan §8 抓]

## Next Action
Based on current state marker: [HANDOFF: xxx]
→ Enter role: xxx
→ Start from: §4 step N
```

## 參考

- `.claude/protocols/execplan-lifecycle.md` 跨 session 接手 SOP
- `.claude/protocols/handoff-protocol.md` 三種 marker 規範
- `state/SCHEMA.md`
- `.claude/settings.json`（確認是否有 MCP 記憶配置）

## 驗證項目

- **產出形式**：handoff document（markdown），含已完成 / 待完成 / 阻塞 / 下一步建議四段。
- **整合 ExecPlan**：寫入對應 `docs/plans/active/F-NNN-*.md` §9 Handoff Manifest。
- **整合 state**：必要時觸發 `pre-compact-snapshot.py`（手動 PreCompact）寫入 `state/session-handoffs/<ts>.json`。
- **與 `/last-word` 區別**：context-aggregator 用於主動聚合多源 context；`/last-word` 是 session 收尾的結構化 dispatch，兩者互補不重複。
- **交接 marker**：`[HANDOFF: next-session]` 或 `[HANDOFF: <specific-agent>]`。
