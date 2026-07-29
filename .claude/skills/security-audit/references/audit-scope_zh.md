# security-audit — 基線、掃描目標與標準對照

> `.claude/skills/security-audit/SKILL_zh.md` 的參考檔。稽核前要盤點什麼、要看哪些地方、各 domain 對應哪個標準、什麼時候要重跑。

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

## Re-assessment Triggers

以下情況需重新執行本審計：
- 任何 CRITICAL finding 已修復（需驗證修復是否確實生效）
- 發生重大架構變更
- 部署新的主要版本
- 確認發生資安事件
- 新增第三方 SDK
- Auth 流程或金流相關流程被修改

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
