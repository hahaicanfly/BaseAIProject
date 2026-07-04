# AI 成本優化指南

> 常駐硬規則見 `.claude/rules/cost-optimization.md` 與 `.claude/rules/model-dispatch.md`；本檔只放延伸說明與範例。
> **適用對象**：所有 agent（在選擇模型和決定是否發 API 請求時參考）。

---

## 模型選用

分級表、升降級路徑、派工規則以 `.claude/rules/model-dispatch.md` 為單一事實源，本檔不重複列表。

---

## Prompt Cache 策略

### 快取命中最大化

- 長系統 prompt（CLAUDE.md、invariants.md）放在訊息**前面**，不要每次重新排列
- 靜態 context（架構文件、規則）放在動態 context（當前任務）之前
- 5 分鐘 TTL：若 session 超過 5 分鐘無活動，cache 會失效

### ScheduleWakeup 間隔選擇

| 場景 | 建議間隔 | 原因 |
|------|---------|------|
| 等待外部 CI/CD | 60–270s | 保持 cache 暖，輪詢外部狀態 |
| 等待較長操作 | 1200–1800s | 超出 cache TTL，省一次 cache miss |
| 避免 300s | — | 剛好 cache 失效但等待太短，最壞情況 |

---

## Context Engineering（Token 預算策略）

### 三層讀取原則

```
第 1 層：讀 index 檔（輕量 ~KB）→ 定位相關頁面
第 2 層：讀 2-3 個核心文件（中量）→ 組合回答
第 3 層：只在前兩層不足時，才讀原始源碼（重量）
```

### 防止 Context Flooding

- 優先讀摘要頁而非原始大檔
- 使用 `grep` 定點讀取而非 `cat` 整個大檔
- Sub-agent 處理重量任務，保護主 context

---

## 邊緣 AI 整合（延伸）

本地可完成的任務清單見 `.claude/rules/cost-optimization.md` 邊緣 AI 優先。額外補充——需要雲端模型的任務：

- 深度語意理解
- 複雜推理與分析
- 跨文件綜合

---

## 監控與分析

### `state/token-usage.jsonl` 追蹤

`pre-compact-snapshot.py` 在每次 PreCompact 時自動記錄 token 用量。

**需追蹤的指標**：
- 每次 API 調用成本
- cache 命中率（`cache_read` / `input_tokens`）
- 平均 session token 消耗

### 警告訊號

- `cache_read` 持續為 0 → prompt 順序問題或 session 間隔過長
- `input_tokens` 飆升 → context flooding，考慮 sub-agent 分拆
- 同一任務反覆呼叫 → 缺少快取層

---

## 延伸重點

- Sub-agent 隔離：重量任務用 sub-agent 執行，避免污染主 context
- 定期審視：每月從 `state/token-usage.jsonl` 分析成本分布
