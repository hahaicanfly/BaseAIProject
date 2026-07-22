# ExecPlan — Spec & Template

> **角色**：本檔是 ExecPlan 的**規格書與範本**。每個 active task 在 `docs/plans/active/F-NNN-<slug>.md` 產生一份實例。
> **依據**：`docs/decisions/ADR-0001-adopt-harness-engineering.md` 決策 D8（active/ 入版控）。
> **跨 session 角色**：ExecPlan = harness 系統的「結構化交接物件」。任何下一個 session、下一個 agent 都應從讀對應 ExecPlan 開始恢復 context。

---

## 1. 何時必須寫 ExecPlan

| 情境 | 是否需 ExecPlan |
|------|----------------|
| Bug fix < 3 檔案、無 schema / API 變動 | 否（commit message 即足） |
| Bug fix 跨 module 或涉及 invariant | **是** |
| 新功能 / 重構 | **強制** |
| API / data class 變動 | **強制** |
| 依賴升級 | **強制** |
| 文件更新（含 ADR） | 否 |
| Hook / harness 內部調整 | **是**（可作為 dogfood） |

---

## 2. 必要段落（嚴格順序）

ExecPlan 必須含以下 9 段，依此順序：

````markdown
# ExecPlan: F-NNN — <Title>

| 欄位 | 值 |
|------|-----|
| Status | todo \| in_progress \| review \| done \| blocked |
| Owner Agent | <agent name>（pm / architect / dev / ... ） |
| Branch | feat/<slug> 或 fix/<slug> |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Linked PR | #NNN（merge 時補上） |

## 1. Goal
<一句話：這個 task 要解決什麼問題？做完應達成什麼可量測結果？>
<Non-Goals / Out of Scope：這個 task 刻意不做什麼——至少列出一項明確邊界；真的沒有才寫「無」>
<Clarify-first：記錄範圍檢查結果——「缺 N/4 欄 → 已提問並於 YYYY-MM-DD 確認」｜「skipped: <plan-first 例外>」｜「原始需求 4 欄齊全」（clarify-first.md §1）>

## 2. Context
<引用 agent_docs/TECHNICAL-REFERENCE.md 的章節錨；列出影響的 module / 既有相關 ADR / 過去類似 PR>

## 3. Constraints
<引用 docs/architecture/invariants.md 中相關 INV-id；列出本 task 不可違反的硬規則>
<引用 docs/architecture/domains.md「變更影響評估」對應行>

## 4. Step-by-step Plan
<逐步動作，每步必須能獨立 verify>
1. [ ] 確認 baseline
2. [ ] 修改目標檔案
3. [ ] 執行 build/lint/test 確認無 regression
4. [ ] 更新相關文件

## 5. Verification Strategy
```acceptance
build: [your build command]
lint: [your lint command]
test: [your test command]
negative: [必須失敗的指令] expect-fail
```
- Manual: <人工驗證的 golden path>

## 6. Progress Log
<Append-only，每次 commit / 進度更新 append 一行>
- [YYYY-MM-DD HH:mm] <agent> <一句話描述>

## 7. Decision Log
<架構性決定，可選；複雜決定升級為獨立 ADR>
- DEC-1: <選 A 不選 B，原因 ...>

## 8. Open Questions
<等待人類仲裁的問題；空時寫「無」>
- Q1: ...

## 9. Handoff Manifest
<下一個 agent / session 需要的最小必要 context>
- Next agent: <name>
- Required reading before resuming: <file paths>
- Current state marker: [HANDOFF: <next>] 或 [VERIFY_FAILED: <reason>]
````

> **§5 acceptance 區塊是機器執行的**：`python3 scripts/acceptance-run.py <plan.md>` 逐行執行 `label: command`（行尾 ` expect-fail` 表示該指令必須失敗才算過），每條證據寫入 `state/acceptance/<plan>.jsonl`，任一 FAIL 即非零退出——reviewer 執行它而非目測 prose（見 review-protocol.md 檢查表）。仍含 `{{` 或 `[your ` 佔位符的行會被 SKIP（模板未活化）。計畫本身的結構由 `python3 scripts/execplan-lint.py` 檢查（9 段、Non-Goals 非空、INV 引用、§9 標記、無殘留佔位符）。

---

## 3. ExecPlan 生命週期 (10 階段)

```
[1] PM agent 寫 §1 Goal + §2 Context + §3 Constraints
        ↓
[2] Architect agent 補 §4 Step-by-step + §5 Verification（plan-reviewer 審）
        ↓
[3] 人類審查員核可 §1-§5 → status: in_progress
        ↓
[4] 開分支 feat/<slug>，state/feature-list.json 加一筆
        ↓
[5] Dev / sub-agent 執行 §4，每 commit 寫 §6 Progress Log
        ↓
[6] 違反 invariant 被 hook 攔截 → §6 記 [VERIFY_FAILED: <INV-id>]
        ↓
[7] 完成執行 → 在輸出尾端標 [HANDOFF: code-reviewer]
        ↓
[8] code-reviewer agent 跑 review → 補 §7 Decision Log
        ↓
[9] PR 開立 → 連結回填到表頭 Linked PR
        ↓
[10] Merge → status: done，檔案從 active/ 移到 completed/，feature-list.json 對應更新
```

詳見 `.claude/protocols/execplan-lifecycle.md`。

---

## 4. ExecPlan 的命名規則

`docs/plans/active/F-NNN-<short-slug>.md`

- `F-NNN`：連號（從 F-001 起，與 `state/feature-list.json` 對齊）
- `<short-slug>`：≤ 5 個英文單字 kebab-case

範例：
- `F-001-user-auth-flow.md`
- `F-002-dashboard-redesign.md`

---

## 5. ExecPlan 與既有資產的對映

| 既有資產 | ExecPlan 何時引用 |
|----------|------------------|
| `agent_docs/TECHNICAL-REFERENCE.md` | §2 Context（引用對應章節錨） |
| `docs/architecture/invariants.md` | §3 Constraints（必引用具體 INV-id） |
| `docs/architecture/domains.md` | §3 Constraints（變更影響評估表） |
| `docs/learnings/ERRORS.md` | §3 Constraints（類似情境的 lesson） |
| `docs/decisions/ADR-NNNN-*.md` | §2 Context 或 §7 Decision Log |
| `state/feature-list.json` | §1 完成時 status / verification 同步 |

---

## 6. 與既有 multi-agent skill 的整合

| 既有 skill | 觸發 | 在 lifecycle 哪一步 | ExecPlan 對應段 |
|-----------|-----|---------------------|------------------|
| `/feature-pipeline` | 大型新功能 | [1]-[8] 全程 | 全段 |
| `/multi-agent-review` | 高風險變更 | [8] 並行 | §7 Decision Log |
| `/code-review` | 一般 PR | [8] | §7 Decision Log |
| `/security-audit` | 涉 auth/secret | [8] | §7 Decision Log |
| `/tdd-workflow` | 核心邏輯 | [5] | §6 Progress Log |
| `/last-word` | session 末段 | 觸發 [5] 寫入 §6 | §6 Progress Log + §9 Handoff |
| `/techdebt` | 季度 | 獨立路徑 | 產出新 ExecPlan 進 [1] |
| `/context` | 接手他人工作 | [4]-[5] 接續時 | 讀 §9 Handoff Manifest |

---

## 7. 範本（複製即用）

複製下方到 `docs/plans/active/F-<NNN>-<slug>.md`：

````markdown
# ExecPlan: F-NNN — <Title>

| 欄位 | 值 |
|------|-----|
| Status | todo |
| Owner Agent | <pm/architect/dev/...> |
| Branch | feat/<slug> |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Linked PR | — |

## 1. Goal


Non-Goals / Out of Scope：
Clarify-first：

## 2. Context
- TECHNICAL-REFERENCE: §<...>
- Related ADR: <ADR-NNNN or none>
- Related past PRs: <PR #NNN>

## 3. Constraints
- Invariants: <INV-XXX-NNN list>
- Domain impact: <domains.md row>
- ERRORS.md hits: <相關 lesson 日期>

## 4. Step-by-step Plan
- [ ] 1. ...
- [ ] 2. ...
- [ ] 3. ...

## 5. Verification Strategy
```acceptance
build: [build command]
lint: [lint command]
test: [test command]
negative: [必須失敗的指令] expect-fail
```
- Manual: <golden path>

## 6. Progress Log
- [YYYY-MM-DD HH:mm] <agent> created plan

## 7. Decision Log
_(空，待 §4 執行中或 review 時補)_

## 8. Open Questions
- 無

## 9. Handoff Manifest
- Next agent: <pending>
- Required reading: agent_docs/TECHNICAL-REFERENCE.md §<...>
- Current state marker: [HANDOFF: pending]
````

---

## 8. 反模式（不要這樣寫 ExecPlan）

- ❌ 把 9 段拼成一段散文 → 後續 agent 無法快速定位資訊
- ❌ §3 Constraints 寫 "follow best practice" → 必須引用具體 INV-id
- ❌ §4 Step-by-step 全部一句話 → 必須細到能 verify
- ❌ §6 Progress Log 用「完成」 → 必須具體說做了什麼
- ❌ §9 Handoff Manifest 留空 → 即使任務完成也要寫 `[HANDOFF: done]`

---

## 9. 引用此檔的位置

- `docs/INDEX.md`
- `.claude/agents/*.md`：每個 agent 的 frontmatter `handoff_artifact`
- `.claude/protocols/execplan-lifecycle.md`：詳細 state machine
- `CLAUDE.md`：rule pointer
