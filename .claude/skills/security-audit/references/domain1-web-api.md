# Domain 1 — Web Application & API Security

**Standard:** OWASP Top 10:2025 + OWASP API Security Top 10
**Scope:** Backend API (Cloudflare Workers) + Client-side API consumption (Ktor)
**Last Updated:** 2026-04

---

## Execution Guide

Assess both **server-side** (Workers code in `../Menu-Superpower/`) and **client-side** (Ktor client in `core/network/`). If backend repo is not accessible, mark server-side items as `N/A — requires backend access` and focus on client-side checks.

---

## A01 — Broken Access Control *(CRITICAL)*

**CWE:** CWE-22, CWE-284, CWE-285, CWE-639, CWE-918

| # | Check Item | Severity | Side |
|---|-----------|----------|------|
| 1.1 | Access control enforced server-side on every request; client-side controls are not sole enforcement. | CRITICAL | Server |
| 1.2 | IDOR prevented — user cannot access another user's resources by modifying IDs (e.g., `deviceId`, `userId`). | CRITICAL | Server |
| 1.3 | Vertical privilege escalation prevented — FREE user cannot invoke PRO-only endpoints. | CRITICAL | Server |
| 1.4 | SSRF protections in place: outbound requests restricted to allowlist; internal endpoints blocked. | CRITICAL | Server |
| 1.5 | Directory traversal mitigated; file path inputs canonicalized. | HIGH | Server |
| 1.6 | JWT validated for signature, expiry, audience, and issuer on every protected endpoint. | HIGH | Both |
| 1.7 | Least privilege applied to all service accounts and API keys. | HIGH | Server |
| 1.8 | CORS policies restrict allowed origins to explicit allowlist; no wildcard on credentialed endpoints. | HIGH | Server |
| 1.9 | Object-level authorization enforced at data layer (D1 queries), not only routing. | HIGH | Server |

**MaiNeu Notes:**
- Device-binding auth: verify `deviceId` in JWT matches request context
- Quota enforcement: verify server rejects requests when quota exhausted (not just client-side UI hiding)
- Check `../Menu-Superpower/src/` for access control middleware

**Remediation:** Centralized access control module. Deny by default. RBAC for user plans (FREE/PRO/ENTERPRISE). Log all access-control failures.

---

## A02 — Security Misconfiguration *(HIGH)*

**CWE:** CWE-16, CWE-209, CWE-611, CWE-732

| # | Check Item | Severity | Side |
|---|-----------|----------|------|
| 2.1 | Default credentials changed on all components (Cloudflare dashboard, D1). | CRITICAL | Server |
| 2.2 | Debug mode and verbose error messages disabled in production Workers. | HIGH | Server |
| 2.3 | Security headers present: `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`. | HIGH | Server |
| 2.5 | Unnecessary features/services/endpoints disabled in production. | HIGH | Server |
| 2.6 | Server/technology stack info suppressed from response headers. | MEDIUM | Server |
| 2.8 | R2 storage buckets private by default; no public read/write unless documented. | CRITICAL | Server |
| 2.9 | Admin interfaces protected by MFA and IP allowlisting (Cloudflare Access). | HIGH | Server |

**MaiNeu Notes:**
- Check if Workers return stack traces in error responses
- Verify admin dashboard (`../Menu-Superpower/admin/`) is behind Cloudflare Access
- Check R2 bucket ACL policies

---

## A03 — Software Supply Chain Failures *(HIGH)*

**CWE:** CWE-494, CWE-829, CWE-937, CWE-1104

| # | Check Item | Severity | Side |
|---|-----------|----------|------|
| 3.1 | SBOM generated for production builds. | HIGH | Both |
| 3.2 | Dependencies pinned to specific versions with lock files (`gradle.lockfile`, `package-lock.json`). | HIGH | Both |
| 3.3 | Dependency scanning (SCA) runs on PRs; critical CVEs block merge. | CRITICAL | Both |
| 3.4 | CI/CD pipeline hardened: secrets not logged, runner environments ephemeral. | HIGH | Both |
| 3.6 | Private package registries used where possible; dependency confusion prevented. | HIGH | Server |
| 3.8 | Transitive dependencies included in vulnerability scan scope. | MEDIUM | Both |

**MaiNeu Notes:**
- Android: Check `libs.versions.toml` for pinned versions, run `./gradlew dependencyCheckAnalyze`
- Workers: Check `package-lock.json`, run `npm audit`
- Verify GitHub Actions / Wrangler deploy pipeline doesn't expose secrets in logs

---

## A04 — Cryptographic Failures *(HIGH)*

**CWE:** CWE-310, CWE-319, CWE-326, CWE-327

| # | Check Item | Severity | Side |
|---|-----------|----------|------|
| 4.1 | All data in transit encrypted via TLS 1.2+; TLS 1.0/1.1 disabled. | CRITICAL | Both |
| 4.2 | Passwords hashed with bcrypt (cost >= 12), Argon2id, or scrypt. No MD5/SHA-1/unsalted SHA-2. | CRITICAL | Server |
| 4.3 | Sensitive data (PII) encrypted at rest. | HIGH | Both |
| 4.4 | Crypto keys stored in KMS, never hardcoded. | CRITICAL | Both |
| 4.5 | TLS certificate validation not disabled in any HTTP client. | HIGH | Client |
| 4.6 | Secure random used for all security-sensitive tokens. | HIGH | Server |

**MaiNeu Notes:**
- Client: Verify Ktor/OkHttp TLS config in `HttpClientFactory.kt`
- Client: Verify `EncryptedSharedPreferences` uses AES256-GCM (already confirmed)
- Server: Check D1 encryption at rest (Cloudflare-managed)

---

## A05 — Injection *(CRITICAL)*

**CWE:** CWE-77, CWE-78, CWE-79, CWE-89, CWE-943

| # | Check Item | Severity | Side |
|---|-----------|----------|------|
| 5.1 | All D1 database queries use parameterized statements. No string concatenation with user input. | CRITICAL | Server |
| 5.4 | Template engines use auto-escaping. | HIGH | Server |
| 5.5 | ORM/query builder does not allow raw query injection. | HIGH | Server |
| 5.6 | All user input validated against strict schema (type, length, format). | HIGH | Both |

**MaiNeu Notes:**
- Client-side: Ktor serialization validates response schema (`@Serializable` data classes)
- Server-side: Check D1 `.bind()` usage vs string interpolation in SQL
- Room DB: Verify `@Query` annotations use parameterized queries (`:param` syntax)

---

## A06 — Insecure Design *(MEDIUM)*

| # | Check Item | Severity |
|---|-----------|----------|
| 6.2 | Rate limiting on sensitive flows: login, registration, password reset, scan API. | HIGH |
| 6.3 | API responses do not expose data beyond caller's authorization. | HIGH |
| 6.4 | Multi-step flows (purchase, subscription) enforce state integrity. | HIGH |
| 6.6 | Race conditions (TOCTOU) prevented in quota checking and token refresh. | MEDIUM |

---

## A07 — Identification & Authentication Failures *(HIGH)*

**CWE:** CWE-287, CWE-307, CWE-384, CWE-613

| # | Check Item | Severity | Side |
|---|-----------|----------|------|
| 7.1 | MFA available for admin/privileged accounts. | CRITICAL | Server |
| 7.2 | Account lockout / progressive delay after repeated failed auth. | HIGH | Server |
| 7.3 | Session tokens: >= 128 bits entropy, HTTPS only, invalidated on logout. | HIGH | Both |
| 7.4 | Session rotated upon privilege escalation (after login). | HIGH | Both |
| 7.7 | Auth error messages generic — do not reveal if email is registered. | MEDIUM | Both |

**MaiNeu Notes:**
- Check `AuthManager` login/link flow error messages
- CLAUDE.md lesson: link failure is expected flow, should not set error state

---

## A08 — Software & Data Integrity Failures *(HIGH)*

| # | Check Item | Severity |
|---|-----------|----------|
| 8.1 | No insecure deserialization of untrusted data. Kotlin serialization with strict schema. | CRITICAL |
| 8.2 | Auto-update mechanisms verify signatures before applying. | HIGH |

**MaiNeu Notes:** Kotlin `@Serializable` with explicit field declarations = safe by default. Check for any `Json { ignoreUnknownKeys = true }` that might be too permissive.

---

## A09 — Security Logging & Monitoring *(HIGH)*

| # | Check Item | Severity |
|---|-----------|----------|
| 9.1 | Auth events (success/failure), authorization failures, admin actions logged with timestamp + source IP + user ID. | HIGH |
| 9.2 | Logs do not contain passwords, tokens, PII. | HIGH |
| 9.3 | Log integrity protected (append-only or remote SIEM). | HIGH |
| 9.4 | Alerting on anomalous patterns (repeated auth failures, mass data export). | HIGH |

---

## A10 — Mishandling of Exceptional Conditions *(HIGH)*

**CWE:** CWE-209, CWE-390, CWE-755, CWE-756

| # | Check Item | Severity | Side |
|---|-----------|----------|------|
| 10.1 | Exception handlers fail closed (deny access) not fail open. | CRITICAL | Both |
| 10.2 | No internal exception details returned to clients in production. | HIGH | Server |
| 10.3 | Null pointer / unhandled exceptions don't crash app observably. | HIGH | Client |
| 10.4 | Resource exhaustion handled gracefully with fallback. | MEDIUM | Both |
| 10.5 | Timeout handling on all external service calls; no cascading failure. | HIGH | Both |
| 10.6 | No exception swallowing in security-critical paths (auth, payment). | HIGH | Both |

**MaiNeu Notes:**
- CLAUDE.md lesson: `catch (e: Exception)` catches `CancellationException` — must guard
- Check `executeWithAuth` recovery logic: registered user must not get anonymous re-auth
- Verify Ktor client timeouts (30s connect, 120s read/write in `HttpClientFactory.kt`)
