# AI 成本優化指南

> **目的**：在保持品質的前提下，最小化 AI API 調用成本。
> **適用對象**：所有 agent（在選擇模型和決定是否發 API 請求時參考）。

---

## 模型選用策略

### 決策矩陣

| 任務類型 | 建議模型 | 原因 |
|---------|---------|------|
| 格式化、簡單驗證、hash 比對 | `haiku` | 快速、低成本 |
| 代碼生成、一般分析、bug 修復 | `sonnet` | 平衡性價比 |
| 架構設計、複雜推理、安全深度分析 | `opus` | 需要深度思考 |

### 具體場景

#### 使用 Haiku（低成本）
- 代碼格式化建議
- 簡單的 yes/no 判斷
- 固定模板填充
- 語法錯誤檢查
- SHA-256 hash 比對、重複偵測

#### 使用 Sonnet（中等成本）
- 功能實作
- Bug 修復
- 單元測試生成
- 代碼解釋
- 一般文件撰寫

#### 使用 Opus（高成本，謹慎使用）
- 系統架構設計
- 複雜重構決策
- 跨模組影響分析
- 安全漏洞深度分析
- 綜合多來源的跨 session 分析

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

## 邊緣 AI 整合（可選）

若專案有本地端 AI 能力，優先在本地完成以下任務（零 API 成本）：

- OCR、格式偵測
- 圖片預處理（縮圖、裁切）
- 簡單語言偵測
- 格式驗證

需要雲端模型的任務：
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

## 最佳實踐

1. **漸進式複雜度** — 先用便宜模型，真正需要推理才升級
2. **智慧快取** — 相同輸入不重複請求（hash 比對）
3. **壓縮輸入** — 提供精確 context 而非整個 repo
4. **Sub-agent 隔離** — 重量任務用 sub-agent，不污染主 context
5. **定期審視** — 每月從 `state/token-usage.jsonl` 分析成本分布
