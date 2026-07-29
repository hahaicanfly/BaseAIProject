# ExecPlan — Spec & Template

> **Role**: This file is the **spec and template** for ExecPlans. Every active task produces one instance at `docs/plans/active/F-NNN-<slug>.md`.
> **Basis**: `docs/decisions/ADR-0001-adopt-harness-engineering.md`, decision D8 (active/ is version-controlled).
> **Cross-session role**: ExecPlan is the harness system's "structured handoff object." Any next session or next agent should start by reading the corresponding ExecPlan to restore context.

---

## 1. When an ExecPlan Is Required

| Situation | ExecPlan required? |
|------|----------------|
| Bug fix touching < 3 files, no schema / API change | No (a commit message suffices) |
| Bug fix spanning modules or touching an invariant | **Yes** |
| New feature / refactor | **Mandatory** |
| API / data class change | **Mandatory** |
| Dependency upgrade | **Mandatory** |
| Documentation update (incl. ADR) | No |
| Hook / harness internal adjustment | **Yes** (can serve as dogfooding) |

---

## 2. Required Sections (strict order)

An ExecPlan must contain the following 9 sections, in this order:

````markdown
# ExecPlan: F-NNN — <Title>

| Field | Value |
|------|-----|
| Status | todo \| in_progress \| review \| done \| blocked |
| Owner Agent | <agent name> (pm / architect / dev / ... ) |
| Branch | feat/<slug> or fix/<slug> |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Linked PR | #NNN (filled in at merge time) |

## 1. Goal
<One sentence: what problem does this task solve? What measurable outcome should exist when done?>
<Non-Goals / Out of Scope: what this task deliberately will NOT cover — state at least one explicit boundary; write "none identified" only if genuinely none>
<Clarify-first: record the scope-check outcome — "N/4 fields missing → asked & confirmed YYYY-MM-DD" | "skipped: <plan-first exception>" | "all 4 fields present in original request" (clarify-first.md §1)>
<Scope Baseline: target user=… / success metric=… / trigger condition=… / confirmation source=<user quote + date, or the clarify-first skip reason>. Survives /clear via the last-word handoff; mid-task user changes append `vN (date): …` lines through the lifecycle's Scope Change procedure — never rewrite earlier versions>

## 2. Context
<Reference the relevant section anchor in agent_docs/TECHNICAL-REFERENCE.md; list affected modules / related existing ADRs / similar past PRs>

## 3. Constraints
<Reference the relevant INV-id(s) in docs/architecture/invariants.md; list hard rules this task must not violate>
<Reference the corresponding row in docs/architecture/domains.md's "change-impact assessment">

## 4. Step-by-step Plan
<Stepwise actions; each step must be independently verifiable>
1. [ ] Confirm baseline
2. [ ] Modify target files
3. [ ] Run build/lint/test to confirm no regression
4. [ ] Update related documentation

## 5. Verification Strategy
```acceptance
build: [your build command]
lint: [your lint command]
test: [your test command]
negative: [command that must fail] expect-fail
```
- Manual: <golden path for manual verification>

## 6. Progress Log
<Append-only; append one line per commit / progress update>
- [YYYY-MM-DD HH:mm] <agent> <one-sentence description>

## 7. Decision Log
<Architectural decisions, optional; complex decisions get promoted to a standalone ADR>
- DEC-1: <chose A over B, because ...>

## 8. Open Questions
<Questions awaiting human arbitration; write "none" if empty>
- Q1: ...

## 9. Handoff Manifest
<The minimum necessary context the next agent / session needs>
- Next agent: <name>
- Required reading before resuming: <file paths>
- Current state marker: [HANDOFF: <next>] or [VERIFY_FAILED: <reason>]
````

> **§5 acceptance block is machine-run**: `python3 scripts/acceptance-run.py <plan.md>` executes each `label: command` line (a trailing ` expect-fail` inverts the expectation), logs per-command evidence to `state/acceptance/<plan>.jsonl`, and exits non-zero on any FAIL — reviewers run this instead of eyeballing prose (see review-protocol.md checklist). Lines still containing `{{` or `[your ` placeholders are SKIPped (unactivated template). Structure of the plan itself is checked by `python3 scripts/execplan-lint.py` (9 sections, non-empty Non-Goals, INV reference, §9 marker, no leftover placeholders, and `INV-ARC-002` completion consistency: a `done` plan has no unticked steps and lives under `completed/`).

---

## 3. ExecPlan Lifecycle (10 stages)

```
[1] PM agent writes §1 Goal + §2 Context + §3 Constraints
        ↓
[2] Architect agent fills in §4 Step-by-step + §5 Verification (reviewed by plan-reviewer)
        ↓
[3] Human reviewer approves §1-§5 → status: in_progress
        ↓
[4] Branch feat/<slug> opened, one entry added to state/feature-list.json
        ↓
[5] Dev / sub-agent executes §4, writing a §6 Progress Log entry per commit
        ↓
[6] Invariant violation intercepted by a hook → logged in §6 as [VERIFY_FAILED: <INV-id>]
        ↓
[7] Execution complete → output ends with [HANDOFF: code-reviewer]
        ↓
[8] code-reviewer agent runs review → fills in §7 Decision Log
        ↓
[9] PR opened → link filled back into the header's Linked PR
        ↓
[10] Merge → status: done, file moved from active/ to completed/, feature-list.json updated accordingly
```

See `.claude/protocols/execplan-lifecycle.md` for details.

---

## 4. ExecPlan Naming Convention

`docs/plans/active/F-NNN-<short-slug>.md`

- `F-NNN`: sequential number (starting at F-001, aligned with `state/feature-list.json`)
- `<short-slug>`: ≤ 5 English words, kebab-case

Examples:
- `F-001-user-auth-flow.md`
- `F-002-dashboard-redesign.md`

---

## 5. Mapping ExecPlan to Existing Assets

| Existing asset | When ExecPlan references it |
|----------|------------------|
| `agent_docs/TECHNICAL-REFERENCE.md` | §2 Context (reference the relevant section anchor) |
| `docs/architecture/invariants.md` | §3 Constraints (must reference specific INV-id(s)) |
| `docs/architecture/domains.md` | §3 Constraints (change-impact assessment table) |
| `docs/learnings/ERRORS.md` | §3 Constraints (lessons from similar situations) |
| `docs/decisions/ADR-NNNN-*.md` | §2 Context or §7 Decision Log |
| `state/feature-list.json` | §1 status / verification synced on completion |

---

## 6. Integration with Existing Multi-Agent Skills

| Existing skill | Trigger | Which lifecycle stage | Corresponding ExecPlan section |
|-----------|-----|---------------------|------------------|
| `/feature-pipeline` | Large new feature | [1]-[8] full lifecycle | All sections |
| `/multi-agent-review` | High-risk change | [8] in parallel | §7 Decision Log |
| `/code-review` | Regular PR | [8] | §7 Decision Log |
| `/security-audit` | Touches auth/secrets | [8] | §7 Decision Log |
| `/tdd-workflow` | Core logic | [5] | §6 Progress Log |
| `/last-word` | End of session | Triggers write into §6 at [5] | §6 Progress Log + §9 Handoff |
| `/techdebt` | Quarterly | Independent path | Produces a new ExecPlan entering [1] |
| `/context` | Taking over someone else's work | When resuming at [4]-[5] | Read §9 Handoff Manifest |

---

## 7. Template (copy and use)

Copy the following to `docs/plans/active/F-<NNN>-<slug>.md`:

````markdown
# ExecPlan: F-NNN — <Title>

| Field | Value |
|------|-----|
| Status | todo |
| Owner Agent | <pm/architect/dev/...> |
| Branch | feat/<slug> |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Linked PR | — |

## 1. Goal


Non-Goals / Out of Scope: 
Clarify-first: 
Scope Baseline: 

## 2. Context
- TECHNICAL-REFERENCE: §<...>
- Related ADR: <ADR-NNNN or none>
- Related past PRs: <PR #NNN>

## 3. Constraints
- Invariants: <INV-XXX-NNN list>
- Domain impact: <domains.md row>
- ERRORS.md hits: <relevant lesson dates>

## 4. Step-by-step Plan
- [ ] 1. ...
- [ ] 2. ...
- [ ] 3. ...

## 5. Verification Strategy
```acceptance
build: [build command]
lint: [lint command]
test: [test command]
negative: [command that must fail] expect-fail
```
- Manual: <golden path>

## 6. Progress Log
- [YYYY-MM-DD HH:mm] <agent> created plan

## 7. Decision Log
_(empty, fill in during §4 execution or review)_

## 8. Open Questions
- None

## 9. Handoff Manifest
- Next agent: <pending>
- Required reading: agent_docs/TECHNICAL-REFERENCE.md §<...>
- Current state marker: [HANDOFF: pending]
````

---

## 8. Anti-patterns (do not write ExecPlans like this)

- ❌ Cramming all 9 sections into a wall of prose → later agents can't quickly locate information
- ❌ Writing "follow best practice" in §3 Constraints → must reference a specific INV-id
- ❌ Reducing §4 Step-by-step to one-liners → must be granular enough to verify
- ❌ Writing "done" in §6 Progress Log → must state specifically what was done
- ❌ Leaving §9 Handoff Manifest blank → write `[HANDOFF: done]` even when the task is complete

---

## 9. Where This File Is Referenced

- `docs/INDEX.md`
- `.claude/agents/*.md`: each agent's frontmatter `handoff_artifact`
- `.claude/protocols/execplan-lifecycle.md`: detailed state machine
- `CLAUDE.md`: rule pointer
