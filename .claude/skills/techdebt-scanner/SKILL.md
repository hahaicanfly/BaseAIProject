---
name: techdebt-scanner
description: 系統性掃描專案技術債（TODO/FIXME、複雜函式、重複程式碼等），產出分級優先報告；當使用者要分析代碼健康度或提及「技術債」「techdebt」時觸發。
---

# Skill: techdebt-scanner

> **用途**：系統性掃描技術債，產出優先級報告。
> **觸發**：`/techdebt`（via `.claude/commands/techdebt.md`）
> **Agent**：techdebt-scanner（sonnet）

## 掃描項目

1. **標記掃描**：TODO / FIXME / HACK / WORKAROUND / XXX
2. **複雜函式**：超過 50 行、超過 4 層巢狀、超過 5 個參數
3. **測試缺失**：有原始碼目錄但無對應 test/
4. **架構問題**：循環依賴、硬編碼 URL/端口、未使用 import

## 掃描指令參考

```bash
# TODO/FIXME 標記（<專案原始碼目錄> 替換為實際路徑，如 src/、app/、lib/）
grep -rn "TODO\|FIXME\|HACK\|WORKAROUND\|XXX" <專案原始碼目錄>

# 硬編碼值
grep -rn "http://\|localhost\|127.0.0.1" <專案原始碼目錄>
```

## 輸出格式

```markdown
## 技術債報告

### 摘要
| 優先級 | 數量 |
|--------|------|
| 🔴 高 | X |
| 🟡 中 | X |
| 🟢 低 | X |

### 行動建議
1. 最優先處理的項目
2. 次要處理的項目

[HUMAN_ATTENTION_REQUIRED: 技術債掃描完成，請人類決定優先處理哪些項目]
```
