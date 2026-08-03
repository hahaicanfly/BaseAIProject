# {{PROJECT_NAME}} — Mechanically Verifiable Invariants

> **Role**: This file lists hard rules that can be **mechanically verified** (unlike `docs/learnings/ERRORS.md`, which is a knowledge base — this file is a lint/test/grep mapping table).
> **Audience**: `.claude/hooks/post-edit-lint.py` / `code-reviewer` agent / human reviewers.
> **Inclusion principle**: only rules that can be written as a lint rule, grep pattern, test assertion, or build check belong here; lessons that can't be mechanically verified stay in ERRORS.md.

---

## Rule Format

```
INV-<NS>-<NNN>  <one-sentence rule>
  CHECK    <executable grep/lint/test command>
  HOOK     <which hook should intercept it, or leave as manual review>
  SOURCE   <date of the corresponding lesson in ERRORS.md>
```

Suggested namespaces (NS):
- `COR` — Coroutines / Async / Concurrency
- `SEC` — Security / Auth / Secrets
- `API` — API / Serialization / Data Models
- `TEST` — Testing / Mocks / Fakes
- `GIT` — Git / Branch / PR
- `BLD` — Build / Dependencies
- `ARC` — Architecture / Refactoring
- `UI` — UI / Components
- `LOG` — Logging / Observability

---

## INV-GIT-* — Git / Branch / PR

### INV-GIT-001 — Must run `git branch --show-current` before commit

```
RULE     Confirm the current branch before every commit / subagent launch / PR merge
CHECK    git symbolic-ref HEAD | grep -E 'refs/heads/(master|main)$'
HOOK     pre-tool-use-guard.py (intercepts git commit on master)
SOURCE   2026-07-04 harness institutionalization session (ADR-0001)
```

### INV-GIT-002 — Never `git commit` directly to master / main

```
RULE     Direct commits to master/main are forbidden
CHECK    git symbolic-ref HEAD | grep -E 'refs/heads/(master|main)$'
HOOK     pre-tool-use-guard.py (enforce — hard guard)
SOURCE   2026-07-04 harness institutionalization session (ADR-0001)
```

### INV-GIT-003 — Never `git push --force` to master / main

```
RULE     Force push to shared branches is forbidden
CHECK    grep -E 'git push.*--force.*\b(master|main)\b'
HOOK     pre-tool-use-guard.py (enforce)
SOURCE   ADR-0001 D5
```

### INV-GIT-004 — Never `git reset --hard origin/master`

```
RULE     Use git rebase origin/master instead when a fast-forward fails
CHECK    grep -E 'git reset --hard origin/(master|main)'
HOOK     pre-tool-use-guard.py (enforce)
SOURCE   2026-07-04 harness institutionalization session (ADR-0001)
```

### INV-GIT-005 — New feature branches must be cut from master

```
RULE     Pull the latest master before git checkout -b feat/xxx
CHECK    python3 scripts/verify-branch-base.py   (PASS/FAIL/WARN; run right after cutting, and before opening a PR)
HOOK     pre-tool-use-guard.py (advisory additionalContext on checkout -b / switch -c) + code-reviewer agent
SOURCE   2026-07-04 harness institutionalization session (ADR-0001); mechanized 2026-08-03 (F-004)
```

---

## INV-SEC-* — Security / Secrets

### INV-SEC-001 — Never hardcode API keys / tokens / passwords

```
RULE     No source file may contain a plaintext API key or token assignment
CHECK    grep -rEn 'api[_-]?key\s*=\s*["\'][A-Za-z0-9_\-]{20,}["\']' src/
HOOK     post-edit-lint.py (sentinel)
SOURCE   General security best practice
```

### INV-SEC-002 — Tokens / secrets must not appear in log / print statements

```
RULE     logger.debug/info/warn/error and print/console.log must not contain sensitive words like token, key, password, secret
CHECK    grep -rEn '(print|console\.log|logger\.\w+)\s*\(.*\b(token|api_key|secret|password)\b' src/
HOOK     post-edit-lint.py (sentinel)
SOURCE   General security best practice
```

### INV-SEC-003 — Sensitive files must never enter git staging

```
RULE     .env, *.pem, *.key, *.keystore, *secret* must never be git added
CHECK    git diff --cached --name-only | grep -E '\.(env|pem|key|keystore|p12)$|secret|credential'
HOOK     pre-tool-use-guard.py (enforce: intercepts git add of sensitive files via literal command matching; already-staged content is out of scope for this hook — relies on code-reviewer and human review)
SOURCE   General security best practice
```

> **When adopting this template**: replace `src/` with your actual source directory, and copy the INV-SEC-001 / INV-SEC-002 patterns into `post-edit-lint.py`'s `QUICK_CHECKS`.

---

## INV-TEST-* — Testing

> Fill in project test invariants, e.g.:

```
INV-TEST-001  Every new interface method must have all fakes/mocks updated
  CHECK    grep -rn ': InterfaceName' --include='*.ts' | grep -i 'fake\|mock'
  HOOK     code-reviewer agent (manual, added to ExecPlan checklist)
  SOURCE   (example entry, no source lesson)
```

---

## INV-API-* — API / Data Models

> Fill in project API invariants.

---

## INV-ARC-* — Architecture

### INV-ARC-001 — The standing context layer must stay inside its per-tier budget

```
RULE     CLAUDE.md + .claude/rules/security.md + the injected tier pack must not exceed
         the line and character ceilings of the active mode in .claude/tiers/budget.json.
         Counted in Unicode characters, not bytes. Anything added to the standing layer
         must either fit the budget or displace something already there.
CHECK    python3 scripts/context-budget.py --tier strong   (likewise mid, light)
HOOK     scripts/context-budget.py (enforce: non-zero exit over budget); wired into every
         ExecPlan acceptance block via scripts/acceptance-run.py
SOURCE   docs/harness/LETTER-TO-FUTURE-SESSIONS.md §I.3; mechanized by F-003 and promoted
         2026-07-29 with user consent
```

> The ceiling is deliberately a **configuration**, not a constant: switch `active_mode` in `budget.json` (`strict` / `balanced` / `generous`) or override the numbers directly. Changing the mode is a normal edit; deleting the check is not.

### INV-ARC-002 — An ExecPlan's completion claim must agree with its own checkboxes

```
RULE     A plan whose Status is done must have zero unticked steps in §4 and must
         live under docs/plans/completed/; a plan under completed/ must say done.
         A plan that logs progress in §6 while §4 records none of it is flagged
         (WARN) as the two accounts having stopped being reconciled.
CHECK    python3 scripts/execplan-lint.py <plan.md>        (checks E7 / W2)
HOOK     scripts/execplan-lint.py (enforce: non-zero exit on E7); already wired
         into harness-gates.yml and every ExecPlan acceptance block
SOURCE   2026-07-29 PR #14 retro — F-003 recorded twelve finished phases in §6 while
         every step in §4 sat unticked, and one step genuinely had not been done;
         it survived three sessions because nothing compared the plan's two
         accounts of itself. Promoted 2026-07-29 with user consent
```

> Why an ERROR for `done` and only a WARN for the divergence: a plan may legitimately
> log a decision before finishing step 1, so early divergence is normal. Claiming
> completion while steps sit unticked is not — that is a plan asserting two
> incompatible things about itself.

> **When adopting this template**: both INV-ARC entries above are harness-level and apply as-is to every fork. Fill the sections below with your own project's architecture rules.

---

## INV-BLD-* — Build

> Fill in project build invariants.

---

## Lessons Not Suited to Mechanical Verification (stay in ERRORS.md)

The following lessons are not included here because their patterns are too contextual / require human judgment; they remain in ERRORS.md only.

---

## Where This File Is Referenced

- `.claude/hooks/post-edit-lint.py` — loads INV-* rules tagged `post-edit-lint.py`
- `.claude/hooks/pre-tool-use-guard.py` — loads INV-* rules tagged `pre-tool-use-guard.py`
- `.claude/agents/code-reviewer.md` — review checklist references this file
- `docs/learnings/ERRORS.md` — each lesson back-references its INV-id
