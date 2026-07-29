# Domain 3 — Cloud Infrastructure Security

> Reference for `.claude/skills/security-audit/SKILL.md` — Phase 1 domain: Cloud Infrastructure (C01-C06). Loaded for the scopes listed in that file's Phase 1 table.

**Standard:** OWASP Cloud-Native Application Security Top 10 + CIS Benchmarks
**Platform:** Cloudflare Workers + D1 + R2 (Serverless Edge)
**Last Updated:** 2026-04

---

## Stack Context

MaiNeu backend runs on **Cloudflare Workers** (serverless edge compute), not traditional cloud VMs or Kubernetes. This significantly changes the audit scope:

- **N/A:** VPC, security groups, EC2, K8s, container images, pod security
- **Applicable:** IAM (Cloudflare API tokens), D1 database access, R2 bucket policies, Workers secrets, Wrangler deployment pipeline, Cloudflare Access for admin

---

## C01 — Identity & Access Management *(CRITICAL)*

| # | Check Item | Severity | What to Check |
|---|-----------|----------|---------------|
| CI-1.1 | Cloudflare root account not used for daily operations; MFA enabled. | CRITICAL | Cloudflare dashboard settings |
| CI-1.2 | API tokens follow least-privilege: scoped to specific zones/accounts, not global. | CRITICAL | `wrangler.toml` token references, Cloudflare API token list |
| CI-1.3 | Team access uses Cloudflare Access with MFA; no shared credentials. | HIGH | Cloudflare Access policies |
| CI-1.4 | Worker-to-D1/R2 bindings use Worker-level permissions, not global API keys. | HIGH | `wrangler.toml` bindings config |
| CI-1.5 | Unused API tokens and team members identified and removed quarterly. | HIGH | Cloudflare dashboard audit |

**Remediation:** Create scoped API tokens per deployment environment (dev/staging/prod). Enable MFA on all team accounts. Use Cloudflare Access for admin dashboard.

---

## C02 — Network & Perimeter Security *(HIGH)*

| # | Check Item | Severity | What to Check |
|---|-----------|----------|---------------|
| CN-1.1 | Workers endpoints enforce HTTPS only (Cloudflare default). Verify no HTTP fallback. | HIGH | Cloudflare SSL/TLS settings |
| CN-1.4 | WAF rules enabled on API endpoints covering OWASP Top 10 patterns. | HIGH | Cloudflare WAF configuration |
| CN-1.5 | DDoS protection enabled (Cloudflare built-in). Verify rate limiting rules. | MEDIUM | Cloudflare rate limiting rules |
| CN-1.6 | Workers analytics and logging enabled for traffic anomaly detection. | HIGH | Cloudflare analytics dashboard |

**MaiNeu Notes:**
- Cloudflare provides built-in DDoS protection and TLS termination
- Focus audit on WAF rules and rate limiting configuration
- Check if API endpoints have per-route rate limits (especially `/auth/*`, `/parse/*`)

---

## C03 — Data Security & Encryption *(HIGH)*

| # | Check Item | Severity | What to Check |
|---|-----------|----------|---------------|
| CD-1.1 | D1 database encryption at rest enabled (Cloudflare-managed). | HIGH | Cloudflare D1 documentation / settings |
| CD-1.2 | Data classification performed; PII stores identified with access restrictions. | HIGH | D1 schema review, R2 bucket contents |
| CD-1.3 | D1 database not publicly accessible; only reachable from authorized Workers. | CRITICAL | `wrangler.toml` D1 bindings |
| CD-1.4 | R2 buckets have public access blocked unless explicitly required. | CRITICAL | R2 bucket policies, `wrangler.toml` |
| CD-1.5 | Data retention and destruction policies defined (GDPR/CCPA compliance). | MEDIUM | Privacy policy, data lifecycle docs |
| CD-1.6 | D1 backups configured and stored securely. | HIGH | Cloudflare D1 backup settings |

**Remediation:** Verify D1 is only accessible through Worker bindings (default behavior). Review R2 bucket policies for any public access. Document data retention policy.

---

## C04 — Container & Kubernetes Security

**STATUS: N/A**

MaiNeu uses Cloudflare Workers (serverless edge), not containers or Kubernetes. Skip entire C04 section. All CK-1.1 through CK-1.8 items are not applicable.

---

## C05 — Secrets Management *(CRITICAL)*

| # | Check Item | Severity | What to Check |
|---|-----------|----------|---------------|
| CS-1.1 | No secrets in source code repositories (even private repos or git history). | CRITICAL | Grep for API keys, passwords in `../Menu-Superpower/` |
| CS-1.2 | Workers secrets managed via `wrangler secret put`, not environment variables in `wrangler.toml`. | HIGH | `wrangler.toml` — no plaintext secrets |
| CS-1.3 | Pre-commit secret detection hooks installed. `.dev.vars` in `.gitignore`. | HIGH | `.gitignore`, pre-commit config |
| CS-1.4 | Secrets rotation policy defined; API keys rotate at least annually. | HIGH | Rotation schedule documentation |
| CS-1.5 | Access to secrets management is audited and restricted. | HIGH | Cloudflare dashboard audit logs |

**MaiNeu Notes:**
- Check `../Menu-Superpower/wrangler.toml` for any plaintext secrets
- Verify `.dev.vars` is gitignored (local development secrets)
- Check git history for any previously committed secrets: `git log -p --all -S 'secret\|api_key\|password'`

**Remediation:** Use `wrangler secret put` exclusively. Add `gitleaks` or `trufflehog` to CI pipeline. Document rotation schedule for all API keys (Anthropic, Gemini, RevenueCat, Google OAuth).

---

## C06 — Observability, Logging & Incident Response *(HIGH)*

| # | Check Item | Severity | What to Check |
|---|-----------|----------|---------------|
| CO-1.1 | Cloudflare audit logging enabled for account actions. | HIGH | Cloudflare audit log settings |
| CO-1.2 | Workers logs capture security events (auth failures, rate limit triggers). | HIGH | Worker logging implementation |
| CO-1.3 | Alerting configured for anomalous patterns (burst auth failures, unusual traffic). | HIGH | Cloudflare notifications / alerts |
| CO-1.4 | Incident response runbook exists for: credential compromise, data exfiltration, API abuse. | MEDIUM | Documentation review |
| CO-1.5 | Disaster recovery plan with RPO/RTO defined and tested. | MEDIUM | Documentation review |

**MaiNeu Notes:**
- Cloudflare provides Workers analytics, but custom logging may be needed for security events
- Check if auth failures are logged with device ID and IP
- Verify Logpush is configured if long-term log retention is needed

---

## Cloudflare-Specific Additional Checks

| # | Check Item | Severity | What to Check |
|---|-----------|----------|---------------|
| CF-1 | Workers per-route rate limiting configured (especially auth, parse, scan endpoints). | HIGH | Cloudflare rate limiting rules |
| CF-2 | Environment isolation: separate Workers for dev/ut/staging/prod with distinct secrets. | HIGH | `wrangler.toml` environments |
| CF-3 | Custom domain TLS: minimum TLS 1.2, HSTS enabled. | HIGH | Cloudflare SSL/TLS settings |
| CF-4 | Bot protection / challenge page enabled for sensitive endpoints. | MEDIUM | Cloudflare security settings |
| CF-5 | Workers CPU time and memory limits appropriate — no DoS via expensive operations. | MEDIUM | Worker code review for unbounded loops |
