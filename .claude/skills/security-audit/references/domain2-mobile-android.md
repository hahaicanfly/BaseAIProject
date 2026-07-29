# Domain 2 — Mobile Application Security (Android)

> Reference for `.claude/skills/security-audit/SKILL.md` — Phase 1 domain: Mobile Android (MASVS). Loaded for the scopes listed in that file's Phase 1 table.

**Standard:** OWASP MASVS v2.x (2025) + OWASP MASTG
**Profile:** MAS-L1 (standard) + selective MAS-L2/MAS-R checks
**Platform:** Android (Kotlin, Jetpack Compose)
**Last Updated:** 2026-04

---

## Execution Guide

For each check item:
1. Read the specified **MaiNeu file(s)** to gather evidence
2. Assign status: `PASS` | `FAIL` | `PARTIAL` | `N/A`
3. Record evidence and remediation if FAIL/PARTIAL
4. CRITICAL/HIGH failures → flag immediately

---

## MASVS-STORAGE — Secure Data Storage

**CWE:** CWE-312, CWE-313, CWE-359, CWE-921, CWE-922

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| S-1.1 | No sensitive data (credentials, tokens, PII) in SharedPreferences without encryption. Verify `EncryptedSharedPreferences` is used exclusively. | CRITICAL | `core/data/.../storage/EncryptedPrefsFactory.kt`, `core/network/.../AndroidTokenStorage.kt` |
| S-1.2 | Android Keystore used for cryptographic key material. Verify `MasterKey` with `AES256_GCM` scheme. | CRITICAL | `core/data/.../storage/EncryptedPrefsFactory.kt` |
| S-1.3 | No sensitive data in Logcat output in release builds. Verify Timber uses `CrashlyticsTree` (not `DebugTree`) in release. Check `SecureLogging` redaction. | HIGH | `app/.../MaiNeuApplication.kt`, `core/network/.../util/SecureLogging.kt` |
| S-1.4 | Keyboard caching disabled on sensitive input fields (passwords, tokens). | MEDIUM | Compose TextField with `KeyboardType.Password` + `visualTransformation` |
| S-1.5 | Screenshots prevented on sensitive views using `FLAG_SECURE`. Check login, payment, and subscription screens. | HIGH | `app/.../LoginActivity.kt`, `app/.../ui/screens/SubscriptionScreen.kt` |
| S-1.6 | No sensitive data written to external storage (SD card) without encryption. Camera images in scoped cache only. | HIGH | `app/src/main/res/xml/file_paths.xml`, image processing code |
| S-1.7 | Room database (`maineu_history.db`) encryption status. If contains PII, should use SQLCipher. | HIGH | `core/data/.../storage/db/AppDatabase.kt` |
| S-1.8 | Sensitive data cleared from memory after use in auth and payment flows. | MEDIUM | `core/network/.../AndroidTokenStorage.kt`, auth flow code |
| S-1.9 | Backup exclusion verified: `android:allowBackup="false"` or backup rules exclude sensitive data. | HIGH | `app/src/main/AndroidManifest.xml` |

**Remediation:** Use `EncryptedSharedPreferences` for all sensitive storage. Add `FLAG_SECURE` to sensitive Activities. Consider SQLCipher for Room if PII is stored. Verify `android:allowBackup="false"`.

---

## MASVS-CRYPTO — Cryptographic Practices

**CWE:** CWE-261, CWE-310, CWE-326, CWE-327, CWE-330

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| C-1.1 | No deprecated algorithms: MD5, SHA-1, DES, RC4, ECB mode. | CRITICAL | Grep entire codebase for `MD5`, `SHA-1`, `DES`, `ECB` |
| C-1.2 | No hardcoded encryption keys in source, binary resources, or config files. | CRITICAL | Grep for `SecretKey`, `AES`, key-like hex/base64 strings |
| C-1.3 | IVs and nonces use `SecureRandom` and are unique per operation. | HIGH | Any custom encryption code |
| C-1.4 | No custom cryptographic implementations — only platform APIs (`javax.crypto`, Android Keystore). | HIGH | Grep for manual crypto operations |
| C-1.5 | Key derivation from passwords uses PBKDF2/bcrypt/Argon2 with adequate iterations. | HIGH | Any password-derived key code (if applicable) |

**Remediation:** Replace any deprecated crypto. Use `MasterKey` + `EncryptedSharedPreferences` (already in place). Never roll custom crypto.

---

## MASVS-AUTH — Authentication & Authorization

**CWE:** CWE-255, CWE-287, CWE-306, CWE-384, CWE-613

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| A-1.1 | Backend auth uses short-lived JWT tokens (not long-lived static credentials). Verify token expiry and refresh flow. | CRITICAL | `core/network/.../AndroidTokenStorage.kt`, `core/network/.../AuthManager.kt` |
| A-1.2 | Biometric auth (if used) implemented via platform APIs within secure enclave — no biometric data exposed to app. | HIGH | Search for `BiometricPrompt` usage |
| A-1.3 | OAuth 2.0 flows use PKCE. Implicit grant flow is not used. | HIGH | `app/.../auth/` Google OAuth flow |
| A-1.4 | Session tokens invalidated server-side on logout — not just client-side deletion. | HIGH | `core/network/.../AuthManager.kt` logout flow |
| A-1.5 | Re-authentication required before sensitive operations (password change, account deletion). | HIGH | Settings / account management screens |

**Remediation:** Ensure JWT access tokens have short expiry (< 30 min). Implement PKCE for all OAuth flows. Server-side token revocation on logout.

---

## MASVS-NETWORK — Network Communication Security

**CWE:** CWE-295, CWE-319, CWE-757

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| N-1.1 | HTTPS enforced for all network communication. HTTP connections to production prohibited. | CRITICAL | `app/src/main/res/xml/network_security_config.xml` |
| N-1.2 | TLS certificate validation NOT disabled anywhere. No `trustAllCerts`, no `ALLOW_ALL_HOSTNAME_VERIFIER`. | CRITICAL | Grep for `trustAll`, `ALLOW_ALL`, `setHostnameVerifier`, `X509TrustManager` |
| N-1.3 | Certificate pinning implemented for production API (MAS-L2). Pin set includes backup pin + rotation procedure. | HIGH | `network_security_config.xml` pin-set section |
| N-1.5 | Android Network Security Config does NOT trust user-installed CA certificates in production. | HIGH | `network_security_config.xml` `<trust-anchors>` |
| N-1.6 | Sensitive data not transmitted in URL query parameters. Tokens sent in headers only. | MEDIUM | `core/network/.../MenuApiClientImpl.kt`, HTTP interceptors |

**Remediation:** Enable certificate pinning in `network_security_config.xml` (template already exists). Verify no debug trust overrides leak to release builds.

---

## MASVS-PLATFORM — Platform Interaction Security

**CWE:** CWE-926, CWE-927, CWE-939

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| P-1.1 | App requests minimum necessary permissions. Each permission has user-facing justification. | HIGH | `app/src/main/AndroidManifest.xml` `<uses-permission>` |
| P-1.2 | Deep link / App Link handlers validate the full URL. Untrusted sources cannot trigger sensitive in-app actions. | HIGH | `AndroidManifest.xml` intent-filters, `LaunchActivity.kt` deep link handling |
| P-1.3 | WebViews: JavaScript disabled on untrusted content. `setAllowUniversalAccessFromFileURLs` and `setAllowFileAccessFromFileURLs` disabled. | HIGH | **N/A for MaiNeu** (no WebView usage — verify with grep) |
| P-1.4 | No sensitive Java objects exposed via `addJavascriptInterface` to untrusted content. | HIGH | **N/A for MaiNeu** (no WebView — verify with grep) |
| P-1.5 | Exported Android components restricted to internal use. Only entry-point Activity should be `exported="true"`. | HIGH | `AndroidManifest.xml` all `<activity>`, `<service>`, `<receiver>`, `<provider>` |
| P-1.7 | URL scheme handlers perform strict input validation. Custom scheme (`maineu://`) validates path and parameters. | HIGH | `LaunchActivity.kt` intent data handling |

**Remediation:** Audit all exported components. Validate deep link parameters before acting on them. If WebView is ever added, apply strict security configuration.

---

## MASVS-CODE — Code Quality & Resilience

**CWE:** CWE-489, CWE-798, CWE-1104

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| Q-1.1 | Production binary compiled with security flags: PIE/ASLR enabled, stack canaries. Verify minification and R8. | HIGH | `app/build.gradle.kts` release build type config |
| Q-1.2 | No hardcoded secrets, API keys, or credentials in binary/strings/bundled assets. Run secret scanning against APK. | CRITICAL | Grep for API key patterns, check `res/values/strings.xml`, `BuildConfig` fields |
| Q-1.3 | Third-party SDK licenses and known CVEs reviewed. SDKs with excessive permissions rejected. | HIGH | `libs.versions.toml`, `app/build.gradle.kts` dependencies |
| Q-1.4 | App built with latest stable SDK targeting current OS minimum. | MEDIUM | `app/build.gradle.kts` `compileSdk`, `targetSdk`, `minSdk` |

**Remediation:** Run `./gradlew dependencyCheckAnalyze` for CVE scanning. Verify R8 minification enabled in release. Scan APK with `apkanalyzer` for embedded secrets.

---

## MASVS-RESILIENCE — Anti-Tampering & Reverse Engineering (MAS-R)

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| R-1.1 | Root/jailbreak detection for high-sensitivity use cases (payment, subscription). | HIGH | Search for SafetyNet/Play Integrity API usage |
| R-1.2 | Debugger attachment detection in production builds. `android:debuggable="false"` in release. | HIGH | `app/build.gradle.kts` release `isDebuggable`, `AndroidManifest.xml` |
| R-1.3 | Integrity verification to detect binary tampering or repackaging. | HIGH | Play Integrity API or equivalent |
| R-1.4 | ProGuard/R8 obfuscation applied to reduce static analysis effectiveness. | MEDIUM | `app/proguard-rules.pro`, `app/build.gradle.kts` `isMinifyEnabled` |

**Remediation:** Enable Play Integrity API for subscription-related flows. Ensure `isDebuggable = false` and `isMinifyEnabled = true` in release build type. Review ProGuard rules for adequate obfuscation.

---

## Android-Specific Additional Checks

| # | Check Item | Severity | MaiNeu Files to Inspect |
|---|-----------|----------|------------------------|
| AX-1 | `EncryptedPrefsFactory` fallback to unencrypted prefs — verify this only happens in test (Robolectric), never in release. | CRITICAL | `core/data/.../storage/EncryptedPrefsFactory.kt` |
| AX-2 | `CancellationException` not caught by generic `catch (e: Exception)` blocks in security-critical paths (auth, token refresh). | HIGH | `core/network/.../AuthManager.kt`, `executeWithAuth` |
| AX-3 | Device ID generation and storage — verify uniqueness and non-guessability. | MEDIUM | Device ID generation code |
| AX-4 | Camera permission granted only when needed, revoked indication shown. | LOW | Permission launchers in camera flow |
| AX-5 | FileProvider paths scoped to minimum necessary directories. | MEDIUM | `app/src/main/res/xml/file_paths.xml` |
