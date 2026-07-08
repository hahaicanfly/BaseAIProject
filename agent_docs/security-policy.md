# Security Policy

> Standing hard rules live in `.claude/rules/security.md` and `docs/architecture/invariants.md` INV-SEC-*; this file only holds extended notes and examples.
> **Update policy**: when a new class of security issue is discovered, update the INV-SEC-* section of `docs/architecture/invariants.md` in sync.

---

## Key Management Strategy (Extended Examples)

### Development Environment
```bash
# .env (not committed, add to .gitignore)
API_KEY=your_key_here
DB_PASSWORD=your_password_here
```

### Template File
```bash
# .env.template (committed)
API_KEY=your_api_key_here
DB_PASSWORD=your_password_here
```

### CI/CD Environment
- Use platform secrets (GitHub Secrets, GitLab CI Variables, etc.)
- Inject via environment variables
- Never store in plaintext in workflow/pipeline config files

---

## Code Security Extensions

### API Security
- Use HTTPS for all outbound communication
- Implement request timeouts (30s recommended)
- Error responses must not leak internal details (stack traces, DB schema, etc.)
- Implement rate limiting

### Dependency Management Examples
Basic principles are in `.claude/rules/security.md`; tooling practice:
- Use Dependabot / Renovate for automated update alerts
- Commit the lock file to version control to pin dependency versions

---

## Agent Behavior Security Rules

### Remote Execution Protection

`pre-tool-use-guard.py` blocks the following patterns:
```
curl ... | sh
wget ... | bash
curl ... | python
```

### Git Operation Protection

- No direct commits to `main` / `master`
- No `git push --force` to shared branches
- No `git reset --hard` against remote

### Filesystem Protection

- No `rm -rf /`
- No reading of sensitive files such as `.env`, `*.pem`, `*.keystore`

---

## Security Code Review Checklist

When performing a code review, the `security-reviewer` agent must confirm:

- [ ] No hardcoded keys, passwords, or tokens
- [ ] No sensitive information in log output
- [ ] Inputs are properly validated and sanitized
- [ ] Error handling does not leak internal details
- [ ] New dependencies have been vetted for security and license
- [ ] HTTPS is used for all outbound communication
- [ ] No remote-execution vulnerabilities (curl|sh, etc.)

---

## When a Security Issue Is Found (Extended Steps)

Basic process is in `.claude/rules/security.md`; additional requirements:
1. If a secret has already leaked, recommend rotating it immediately
2. Log it under the Security / Auth category in `docs/learnings/ERRORS.md`
3. Notify the user with `[HUMAN_ATTENTION_REQUIRED: security issue found]`
