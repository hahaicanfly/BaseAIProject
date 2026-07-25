---
name: security
description: Mandatory security-related rules
always: true
---

# Security Rules

*白話:密碼、金鑰這類機密資訊絕對不能寫死在程式碼或紀錄裡,也不能被提交進版本控制。*

## Absolutely Forbidden

### 1. Hardcoding Sensitive Information
```
// ❌ Never do this
apiKey = "sk-xxxxx"
password = "my_password"
token = "ghp_xxxxx"

// ✅ Correct approach
apiKey = process.env.API_KEY
apiKey = BuildConfig.API_KEY
apiKey = os.getenv("API_KEY")
```

### 2. Log Leakage
```
// ❌ Forbidden
log("Request with key: " + apiKey)
log("Password: " + password)
print(f"Token: {token}")

// ✅ Correct
log("Request sent")
log("Authentication failed")
```

### 3. Committing Sensitive Files
The following files must never be committed to git:
- `.env`, `.env.*`
- `local.properties`, `local-prod.properties`
- `*.keystore`, `*.jks`
- `*.pem`, `*.key`, `*.p12`
- `*secret*`, `*credential*`
- `serviceAccountKey.json`
- `google-services.json` (if it contains sensitive info)

## When an Issue Is Found

If sensitive information is found in code:
1. **Stop immediately** — halt the current operation
2. **Warn the user** of the potential risk
3. **Suggest a fix**
4. **Do not** perform any git operation that could cause leakage

## When to Proactively Check Security

Proactively check security at the following times:
- Any code involving API calls
- Modifications to configuration files
- Adding new dependencies
- Before a git commit
- Code that handles user input

## Security Best Practices

### Input Validation
- Validate all external input
- Set reasonable length/size limits
- Use allowlists(白話:只放行清單內許可的東西,其餘一律擋下,預設最安全) rather than denylists(白話:只擋清單內禁止的東西,清單外一律放行,容易漏掉沒想到的情況)

### Error Handling
- Don't expose internal details in error messages
- Log errors but not sensitive data
- Provide generic user-facing error messages

### Dependency Management
- Update dependencies regularly
- Check for known vulnerabilities
- Review the security posture of new dependencies
