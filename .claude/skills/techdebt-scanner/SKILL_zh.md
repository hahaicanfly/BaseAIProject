---
name: techdebt-scanner
description: 系統性掃描專案技術債（TODO/FIXME、複雜函式、重複程式碼等），產出分級優先報告；當使用者要分析代碼健康度或提及「技術債」「techdebt」時觸發。
---

# Skill: techdebt-scanner

> **用途**：系統性掃描技術債，產出優先級報告。
> **觸發**：`/techdebt`（via `.claude/commands/techdebt.md`）
> **Agent**：techdebt-scanner（sonnet）

## 使用方式

```
/techdebt [範圍: full | 指定路徑；未指定則掃描 CLAUDE.md Quick Commands 定義的專案原始碼目錄]
```

## 掃描流程

### Step 1: 快速概覽
- 統計專案原始碼檔案數量（副檔名依專案技術棧調整，如 .ts/.py/.go/.kt）
- 掃描 TODO/FIXME/HACK/WORKAROUND/XXX 標記
- 統計 suppress/ignore 註解與 deprecated 標記（如 `@Deprecated`、`# noqa`、`eslint-disable`）使用量
- 產出初步數字摘要

### Step 2: 深入分析
- 識別超過 50 行的函式、超過 4 層巢狀、超過 5 個參數的函式
- 檢查缺失測試的核心模組
- 掃描硬編碼的 URL、路徑、端口
- 檢查未使用的 import / 未使用的程式碼
- 評估模組間依賴方向（循環依賴、跨層直接調用）

### Step 3: 產出報告
- 按優先級（P0/P1/P2）分類所有發現
- 為每個問題標記具體位置（`file:line`）
- 提供修復建議和預估工作量
- 列出建議的行動順序

## 掃描範圍

預設掃描目錄：依專案 CLAUDE.md Quick Commands 定義的原始碼目錄；未定義時掃描整個 repo，排除編譯輸出目錄與套件管理快取（如 `build/`、`dist/`、`node_modules/`、`.gradle/`、`vendor/`）。

## 掃描指令參考

```bash
# <SRC_DIR> = 專案原始碼目錄（依 CLAUDE.md 填入，如 src/、app/、lib/）
# TODO/FIXME 標記
grep -rn "TODO\|FIXME\|HACK\|WORKAROUND\|XXX" <SRC_DIR>

# 硬編碼值
grep -rn "http://\|localhost\|127.0.0.1" <SRC_DIR>
```

## 輸出範本

```markdown
## 技術債報告

### 掃描範圍
- 目錄：<SRC_DIR>
- 檔案數：N 個
- 日期：YYYY-MM-DD

### 摘要
| 優先級 | 數量 |
|--------|------|
| P0（高）| X |
| P1（中）| X |
| P2（低）| X |

### 詳細發現
[按優先級列出，含 file:line 與修復建議]

### 行動建議
[排序的修復清單]
```

## 參考文件

開始前先檢查：
- CLAUDE.md（專案規範、Quick Commands）
- `agent_docs/TECHNICAL-REFERENCE.md`（架構，填實後適用；仍含未填佔位符則跳過，判準見 CLAUDE.md「啟用狀態」節）

## 驗證項目

- **產出形式**：技術債報告（含優先級 P0/P1/P2 + 影響範圍 + 估時）。
- **整合**：每筆 P0/P1 候選 → 由 PM agent 起新 ExecPlan 進入 `docs/plans/active/`。
- **去重**：與 `docs/learnings/ERRORS.md` Active Lessons 比對，避免重複立項。
- **觸發頻率**：建議季度執行，非每次 PR。
- **交接 marker**：`[HUMAN_ATTENTION_REQUIRED: 技術債掃描完成，請人類決定優先處理哪些項目]`
