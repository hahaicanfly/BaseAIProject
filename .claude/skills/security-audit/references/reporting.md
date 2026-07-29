# security-audit — severity, findings and report templates

> Reference for `.claude/skills/security-audit/SKILL.md`. Everything about how a finding is graded, escalated and written up.

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

For each `FAIL` or `PARTIAL` item:

```markdown
### FINDING #[N]

| Field | Value |
|-------|-------|
| **Check ID** | [e.g., S-1.7, A01-1.6, API-2] |
| **Title** | [short title] |
| **Severity** | CRITICAL / HIGH / MEDIUM / LOW |
| **Status** | FAIL / PARTIAL |
| **Description** | [what was found] |
| **Evidence** | [file path + line number, or grep result] |
| **CWE** | CWE-[XXX] |
| **Remediation** | [concrete fix and code guidance] |
| **OWASP Ref** | [standard + section, e.g. MASVS-STORAGE S-1.7] |
```

## Escalation Rules

| Condition | Action |
|-----------|--------|
| Any single CRITICAL finding | **Escalate immediately** — notify the user before continuing the audit |
| 3+ HIGH findings within the same domain | mark that domain as **HIGH RISK** |
| Evidence of active exploitation found | **Stop the assessment** — escalate |
| A secret / credential found in code | **Warn immediately** — recommend key rotation |

## Scoring Summary Template

```markdown
## OWASP Security Audit Report — [Project Name]

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
1. **Immediate** (< 24h): [CRITICAL fixes]
2. **Short-term** (< 7 days): [HIGH fixes]
3. **Next release**: [MEDIUM fixes]
4. **Backlog**: [LOW/INFO items]
```

---

## Severity Classification Matrix

| Severity | CVSS v3 Range | Response SLA | Example |
|----------|--------------|-------------|---------|
| CRITICAL | 9.0 - 10.0 | < 24 hours | Plaintext-stored token, public bucket with PII, hardcoded API key |
| HIGH | 7.0 - 8.9 | < 7 days | Cert pinning not enabled, TLS validation disabled, no rate limiting on auth endpoint |
| MEDIUM | 4.0 - 6.9 | < 30 days | Overly verbose error messages, missing security headers, weak password policy |
| LOW | 0.1 - 3.9 | Next release | Server banner leaking version info, missing cookie flags |
| INFO | N/A | Backlog | Best-practice suggestion, documentation gap |
