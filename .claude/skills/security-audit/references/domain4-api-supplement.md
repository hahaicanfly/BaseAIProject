# Domain 4 — API Security Supplement

> Reference for `.claude/skills/security-audit/SKILL.md` — Phase 1 domain: API Supplement (API-1~10). Loaded for the scopes listed in that file's Phase 1 table.

**Standard:** OWASP API Security Top 10 (2023)
**Scope:** MaiNeu REST API (`api.maineu.com`) — both server and client perspectives
**API Spec:** `../Menu-Superpower/contracts/openapi.yaml` (Source of Truth)
**Last Updated:** 2026-04

---

## Execution Guide

This domain supplements Domain 1 with API-specific depth. Assess from both sides:
- **Server-side:** Workers handlers, middleware, D1 queries
- **Client-side:** Ktor client in `core/network/`, response handling, error propagation

---

## API Security Top 10 Checklist

| # | Category | Check Item | Severity | MaiNeu Mapping |
|---|----------|-----------|----------|----------------|
| API-1 | Broken Object Level Authorization | Every endpoint enforces object-level auth; requests for other users' resources return 403, not 200 with filtered data. | CRITICAL | Device-binding: `deviceId` in JWT must match request. User cannot access other users' scan history/orders. |
| API-2 | Broken Authentication | Tokens have defined expiry; refresh token rotation implemented; revoked tokens immediately invalidated server-side. | CRITICAL | `AndroidTokenStorage` token expiry (5 min buffer). Check server-side revocation on logout/device revoke. |
| API-3 | Broken Object Property Level Authorization | Responses exclude unauthorized fields; mass assignment prevented (no accepting all fields without allowlist). | HIGH | Check if `@Serializable` request models expose internal fields. Verify server allowlists writable fields. |
| API-4 | Unrestricted Resource Consumption | Rate limiting, request size limits, and query complexity limits enforced on all endpoints. | HIGH | Check Cloudflare rate limiting on `/auth/*`, `/parse/*`, `/scan/*`. Verify request body size limits. |
| API-5 | Broken Function Level Authorization | Admin functions on separate auth domain or require elevated privilege — not merely hidden from UI. | CRITICAL | Admin dashboard at `../Menu-Superpower/admin/` must be behind Cloudflare Access. Verify admin API routes not accessible with user JWT. |
| API-6 | Unrestricted Access to Sensitive Business Flows | High-value flows (registration, referral redemption, scan) have abuse rate controls. | HIGH | Quota system server-side enforcement. Check referral code redemption for abuse prevention. |
| API-7 | Server-Side Request Forgery | APIs accepting URLs validate against allowlist; no internal network requests from user-supplied URLs. | HIGH | Check if any endpoint accepts URL input (e.g., image URL for parsing). |
| API-8 | Security Misconfiguration | API documentation (OpenAPI/Swagger) not publicly accessible in production; default credentials changed. | HIGH | Verify `openapi.yaml` not served by production Workers. Check admin default creds. |
| API-9 | Improper Inventory Management | Complete API inventory maintained; deprecated versions decommissioned; shadow APIs identified. | MEDIUM | Compare `openapi.yaml` spec vs actual Worker routes. Identify undocumented endpoints. |
| API-10 | Unsafe Consumption of APIs | Third-party API responses treated as untrusted input; schema validation before processing. | HIGH | Gemini/Claude API responses: verify validation before storing/displaying. RevenueCat webhook payload validation. |

---

## Client-Side API Security Checks

Specific to the Android client's API consumption layer.

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| CL-1 | Ktor client enforces TLS; no plaintext HTTP to production. | CRITICAL | `core/network/.../HttpClientFactory.kt` |
| CL-2 | JWT tokens transmitted in `Authorization` header only, never in URL query params or body. | HIGH | `core/network/.../MenuApiClientImpl.kt` |
| CL-3 | API error responses do not leak server internals to client logs. | HIGH | `core/network/.../util/SecureLogging.kt`, error handling |
| CL-4 | Response deserialization uses strict schema (`@Serializable` with explicit fields). Reject unknown/malformed responses. | HIGH | `core/network/.../ApiModels.kt`, Json config |
| CL-5 | Token refresh race condition handled: concurrent requests wait for single refresh, not parallel refreshes. | HIGH | `core/network/.../AuthManager.kt` `executeWithAuth` |
| CL-6 | `CancellationException` not swallowed in API call error handlers. | HIGH | All `catch (e: Exception)` blocks in network layer |
| CL-7 | Device ID sent with every authenticated request; backend validates device binding. | HIGH | Request interceptor, `AuthManager` |
| CL-8 | API responses with `null` fields handled defensively (nullable fields with defaults in data classes). | MEDIUM | `core/network/.../ApiModels.kt` field declarations |

**MaiNeu Notes:**
- CLAUDE.md lessons document multiple `CancellationException` issues — verify all are fixed
- `executeWithAuth` has ACCOUNT_REVOKED recovery that must distinguish registered vs anonymous users
- `@Serializable` fields should default to nullable for non-core backend fields

---

## Auth Flow Security Checks

Specific to MaiNeu's device-binding + JWT auth model.

| # | Check Item | Severity | What to Check |
|---|-----------|----------|---------------|
| AF-1 | Anonymous auth request includes `deviceId`; backend binds token to device. | CRITICAL | `AnonymousAuthRequest`, `AuthManager.authenticate()` |
| AF-2 | Login/link request includes `deviceId`; DEVICE_NOT_FOUND handled correctly. | CRITICAL | `LoginRequest`, `OAuthRequest` |
| AF-3 | Token refresh preserves device binding; new token still bound to same device. | HIGH | Refresh token flow |
| AF-4 | `restoreSession()` validates token AND device binding, not just `hasRegisteredAccount` flag. | HIGH | `AuthManager.restoreSession()` |
| AF-5 | `applyCloudData()` only merges cloud-synced fields; does not overwrite client-only preferences. | HIGH | Cloud data sync flow |

**MaiNeu Notes:** These checks derive directly from CLAUDE.md accumulated lessons — they represent real bugs that were found and fixed. The audit verifies the fixes remain in place.
