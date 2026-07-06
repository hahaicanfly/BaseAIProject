---
name: model-dispatch
description: 模型調度、派工三件套、升降級路徑、驗證不自驗（單一事實源）
always: true
---

# 模型調度守則（Model Dispatch）

> 本檔為常駐規則（每 session 自動載入），只放判準與硬規則。
> 派工模板全文見 `.claude/templates/delegation-templates.md`；判斷類 rubric 見 `.claude/rules/judgment-rubrics.md`。

## 0. 本機實際可用檔位（2026-07 盤點，事實不憑印象）

| 檔位 | Agent tool `model` 值 | 用途 |
|------|----------------------|------|
| Haiku 4.5 | `haiku` | 格式化、固定模板套用、單點查詢 |
| Sonnet | `sonnet` | 預設工作馬：實作、搜尋、審查、研究 |
| Opus 4.8 | `opus` | 架構決策、跨模組重構、疑難 debug |
| Fable 5 | `fable` | 僅特殊授權 session；日常不可假設可用 |

- 主對話模型由 `~/.claude/settings.json` 的 `model` 決定；不要在對話中假設自己是哪個模型，用行為規則而非身分判斷。
- effort 參數：只有 Workflow 工具的 `agent(prompt, {effort})` 可設（`low|medium|high|xhigh|max`）；環境沒有 Workflow 工具時忽略本行。Agent tool 無 effort 參數，繼承 session 設定。
- Agent tool 省略 `model` 時繼承主對話模型 —— **派輕量任務必須顯式寫 `model: "haiku"` 或 `"sonnet"`，否則會用主對話的貴模型跑雜活**。

## 1. 指揮官不下場

主對話（指揮官）只做：決策、拆解、派工、驗收結論、與使用者溝通。

**必須派 subagent** 的觸發條件（任一成立即派，不自己動手）：
- 預估要讀 3 個以上檔案、或單檔超過 400 行的通讀
- 全 repo 掃描 / 關鍵字追蹤（→ `Explore` agent）
- 網頁搜尋或文件研究（→ `general-purpose`，`model: sonnet`）
- 批次修改 5 個以上檔案（→ 派工 + worktree 隔離，見 parallel-worktree.md）
- 任何「先大量閱讀才能下結論」的分析

**主對話可以自己做**：改單一已知檔案（< 20 行 diff）、讀已知檔案的特定區段、跑單一指令並看結果、寫最終交付文字。

## 2. 派工三件套（每次派工 prompt 必含三節，缺一不派）

1. **目標與動機**：要達成什麼、為什麼（讓 subagent 能自行做小決定）
2. **驗收條件**：可機械檢查的完成定義（檔案存在、測試通過、回報含特定欄位）
3. **回報格式**：明確規定回報結構與長度上限

模板直接抄 `.claude/templates/delegation-templates.md`，不要即興發揮。

## 3. 回報合約（subagent 端）

- 回報 ≤ 40 行；只回結論、清單、`檔案:行號` 引用
- 禁止在回報中貼超過 10 行的代碼或原文 —— 長產物一律落檔，回傳路徑
- 回報最後一行必須是 handoff marker（見 `.claude/protocols/handoff-protocol.md`）
- 失敗要如實回報：說明卡在哪、試過什麼，不得回報「大致完成」

## 4. 升降級路徑

| 情況 | 動作 |
|------|------|
| Haiku 出現工具呼叫錯誤或語法錯誤 **1 次** | 直接改派 Sonnet 重做，不重試 Haiku |
| Sonnet 同一子任務**連錯 2 次** | 升 Opus，且 prompt 必須附完整失敗軌跡：原始指令、兩次的錯誤輸出、期望結果 |
| Opus 解出了可重複的固定模式 | 把模式寫成規則/範例（落檔），降回 Sonnet/Haiku 批次套用 |
| 升級後（Opus）**再敗 1 次** | 停止重試 → 熔斷，帶失敗軌跡問使用者（見 judgment-rubrics.md §3） |

完整序列（唯一解讀）：同模型連敗 2 次 → 升級一次 → 升級後再敗 1 次 → 熔斷問人。升級那一次的嘗試不重置計數、也不另開新預算。
「同一子任務」判定：目標與驗收條件相同即算同一子任務，換個說法重派仍計入失敗次數。

## 5. 驗證不自驗

- 實作者不得宣告自己的產出通過驗收。
- 驗收一律派 **fresh-context subagent**（新開、不帶實作過程 context）：
  - 文件/設定產出 → read-back：重新讀檔，對照驗收條件逐條檢查
  - 代碼產出 → 實跑測試或實跑程式，貼出實際輸出
  - 高風險判斷（架構選型、安全、不可逆操作）→ 第二意見：再派一個不同模型或不同角度的 agent 獨立作答，比對結論；不一致時升級或問使用者
- 驗收 agent 的回報只能是：`PASS`（逐條列驗收條件與證據）或 `FAIL`（列出未過項與證據）。不接受「看起來沒問題」。
- 驗收邊界：FAIL 只准基於派工時列明、可機械檢查的驗收條件；風格/寫法/觀點類意見進「建議（非阻斷）」欄，不得阻擋交付——防驗收員越權造成重工空轉。
