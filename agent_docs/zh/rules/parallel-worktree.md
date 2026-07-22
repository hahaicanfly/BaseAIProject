---
name: parallel-worktree
description: 多 agent 平行開發時的 Git worktree 隔離規則
always: true
---

# Parallel Worktree Development Rules

> 本檔為 .claude/rules/parallel-worktree.md 的繁體中文鏡像（2026-07-23 同步）。

## 總覽

當多個 AI agent 或 session 同時處理同一個專案時，每個都**必須**使用隔離的 git worktree 以避免衝突。

## 一般規則

1. 在 worktree 模式下運作時，**絕不修改主專案目錄內的檔案**
2. 每個任務有唯一的 `{TASK_ID}` 與分支 `agent/{TASK_ID}`
3. 沒有通過 build 與測試絕不 push
4. 一個 worktree = 一個任務 = 一個分支 = 一個 PR

## 建立 Worktree

### 方案 A：Claude Code 內建（單一 Session）

使用 `EnterWorktree` tool 或 Agent tool 加 `isolation: "worktree"`：
```
Agent(
  prompt: "implement feature X",
  isolation: "worktree"
)
```
Claude Code 會自動管理 worktree 的生命週期。

### 方案 B：手動 git worktree（多 Session / 手動）

```bash
git worktree add ../<project>-worktrees/<TASK_ID> -b agent/<TASK_ID> [BASE_BRANCH]
```
會在 `../<project>-worktrees/<TASK_ID>/` 建立 worktree，分支為 `agent/<TASK_ID>`（若省略 `BASE_BRANCH`，預設從目前 HEAD 分支出去）。

## 代碼修改安全性

- 確認每個檔案路徑都以目前 worktree 目錄開頭
- 修改前先讀（同主專案規則）
- 只修改與目前任務相關的檔案
- 不要動屬於其他 agent 任務的檔案

## 允許的 Git 操作

```
git status / git diff / git log        # 讀取操作
git add / git commit                   # 暫存與提交
git push -u origin <branch>           # push 自己的分支
git fetch / git rebase <base>         # 保持與上游同步
```

## 禁止的 Git 操作

- `git reset --hard`（改用 `git stash`）
- 刪除不屬於自己的分支（`agent/other-task`）
- 修改 remote 設定
- 對共享分支 force push
- 直接對 `master` commit

## Push 前的 Build 驗證

依專案的 build 系統調整：

```bash
# 換成你專案實際的 build/lint/test 指令
# 例：Node.js: npm run build && npm test
# 例：Python:  python -m pytest
# 例：Go:      go build ./... && go test ./...
# 例：Rust:    cargo build && cargo test
[你的 build 指令]
[你的 lint 指令]
[你的 test 指令]
```

> 專案特定的 build 規則（INV-BLD-*）見 `docs/architecture/invariants.md`。

## 清理

PR merge 後：
```bash
git worktree remove ../<project>-worktrees/<TASK_ID>
git branch -d agent/<TASK_ID>

# 批次清理：列出所有 worktree，再手動移除每個已 merge 的
git worktree list
git worktree prune
```

## 何時使用 Worktree 模式

| 情境 | 用 Worktree？ |
|----------|--------------|
| 多個 agent 同時工作 | 是 |
| 長期功能開發與快速修復並行 | 是 |
| 單一小改動 | 否 —— 在主目錄工作 |
| 探索性研究（唯讀） | 否 —— 不修改檔案 |
