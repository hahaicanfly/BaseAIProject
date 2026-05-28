# 安全政策

> **適用範圍**：所有 agent 在處理機敏資訊、提交代碼、執行 shell 命令時必須遵守本政策。
> **更新策略**：當發現新類型的安全問題時，同步更新 `docs/architecture/invariants.md` 的 INV-SEC-* 區塊。

---

## 機敏資訊保護

### 絕對禁止

1. **硬編碼金鑰 / 密碼 / Token**

   ```
   # ❌ 禁止
   API_KEY = "sk-ant-api03-xxxxx"
   DB_PASSWORD = "my_secret_password"

   # ✅ 正確：從環境變數或設定檔讀取
   API_KEY = os.environ["API_KEY"]
   DB_PASSWORD = config.get("database", "password")
   ```

2. **提交敏感檔案**（`pre-tool-use-guard.py` 強制阻擋）
   - `.env`
   - `*.pem`, `*.key`, `*.keystore`, `*.p12`
   - `*secret*`, `*credential*`, `*password*`
   - `local.properties`（如果包含 API key）
   - `google-services.json`（若包含金鑰）

3. **日誌洩漏**

   ```
   # ❌ 禁止
   logger.debug(f"Request with key: {api_key}")

   # ✅ 正確
   logger.debug("Request sent")
   ```

### 金鑰管理策略

#### 開發環境
```bash
# .env（不提交，加入 .gitignore）
API_KEY=your_key_here
DB_PASSWORD=your_password_here
```

#### 範本檔案
```bash
# .env.template（提交）
API_KEY=your_api_key_here
DB_PASSWORD=your_password_here
```

#### CI/CD 環境
- 使用平台 Secrets（GitHub Secrets、GitLab CI Variables 等）
- 使用環境變數注入
- 不在 workflow / pipeline 配置檔中明文存放

---

## 代碼安全

### 輸入驗證
- 驗證所有外部輸入（使用者輸入、API 回應、檔案上傳）
- 限制上傳檔案大小（防止 DoS）
- JSON 解析必須有錯誤處理

### API 安全
- 所有對外通訊使用 HTTPS
- 實作 request timeout（建議 30s）
- 錯誤回應不洩漏內部資訊（stack trace、DB schema 等）
- 實作 rate limiting

### 依賴管理
- 定期更新依賴（建議使用 Dependabot / Renovate）
- 新增依賴前審查授權與安全性
- 鎖定依賴版本（lock file 入版控）

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

## 發現安全問題時

1. 立即通知用戶（`[HUMAN_ATTENTION_REQUIRED: security issue found]`）
2. 不執行可能造成洩漏的操作
3. 建議具體修復方案
4. 若已洩漏，建議立即輪換金鑰
5. 記錄到 `docs/learnings/ERRORS.md` 的 Security / Auth 分類
