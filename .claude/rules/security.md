---
name: security
description: Mandatory security-related rules
always: true
---

# Security Rules

> Plain-language version for human readers: `docs/PLAIN/security-plain.md`

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
- Use allowlists rather than denylists

### Error Handling
- Don't expose internal details in error messages
- Log errors but not sensitive data
- Provide generic user-facing error messages

### Dependency Management
- Update dependencies regularly
- Check for known vulnerabilities
- Review the security posture of new dependencies
