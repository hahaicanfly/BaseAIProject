---
name: security-audit
description: 完整安全審查，涵蓋認證、密鑰洩漏、依賴漏洞與 OWASP 標準檢查；當使用者要做安全稽核、弱點掃描或提及「安全審查」「security audit」時觸發。
---

# Skill: security-audit

> **用途**：基於 OWASP 2025 標準的系統性資安審計，涵蓋 auth / secret / 依賴漏洞 4 個 domain（Web/API、Mobile Android、Cloud Infra、API 補充），可依專案技術棧裁剪範圍。
> **觸發**：`/security-audit [scope]`
> **Agent**：security-reviewer（opus，見 `.claude/agents/security-reviewer.md`）

## Usage

```
/security-audit [scope]
```

| Scope | Description | Reference Files Loaded |
|-------|-------------|----------------------|
| `full` | 完整 4-domain 審計 | 全部 4 個 reference 檔 |
| `mobile` | Android MASVS 檢查（Android 專案適用） | `references/domain2-mobile-android.md` |
| `api` | 後端 API 安全 | `references/domain1-web-api.md` + `references/domain4-api-supplement.md` |
| `cloud` | 雲端基礎設施 | `references/domain3-cloud-infra.md` |
| `quick` | 快速 secrets/config/deps 掃描 | 無（inline checklist） |

Default scope：`full`

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

### Phase 0 — Pre-flight（永遠先執行）

不論 scope 為何，先執行以下檢查：

**0.1 — Secrets Scan**

對整個代碼庫掃描以下 pattern（排除 build 產出目錄、`node_modules/`、`.gradle/` 等）：
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

檔案類型依專案技術棧調整，例如 `*.ts`, `*.js`, `*.py`, `*.go`；Android 專案適用：另掃 `*.kt`, `*.java`, `*.xml`, `*.gradle.kts`。

**0.2 — Configuration Validation**
```
[ ] .gitignore 涵蓋：.env*、*secret*、*credential*、*.pem、*.key、*.p12
[ ] Android 專案適用：.gitignore 另涵蓋 local.properties、*.keystore、*.jks、google-services.json
[ ] 機敏設定檔（local.properties / .env.production 等）未被 commit 到 git
[ ] repo 中沒有 keystore / 私鑰檔案
[ ] 建置設定中的 secrets 來自環境變數或 CI secret store，非硬編碼
```

**0.3 — Dependency Audit**

依專案技術棧擇一執行（詳見 CLAUDE.md Quick Commands）：
```bash
npm audit            # Node.js
pip-audit             # Python
cargo audit           # Rust
```
Android 專案適用：透過 Gradle 執行相依性檢查任務（如 OWASP Dependency-Check plugin）與列出完整相依套件清單供人工複核。

若 scope = `quick`，到此為止並輸出報告。

---

### Phase 1 — Domain Execution

依 scope 依序執行對應 domain。每個 domain 先讀對應 reference 檔，再逐項評估。

| Order | Domain | Reference File | Scopes |
|-------|--------|---------------|--------|
| 1 | Web & API Security (A01-A10) | `references/domain1-web-api.md` | `full`, `api` |
| 2 | Mobile Android (MASVS)（Android 專案適用） | `references/domain2-mobile-android.md` | `full`, `mobile` |
| 3 | Cloud Infrastructure (C01-C06) | `references/domain3-cloud-infra.md` | `full`, `cloud` |
| 4 | API Supplement (API-1~10) | `references/domain4-api-supplement.md` | `full`, `api` |

> `references/domain2-mobile-android.md` 與 `references/domain3-cloud-infra.md` 內含具體範例（Ktor / Cloudflare Workers 等）；若專案技術棧不同，把該內容當作檢查項的參考範例，逐項對照到專案實際的等價機制（例如換成專案自己的 HTTP client、雲端平台）。

**Per-Item Assessment Protocol：**

對 reference 檔中的每個 check item：

1. **Read** 相關的專案檔案以取得證據
2. **Assess** 對照 check criteria
3. **Assign status:** `PASS` | `FAIL` | `PARTIAL` | `N/A`
4. **Record** 依下方輸出格式記錄
5. **CRITICAL findings** — 立即標記，不等完整報告產出後才提出

---

### Phase 2 — Scoring & Report

所有 domain 評估完成後，產出評分摘要與優先修復清單。

---

## 專案安全基線（Project Security Baseline）

正式審計前，先盤點專案既有的安全措施，聚焦「已實作什麼」與「已知落差」，把審計精力放在差異與新增程式碼上。基線資料的來源：`agent_docs/TECHNICAL-REFERENCE.md`（填實後）或專案自有安全文件；若尚未整理，先用下表當作盤點範本自行填寫，不要臆造內容。

| Area | Status | Key Files |
|------|--------|-----------|
| Token / secret 加密儲存 | [依專案填入] | [依專案填入] |
| 日誌脫敏（避免 token/PII 進 log） | [依專案填入] | [依專案填入] |
| 傳輸層安全（TLS 設定 / cert pinning） | [依專案填入] | [依專案填入] |
| Android 專案適用：備份與元件匯出限制（`allowBackup`、`exported`） | [依專案填入] | `AndroidManifest.xml` |
| 建置產出強化（obfuscation / minification） | [依專案填入] | [依專案填入] |

**已知落差（Known Gaps）**：把尚未修復或刻意延後的風險項列在這裡（例如：cert pinning 尚未啟用、資料庫未加密、缺少 root/jailbreak 偵測），做為優先審計標的，避免重複發現已知問題卻沒有排入修復排程。

---

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

---

## Escalation Rules

| Condition | Action |
|-----------|--------|
| 出現任何單一 CRITICAL finding | **立即升級** — 在繼續審計前先告知使用者 |
| 同一 domain 內出現 3+ HIGH findings | 該 domain 標記為 **HIGH RISK** |
| 發現主動遭利用的證據 | **停止評估** — 升級處理 |
| 代碼中發現 secret / credential | **立即警示** — 建議輪替金鑰 |

---

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

---

## Re-assessment Triggers

以下情況需重新執行本審計：
- 任何 CRITICAL finding 已修復（需驗證修復是否確實生效）
- 發生重大架構變更
- 部署新的主要版本
- 確認發生資安事件
- 新增第三方 SDK
- Auth 流程或金流相關流程被修改

---

## Quick Reference — Scan Targets

以下為常見掃描標的分類，具體檔案路徑依專案結構調整（可對照 `agent_docs/TECHNICAL-REFERENCE.md`）：

### Android 用戶端（Android 專案適用）
```
AndroidManifest.xml                       — 權限、exported components、backup 設定
res/xml/network_security_config.xml       — TLS、cert pinning
res/xml/file_paths.xml (若使用 FileProvider) — FileProvider 範圍
build.gradle.kts                          — 相依套件、build config、minification
proguard-rules.pro                        — obfuscation 規則
[專案自訂] token 儲存實作                   — token 加密與生命週期管理
[專案自訂] HTTP client 設定                 — TLS 設定、憑證驗證
[專案自訂] auth 流程管理                    — token 生命週期、登入/登出/撤銷
[專案自訂] API client 實作                  — API 呼叫、header 注入
[專案自訂] 日誌工具                         — log 脫敏
[專案自訂] 加密儲存設定                     — encryption at rest 設定
[專案自訂] 本地資料庫設定                    — DB 加密設定
```

### 後端服務（如可存取）
```
環境 / secrets 設定檔（.env、wrangler 類設定、IaC 變數檔）— 綁定、secrets 參照
API handler / middleware 原始碼             — 存取控制、輸入驗證
API 規格文件（OpenAPI/Swagger 等）           — API 契約與實際路由比對
管理後台（若有）                            — 是否有獨立於一般使用者的存取控制
.gitignore                                — 機敏檔案排除規則
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

## 驗證項目

- **產出形式**：OWASP-style 安全報告，覆蓋 4 domains（Web/API、Mobile MASVS、Cloud Infra、API Top 10）。
- **必查 invariants**：`docs/architecture/invariants.md` 中 `INV-SEC-001` ~ `INV-SEC-003`（依 invariants.md 現行清單；無對應 INV 時自行列出 auth/secret 風險項）；secret 掃描 `grep -rE 'API_KEY|TOKEN|PASSWORD'` 無命中。
- **發現項處置**：Critical/High 發現升級為新 ExecPlan（`docs/plans/active/`，格式見 `docs/plans/PLANS.md`）或寫入既有 ExecPlan 的 Open Questions 區塊；Medium 文件化即可；Low 進 backlog。
- **嚴重度**：Critical / High → 必須阻止 merge；Medium → ExecPlan 文件化；Low → backlog。
- **交接 marker**：通過時 `[HANDOFF: human-pr-review]`；發現 Critical/High 則 `[HUMAN_ATTENTION_REQUIRED: <reason>]`。

## 參考

- `.claude/agents/security-reviewer.md`
- `docs/architecture/invariants.md` INV-SEC-*
- `references/domain1-web-api.md`、`references/domain2-mobile-android.md`、`references/domain3-cloud-infra.md`、`references/domain4-api-supplement.md`
