---
name: security
description: 安全相關的強制規則
always: true
---

# Security Rules

## 絕對禁止

### 1. 硬編碼機敏資訊
```
// ❌ 永遠不要這樣做
apiKey = "sk-xxxxx"
password = "my_password"
token = "ghp_xxxxx"

// ✅ 正確做法
apiKey = process.env.API_KEY
apiKey = BuildConfig.API_KEY
apiKey = os.getenv("API_KEY")
```

### 2. 日誌洩漏
```
// ❌ 禁止
log("Request with key: " + apiKey)
log("Password: " + password)
print(f"Token: {token}")

// ✅ 正確
log("Request sent")
log("Authentication failed")
```

### 3. 提交敏感檔案
以下檔案絕對不能提交到 git：
- `.env`, `.env.*`
- `local.properties`, `local-prod.properties`
- `*.keystore`, `*.jks`
- `*.pem`, `*.key`, `*.p12`
- `*secret*`, `*credential*`
- `serviceAccountKey.json`
- `google-services.json` (如包含敏感資訊)

## 發現問題時

如果在代碼中發現機敏資訊：
1. **立即停止**當前操作
2. **警告用戶**潛在風險
3. **建議修復**方案
4. **不要**執行可能造成洩漏的 git 操作

## 審查時機

在以下時機主動檢查安全：
- 任何涉及 API 調用的代碼
- 配置檔案的修改
- 新增依賴
- git commit 前
- 處理用戶輸入的代碼

## 安全最佳實踐

### 輸入驗證
- 驗證所有外部輸入
- 設定合理的長度/大小限制
- 使用白名單而非黑名單

### 錯誤處理
- 不在錯誤訊息中暴露內部細節
- 記錄錯誤但不記錄敏感資料
- 提供通用的用戶錯誤訊息

### 依賴管理
- 定期更新依賴
- 檢查已知漏洞
- 審查新依賴的安全性
