# security-audit — Phase 0 前置檢查

> `.claude/skills/security-audit/SKILL_zh.md` 的參考檔。無論 scope 為何都先跑這一段；scope 為 `quick` 時做完本檔即結束。

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
