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


## 白話層（給非技術背景使用者）

| 檔案 | 用途 |
|------|------|
| [`PLAIN/START-HERE_zh.md`](PLAIN/START-HERE_zh.md) | 無術語入口：第一句話該打什麼、接下來會發生什麼、它絕對不會擅自做的事 |
| [`PLAIN/claude-md-crib-sheet.md`](PLAIN/claude-md-crib-sheet.md) | 一頁講清楚「直接做」與「先寫計畫」是怎麼分的 |

> 衍生層，非正典。這些是規則檔的唯讀翻譯 —— 與來源檔牴觸時，以來源檔為準。

---

---

## Harness 制度文件（2026-07-04 建立）

| 檔案 | 用途 |
|------|------|
| [`harness/DIAGNOSIS.md`](harness/DIAGNOSIS.md) | 漏水診斷書：Top3 漏 token／失焦／易錯 + 修法 + 能力極限 |
| [`harness/LETTER-TO-FUTURE-SESSIONS.md`](harness/LETTER-TO-FUTURE-SESSIONS.md) | 給未來 session 的信 + 未完成交接清單 |
| `../.claude/tiers/README.md` | **實際生效的常駐規則**：依執行模型選出的 tier pack 如何決定與注入（F-003） |
| `../.claude/rules/model-dispatch.md` | 模型調度守則 — tier pack 背後的全文參考檔，非自動載入 |
| `../.claude/rules/judgment-rubrics.md` | 判斷力外化矩陣 — tier pack 背後的全文參考檔，非自動載入 |
| `../.claude/templates/delegation-templates.md` | 派工 prompt 模板 ×6 |
| `../.claude/protocols/harness-maintenance.md` | harness 檔案維護協議（權限分級／教訓格式／精簡觸發） |

> F-003 之後只有 `.claude/rules/security.md` 自動載入。其餘規則檔原地保留但標記 `always: false`；真正抵達 session 的是 `.claude/tiers/` 下生成的 pack。邊界情況需要查判準背後的理由時才去讀規則全文檔。

---

## 知識地圖（誰寫誰讀、何時流動）

| 層 | 位置 | 誰寫 | 誰讀 | 流動規則 |
|----|------|------|------|----------|
| 教訓 | `docs/learnings/ERRORS.md` | hook 自動 append + 模型手動 append；人週審 promote | 所有 agent | 可機械化者晉升 invariants |
| 硬規則 | `docs/architecture/invariants.md` | 人（紅級） | hooks 與所有 agent | 由 ERRORS 晉升 |
| 架構決策 | `docs/decisions/ADR-*.md` | 人核可 | 規劃類 agent | 不回流 |
| Session 快照 | `state/session-handoffs/` | pre-compact-snapshot.py 自動 | 續接 session | 唯讀不回流 |
| 原生 memory | `~/.claude/projects/<proj>/memory/` | Claude Code 自動 | 下個 session 的 Claude | **只准存跨 session 指標與個人偏好；教訓一律走 ERRORS.md，promote 後從 memory 刪全文留指標** |

---

## 引用此檔的位置

- `CLAUDE.md`：文件地圖（"文件總索引"）
- `docs/plans/PLANS.md` §5
