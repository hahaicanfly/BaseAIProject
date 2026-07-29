---
name: security-audit
description: Full security review covering authentication, key leakage, dependency vulnerabilities, and OWASP standard checks; triggers when the user wants a security audit, vulnerability scan, or mentions "安全審查", "security audit".
---

# Skill: security-audit

> **Purpose**: A systematic security audit based on the OWASP 2025 standards, covering auth / secrets / dependency-vulnerability across 4 domains (Web/API, Mobile Android, Cloud Infra, API Supplement); scope can be tailored to the project's tech stack.
> **Trigger**: `/security-audit [scope]`
> **Agent**: security-reviewer (opus, see `.claude/agents/security-reviewer.md`)

## Usage

```
/security-audit [scope]
```

| Scope | Description | Domain Files Loaded |
|-------|-------------|----------------------|
| `full` | Full 4-domain audit | All 4 domain files |
| `mobile` | Android MASVS checks (for Android projects) | `references/domain2-mobile-android.md` |
| `api` | Backend API security | `references/domain1-web-api.md` + `references/domain4-api-supplement.md` |
| `cloud` | Cloud infrastructure | `references/domain3-cloud-infra.md` |
| `quick` | Quick secrets/config/deps scan | none — Phase 0 only |

Default scope: `full`

## Execution Workflow

### Phase 0 — Pre-flight

Always first, whatever the scope: secrets scan, `.gitignore` and config validation, dependency audit. Patterns and checklists: `references/preflight.md`. Scope `quick` stops here and reports.

### Phase 1 — Domain Execution

Run the domains the scope selects, in this order. Read each domain file first, then assess item by item.

| Order | Domain | Domain File | Scopes |
|-------|--------|---------------|--------|
| 1 | Web & API Security (A01-A10) | `references/domain1-web-api.md` | `full`, `api` |
| 2 | Mobile Android (MASVS) (for Android projects) | `references/domain2-mobile-android.md` | `full`, `mobile` |
| 3 | Cloud Infrastructure (C01-C06) | `references/domain3-cloud-infra.md` | `full`, `cloud` |
| 4 | API Supplement (API-1~10) | `references/domain4-api-supplement.md` | `full`, `api` |

> `references/domain2-mobile-android.md` and `references/domain3-cloud-infra.md` contain concrete examples (Ktor / Cloudflare Workers, etc.); if the project's tech stack differs, treat that content as a reference example for the check item and map it to the project's actual equivalent mechanism (e.g. the project's own HTTP client, cloud platform).

**Per-Item Assessment Protocol:**

For each check item in the domain file:

1. **Read** the relevant project files to gather evidence
2. **Assess** against the check criteria
3. **Assign status:** `PASS` | `FAIL` | `PARTIAL` | `N/A`
4. **Record** per the finding format in `references/reporting.md`
5. **CRITICAL findings** — tell the user immediately with `[HUMAN_ATTENTION_REQUIRED: <reason>]`; don't wait for the full report

### Phase 2 — Scoring & Report

Once all domains are assessed, produce a scoring summary and prioritized remediation list.

## Supporting References

| File | Read it when |
|------|--------------|
| `references/preflight.md` | Running Phase 0 — secret patterns, config checklist, dependency-audit commands |
| `references/reporting.md` | Writing anything up — the CRITICAL/HIGH/MEDIUM/LOW/INFO scale with CVSS ranges and SLAs, finding format, escalation rules, scoring-summary template |
| `references/audit-scope.md` | Planning the audit — security baseline inventory, scan-target lists, OWASP standard cross-reference, re-assessment triggers |

## Verification Items

- **Output form**: an OWASP-style security report covering 4 domains (Web/API, Mobile MASVS, Cloud Infra, API Top 10).
- **Required invariants check**: `INV-SEC-001` ~ `INV-SEC-003` in `docs/architecture/invariants.md` (per the current list in invariants.md; if no corresponding INV exists, list auth/secret risk items independently); secret scan `grep -rE 'API_KEY|TOKEN|PASSWORD'` returns no hits.
- **Finding disposition**: Critical/High findings are escalated into a new ExecPlan (`docs/plans/active/`, format per `docs/plans/PLANS.md`) or written into the Open Questions section of an existing ExecPlan; Medium is documented only; Low goes to backlog.
- **Severity**: Critical / High → must block merge; Medium → documented in an ExecPlan; Low → backlog.
- **Handoff marker**: on pass, `[HANDOFF: human-pr-review]`; if Critical/High findings exist, `[HUMAN_ATTENTION_REQUIRED: <reason>]`.

## References

- `.claude/agents/security-reviewer.md`
- `docs/architecture/invariants.md` INV-SEC-*
