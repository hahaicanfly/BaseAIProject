# {{PROJECT_NAME}} — Docs Index

> 本目錄收納所有設計文件、架構決策、計畫與學習記錄。
> 所有 agent 讀文件前必須先查本 INDEX，避免讀錯版本。

---

## 架構文件

| 檔案 | 用途 |
|------|------|
| [`architecture/invariants.md`](architecture/invariants.md) | 可機械驗證的硬規則（INV-*），hooks 直接引用 |
| [`architecture/domains.md`](architecture/domains.md) | 領域邊界與變更影響評估表 |

---

## 計畫系統

| 檔案 / 目錄 | 用途 |
|------------|------|
| [`plans/PLANS.md`](plans/PLANS.md) | ExecPlan 規格書與範本 |
| [`plans/active/`](plans/active/) | 進行中的 ExecPlan 實例（入版控） |
| [`plans/completed/`](plans/completed/) | 已完成的 ExecPlan（歸檔，入版控） |

---

## 架構決策記錄（ADR）

| 檔案 | 狀態 | 摘要 |
|------|------|------|
| [`decisions/ADR-template.md`](decisions/ADR-template.md) | Template | ADR 撰寫範本 |

> 新增 ADR 時：`decisions/ADR-NNNN-<short-slug>.md`，並在此表新增一行。

---

## 累積教訓

| 檔案 | 用途 |
|------|------|
| [`learnings/ERRORS.md`](learnings/ERRORS.md) | AI 犯錯紀錄（Pending Review → Active Lessons） |

---

## 引用此檔的位置

- `CLAUDE.md`：rule pointer（"讀 docs/INDEX.md 定位文件"）
- `.claude/agents/*.md`：每個 agent frontmatter `always_read`
- `docs/plans/PLANS.md` §5
