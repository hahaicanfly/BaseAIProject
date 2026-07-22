# ExecPlan: F-001 — Harness Verifiability Batch (PR #2 follow-ups + O2–O15)

| Field | Value |
|------|-----|
| Status | in_progress |
| Owner Agent | dev (main conversation) |
| Branch | feat/harness-verifiability-batch |
| Created | 2026-07-22 |
| Last Updated | 2026-07-22 |
| Linked PR | — |

## 1. Goal

Close every remaining finding from the PR #2 multi-agent review (R4–R10; R1/R2/R3 already merged in PR #2) and implement all 14 vetted/proposed workflow-optimization items (O2–O15), so that AI outputs in this harness — code, decisions, strategy docs — are mechanically verifiable, traceable, and auditable, instead of relying on prose self-discipline.

Non-Goals / Out of Scope:
- No changes to product/application code (this repo is the harness template itself).
- No new always-on prose rules beyond what O-items specify — mechanical gates are preferred; rule-text growth is itself governed by O15's budget check.
- O-item ideas rejected during vetting (already-exists/conflicting) are not revisited here.
- No auto-merge of the final PR: human review decides (user authorized implementation, not merge).

## 2. Context

- TECHNICAL-REFERENCE: not activated (template placeholders) — skipped per CLAUDE.md Activation Status.
- Related ADR: ADR-0001 (harness engineering; D5 single-enforce-hook, D7 handoff markers, D8 plans version-controlled).
- Related past PRs: PR #2 (clarify-first gate + missing-marker sentinel + non-goals field; merged 2026-07-22 with fix commit 5f1894a).
- Origin: multi-agent review + 6-lens optimization workflow (2026-07-22, session 077d3a3f); proposals vetted against the repo (16 vetted viable, 16 pending-vet due to session limit — re-vet inline before implementing C4 items).
- User authorization (verbatim, 2026-07-22): 「先將R1+R2修復後合併, 接著 繼續處理 R3-R10 以及所有優化提案 P1-P3 (01-015) 的所有項目」.

## 3. Constraints

- Invariants: INV-GIT-* (never commit to master — work on this branch; guard hook enforces), INV-SEC-* (no secrets in code/logs; hook excerpts must not widen secret exposure).
- ERRORS.md hits: 2026-07-04 (hooks must get black-box smoke tests: block→exit2, pass→exit0; chmod +x), 2026-07-04 (dedup hash = essence fields only), 2026-07-07 (measure against the literal budget definition), 2026-07-04 (single canon per fact — no duplicated tables; new docs reference, don't copy).
- All English harness-doc edits sync their Traditional Chinese mirrors (CLAUDE.md Document Map rule).
- stop-retro-logger stays SENTINEL (never blocks, exit 0 on every path).

## 4. Step-by-step Plan

Phase B — sentinel hardening + doc coherence (R4–R10, O1 remainder):
- [x] B1. Single-pass transcript parse shared by harvest / missing-marker / git-commit detection (R10 perf: 3 reads → 1).
- [x] B2. `_detect_git_commits` parses actual Bash tool_use `command` inputs (no more prose-mention false PR_RETRO; R10).
- [x] B3. Marker semantic validation (R4+O1): strip markdown wrapping before match; placeholder reasons (`<target>`) = violation; HANDOFF target whitelist from handoff-protocol table; VERIFY_FAILED/HAR reason non-empty ≤80 chars.
- [x] B4. Fence-escape excerpt/context before writing into ERRORS.md code fences (R7).
- [x] B5. Best-effort flock around ERRORS.md read-modify-write (R8).
- [x] B6. handoff-protocol.md: sentinel-coverage note in "Where Markers Appear"; reconcile the three main-conversation requirement statements (:11/:111/execplan-lifecycle Phase 5) (R6); execplan-lifecycle Phase 1 Exit requires Non-Goals (R10); zh mirrors.
- [x] B7. PR #2 errata comment via gh (86/85 line counts; state/*.jsonl retention rationale) (R9).
- [x] B8. zh mirror for docs/harness-eval-2026-07-21.md (R10).
- [x] B9. Extend sandbox suite for all Phase B behaviors incl. concurrency; fresh-context verification; commit.

Phase C1 — traceability base (O2, O3):
- [x] C1a. post-edit-lint.py records `session` in tool-calls.jsonl; SCHEMA.md §4 updated (O2).
- [x] C1b. New PostToolUse Bash hook `post-bash-commit-ledger.py` → state/commits.jsonl {ts, session_id, branch, head_hash, msg_first_line}; settings.json wiring; SCHEMA.md section (O2).
- [x] C1c. New SessionStart hook `session-activation-check.py`: warn on unfilled template placeholder slots (Quick Commands, init.sh, invariants, TECHNICAL-REFERENCE); settings.json SessionStart wiring; log to hook-events (O3).

Phase C2 — verifiability main line (O4–O7):
- [x] C2a. PLANS.md §5 (spec + copy template) machine-parseable ```acceptance block; scripts/acceptance-run.py executes it, writes state/acceptance/F-NNN.jsonl; review-protocol checklist wired to run it; SCHEMA.md (O4).
- [x] C2b. docs/reviews/ convention + delegation-templates §6 requires Write of full report + machine-greppable `VERDICT: PASS|FAIL <path>` line; stop-retro-logger harvests VERDICT on SubagentStop → state/verifications.jsonl; FAIL also → Pending Review; SCHEMA.md (O5).
- [x] C2c. New PreToolUse Task hook `delegation-ledger.py` → state/delegations.jsonl with three-essentials booleans; SCHEMA.md (O6).
- [x] C2d. .github/workflows/harness-gates.yml: secret-scan on PR files (reuse guard/lint patterns), execplan-lint on docs/plans changes, placeholder-introduction gate (O7).
- [x] C2e. scripts/execplan-lint.py + post-edit-lint branch for docs/plans/*.md; PLANS.md §1 adds `Clarify-first:` provenance line (O-item "ExecPlan lint 與澄清留痕").
Phase C3 — anti-hallucination (O8–O11):
- [ ] C3a. scripts/check-doc-refs.py (paths, file:line, § refs, zh-mirror pairing) + post-edit-lint wiring + allowlist (O8).
- [ ] C3b. stop-retro-logger `detect_unfetched_citations` on SubagentStop: report URLs not fetched in-transcript → UNVERIFIED_CITATION finding (O9).
- [ ] C3c. `[UNCONFIRMED: ...]` inline marker standard in handoff-protocol + harvest pipeline; delegation-templates/judgment-rubrics pointers (O10).
- [ ] C3d. API evidence-table requirement in delegation-templates §2/§6 + review-protocol checklist item (O10).
- [ ] C3e. review-protocol adds Document Reviewer Checklist (sources spot-fetch, quantified-claims sourcing, second-opinion objective trigger) (O11); zh mirrors.

Phase C4 — scope & strategy & loop (O12–O15; re-vet each against repo before implementing):
- [ ] C4a. Non-Goals consumption: review-protocol reverse check + [SCOPE] tag; plan-reviewer completeness item; lifecycle Phase 6 reading list adds §1 (O12).
- [ ] C4b. Scope Baseline field in PLANS.md §1 + lifecycle Phase 1 Exit; Scope Change procedure section (Phase 4–7); clarify-first §3 amendment; last-word template line (O13).
- [ ] C4c. docs/research/ + INDEX rules; delegation-templates §7 strategy-research template (file-first, ≤40-line summary back); 4 research agents' frontmatter handoff_artifact + hypothesis-evidence table in output formats; docs/decisions/PDR-template.md (O14).
- [ ] C4d. Telemetry markers ([RULE_FIRED:...] etc.) in handoff-protocol + harvest → state/rule-events.jsonl; scripts/retro-status.py + SessionStart overdue reminder; monthly rollup in rotate (state/metrics-monthly.jsonl); rule-budget warn in post-edit-lint; harness-maintenance §6 standing-rule gate (O15).
- [ ] Final: full-suite rerun, doc-ref check over all touched docs, fresh-context batch verification, open PR.

## 5. Verification Strategy

```acceptance
build: python3 -m py_compile .claude/hooks/*.py scripts/*.py
lint-settings: python3 -m json.tool .claude/settings.json > /dev/null
plan-lint: python3 scripts/execplan-lint.py docs/plans/active/F-001-harness-verifiability-batch.md
negative-lint: python3 scripts/execplan-lint.py /dev/null expect-fail
```
- Manual: per-hook sandbox suites under scratchpad (b-smoke/c1-smoke run-tests.py — rerun full after each phase; every new/changed hook gets block/pass black-box cases per ERRORS.md 2026-07-04 lesson, `chmod +x` verified); live E2E probes via real subagents for SubagentStop-path features (missing marker, VERDICT harvest)
- Negative (covered in sandbox suites): violating probe flagged / compliant probe not; concurrent 5× hook invocations lose no findings; prose "git commit" mention must NOT trigger PR_RETRO

## 6. Progress Log
- [2026-07-22 23:10] dev created plan; Stage A (R1+R2+R3) already merged via PR #2 (commit 5f1894a, merge 1b9dfac)
- [2026-07-22 23:40] dev Phase B done: single-pass parse, Bash-tool-use-only commit detection, marker semantic validation (whitelist/placeholder/80-char), fence escaping, flock; protocol docs + zh mirrors synced; harness-eval zh mirror added; PR #2 errata comment posted. Sandbox suite 21/21 PASS (52ms/1.5MB perf); fresh-context verification PASS (6/6 items).
- [2026-07-22 23:25] dev Phase C1 done: session field in tool-calls, commits.jsonl ledger hook (PostToolUse Bash), session-activation-check (SessionStart); settings.json wired; SCHEMA.md §3/§4/§4a updated (incl. fixing the never-true duration_ms/exit_code schema). Sandbox 9/9 PASS; live run verified (unactivated warn fires on this repo).
- [2026-07-22 23:50] dev Phase C2 done: acceptance-run + execplan-lint scripts (dogfood caught a live pre-compact-snapshot syntax error), VERDICT harvest -> state/verifications.jsonl (live E2E: C2 verifier's FAIL verdict + over-80-char reason violation both harvested), delegation-ledger wired (live: verifier spawn recorded with trio booleans), harness-gates CI. Sandbox 24/24; fresh-context verification 11/12 (single FAIL = ERRORS.md change-set hygiene, resolved by declaring the sentinel-generated entries in this commit).

## 7. Decision Log
- DEC-1: One branch + one PR for the whole batch (instead of 5 stacked PRs), because all items form one initiative under this single ExecPlan, the hook files are sequentially dependent, and the user gets a single review/merge decision point.
- DEC-2: R3 was folded into the PR #2 fix commit (same function, same data-source bug); the follow-up batch therefore starts at R4.
- DEC-3: Scope authorization comes from the user's message (§2); merge of the final PR is deliberately left to human review (Non-Goals).

## 8. Open Questions
- None

## 9. Handoff Manifest
- Next agent: dev (main conversation continues)
- Required reading: this file; .claude/hooks/stop-retro-logger.py; scratchpad proposal dumps (viable.json / all_lens_proposals.json) if session survives, else §4 above is self-contained
- Current state marker: [HANDOFF: dev]
