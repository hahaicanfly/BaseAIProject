# PDR-NNNN — [短標題]

> **狀態**：Proposed / Accepted / Superseded
> **日期**：YYYY-MM-DD
> **作者**：[agent name / human]
> **複查日期**：YYYY-MM-DD（到期時檢查「成功指標」是否達標；未達標 → 狀態改為 Superseded）
> **依據研究報告**：`docs/research/<YYYY-MM-DD>-<slug>.md`（若有；無則寫「無，理由：...」）

> PDR（Product Decision Record）是 ADR 的產品決策版：ADR 記錄架構/技術決策，PDR 記錄
> 功能/產品層級決策（例如：是否做某功能、優先序、目標客群、定價方向）。何時必須產出 PDR，
> 見 `.claude/agents/pm.md` Output Format 尾段（priority=P0 的功能/產品決策強制要求）。

---

## 1. 決策問題與背景

[描述促使此決策的問題、背景、觸發原因。這不是自由發揮欄位——目標使用者、成功判準、
非目標邊界、觸發條件缺兩項以上時，先在主對話澄清後才進入 PDR 撰寫（clarify-first.md）。]

---

## 2. 選項比較表（至少 2 案）

| 方案 | 說明 | 優點 | 缺點 / Trade-offs | 成本估計 |
|-----|------|------|------|------|
| Option A（已選） | ... | ... | ... | ... |
| Option B | ... | ... | ... | ... |
| Option C（可省略） | ... | ... | ... | ... |

---

## 3. 採用決策

[明確陳述選了哪個方案、為什麼；一段話講清楚，不要只留表格讓讀者自己猜。]

---

## 4. 證據清單

[決策依據的每一條證據都要能追溯來源。無出處的宣稱一律標記 `[UNCONFIRMED: <claim>]`，
禁止捏造。]

| 證據 | 來源（URL 或 file:line） | 取得日期 |
|------|------|------|
| [宣稱 1] | https://example.com/source 或 `path/to/file:42` | YYYY-MM-DD |
| [宣稱 2，若無出處] | `[UNCONFIRMED: <claim>]` | — |

---

## 5. 關鍵假設

[這個決策成立所依賴、但尚未完全證實的假設；信心欄位誠實填寫，不要全部填「高」。]

| 假設 | 信心（高/中/低） | 依據 |
|------|------|------|
| [假設 1] | 中 | [為何是這個信心等級：資料量、來源可靠度、時效性] |

---

## 6. 可證偽成功指標

[必須是「什麼觀察會證明決策錯誤/成功」，不是「希望達到什麼」的願望式描述。到了複查日期
（見檔頭）若未達標，本 PDR 狀態改為 Superseded，並在下方 Implementation Notes 記錄後續動作。]

| 指標 | 目標值 | 量測方法 | 複查日期 |
|------|------|------|------|
| [指標 1] | [具體數字/門檻] | [怎麼量、從哪個資料源] | YYYY-MM-DD |

---

## 7. Non-Goals

[明確排除、本決策刻意不涵蓋的範圍，避免執行時 scope creep。]

- [非目標 1]
- [非目標 2]

---

## 8. 狀態

- **目前狀態**：Proposed / Accepted / Superseded
- 若為 Superseded：接替此決策的文件路徑 `docs/decisions/PDR-NNNN-....md`，以及取代原因

---

## Implementation Notes

[實作/執行時需要注意的細節；若因複查未達標而轉為 Superseded，在此記錄後續處置。]

---

## 引用此 PDR 的位置

- ExecPlan §7 Decision Log（相關 feature，若此決策驅動了實作）
- `docs/research/<YYYY-MM-DD>-<slug>.md`（若此 PDR 引用了研究報告，於該報告加一行反向連結）
