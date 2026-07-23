---
name: clarify-first
description: 進 ExecPlan / Plan Mode 前的主動範圍／需求確認 — 客觀訊號，非憑感覺
always: true
---

# Clarify First

> 常駐規則。與 `judgment-rubrics.md` §3（反應式熔斷，任務進行中才觸發）互補——本規則是**主動式**：在你開始撰寫 ExecPlan 或 Plan Mode 計劃**之前**執行，而非執行中撞到歧義才處理。格式沿用 `judgment-rubrics.md` 的慣例：**訊號（可觀察）→ 行動**，附正／反例。

## 1. 何時該先停下釐清，才開始寫計劃

**訊號**（下列 4 項，缺 2 項以上 → 動筆前先釐清）：
1. **目標用戶** — 誰會用這個 / 誰受影響
2. **成功指標** — 怎麼知道做完了／有效
3. **明確邊界或非目標** — 刻意不做的是什麼
4. **具體觸發條件** — 什麼時候跑／被什麼觸發

- ✅ Good：用戶說「加一個匯出功能」。缺：目標用戶、成功指標、非目標、觸發條件（4/4 都缺）→ 先問，再進 Plan Mode 或 ExecPlan。
- ❌ Bad：同樣需求 → 直接進 Plan Mode，自己默默決定「匯出成 CSV、按鈕觸發、給所有用戶用」，完全沒有確認過。

此閘門觸發時，請行內發出 telemetry marker——觸發釐清時用 `[RULE_FIRED: clarify-first|missing=N, asked]`，跳過時用 `[RULE_SKIPPED: clarify-first|<§4 例外>]`——讓規則命中率可被量測（語法見 handoff-protocol.md「行內輔助標記」；收割進 state/rule-events.jsonl）。

## 2. 釐清要在哪裡做（context_firewall 限制）

`.claude/agents/` 底下所有 agent 都跑在 `context_firewall: true` 之下——非互動式 subagent，無法在任務進行中暫停向用戶提問。因此釐清必須在**主對話**中進行，絕不能發生在被派工的 subagent 裡：

- 直接在主對話發問（`AskUserQuestion` 或純文字），或
- 呼叫 `pm` 或 `spectra-amplifier` 產出候選解讀，再把結果帶回**主對話**跟用戶確認，確認完才交接進 ExecPlan / Plan Mode。

- ✅ Good：主對話先問「你是指這兩種裡的哪一種？」，確認後才派工給 `architect`。
- ❌ Bad：直接派工給 subagent，指望它會「去問用戶」——被 context-firewall 隔開的 subagent 提出的問題永遠傳不到用戶那裡；它只會悄悄用猜的、卡住，或編一個答案。

## 3. 與 judgment-rubrics.md §3 的關係

§3 是**反應式**出口：任務**執行中**才觸發，條件是「存在兩種合理解讀，選錯要浪費 30 分鐘以上」。本規則是**主動式**閘門：在動筆**之前**就用上面 §1 的客觀 4 項檢查清單觸發。通過這道閘門不代表之後就不會撞到 §3——若任務中途仍冒出歧義，照 §3 處理即可；不必在任務中途重跑這份清單。但有一個例外：任務中途的**使用者發起需求變更**不在此「不重跑」條款範圍內——它走 execplan-lifecycle.md 的「Scope Change」程序（只針對差異部分的 4 項檢查 + Scope Baseline 版本行）。

## 4. 何時可跳過

以下情況比照 `plan-first.md` 的例外清單跳過——這些任務本來就不會進 Plan Mode 或 ExecPlan，沒有計劃可言，自然沒有範圍需要釐清：
- 單一檔案 < 20 行的小修改
- 純格式調整或註解更新
- 已定位問題的 bug 修復
- 用戶明確說「直接做」

- ✅ Good：「修第 42 行的 typo」→ 問題已定位、單一檔案 → 整套 clarify-first 直接跳過。
- ❌ Bad：對一個單行格式修正跑完整 4 項檢查清單，在毫無歧義的任務上浪費一輪確認往返。
