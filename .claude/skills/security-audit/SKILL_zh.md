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

| Scope | Description | Domain Files Loaded |
|-------|-------------|----------------------|
| `full` | 完整 4-domain 審計 | 全部 4 個 domain 檔 |
| `mobile` | Android MASVS 檢查（Android 專案適用） | `references/domain2-mobile-android.md` |
| `api` | 後端 API 安全 | `references/domain1-web-api.md` + `references/domain4-api-supplement.md` |
| `cloud` | 雲端基礎設施 | `references/domain3-cloud-infra.md` |
| `quick` | 快速 secrets/config/deps 掃描 | 無 — 只跑 Phase 0 |

Default scope：`full`

## Execution Workflow

### Phase 0 — 前置檢查

無論 scope 為何都先跑：secrets 掃描、`.gitignore` 與設定檔驗證、依賴稽核。掃描樣式與檢查清單見 `references/preflight_zh.md`。scope 為 `quick` 時做完即出報告。

### Phase 1 — Domain Execution

依 scope 依序執行對應 domain。每個 domain 先讀對應檔案，再逐項評估。

| Order | Domain | Domain File | Scopes |
|-------|--------|---------------|--------|
| 1 | Web & API Security (A01-A10) | `references/domain1-web-api.md` | `full`, `api` |
| 2 | Mobile Android (MASVS)（Android 專案適用） | `references/domain2-mobile-android.md` | `full`, `mobile` |
| 3 | Cloud Infrastructure (C01-C06) | `references/domain3-cloud-infra.md` | `full`, `cloud` |
| 4 | API Supplement (API-1~10) | `references/domain4-api-supplement.md` | `full`, `api` |

> `references/domain2-mobile-android.md` 與 `references/domain3-cloud-infra.md` 內含具體範例（Ktor / Cloudflare Workers 等）；若專案技術棧不同，把該內容當作檢查項的參考範例，逐項對照到專案實際的等價機制（例如換成專案自己的 HTTP client、雲端平台）。

**Per-Item Assessment Protocol：**

對 domain 檔中的每個 check item：

1. **Read** 相關的專案檔案以取得證據
2. **Assess** 對照 check criteria
3. **Assign status:** `PASS` | `FAIL` | `PARTIAL` | `N/A`
4. **Record** 依 `references/reporting_zh.md` 的 finding 格式記錄
5. **CRITICAL findings** — 立即以 `[HUMAN_ATTENTION_REQUIRED: <reason>]` 告知使用者，不等完整報告產出後才提出

### Phase 2 — Scoring & Report

所有 domain 評估完成後，產出評分摘要與優先修復清單。

## 支援參考檔

| 檔案 | 什麼時候讀 |
|------|-----------|
| `references/preflight_zh.md` | 執行 Phase 0 — secret 樣式、設定檔檢查清單、依賴稽核指令 |
| `references/reporting_zh.md` | 要寫任何東西時 — CRITICAL/HIGH/MEDIUM/LOW/INFO 分級（含 CVSS 區間與回應 SLA）、finding 格式、升級規則、評分摘要範本 |
| `references/audit-scope_zh.md` | 規劃稽核範圍 — 安全基線盤點、掃描目標清單、OWASP 標準對照、重跑觸發條件 |

## 驗證項目

- **產出形式**：OWASP-style 安全報告，覆蓋 4 domains（Web/API、Mobile MASVS、Cloud Infra、API Top 10）。
- **必查 invariants**：`docs/architecture/invariants.md` 中 `INV-SEC-001` ~ `INV-SEC-003`（依 invariants.md 現行清單；無對應 INV 時自行列出 auth/secret 風險項）；secret 掃描 `grep -rE 'API_KEY|TOKEN|PASSWORD'` 無命中。
- **發現項處置**：Critical/High 發現升級為新 ExecPlan（`docs/plans/active/`，格式見 `docs/plans/PLANS.md`）或寫入既有 ExecPlan 的 Open Questions 區塊；Medium 文件化即可；Low 進 backlog。
- **嚴重度**：Critical / High → 必須阻止 merge；Medium → ExecPlan 文件化；Low → backlog。
- **交接 marker**：通過時 `[HANDOFF: human-pr-review]`；發現 Critical/High 則 `[HUMAN_ATTENTION_REQUIRED: <reason>]`。

## 參考

- `.claude/agents/security-reviewer.md`
- `docs/architecture/invariants.md` INV-SEC-*
