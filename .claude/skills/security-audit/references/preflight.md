# security-audit — Phase 0 pre-flight

> Reference for `.claude/skills/security-audit/SKILL.md`. Runs before any domain work, whatever the scope. Scope `quick` stops at the end of this file.

### Phase 0 — Pre-flight (always run first)

Regardless of scope, run the following checks first:

**0.1 — Secrets Scan**

Scan the entire codebase for the following patterns (excluding build output directories, `node_modules/`, `.gradle/`, etc.):
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

File types depend on the project's tech stack, e.g. `*.ts`, `*.js`, `*.py`, `*.go`; for Android projects also scan `*.kt`, `*.java`, `*.xml`, `*.gradle.kts`.

**0.2 — Configuration Validation**
```
[ ] .gitignore covers: .env*, *secret*, *credential*, *.pem, *.key, *.p12
[ ] For Android projects: .gitignore also covers local.properties, *.keystore, *.jks, google-services.json
[ ] Sensitive config files (local.properties / .env.production, etc.) are not committed to git
[ ] No keystore / private key files in the repo
[ ] Secrets in build config come from environment variables or the CI secret store, not hardcoded
```

**0.3 — Dependency Audit**

Choose based on the project's tech stack (see CLAUDE.md Quick Commands for details):
```bash
npm audit            # Node.js
pip-audit             # Python
cargo audit           # Rust
```
For Android projects: run a dependency-check task via Gradle (e.g. the OWASP Dependency-Check plugin) and list the full dependency tree for manual review.

If scope = `quick`, stop here and output the report.
