# state/ — Harness Runtime State Schema

> **角色**：本目錄收納 harness 執行期狀態（feature 進度 / session handoff / observability log）。
> **版控策略**：`state/*` 全部 gitignored，但本 `SCHEMA.md` 入版控，讓 contributor 知道格式。
> **物理目錄會在第一次 hook 觸發時自動建立**，無需手動 init。

---

## 1. `state/feature-list.json` — Active task 單一事實源

**性質**：可被 model 讀寫的 JSON。優先選 JSON 而非 Markdown，因 JSON 對 model-induced corruption 抵抗力較強（OpenAI Codex 一百萬行實驗的結論）。
**用途**：跨 session 追蹤目前 in-flight 的 task 狀態。**與 `docs/plans/PLANS.md` 分工**：PLANS.md 是 ExecPlan 規格（長期），feature-list.json 是 active harness 狀態（即時）。

### Schema v1.0

```json
{
  "schema_version": "1.0",
  "last_updated_session": "<claude session id 或 ISO timestamp>",
  "features": [
    {
      "id": "F-NNN",                                      // F-XXX 連號，與 ExecPlan 對應
      "title": "Short human-readable title",
      "status": "todo|in_progress|review|done|blocked",
      "owner_agent": "tech-lead|architect|dev|code-reviewer|...",
      "exec_plan": "docs/plans/active/F-NNN-slug.md",     // 完成後改指向 completed/
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

### 寫入時機

- ExecPlan 建立時：`status: todo` 一行
- 開分支時：`status: in_progress` + `branch:` 補入
- code-reviewer agent 跑完無 Blocker：`status: review`
- PR merge：`status: done` + `exec_plan` 路徑改為 `docs/plans/completed/`
- hook 偵測到 build/lint/test 結果：`verification.*` 對應更新

---

## 2. `state/session-handoffs/<ISO timestamp>.json` — PreCompact 快照

**性質**：純 append（每次 PreCompact 寫一個新檔，永不修改）。
**寫入者**：`.claude/hooks/pre-compact-snapshot.py`。
**用途**：context 接近上限被 compact 之前，把當前 active context 凝固成一份結構化檔案，作為 cold start / context reset 的還原點。

### Schema v1.0

```json
{
  "schema_version": "1.0",
  "snapshot_at": "ISO 8601",
  "session_id": "<claude session id>",
  "active_execplan": "docs/plans/active/F-NNN-slug.md",   // null 若無
  "active_branch": "feat/<slug>",
  "active_handoff_marker": "[HANDOFF: code-reviewer]",     // 最後一個 [HANDOFF:*] 標記
  "open_questions": ["..."],                                // 從 ExecPlan 抓
  "todo_items": ["..."],                                    // 從 TodoList 抓
  "recent_invariant_violations": []                         // 從 stop-retro logger 抓
}
```

---

## 3. `state/hook-events.jsonl` — Hook 觸發 audit log

**性質**：JSON Lines（每行一筆，append-only）。
**寫入者**：每個 hook 自身寫入第一行。
**輪替策略**：30 天 rotate，每日至多執行一次（`stop-retro-logger.py` 的 `rotate_state_if_due()`，由 `state/.last-rotate` 的 mtime 判斷是否已過 24 小時；失敗靜默跳過，不會讓 hook 崩潰）。

### Schema (per line)

```json
{ "ts": "ISO 8601", "hook": "pre-tool-use-guard|post-edit-lint|pre-compact-snapshot|stop-retro-logger", "tool": "<tool name if applicable>", "result": "pass|fail|sentinel|enforced_block", "reason": "<short msg>" }
```

---

## 3a. `state/retro-hashes.jsonl` — 週審墓碑帳本

**性質**：JSON Lines，append-only。
**寫入者**：`.claude/hooks/stop-retro-logger.py` 每次成功 append 一筆 finding 到 `ERRORS.md` `## Pending Review` 後，同步把該 hash 寫入本檔。
**用途**：判重時取「`ERRORS.md` 現存 hash ∪ 本帳本 hash」的聯集 —— 人類週審把 `## Pending Review` 條目刪掉後，該 hash 仍留在帳本中，下次 Stop 事件不會把同一 finding 重新 append（同 hash 對應同一 transcript 內容永遠不變）。
**輪替策略**：90 天 rotate，同 `.last-rotate` 閘門與 `hook-events.jsonl` 共用。
**檔案不存在時**：hook 自動建立（首次 append 時）。
**備註（F-004）**：PR_RETRO 提醒不再經過本帳本 —— 改存 `retro-reminders.jsonl`（§3f），完全不碰 `ERRORS.md`。

### Schema (per line)

```json
{ "hash": "<10 hex chars>", "ts": "ISO 8601" }
```

---

## 3f. `state/retro-reminders.jsonl` — 待辦 /pr-retro 提醒（易變）

**性質**：JSON Lines，整檔重寫；每個 session 一筆，commit 數成長時就地更新。
**寫入者**：`.claude/hooks/stop-retro-logger.py`（`_append_retro_suggestion`）。
**讀取者**：`scripts/retro-status.py`（回報待辦提醒數）。
**用途**：F-004 把 PR_RETRO 提醒從 `ERRORS.md` `## Pending Review` 遷來 —— 提醒的時間戳每次 Stop 事件都會更新，易變的機器狀態放在 tracked 檔案裡使工作區永遠不乾淨（2026-07-29 兩度擋下 `git checkout`/`git pull`）。`ERRORS.md` 從此只留耐久的、人審過的內容。
**消化方式**：某 session 跑完 `/pr-retro`（或決定跳過）後，於週審時刪掉該 session 的行——或直接清空檔案；沒有墓碑機制，已完結 session 刪了就是刪了。

### Schema (per line)

```json
{ "ts": "ISO 8601", "session": "<claude session id>", "commit_count": <int> }
```

---

## 3b. `state/.last-rotate` — Rotate 節流時間戳

**性質**：單一時間戳字串（非 JSON），純覆寫（每次 rotate 執行後重寫整檔）。
**寫入者**：`.claude/hooks/stop-retro-logger.py` 的 `rotate_state_if_due()`。
**用途**：用檔案 mtime（或內容，兩者皆為同次寫入的 ISO 時間）判斷距上次 rotate 是否已超過 24 小時；未超過則本次 Stop 事件跳過 rotate，避免每次 session 結束都掃描整個 jsonl。
**內容**：`now_iso()` 的輸出，例如 `2026-07-04T12:46:33+0000`。

---

## 4. `state/tool-calls.jsonl` — Tool 用量 audit log

**性質**：JSON Lines，append-only。
**寫入者**：`.claude/hooks/post-edit-lint.py` 順帶寫；其他 hook 在 PostToolUse 上時也可寫。
**用途**：定位 tool 路由錯誤、發現 tool 膨脹。

### Schema

```json
{ "ts": "ISO 8601", "tool": "<tool name>", "duration_ms": 1234, "exit_code": 0, "matcher": "<hook matcher>" }
```

---

## 5. `state/token-usage.jsonl` — Token 消耗追蹤

**性質**：JSON Lines，append-only。
**寫入者**：`.claude/hooks/pre-compact-snapshot.py`（compact 時抓）。
**用途**：偵測 context anxiety / context flooding，找出 cache miss 模式。

### Schema

```json
{ "ts": "ISO 8601", "session_id": "...", "input_tokens": 0, "output_tokens": 0, "cache_creation": 0, "cache_read": 0, "trigger": "pre-compact|stop" }
```

---

## 6. 隱私與共享性

- `state/` 內所有 jsonl 與 json 檔**不入版控**（避免 token / branch / commit hash 等敏感字串外洩）。
- `state/feature-list.json` 雖 gitignored，仍應**避免**寫入機密內容（API key、密碼、token）。
- 跨 session 的進度同步只透過 `docs/plans/active/*.md`（版控）+ `state/feature-list.json`（本機）兩個來源協同。

---

## 7. 演進

- 50 task 後若觀察到 jsonl 體積快速膨脹，引入 rotate（每月 archive 一次到 `state/archive/`）。
- 若決定升級到正式觀察性平台（Datadog / Honeycomb），由 stop-retro-logger 改寫成同時 ship to remote。
- Schema 升級採 `schema_version` 顯式標示；不向下相容時 stop-retro-logger 自動 migrate。
