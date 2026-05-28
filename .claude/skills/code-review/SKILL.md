# Skill: code-review

> **用途**：單一 reviewer 對 PR diff 進行標準代碼審查。
> **觸發**：`/code-review`
> **Agent**：code-reviewer（sonnet）

## 執行步驟

1. 讀 active ExecPlan 的 §3 Constraints + §5 Verification Strategy
2. 讀 `docs/architecture/invariants.md` 相關 INV-id
3. 執行 `git diff master...HEAD`
4. 逐條驗證 Constraints
5. 輸出 Review Report（Blockers / Warnings / Suggestions / Praise）
6. 同步寫入 ExecPlan §7 Decision Log

## 輸出格式

```markdown
# Review Report — F-NNN

**Reviewer**: code-reviewer
**Scope**: <git range>
**Generated**: YYYY-MM-DD

## Findings
### Blockers
### Warnings
### Suggestions
### Praise

## Decision
Pass / Block / Conditional Pass

[HANDOFF: dev | human-pr-review]
```

## 參考

- `.claude/protocols/review-protocol.md`
- `docs/architecture/invariants.md`
