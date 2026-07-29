# BaseAIProject — Antigravity (agy) 操作憲法

> **本檔為 Antigravity agent 的啟動協議。**
> 每次 agy agent 在此專案中啟動任何任務時，**必須先完整讀取本檔，再讀取 `CLAUDE.md`**。
> 所有工作規範以 `CLAUDE.md` 為最終依據，本檔為 agy 的橋接說明。

---

## 第一步：立即讀取 CLAUDE.md

```
必讀：CLAUDE.md（本專案根目錄）
```

`CLAUDE.md` 是本專案的操作地圖，包含：
- Quick Commands（常用指令）
- 正典層級與硬防線（INV-* 規則入口）；動手前的路由表現在放在 `.claude/tiers/` 下注入的 tier pack
- 常駐規則、交接與 Session 管理
- 文件地圖（Virtual Team／Multi-Agent Skills 清單見 `agent_docs/AI-TEAM-REGISTRY.md`）
- Tech Stack 與 Project Relations

**在未讀完 `CLAUDE.md` 前，禁止執行任何檔案修改操作。**

---

## Antigravity 工作流對應

本專案採用 **Harness Engineering** 工作流。Antigravity agents 的工作方式對應如下：

### agy agents ↔ .claude/agents/

| agy 呼叫（invoke_subagent / 直接使用） | 對應角色 | 必讀文件 |
|--------------------------------------|---------|---------|
| 需求分析任務 | `.claude/agents/pm.md` | `CLAUDE.md` + `TECHNICAL-REFERENCE.md` |
| 架構設計任務 | `.claude/agents/architect.md` | `CLAUDE.md` + `invariants.md` |
| 實作任務 | `.claude/agents/tech-lead.md` | `CLAUDE.md` + 對應 ExecPlan |
| 代碼審查 | `.claude/agents/code-reviewer.md` | `review-protocol.md` |
| 測試任務 | `.claude/agents/qa-engineer.md` | `CLAUDE.md` + `invariants.md` |
| 安全審計 | `.claude/agents/security-reviewer.md` | `security-policy.md` |
| 計劃審查 | `.claude/agents/plan-reviewer.md` | `execplan-lifecycle.md` |
| UI/UX 任務 | `.claude/agents/uiux-agent.md` | `.claude/uiux/WORKFLOW.md` |

### agy skills ↔ .claude/skills/

所有 agy skills 在此專案中執行時，必須先確認 Harness 工作流要求：

| Skill 類型 | 對應 .claude/skills/ | 前置要求 |
|-----------|---------------------|---------|
| 功能開發 | `feature-pipeline/` | 建 ExecPlan → 人類核可 → 開 branch |
| 代碼審查 | `code-review/` | 讀 ExecPlan §3 + §5 |
| 安全審計 | `security-audit/` | 讀 `invariants.md` |
| 技術債 | `techdebt-scanner/` | 產出 report 到 `docs/learnings/` |
| UI/UX | `ui-ux-pro-max/` | 讀 `.claude/uiux/WORKFLOW.md` |

---

## 啟動任務的標準程序

### 1. 讀取階段（必做，不得跳過）
```
Step 1: 讀 GEMINI.md（本檔）           <- 你正在讀
Step 2: 讀 CLAUDE.md                   <- 操作地圖
Step 3: 讀 agent_docs/TECHNICAL-REFERENCE.md
Step 4: 讀 docs/architecture/invariants.md
Step 5: 讀 state/feature-list.json     <- 確認是否有 in_progress task
```

### 2. 判斷任務類型
```
簡單問答 / 說明     -> 直接回答，無需 ExecPlan
單一檔案小修改     -> Read 該檔 -> 修改 -> lint
跨模組 / API 變更  -> 必須先建 ExecPlan -> 等人類核可 -> 開 branch
```

### 3. 有 in_progress ExecPlan 時
```
讀 docs/plans/active/F-NNN-*.md
看 §6 Progress Log 最後一行
看 §9 Handoff Manifest 的 Current state marker
依 marker 決定接手行動
```

---

## Handoff 標記（agy agents 必須遵守）

agy 的每個 subagent（invoke_subagent）完成任務時，final response 必須符合正典 `.claude/protocols/handoff-protocol.md` 定義的三種 marker 之一。這不只是 Claude Code 的規範，而是**本專案的硬性要求**，適用於所有在此專案執行的 AI agents。

---

## Git 規則（agy 必須主動遵守，無 hook 自動攔截）

Antigravity 環境沒有 Claude Code 的 Python hooks 自動攔截，**agy agents 必須在每次 git 操作前主動確認**：

```bash
# 每次 git commit 前必做
git branch --show-current   # 確認不是 master/main
```

禁止指令的完整清單（INV-GIT-002/003/004）見正典 `docs/architecture/invariants.md`；hook 不會攔截，違反與否全靠 agy 自律。

---

## 輸出語言與格式

輸出語言、commit message 規範與回報格式，完整遵循正典 `CLAUDE.md` 的 Communication Style 一節，agy 無特例。

---

## 快速參考

| 需要 | 去讀 |
|------|------|
| 工作規範總覽 | `CLAUDE.md` |
| 當前架構 | `agent_docs/TECHNICAL-REFERENCE.md` |
| INV 硬規則 | `docs/architecture/invariants.md` |
| 建新 ExecPlan | `docs/plans/PLANS.md` |
| 查進行中任務 | `state/feature-list.json` |
| Handoff 規範 | `.claude/protocols/handoff-protocol.md` |
| ExecPlan 流程 | `.claude/protocols/execplan-lifecycle.md` |
| 審查標準 | `.claude/protocols/review-protocol.md` |
| Virtual Team | `agent_docs/AI-TEAM-REGISTRY.md` |
| Multi-Agent 指南 | `agent_docs/multi-agent-guide.md` |
