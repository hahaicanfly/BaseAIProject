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

## Harness 制度文件（2026-07-04 建立）

| 檔案 | 用途 |
|------|------|
| [`harness/DIAGNOSIS.md`](harness/DIAGNOSIS.md) | 漏水診斷書：Top3 漏 token／失焦／易錯 + 修法 + 能力極限 |
| [`harness/LETTER-TO-FUTURE-SESSIONS.md`](harness/LETTER-TO-FUTURE-SESSIONS.md) | 給未來 session 的信 + 未完成交接清單 |
| `../.claude/rules/model-dispatch.md` | 模型調度守則（常駐） |
| `../.claude/rules/judgment-rubrics.md` | 判斷力外化矩陣（常駐） |
| `../.claude/templates/delegation-templates.md` | 派工 prompt 模板 ×6 |
| `../.claude/protocols/harness-maintenance.md` | harness 檔案維護協議（權限分級／教訓格式／精簡觸發） |

---

## 引用此檔的位置

- `CLAUDE.md`：文件地圖（"文件總索引"）
- `docs/plans/PLANS.md` §5
