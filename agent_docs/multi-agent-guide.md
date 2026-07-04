# Multi-Agent Collaboration Guide

> 多代理協作指南 — 利用 Claude Code 的 Agent 工具實現團隊協作模式

## 概述

本指南說明如何利用 Claude Code 的 **Agent 工具** 實現多代理協作，模擬 Code Review Swarm、Feature Factory 等協作模式。

## 可用協作模式

### 1. Swarm 模式（並行審查）

多個專家代理同時審查同一目標，各自專注不同面向。

```
                    ┌─────────────────┐
                    │  Target Code    │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ Tech Lead   │   │  Security   │   │     QA      │
    │ 代碼品質    │   │  安全漏洞   │   │  可測試性   │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Integrated Report│
                    └─────────────────┘
```

**使用方式**: `/multi-agent-review [目標]`

### 2. Pipeline 模式（流水線開發）

代理按順序接力，每個階段的輸出是下一階段的輸入。

```
┌────┐    ┌──────────┐    ┌────────┐    ┌──────┐    ┌────────┐
│ PM │ ─▶ │ Architect│ ─▶ │ UI/UX  │ ─▶ │ Dev  │ ─▶ │ Review │
└────┘    └──────────┘    └────────┘    └──────┘    └────────┘
需求       架構設計         UI 設計      實作        審查
```

**使用方式**: `/feature-pipeline [功能描述]`

### 3. Council 模式（技術決策）

多個代理對同一問題提供不同角度的分析，協助用戶做決策。

**手動啟動方式**:
```
同時啟動:
- Architect: 架構可行性分析
- Tech Lead: 技術債評估
- PM: 業務價值分析
```

### 4. Watchdog 模式（守護檢查）

在關鍵操作前後自動執行安全檢查。

**自動觸發時機**:
- git commit 前: 安全掃描（`pre-tool-use-guard.py`）
- API 變更: 向後相容性檢查
- 依賴更新: 漏洞掃描

### 5. Worktree 模式（平行開發）

多個 Agent 各自在獨立的 git worktree 中工作，實現真正的平行開發。

```
┌──────────────────────────────────────────┐
│              Orchestrator                │
│         (人類 or 管理 Agent)              │
└────────┬──────────┬──────────┬───────────┘
         │          │          │
    ┌────▼────┐ ┌───▼────┐ ┌──▼─────┐
    │ Agent A │ │Agent B │ │Agent C │
    │ WT: T-1 │ │WT: T-2 │ │WT: T-3 │
    │ feat/x  │ │fix/y   │ │refact/z│
    └────┬────┘ └───┬────┘ └──┬─────┘
         │          │          │
         └──────────┼──────────┘
                    ▼
              PR → Merge
```

**使用場景**：
- 多個獨立任務需要同時進行
- 長時間功能開發不影響快速修復
- 需要物理隔離避免工作區衝突

**Agent 工具使用**:
```
Agent(
  isolation: "worktree",     # 自動建立 git worktree
  prompt: "implement F-NNN ...",
  mode: "auto"
)
```

**詳見**: `.claude/rules/parallel-worktree.md`

## 代理角色一覽

> 完整代理清單與觸發詞詳見 `agent_docs/AI-TEAM-REGISTRY.md`。

## 實作機制

### Agent 工具使用

```
Agent(
  subagent_type: "tech-lead",     # 使用專案定義的代理
  prompt: "審查 xxx 的代碼品質",
  model: "sonnet",                # 可選: haiku, sonnet, opus
  run_in_background: true         # 並行執行
)
```

### 並行執行

同時啟動多個代理進行並行審查（在單一訊息中多個 Agent 調用）：

```
Agent(tech-lead, "審查代碼品質", background=true)
Agent(security-reviewer, "審查安全性", background=true)
Agent(qa-engineer, "審查可測試性", background=true)
```

### 結果整合

收集所有背景代理的結果，整合成統一報告，依嚴重度排序。

## 成本優化

> 模型選用表詳見 `.claude/rules/model-dispatch.md`。

## 最佳實踐

### DO

- 對重要變更使用多代理審查
- 在並行模式中設定 `run_in_background: true`
- 整合報告時去重和排序
- 按嚴重度排列問題

### DON'T

- 對簡單改動過度使用多代理
- 同時啟動過多代理（建議 ≤ 3）
- 忽略代理間的衝突意見
- 不等待所有代理完成就整合結果

## 相關文件

- Skills: `.claude/skills/multi-agent-review/`, `.claude/skills/feature-pipeline/`
- Agents: `.claude/agents/`
- Worktree Rules: `.claude/rules/parallel-worktree.md`
- 安全政策: `agent_docs/security-policy.md`
- 成本優化: `agent_docs/cost-optimization.md`
