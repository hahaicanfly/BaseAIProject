# 安全政策

> 常駐硬規則見 `.claude/rules/security.md` 與 `docs/architecture/invariants.md` INV-SEC-*；本檔只放延伸說明與範例。
> **更新策略**：當發現新類型的安全問題時，同步更新 `docs/architecture/invariants.md` 的 INV-SEC-* 區塊。

---

## 金鑰管理策略（延伸範例）

### 開發環境
```bash
# .env（不提交，加入 .gitignore）
API_KEY=your_key_here
DB_PASSWORD=your_password_here
```

### 範本檔案
```bash
# .env.template（提交）
API_KEY=your_api_key_here
DB_PASSWORD=your_password_here
```

### CI/CD 環境
- 使用平台 Secrets（GitHub Secrets、GitLab CI Variables 等）
- 使用環境變數注入
- 不在 workflow / pipeline 配置檔中明文存放

---

## 代碼安全延伸

### API 安全
- 所有對外通訊使用 HTTPS
- 實作 request timeout（建議 30s）
- 錯誤回應不洩漏內部資訊（stack trace、DB schema 等）
- 實作 rate limiting

### 依賴管理範例
基本原則見 `.claude/rules/security.md`；工具實務：
- 使用 Dependabot / Renovate 自動化更新提醒
- Lock file 入版控以鎖定依賴版本

---

## Agent 行為安全規則

### 遠端執行防護

`pre-tool-use-guard.py` 阻擋以下模式：
```
curl ... | sh
wget ... | bash
curl ... | python
```

### Git 操作防護

- 禁止直接 commit 到 `main` / `master`
- 禁止 `git push --force` 到共享分支
- 禁止 `git reset --hard` 到 remote

### 檔案系統防護

- 禁止 `rm -rf /`
- 禁止讀取 `.env`、`*.pem`、`*.keystore` 等敏感檔案

---

## 安全 Code Review 檢查清單

在執行 code review 時，`security-reviewer` agent 必須確認：

- [ ] 無硬編碼金鑰、密碼、token
- [ ] 無敏感資訊在日誌輸出中
- [ ] 輸入有適當驗證與清理
- [ ] 錯誤處理不洩漏內部資訊
- [ ] 新依賴已審查安全性與授權
- [ ] HTTPS 用於所有對外通訊
- [ ] 無遠端執行漏洞（curl|sh 等）

---

## 發現安全問題時（延伸步驟）

基本流程見 `.claude/rules/security.md`；額外要求：
1. 若已洩漏，建議立即輪換金鑰
2. 記錄到 `docs/learnings/ERRORS.md` 的 Security / Auth 分類
3. 以 `[HUMAN_ATTENTION_REQUIRED: security issue found]` 通知用戶
