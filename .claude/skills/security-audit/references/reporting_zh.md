# security-audit — 嚴重度、findings 與報告範本

> `.claude/skills/security-audit/SKILL_zh.md` 的參考檔。findings 如何分級、升級與撰寫的全部說明。

## Agent Operating Protocol

```
ROLE:        Security Auditor Agent
FRAMEWORK:   OWASP 2025 (Top 10 + MASVS v2 + API Security + Cloud-Native)
MODE:        Systematic Checklist Execution
SEVERITY:
  CRITICAL — Immediate exploitability; data breach or system compromise likely
  HIGH     — Significant risk; requires urgent remediation
  MEDIUM   — Exploitable under specific conditions; address in next release
  LOW      — Minor risk; address in routine maintenance
  INFO     — Observation or best-practice note
```

## Finding Output Format

對每個 `FAIL` 或 `PARTIAL` 項目：

```markdown
### FINDING #[N]

| Field | Value |
|-------|-------|
| **Check ID** | [e.g., S-1.7, A01-1.6, API-2] |
| **Title** | [簡短標題] |
| **Severity** | CRITICAL / HIGH / MEDIUM / LOW |
| **Status** | FAIL / PARTIAL |
| **Description** | [發現了什麼] |
| **Evidence** | [檔案路徑 + 行號，或 grep 結果] |
| **CWE** | CWE-[XXX] |
| **Remediation** | [具體修復方式與程式碼指引] |
| **OWASP Ref** | [標準 + 章節，例如 MASVS-STORAGE S-1.7] |
```

## Escalation Rules

| Condition | Action |
|-----------|--------|
| 出現任何單一 CRITICAL finding | **立即升級** — 在繼續審計前先告知使用者 |
| 同一 domain 內出現 3+ HIGH findings | 該 domain 標記為 **HIGH RISK** |
| 發現主動遭利用的證據 | **停止評估** — 升級處理 |
| 代碼中發現 secret / credential | **立即警示** — 建議輪替金鑰 |

## Scoring Summary Template

```markdown
## OWASP Security Audit Report — [專案名稱]

### Audit Metadata
- **Date:** [YYYY-MM-DD]
- **Scope:** [full / mobile / api / cloud / quick]
- **Standards:** OWASP Top 10:2025, MASVS v2, API Security Top 10
- **Auditor:** security-reviewer agent

### Risk Summary

| Severity | Count |
|----------|-------|
| CRITICAL | X |
| HIGH     | X |
| MEDIUM   | X |
| LOW      | X |
| INFO     | X |

### Domain Scores

| Domain | PASS | FAIL | PARTIAL | N/A | Risk Level |
|--------|------|------|---------|-----|------------|
| Web & API (A01-A10) | X | X | X | X | [LOW/MED/HIGH/CRIT] |
| Mobile Android (MASVS) | X | X | X | X | [LOW/MED/HIGH/CRIT] |
| Cloud Infrastructure | X | X | X | X | [LOW/MED/HIGH/CRIT] |
| API Supplement | X | X | X | X | [LOW/MED/HIGH/CRIT] |

### Overall Risk Rating: [LOW / MEDIUM / HIGH / CRITICAL]

### Findings (sorted by severity)

[Finding records here...]

### Prioritized Remediation

| Priority | Finding | Effort | Impact |
|----------|---------|--------|--------|
| 1 | [CRITICAL item] | [Low/Med/High] | [Description] |
| 2 | [HIGH item] | [Low/Med/High] | [Description] |
| ... | | | |

### Recommendations
1. **Immediate** (< 24h)：[CRITICAL fixes]
2. **Short-term** (< 7 days)：[HIGH fixes]
3. **Next release**：[MEDIUM fixes]
4. **Backlog**：[LOW/INFO items]
```

---

## Severity Classification Matrix

| Severity | CVSS v3 Range | Response SLA | Example |
|----------|--------------|-------------|---------|
| CRITICAL | 9.0 - 10.0 | < 24 hours | 明文儲存 token、public bucket 含 PII、硬編碼 API key |
| HIGH | 7.0 - 8.9 | < 7 days | 未啟用 cert pinning、TLS 驗證被關閉、auth 端點無 rate limiting |
| MEDIUM | 4.0 - 6.9 | < 30 days | 錯誤訊息過於詳細、缺少安全 headers、弱密碼政策 |
| LOW | 0.1 - 3.9 | Next release | Server banner 洩漏版本資訊、cookie flag 缺失 |
| INFO | N/A | Backlog | 最佳實踐建議、文件缺口 |
