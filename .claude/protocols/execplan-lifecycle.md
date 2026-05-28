# Protocol: ExecPlan Lifecycle

> **角色**：定義 ExecPlan 從建立、執行到歸檔的 10 階段 state machine。
> **使用對象**：所有 sub-agent 在執行 task 前必須讀此檔；`code-reviewer` 與 `plan-reviewer` 用此檔判斷 ExecPlan 的階段合規性。
> **依據**：`docs/plans/PLANS.md` §3 + `docs/decisions/ADR-0001-adopt-harness-engineering.md` D8。

---

## State Machine

```
       ┌─────────────────────────────────────────────────────────┐
       │                                                          │
       ▼                                                          │
   [PROPOSED] ──► [PLANNED] ──► [APPROVED] ──► [IN_PROGRESS]      │
       │             │             │                 │             │
       │             │             │                 ▼             │
       │             │             │            [VERIFYING]        │
       │             │             │                 │             │
       │             │             │                 ▼             │
       │             │             │            [REVIEWING] ───┐   │
       │             │             │                 │          │   │
       │             │             │                 ▼          │   │
       │             ▼             ▼            [DONE]          │   │
       │        [REJECTED]    [REJECTED]            │            │   │
       │                                            │            │   │
       └────────[BLOCKED]────────────────────────  ─┘            │   │
                    │                                             │   │
                    └─────────────────────────────────────────────┘
```

### 階段映射到 `state/feature-list.json` 的 `status`

| Lifecycle 階段 | `status` 欄位值 |
|---------------|----------------|
| PROPOSED, PLANNED, APPROVED | `todo` |
| IN_PROGRESS, VERIFYING, REVIEWING | `in_progress` |
| BLOCKED | `blocked` |
| REJECTED | `done`（標記 cancelled） |
| DONE | `done` |

---

## 10 Phases

### Phase 1 — PROPOSED

**Trigger**：人類或 PM agent 提出需求。
**Owner**：`pm` agent（觸發詞：需求、規劃、PRD、用戶故事、功能）。
**Action**：建立 `docs/plans/active/F-NNN-<slug>.md`，填 §1 Goal + §2 Context（部分）。
**Exit**：填完 Goal，輸出 `[HANDOFF: architect]`。

### Phase 2 — PLANNED

**Trigger**：`[HANDOFF: architect]` 接收。
**Owner**：`architect` agent（觸發詞：架構、設計、規劃）。
**Action**：補完 §2 Context、§3 Constraints（含 INV-id）、§4 Step-by-step、§5 Verification Strategy。
**Exit**：輸出 `[HANDOFF: plan-reviewer]`。

### Phase 3 — APPROVED

**Trigger**：`[HANDOFF: plan-reviewer]` 接收。
**Owner**：`plan-reviewer` agent。
**Action**：審查 §1-§5 完整性、可驗證性、constraints 是否齊全、Open Questions 是否有未解決項。
**Exit**：
- 通過 → `[HANDOFF: <next-dev-or-feature-pipeline>]` + 寫 §7 Decision Log「Plan approved by plan-reviewer」
- 駁回 → 在 §8 Open Questions 補問題，回 Phase 2

> **人類審查員 gate**：Phase 3 通過後**必須等人類核可**才開分支進 Phase 4（PR-style review on `docs/plans/active/F-NNN.md`）。

### Phase 4 — IN_PROGRESS（開分支）

**Trigger**：人類核可後。
**Action**：
1. `git checkout master && git pull && git checkout -b feat/<slug>`（INV-GIT-005）
2. `state/feature-list.json` 加一筆 `status: in_progress`
3. ExecPlan 表頭 `Status: in_progress`、`Branch: feat/<slug>`
4. 開始執行 §4 Step-by-step

### Phase 5 — IN_PROGRESS（執行）

**Owner**：`tech-lead` 或 dev path subagent。
**Action**：每完成一步 §4 → 立即 commit → append 一行到 §6 Progress Log。
**鐵律**：
- 每次 commit 前 `git branch --show-current`（INV-GIT-001）
- 每次編輯後跑對應 lint/test（hook 自動或手動）
- 違反 invariant 被 hook 攔截 → 修完才 commit；attempt 記錄到 §6
**Exit**：§4 全打勾 → `[HANDOFF: code-reviewer]`

### Phase 6 — VERIFYING

**Owner**：`code-reviewer` agent（model: Sonnet）。
**Action**：
1. 讀 ExecPlan §3 Constraints 與 §5 Verification Strategy
2. 跑 `git diff master...HEAD` 對照 §4
3. 逐條對照 INV-id 確認無違反
4. 跑 §5 的所有 verification 指令
5. 寫 §7 Decision Log（Pass / Blocker / Warning / Suggestion）
**Exit**：
- 全 Pass → `[HANDOFF: human-pr-review]`
- 有 Blocker / Warning → 回 Phase 5 修復
- 發現 invariant 漏記 → append 到 ERRORS.md Pending Review

### Phase 7 — REVIEWING（PR）

**Action**：
1. 開 PR（`gh pr create --base master`）
2. ExecPlan 表頭補 `Linked PR: #NNN`
3. 等 GitHub PR review

> **人類審查員 gate**：PR review 通過才進 Phase 8。

### Phase 8 — DONE（merge + 歸檔）

**Trigger**：PR merged。
**Action**：
1. `git checkout master && git pull`
2. ExecPlan 從 `docs/plans/active/` 移到 `docs/plans/completed/`
3. ExecPlan 表頭 `Status: done`，§6 補 final entry
4. `state/feature-list.json` 更新 `status: done`、`exec_plan` 路徑改為 `completed/`
5. `verification.{build_ok, lint_ok, tests_passing}` 全部 `true`

### Phase 9 — BLOCKED（任意階段都可進入）

**Trigger**：發現外部依賴未就緒（後端 API 未上線、第三方 SDK bug、設計稿待補）。
**Action**：
1. ExecPlan §8 Open Questions 寫明 blocker
2. `state/feature-list.json` `status: blocked`
3. 輸出 `[HUMAN_ATTENTION_REQUIRED: <reason>]`
**Exit**：blocker 解除 → 回原階段繼續。

### Phase 10 — REJECTED

**Trigger**：plan-reviewer 兩輪駁回，或 PR 被人類 close。
**Action**：
1. ExecPlan 從 `active/` 移到 `completed/`，加 `## Rejection Reason` 段
2. `state/feature-list.json` 移除該筆或標記 cancelled
3. 將駁回理由 append 到 `docs/learnings/ERRORS.md` Pending Review

---

## ExecPlan 跨 session 接手 SOP

新 session 接續中斷的 ExecPlan 時：

1. 讀 `state/feature-list.json` 找 `status: in_progress` 的 task
2. 讀對應 `docs/plans/active/F-NNN-*.md` 全文
3. 重點看 §6 Progress Log 最後一行 + §9 Handoff Manifest 的 `Current state marker`
4. 若 marker 為 `[VERIFY_FAILED: <INV-id>]` → 從該 INV-id 對應的修復開始
5. 若 marker 為 `[HANDOFF: <agent>]` → 進入該 agent role 接手
6. 若 marker 為 `[HUMAN_ATTENTION_REQUIRED: ...]` → 不要繼續，先請示人類

---

## Trace 示例

```
[2026-05-08 10:00] pm Created F-042-export-history.md, marked [HANDOFF: architect]
[2026-05-08 10:30] architect Filled Constraints (INV-API-001, INV-TEST-001) and Plan, [HANDOFF: plan-reviewer]
[2026-05-08 11:00] plan-reviewer Approved with note on §5 negative case, [HANDOFF: human-approval]
[2026-05-08 14:00] human Approved, branch feat/export-history created
[2026-05-08 14:30] dev Step 1 done, commit a1b2c3
[2026-05-08 15:00] dev Step 2 violated INV-API-001 (missing default for field), hook flagged, fixed in commit d4e5f6
[2026-05-08 15:30] dev Step 3-5 done, [HANDOFF: code-reviewer]
[2026-05-08 16:00] code-reviewer 1 Warning (missing test for negative case), [HANDOFF: dev]
[2026-05-08 16:30] dev Added test, commit 7890ab, [HANDOFF: code-reviewer]
[2026-05-08 17:00] code-reviewer All pass, [HANDOFF: human-pr-review]
[2026-05-08 17:30] human PR #142 opened
[2026-05-09 10:00] human PR #142 merged → moved to completed/
```

---

## 引用此檔的位置

- `docs/plans/PLANS.md` §3
- `.claude/agents/*.md`（每個 agent 的 Harness 交接協議段）
- `.claude/protocols/handoff-protocol.md`
