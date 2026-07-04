---
name: security-audit
description: 完整安全審查，涵蓋認證、密鑰洩漏、依賴漏洞與 OWASP 標準檢查；當使用者要做安全稽核、弱點掃描或提及「安全審查」「security audit」時觸發。
---

# Skill: security-audit

> **用途**：完整安全審查，涵蓋 auth / secret / 依賴漏洞。
> **觸發**：`/security-audit`
> **Agent**：security-reviewer（sonnet）

## 執行步驟

1. 讀 `docs/architecture/invariants.md` INV-SEC-*（依 invariants.md 現行清單；無對應 INV 時自行列出 auth 風險項）相關規則
2. 掃描代碼中的硬編碼 secret：
   ```bash
   grep -rn "API_KEY\|TOKEN\|PASSWORD\|SECRET" --include="*.ts" --include="*.js" --include="*.py" src/
   ```
3. 檢查 OAuth / JWT / token 流程
4. 驗證敏感頁面保護措施
5. 審查依賴漏洞（`npm audit` / `pip-audit` / `cargo audit` 等）
6. 輸出安全報告

## 輸出格式

```markdown
# Security Audit Report

## Critical Issues
## High Issues
## Medium Issues
## Recommendations

[HANDOFF: dev | human-pr-review]
```

## 參考

- `.claude/agents/security-reviewer.md`
- `docs/architecture/invariants.md` INV-SEC-*（依 invariants.md 現行清單；無對應 INV 時自行列出 auth 風險項）
