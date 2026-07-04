---
name: context-aggregator
description: 聚合 MCP 記憶、Git 歷史、本地檔案等多來源資訊，產出結構化摘要以利 session 交接與工作延續；當使用者要整理上下文、寫交接報告或提及「聚合」「摘要」「交接」時觸發。
---

# Skill: context-aggregator

> **用途**：接手他人工作時，快速聚合所有必要 context，冷啟動無縫銜接。
> **觸發**：`/context`

## 執行步驟

1. 讀 `state/feature-list.json` 找 in_progress tasks
2. 讀對應 ExecPlan 全文（重點：§6 Progress Log 最後一行 + §9 Handoff Manifest）
3. 讀 `git log --oneline -10` 了解最近提交
4. 讀 `docs/architecture/invariants.md` 相關 INV-id
5. 輸出「接手摘要」給 agent

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
- `state/SCHEMA.md`
