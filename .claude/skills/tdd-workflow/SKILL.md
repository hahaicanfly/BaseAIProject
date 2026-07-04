---
name: tdd-workflow
description: 執行 Red → Green → Refactor 的測試驅動開發流程，用於核心業務邏輯與高可靠性需求；當使用者要 TDD 開發或提及「測試驅動」「先寫測試」時觸發。
---

# Skill: tdd-workflow

> **用途**：測試驅動開發流程（Red → Green → Refactor）。
> **觸發**：`/tdd-workflow`
> **適用場景**：核心業務邏輯、高可靠性需求

## 執行步驟

1. **Red**：先寫失敗的 test，確認預期行為
2. **Green**：寫最小實作讓 test 通過
3. **Refactor**：改善代碼品質，確保 test 仍通過

## TDD 規範

- Test 命名：`should_[behavior]_when_[condition]`
- 每個 test 只驗一個行為
- 包含 positive + negative cases
- 使用 test doubles（fake/mock/stub）隔離外部依賴

## 驗證指令

```bash
# 替換為實際測試指令
[your test runner] --watch
```

## 參考

- `.claude/agents/qa-engineer.md`
- `docs/architecture/invariants.md` INV-TEST-*
