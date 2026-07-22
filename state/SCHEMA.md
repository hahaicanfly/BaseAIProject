# state/ — Harness Runtime State Schema

> **Role**: this directory holds harness runtime state (feature progress / session handoff / observability logs).
> **Version-control policy**: everything in `state/*` is gitignored, but this `SCHEMA.md` is checked in so contributors know the format.
> **The physical directory is auto-created on the first hook trigger** — no manual init needed.

---

## 1. `state/feature-list.json` — Single source of truth for active tasks

**Nature**: JSON readable/writable by models. JSON is preferred over Markdown because it resists model-induced corruption better (conclusion from OpenAI Codex's million-line experiment).
**Purpose**: track in-flight task status across sessions. **Division of labor with `docs/plans/PLANS.md`**: PLANS.md is the ExecPlan spec (long-term); feature-list.json is active harness state (real-time).

### Schema v1.0

```json
{
  "schema_version": "1.0",
  "last_updated_session": "<claude session id or ISO timestamp>",
  "features": [
    {
      "id": "F-NNN",                                      // F-XXX sequential number, matches the ExecPlan
      "title": "Short human-readable title",
      "status": "todo|in_progress|review|done|blocked",
      "owner_agent": "tech-lead|architect|dev|code-reviewer|...",
      "exec_plan": "docs/plans/active/F-NNN-slug.md",     // repoint to completed/ once done
      "branch": "feat/<slug>",
      "verification": {
        "build_ok": false,
        "lint_ok": false,
        "tests_passing": false
      },
      "created_at": "ISO 8601",
      "updated_at": "ISO 8601"
    }
  ]
}
```

### When to write

- ExecPlan created: one entry with `status: todo`
- Branch opened: `status: in_progress` + fill in `branch:`
- code-reviewer agent finishes with no Blockers: `status: review`
- PR merged: `status: done` + `exec_plan` path updated to `docs/plans/completed/`
- Hook detects build/lint/test results: update the corresponding `verification.*` fields

---

## 2. `state/session-handoffs/<ISO timestamp>.json` — PreCompact snapshot

**Nature**: append-only (each PreCompact writes a new file, never modified).
**Writer**: `.claude/hooks/pre-compact-snapshot.py`.
**Purpose**: before context nears its limit and gets compacted, freeze the current active context into a structured file, serving as a restore point for cold start / context reset.

### Schema v1.0

```json
{
  "schema_version": "1.0",
  "snapshot_at": "ISO 8601",
  "session_id": "<claude session id>",
  "active_execplan": "docs/plans/active/F-NNN-slug.md",   // null if none
  "active_branch": "feat/<slug>",
  "active_handoff_marker": "[HANDOFF: code-reviewer]",     // the last [HANDOFF:*] marker
  "open_questions": ["..."],                                // pulled from the ExecPlan
  "todo_items": ["..."],                                    // pulled from the TodoList
  "recent_invariant_violations": []                         // pulled from the stop-retro logger
}
```

---

## 3. `state/hook-events.jsonl` — Hook trigger audit log

**Nature**: JSON Lines (one record per line, append-only).
**Writer**: each hook writes its own line.
**Rotation policy**: 30-day rotate, run at most once per day (`rotate_state_if_due()` in `stop-retro-logger.py`, using the mtime of `state/.last-rotate` to judge whether 24 hours have passed; failures are silently skipped and never crash the hook).

### Schema (per line)

```json
{ "ts": "ISO 8601", "hook": "pre-tool-use-guard|post-edit-lint|pre-compact-snapshot|stop-retro-logger|post-bash-commit-ledger|session-activation-check", "tool": "<tool name if applicable>", "result": "pass|fail|warn|sentinel|enforced_block", "reason": "<short msg>" }
```

---

## 3a. `state/retro-hashes.jsonl` — Weekly-review tombstone ledger

**Nature**: JSON Lines, append-only.
**Writer**: `.claude/hooks/stop-retro-logger.py` — every time it successfully appends a finding/reminder to `ERRORS.md` `## Pending Review`, it also writes that hash into this file.
**Purpose**: dedup uses the union of "hashes currently in `ERRORS.md` ∪ hashes in this ledger" — after a human weekly review deletes an entry from `## Pending Review`, its hash remains in the ledger, so the next Stop event will not re-append the same finding (the same hash always maps to the same transcript content).
**Rotation policy**: 90-day rotate, sharing the same `.last-rotate` gate as `hook-events.jsonl`.
**If the file does not exist**: the hook creates it automatically (on first append).

### Schema (per line)

```json
{ "hash": "<10 hex chars>", "ts": "ISO 8601" }
```

---

## 3b. `state/.last-rotate` — Rotate throttle timestamp

**Nature**: a single timestamp string (not JSON), overwrite-only (rewritten whole after each rotate run).
**Writer**: `rotate_state_if_due()` in `.claude/hooks/stop-retro-logger.py`.
**Purpose**: use the file's mtime (or its content — both are the ISO time of the same write) to judge whether more than 24 hours have passed since the last rotate; if not, this Stop event skips rotation, avoiding a full jsonl scan at every session end.
**Content**: output of `now_iso()`, e.g. `2026-07-04T12:46:33+0000`.

---

## 4. `state/tool-calls.jsonl` — Tool usage audit log

**Nature**: JSON Lines, append-only.
**Writer**: `.claude/hooks/post-edit-lint.py` writes it as a side effect; other hooks on PostToolUse may also write.
**Purpose**: locate tool-routing errors, detect tool bloat; `session` makes rows joinable with `hook-events.jsonl` / `commits.jsonl` ("which session edited this file").

### Schema

```json
{ "ts": "ISO 8601", "tool": "Write|Edit|MultiEdit", "file": "<repo-relative path>", "matcher": "<hook matcher>", "session": "<claude session id>" }
```

> Historical note: an earlier version of this schema documented `duration_ms` / `exit_code` fields that no writer ever produced; the schema above now matches what `post-edit-lint.py` actually writes. Rows written before 2026-07-22 lack the `session` field — treat missing as unknown.

---

## 4a. `state/commits.jsonl` — Session↔commit join ledger

**Nature**: JSON Lines, append-only.
**Writer**: `.claude/hooks/post-bash-commit-ledger.py` (PostToolUse, matcher `Bash`).
**Purpose**: git history is the only durable cross-machine trail; this ledger links each commit hash to the session that produced it, making `head_hash` the join key across commits ↔ sessions ↔ tool-calls ↔ hook-events.
**Dedup / failure handling**: after a Bash command containing `git commit`, the hook records only if `git rev-parse HEAD` differs from the last recorded `head_hash` — denied/failed commit attempts leave HEAD unchanged and are skipped.

### Schema

```json
{ "ts": "ISO 8601", "session": "<claude session id>", "branch": "<branch name>", "head_hash": "<full sha>", "msg_first_line": "<commit subject, ≤120 chars>" }
```

---

## 4b. `state/delegations.jsonl` — Delegation ledger

**Nature**: JSON Lines, append-only.
**Writer**: `.claude/hooks/delegation-ledger.py` (PreToolUse, matcher `Task|Agent`; sentinel — always exit 0, a non-zero PreToolUse exit would block the delegation).
**Purpose**: records every subagent delegation with prompt-quality signals — whether the prompt carries model-dispatch.md §2's mandatory trio (goal/acceptance-criteria/report-format) plus scope declaration and marker requirement. Weak delegations become measurable instead of anecdotal.

### Schema

```json
{ "ts": "ISO 8601", "session": "<claude session id>", "subagent_type": "<agent type>", "model": "<override or empty>", "desc": "<description ≤120>", "prompt_sha1_10": "<10 hex>", "prompt_chars": 0, "has_goal": true, "has_ac": true, "has_report_format": true, "has_scope": true, "has_marker_req": true }
```

---

## 4c. `state/verifications.jsonl` — Fresh-context verdict ledger

**Nature**: JSON Lines, append-only.
**Writer**: `.claude/hooks/stop-retro-logger.py` on `SubagentStop` — harvests the `VERDICT: PASS|FAIL <evidence-path>` line that delegation-templates.md §6 requires every fresh-context acceptance agent to emit (full report persisted under `docs/reviews/`).
**Purpose**: acceptance outcomes survive the verifier's ephemeral context; `verdict=FAIL` additionally lands in `ERRORS.md` Pending Review as an `ACCEPTANCE_FAIL` finding.

### Schema

```json
{ "ts": "ISO 8601", "session": "<claude session id>", "agent": "<subagent id>", "verdict": "PASS|FAIL", "evidence_path": "docs/reviews/<file>.md" }
```

---

## 4d. `state/acceptance/<plan-stem>.jsonl` — ExecPlan acceptance-run evidence

**Nature**: JSON Lines, append-only (one line per executed command per run).
**Writer**: `scripts/acceptance-run.py` (executes the ExecPlan §5 ```acceptance block; see docs/plans/PLANS.md).
**Purpose**: the §5 verification strategy stops being prose — every run leaves per-command evidence (exit code + output tail) reviewers and future sessions can re-check.

### Schema

```json
{ "ts": "ISO 8601", "plan": "docs/plans/active/F-NNN-<slug>.md", "label": "build|lint|test|negative|...", "cmd": "<command>", "expect_fail": false, "exit_code": 0, "pass": true, "skipped": false, "output_tail": "<last ≤10 lines>" }
```

---

## 5. `state/token-usage.jsonl` — Token consumption tracking

**Nature**: JSON Lines, append-only.
**Writer**: `.claude/hooks/pre-compact-snapshot.py` (captured at compact time).
**Purpose**: detect context anxiety / context flooding, identify cache-miss patterns.

### Schema

```json
{ "ts": "ISO 8601", "session_id": "...", "input_tokens": 0, "output_tokens": 0, "cache_creation": 0, "cache_read": 0, "trigger": "pre-compact|stop" }
```

---

## 6. Privacy & shareability

- All jsonl and json files inside `state/` are **not version-controlled** (to avoid leaking sensitive strings like tokens / branch names / commit hashes).
- Even though `state/feature-list.json` is gitignored, still **avoid** writing secrets into it (API keys, passwords, tokens).
- Cross-session progress sync relies only on two coordinated sources: `docs/plans/active/*.md` (version-controlled) + `state/feature-list.json` (local).

---

## 7. Evolution

- After ~50 tasks, if jsonl size grows rapidly, introduce rotation (archive monthly into `state/archive/`).
- If upgrading to a proper observability platform (Datadog / Honeycomb), rewrite stop-retro-logger to also ship to remote.
- Schema upgrades are explicitly marked via `schema_version`; on backward-incompatible changes, stop-retro-logger migrates automatically.
