# security-audit — baseline, scan targets and standards

> Reference for `.claude/skills/security-audit/SKILL.md`. What to inventory before auditing, where to look, which standard each domain maps to, and when to re-run.

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

## Re-assessment Triggers

Re-run this audit under the following circumstances:
- Any CRITICAL finding has been fixed (verify the fix actually took effect)
- A major architectural change occurred
- A new major version was deployed
- A confirmed security incident occurred
- A new third-party SDK was added
- The auth flow or a payment-related flow was modified

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
