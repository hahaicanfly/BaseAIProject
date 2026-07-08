---
name: security-audit
description: Full security review covering authentication, key leakage, dependency vulnerabilities, and OWASP standard checks; triggers when the user wants a security audit, vulnerability scan, or mentions "安全審查", "security audit".
---

# Skill: security-audit

> **Purpose**: A systematic security audit based on the OWASP 2025 standards, covering auth / secrets / dependency-vulnerability across 4 domains (Web/API, Mobile Android, Cloud Infra, API Supplement); scope can be tailored to the project's tech stack.
> **Trigger**: `/security-audit [scope]`
> **Agent**: security-reviewer (opus, see `.claude/agents/security-reviewer.md`)

## Usage

```
/security-audit [scope]
```

| Scope | Description | Reference Files Loaded |
|-------|-------------|----------------------|
| `full` | Full 4-domain audit | All 4 reference files |
| `mobile` | Android MASVS checks (for Android projects) | `references/domain2-mobile-android.md` |
| `api` | Backend API security | `references/domain1-web-api.md` + `references/domain4-api-supplement.md` |
| `cloud` | Cloud infrastructure | `references/domain3-cloud-infra.md` |
| `quick` | Quick secrets/config/deps scan | none (inline checklist) |

Default scope: `full`

---

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

---

## Execution Workflow

### Phase 0 — Pre-flight (always run first)

Regardless of scope, run the following checks first:

**0.1 — Secrets Scan**

Scan the entire codebase for the following patterns (excluding build output directories, `node_modules/`, `.gradle/`, etc.):
```
api[_-]?key\s*=\s*["'][^"']+
secret[_-]?key\s*=\s*["'][^"']+
password\s*=\s*["'][^"']+
credential
bearer\s+[A-Za-z0-9\-._~+/]+=*
private[_-]?key
-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----
sk-[a-zA-Z0-9]{20,}
ghp_[a-zA-Z0-9]{36}
goog_[a-zA-Z0-9]{20,}
```

File types depend on the project's tech stack, e.g. `*.ts`, `*.js`, `*.py`, `*.go`; for Android projects also scan `*.kt`, `*.java`, `*.xml`, `*.gradle.kts`.

**0.2 — Configuration Validation**
```
[ ] .gitignore covers: .env*, *secret*, *credential*, *.pem, *.key, *.p12
[ ] For Android projects: .gitignore also covers local.properties, *.keystore, *.jks, google-services.json
[ ] Sensitive config files (local.properties / .env.production, etc.) are not committed to git
[ ] No keystore / private key files in the repo
[ ] Secrets in build config come from environment variables or the CI secret store, not hardcoded
```

**0.3 — Dependency Audit**

Choose based on the project's tech stack (see CLAUDE.md Quick Commands for details):
```bash
npm audit            # Node.js
pip-audit             # Python
cargo audit           # Rust
```
For Android projects: run a dependency-check task via Gradle (e.g. the OWASP Dependency-Check plugin) and list the full dependency tree for manual review.

If scope = `quick`, stop here and output the report.

---

### Phase 1 — Domain Execution

Run the domains corresponding to the given scope, in order. For each domain, read the corresponding reference file first, then assess item by item.

| Order | Domain | Reference File | Scopes |
|-------|--------|---------------|--------|
| 1 | Web & API Security (A01-A10) | `references/domain1-web-api.md` | `full`, `api` |
| 2 | Mobile Android (MASVS) (for Android projects) | `references/domain2-mobile-android.md` | `full`, `mobile` |
| 3 | Cloud Infrastructure (C01-C06) | `references/domain3-cloud-infra.md` | `full`, `cloud` |
| 4 | API Supplement (API-1~10) | `references/domain4-api-supplement.md` | `full`, `api` |

> `references/domain2-mobile-android.md` and `references/domain3-cloud-infra.md` contain concrete examples (Ktor / Cloudflare Workers, etc.); if the project's tech stack differs, treat that content as a reference example for the check item and map it to the project's actual equivalent mechanism (e.g. the project's own HTTP client, cloud platform).

**Per-Item Assessment Protocol:**

For each check item in the reference file:

1. **Read** the relevant project files to gather evidence
2. **Assess** against the check criteria
3. **Assign status:** `PASS` | `FAIL` | `PARTIAL` | `N/A`
4. **Record** per the output format below
5. **CRITICAL findings** — flag immediately, don't wait for the full report

---

### Phase 2 — Scoring & Report

Once all domains are assessed, produce a scoring summary and prioritized remediation list.

---

## Project Security Baseline

Before a formal audit, inventory the project's existing security measures first, focusing on "what's already implemented" and "known gaps" — this focuses audit effort on deltas and new code. Baseline data comes from `agent_docs/TECHNICAL-REFERENCE.md` (once filled in) or a project's own security documentation; if that hasn't been assembled yet, use the table below as an inventory template to fill in yourself — don't fabricate content.

| Area | Status | Key Files |
|------|--------|-----------|
| Token / secret encrypted storage | [fill in per project] | [fill in per project] |
| Log redaction (avoid token/PII in logs) | [fill in per project] | [fill in per project] |
| Transport security (TLS config / cert pinning) | [fill in per project] | [fill in per project] |
| For Android projects: backup and component export restrictions (`allowBackup`, `exported`) | [fill in per project] | `AndroidManifest.xml` |
| Build hardening (obfuscation / minification) | [fill in per project] | [fill in per project] |

**Known Gaps**: list unresolved or intentionally deferred risk items here (e.g. cert pinning not yet enabled, database not encrypted, no root/jailbreak detection) — treat these as priority audit targets, to avoid rediscovering known issues without scheduling a fix.

---

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

---

## Escalation Rules

| Condition | Action |
|-----------|--------|
| Any single CRITICAL finding | **Escalate immediately** — notify the user before continuing the audit |
| 3+ HIGH findings within the same domain | mark that domain as **HIGH RISK** |
| Evidence of active exploitation found | **Stop the assessment** — escalate |
| A secret / credential found in code | **Warn immediately** — recommend key rotation |

---

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

---

## Re-assessment Triggers

Re-run this audit under the following circumstances:
- Any CRITICAL finding has been fixed (verify the fix actually took effect)
- A major architectural change occurred
- A new major version was deployed
- A confirmed security incident occurred
- A new third-party SDK was added
- The auth flow or a payment-related flow was modified

---

## Quick Reference — Scan Targets

Below are common scan-target categories; specific file paths depend on the project structure (cross-reference `agent_docs/TECHNICAL-REFERENCE.md`):

### Android Client (for Android projects)
```
AndroidManifest.xml                       — permissions, exported components, backup settings
res/xml/network_security_config.xml       — TLS, cert pinning
res/xml/file_paths.xml (if using FileProvider) — FileProvider scope
build.gradle.kts                          — dependencies, build config, minification
proguard-rules.pro                        — obfuscation rules
[project-specific] token storage implementation — token encryption and lifecycle management
[project-specific] HTTP client config     — TLS config, certificate validation
[project-specific] auth flow management   — token lifecycle, login/logout/revocation
[project-specific] API client implementation — API calls, header injection
[project-specific] logging utility        — log redaction
[project-specific] encrypted storage config — encryption-at-rest settings
[project-specific] local database config  — DB encryption settings
```

### Backend Services (if accessible)
```
Environment / secrets config files (.env, wrangler-style config, IaC variable files) — bindings, secret references
API handler / middleware source            — access control, input validation
API spec document (OpenAPI/Swagger, etc.)  — API contract vs. actual routes
Admin dashboard (if any)                   — whether access control is separated from regular users
.gitignore                                 — sensitive-file exclusion rules
```

---

## OWASP Standard Cross-Reference

| Standard | Domain | Version |
|----------|--------|---------|
| OWASP Top 10 | Web / API Backend | 2025 |
| OWASP API Security Top 10 | REST APIs | 2023 |
| OWASP MASVS | Android Mobile | v2.x (2025) |
| OWASP MASTG | Mobile Testing | Current (2025) |
| OWASP ASVS | Web Verification | v4.0.3 |
| OWASP Cloud-Native AppSec Top 10 | Cloud | 2022 |

---

## Verification Items

- **Output form**: an OWASP-style security report covering 4 domains (Web/API, Mobile MASVS, Cloud Infra, API Top 10).
- **Required invariants check**: `INV-SEC-001` ~ `INV-SEC-003` in `docs/architecture/invariants.md` (per the current list in invariants.md; if no corresponding INV exists, list auth/secret risk items independently); secret scan `grep -rE 'API_KEY|TOKEN|PASSWORD'` returns no hits.
- **Finding disposition**: Critical/High findings are escalated into a new ExecPlan (`docs/plans/active/`, format per `docs/plans/PLANS.md`) or written into the Open Questions section of an existing ExecPlan; Medium is documented only; Low goes to backlog.
- **Severity**: Critical / High → must block merge; Medium → documented in an ExecPlan; Low → backlog.
- **Handoff marker**: on pass, `[HANDOFF: human-pr-review]`; if Critical/High findings exist, `[HUMAN_ATTENTION_REQUIRED: <reason>]`.

## References

- `.claude/agents/security-reviewer.md`
- `docs/architecture/invariants.md` INV-SEC-*
- `references/domain1-web-api.md`, `references/domain2-mobile-android.md`, `references/domain3-cloud-infra.md`, `references/domain4-api-supplement.md`
