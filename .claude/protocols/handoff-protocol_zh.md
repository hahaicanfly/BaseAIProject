# Protocol: Agent Handoff Markers

> **角色**：定義 agent 之間、agent 與人類之間的結構化交接訊號。
> **使用對象**：所有 sub-agent 在輸出末段必須使用本協議的標記。
> **依據**：`docs/decisions/ADR-0001-adopt-harness-engineering.md` D7。

---

## 標記語法

每個 sub-agent 的 final response **必須**以下列三個標記之一為結尾（單行，方括號）；主對話僅在 ExecPlan lifecycle 出口必須帶標記，task workflow 內其餘回合為建議（見下方「標記出現位置」與「哨兵覆蓋範圍」）：

```
[HANDOFF: <next-agent-or-state>]
[VERIFY_FAILED: <INV-id-or-reason>]
[HUMAN_ATTENTION_REQUIRED: <reason>]
```

有實際作業（至少一次 tool call）的 sub-agent 以任何其他形式結尾，視為 protocol violation，由 `stop-retro-logger.py` 標記送 `docs/learnings/ERRORS.md` Pending Review。哨兵同時驗證標記*語意*：照抄文件的佔位符 reason（`<target>`）、§1 表格以外的 `[HANDOFF:]` target、超過 80 字元的 `[VERIFY_FAILED:]`/`[HUMAN_ATTENTION_REQUIRED:]` reason，都視為 violation。標記行外的 markdown 包裹（如 `**[HANDOFF: main]**`）可容忍。此檢查僅適用於 `SubagentStop` 事件——主對話的一般回合（`Stop` 事件）不要求以標記結尾。

---

## 1. `[HANDOFF: <target>]`

**用途**：正常完成自己負責的階段，移交下一個角色。
**Target 必須是下列之一**（此表是 `stop-retro-logger.py` 中 `VALID_HANDOFF_TARGETS` 的同步來源——改表必須同時改該常數）：

| Target | 意義 |
|--------|------|
| `architect` | 移交給 architect agent |
| `plan-reviewer` | 移交給 plan-reviewer agent 審 ExecPlan |
| `tech-lead` | 移交給 tech-lead 開始實作 |
| `dev` | 移交給開發路徑（可能是主對話 + 多個 sub-agent） |
| `code-reviewer` | 完成實作，等待 review |
| `qa-engineer` | 移交給 QA agent 寫測試 / 跑驗證 |
| `security-reviewer` | 涉及 auth/secret 的最終審查 |
| `uiux-agent` | UI 相關，進三階段流程 |
| `human-approval` | ExecPlan §1-§5 已完成，等人類核可 |
| `human-pr-review` | code-review 通過，等人類審 PR |
| `done` | task 全部完成（merged）|
| `main` | 回報主對話（指揮官）— 派工 subagent（見 `.claude/templates/delegation-templates.md`）完成子任務時使用 |
| `pending` | 尚未確定下一個（極少用，多半搭配 Open Questions） |

**範例**（INV id 為示意，實填依 `docs/architecture/invariants.md` 現行清單）：
```
✓ Plan 完成，§3 Constraints 引用 INV-GIT-002 / INV-SEC-001
→ 下一步：等待 plan-reviewer 審查
[HANDOFF: plan-reviewer]
```

---

## 2. `[VERIFY_FAILED: <INV-id-or-reason>]`

**用途**：執行中發現驗證失敗（lint / test / hook 攔截 / invariant 違反）。
**Reason 格式**：
- 如果違反某條 invariant：填該條 INV id（如 `INV-GIT-002`，依 `docs/architecture/invariants.md` 現行清單）
- 如果是其他原因：簡短一句話（≤80 字元）

**規則**：
- 看到 `[VERIFY_FAILED:]` → 不得繼續、不得 commit、必須修復後重試
- 連續 3 次 `[VERIFY_FAILED:]` → 必須升級為 `[HUMAN_ATTENTION_REQUIRED:]`
- `stop-retro-logger.py`（Phase D）會把所有 `[VERIFY_FAILED:]` 與其前 5 行 context 收割到 `docs/learnings/ERRORS.md` Pending Review

**範例**（INV id 為示意，依專案 invariants 實填）：
```
✗ post-edit-lint 攔截：INV-SEC-001 diff 中偵測到疑似硬編碼金鑰
→ 修復方案：改讀環境變數並更新 .env.example
[VERIFY_FAILED: INV-SEC-001]
```

---

## 3. `[HUMAN_ATTENTION_REQUIRED: <reason>]`

**用途**：超出 agent 可自主決定的範圍，必須人類介入。
**6 種觸發情境**（任一即可標記）：

1. **連續 3 次 lint/test 失敗仍無法定位根因**
2. **偵測到 secret / 硬編碼 API key / 密碼**
3. **invariant 衝突無法以技術手段化解**（例：兩條 INV 互斥）
4. **ExecPlan §8 Open Questions 未獲解答阻擋進度**
5. **跨 repo / 跨平台影響**（如前端改動需後端配合）
6. **任何 destructive op**（rm -rf / git reset --hard / branch -D / force-push）

**規則**：
- 標記後**必須立即停止**，不得試圖自己解決
- 必須輸出**結構化問題清單**讓人類能快速回覆
- 與 ExecPlan §8 Open Questions 同步

**範例**（INV id 為示意，依專案 invariants 實填）：
```
⚠ 偵測到 Request data class 缺 deviceId field，違反 INV-SEC-002
   修復方案有兩種：
   a) 加 default null，相容舊 client
   b) 加 non-null 必填 → 所有呼叫點要同步改

→ 不在 ExecPlan 預期範圍內，請選擇方案
[HUMAN_ATTENTION_REQUIRED: 修復方案需人類選擇 a 或 b]
```

---

## 行內輔助標記

`[UNCONFIRMED: <claim, ≤80 字元>]` —— judgment-rubrics.md §6 誠實條款（「超出環境的事實 → 寫未確認，不要編造」）的標準語法：

- 在文字中**主張出現的當下**內嵌標記（行內，不是放在結尾）；每個無出處主張標一個標籤。
- 下游文件若引用了帶有未確認標籤的主張，必須保留該標籤；唯一移除方式是補上出處（URL 或 file:line）。
- `stop-retro-logger.py` 會把每次實際出現的標記收割進 `docs/learnings/ERRORS.md` Pending Review（kind `UNCONFIRMED`），讓無出處主張進入週檢而不是靜默擴散。
- 這**不是**結尾標記 —— 報告仍須以上述三種標記之一結尾。

**Telemetry markers（遙測標記）** —— 在規則實際觸發的當下行內發出，由 `stop-retro-logger.py` 收割進 `state/rule-events.jsonl`（同一 session 內去重），讓規則命中率可被量測而非只靠軼事：

```
[RULE_FIRED: <rule-name>|<detail>]      例：[RULE_FIRED: clarify-first|missing=3, asked]
[RULE_SKIPPED: <rule-name>|<why>]       例：[RULE_SKIPPED: clarify-first|plan-first exception: <20-line fix]
[ESCALATION: <from>-><to>|<task>]       例：[ESCALATION: sonnet->opus|race-condition fix]
```

與 `[UNCONFIRMED:]` 一樣，這些是行內標記，不是結尾標記。驗收結果不需要 telemetry marker —— `VERDICT:` 那一行已經會落入 `state/verifications.jsonl`；circuit-break 則透過 `[HUMAN_ATTENTION_REQUIRED:]` 收割呈現。

---

## 標記出現位置

| 位置 | 行為 |
|------|------|
| Sub-agent 的 final response | **必須**有單行 marker 結尾 |
| ExecPlan §9 Handoff Manifest | 寫入 `Current state marker:` 欄位 |
| ExecPlan §6 Progress Log | 每行末段可加 marker |
| 主對話的 turn 結尾 | 非 task workflow 不要求；task 中建議加；ExecPlan lifecycle 出口（如 Phase 5 → `[HANDOFF: code-reviewer]`）**必須**加，由 review 把關而非 hook |

---

## 哨兵覆蓋範圍

`stop-retro-logger.py` 機械檢查的範圍 vs. 仍靠自律的範圍——避免把「文件上的義務」誤認為「被強制的義務」：

| 路徑 | 覆蓋 |
|------|------|
| Sub-agent final response（`SubagentStop` 且有 `agent_transcript_path`） | **有檢查**：最後非空行的標記存在性、`[HANDOFF:]` target 合法（§1 表）、reason 非佔位符、`[VERIFY_FAILED:]`/`[HUMAN_ATTENTION_REQUIRED:]` reason ≤80 字元 |
| 以 tool call 結尾的 sub-agent（Workflow structured-output 代理、被中斷的代理） | 豁免——沒有結尾文字報告可供檢查 |
| 主對話回合（`Stop`） | hook 不檢查；ExecPlan lifecycle 出口標記由 plan/code review 把關 |
| agy / Antigravity 代理 | 不檢查——該環境不執行 Python hooks（CLAUDE.md Antigravity 橋接段）；靠手動遵守 |

---

## Handoff 必要 context

每次 `[HANDOFF: <next>]` 之前，輸出必須包含足夠 context 讓下一個 agent 能 cold start：

| 資訊 | 是否必要 |
|------|---------|
| ExecPlan 路徑（`docs/plans/active/F-NNN-*.md`） | **必要** |
| 當前 branch | **必要** |
| 最後 commit hash | **必要** |
| §4 Step 進度（哪步完成、哪步進行中） | **必要** |
| 已知 Open Questions | 若有則必要 |
| 推薦執行順序（給下一個 agent） | 建議 |

**範例 handoff payload**（在 marker 前一段）：

```
HANDOFF SUMMARY
- ExecPlan: docs/plans/active/F-042-export-history.md
- Branch: feat/export-history (commit 7890ab)
- Step status: §4.1-§4.4 done, §4.5 (test) pending
- Open Questions: 無
- Suggested next: code-reviewer 跑 review，重點看 §5 negative case 是否覆蓋

[HANDOFF: code-reviewer]
```

---

## 反模式

- ❌ 用「完成」「ok」「done」當結尾，沒有 marker
- ❌ 在 marker 後又繼續輸出（marker 必須是最後一行）
- ❌ `[HANDOFF: code-review]` （正確是 `code-reviewer`，含 -er）
- ❌ `[VERIFY_FAILED: failed]` （reason 必須具體；INV-id 或一句話）
- ❌ `[HUMAN_ATTENTION_REQUIRED:]` 後自己又試著 workaround（看到此 marker 必須停）

---

## 引用此檔的位置

- `.claude/agents/*.md`（每個 agent 的 Harness 交接協議段）
- `.claude/protocols/execplan-lifecycle.md`
- `.claude/hooks/stop-retro-logger.py`（Phase D）
