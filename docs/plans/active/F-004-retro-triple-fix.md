# ExecPlan: F-004 — Retro Triple Fix（三課題一次解決：易變狀態遷移 / Agent 催收協議 / Git 基底驗證）

| Field | Value |
|------|-----|
| Status | in_progress |
| Owner Agent | dev (main conversation) |
| Branch | feat/f-004-retro-triple-fix |
| Created | 2026-08-03 |
| Last Updated | 2026-08-03 |
| Linked PR | (filled in at merge time) |

## 1. Goal

一次解決 2026-07-29 retro 產出的三個課題（ERRORS.md Pending Review 行 32-52），可量測成果：(1) session 結尾後 `git status` 對 ERRORS.md 乾淨——PR_RETRO 提醒改寫入 `state/retro-reminders.jsonl`；(2) 子 agent idle 催收協議進入 tier pack 注入層，未來 session 實際讀得到；(3) `scripts/verify-branch-base.py` 可機械判定分支基底、INV-GIT-005 的 CHECK 欄位變為可執行。

Non-Goals / Out of Scope:
- 不遷移 PROTOCOL_VIOLATION / UNCONFIRMED / UNVERIFIED_CITATION 等一次性 harvest（使用者 2026-08-03 裁定選項 A：只遷 PR_RETRO）
- 不改 pr-retro skill 的人審寫入路徑；不做週審流程改造
- 不動 pre-tool-use-guard.py 既有 block 語意（INV-GIT-002/003/004 與 secret 攔截一律不變）
- 課題 3 的 hook 警告（B 方案）以 spike 結果定去留——實測無有效回饋管道就放棄，不硬塞無效機制

Clarify-first: 使用者原始請求「將三個新課題一次解決」缺 success metric 與邊界（2/4 missing）→ 經 Plan Mode 探索 + 雙模型審查（Opus 自查 + Sonnet plan-reviewer REQUEST_CHANGES）修訂為 v2 計畫，2026-08-03 以 AskUserQuestion 裁定兩項範圍決策後定案。

Scope Baseline: target user=本模板專案的 harness 維護流程（所有未來 session）/ success metric=§5 驗收全項 PASS / trigger condition=使用者 2026-08-03 批准 v2 計畫並裁定範圍 / confirmation source=使用者 2026-08-03 選擇「A. 只遷 PR_RETRO（推薦）」+「合併一份 F-004（推薦）」。

## 2. Context

- 三課題同源：F-003 收尾 retro（ERRORS.md 行 32-52，2026-07-29）
- `agent_docs/TECHNICAL-REFERENCE.md` 仍未活化，依 CLAUDE.md Activation Status 略過章節錨點
- 受影響模組：`.claude/hooks/stop-retro-logger.py`、`scripts/retro-status.py`、`docs/learnings/ERRORS.md`、`.claude/tiers/src/` + 重建產物、`.claude/rules/model-dispatch.md`、`.claude/protocols/handoff-protocol.md`、`scripts/verify-branch-base.py`（新）、`.claude/hooks/pre-tool-use-guard.py`（視 spike）、`docs/architecture/invariants.md`（+ _zh 鏡像）、`state/SCHEMA.md`（+ _zh）、`CLAUDE.md` Quick Commands
- 審查發現的關鍵耦合（Sonnet plan-review 2026-08-03）：
  - stop-retro-logger.py:709,740 的 dedup 依賴 `existing_pending_hashes()` / retro-hashes.jsonl 帳本，遷移需重設計
  - handoff-protocol.md:19,63 明文「harvests into ERRORS.md Pending Review」，改後需同步
  - exit 0 + stderr 不回饋模型（guard docstring:20-23 自證），hook 警告需 spike 實測
  - merge-base == origin/master HEAD 的判定法對「master 已前進的正常分支」會誤報，需改 ancestor/fork-point 檢查

## 3. Constraints

- `INV-GIT-002`（禁 commit 到 master）、`INV-GIT-005`（新分支從 master 切出——本分支已驗證：merge-base == e0f379d == origin/master HEAD）
- `INV-SEC-003`：新腳本不讀寫 secret 路徑；全程 Python 3 標準庫
- `INV-ARC-001`（常駐層預算）：tier pack 新增內容後 `context-budget.py --tier strong` 仍須 PASS
- `INV-ARC-002`（完成聲明與勾選一致）：本檔 done 前 §4 全勾
- harness-maintenance.md 檔案分級：stop-retro-logger.py / pre-tool-use-guard.py 屬 **Red tier**（乾淨還原點 → 改 → fresh-context read-back → smoke test 雙情境）；tiers/src、rules、protocols、scripts 屬 **Yellow tier**（backup → 改 → read-back）
- 鏡像同步義務：invariants_zh.md、SCHEMA_zh.md、CLAUDE.md 相關段落改動需過 `check-mirror-parity.py`
- Fail-safe：stop-retro-logger 寫 state/ 失敗時不得阻斷 Stop 事件（維持 sentinel 語意，exit 0）

## 4. Step-by-step Plan

### Phase A — 課題 2：Agent 催收協議（文檔，零風險先行）
1. [x] `.claude/tiers/src/00-core-criteria.md` 加入催收協議骨架（訊號→動作格式，≤6 行）
2. [x] 跑 `python3 scripts/build-tier-packs.py` 重建三個 tier pack，`context-budget.py --tier strong` 確認預算 PASS（13988/14000，首版超標 302 字元後精簡）
3. [x] `model-dispatch.md` §6 全文參考版（+ agent_docs/zh 鏡像同步）
4. [x] `handoff-protocol.md` 補 idle 場景說明（含 [HUMAN_ATTENTION_REQUIRED: subagent-timeout] 用法）
5. [x] `check-mirror-parity.py` PASS（0 ERROR）；`check-doc-refs.py` 本次改動檔案零新增 ERROR（既存 9 ERROR 均在未觸碰檔案）

### Phase B — 課題 1：PR_RETRO 易變狀態遷移
6. [x] 修改 `stop-retro-logger.py`（Red tier）：`_append_retro_suggestion*` 改寫 `state/retro-reminders.jsonl`（session id 為 key 就地更新）；PR_RETRO 不再進 ERRORS.md 也不再記 retro-hashes.jsonl；docstring 與 COUPLING 註解同步
7. [x] 修改 `retro-status.py`：計數新增 reminders.jsonl 來源（獨立欄位 retro_reminders，Pending 計數維持 ERRORS.md）
8. [x] 清理 ERRORS.md：僅移除 4 個 PR_RETRO harvest 區塊，其餘 harvest 與人寫課題保留；Pending Review 頭注說明新去向
9. [x] `state/SCHEMA.md` + `SCHEMA_zh.md` 登記 retro-reminders.jsonl（§3f）；handoff-protocol.md:19,63 經查描述的是 VERIFY_FAILED/PROTOCOL_VIOLATION 收割（選項 A 下仍走 ERRORS.md）無需修改；另補 state/.gitignore 白名單 SCHEMA_zh.md（既存不一致）
10. [x] Smoke test 三情境 PASS：同 session 就地更新（count 2→3 單行）、新 session 新增行、ERRORS.md md5 不變；殘留 `_ledger_record` 呼叫由 smoke test 抓出並修除；retro-status.py 顯示「retro 提醒 N 條 (state/)」

### Phase C — 課題 3：Git 基底驗證
11. [x] 新建 `scripts/verify-branch-base.py`：post-fork commit ownership 檢查 + PASS/FAIL/WARN 三態 + 領先/落後距離輸出；master 已前進的正常分支不誤報
12. [x] 三情境以 `--self-test`（拋棄式 repo）機械驗證：fresh-cut=PASS / stacked=FAIL / aged=PASS；self-test 首輪即抓到「fork==tip 不代表 fresh cut」的演算法 bug 並修正；本 F-004 分支實跑 PASS（dogfooding）
13. [x] Spike 完成：exit 0 三管道中**僅 hookSpecificOutput.additionalContext 到達模型 context**（permissionDecisionReason 與 stderr 皆否，實測記錄見 §7 DEC-5）→ guard 新增 advisory（allow + additionalContext，不 block）；五情境 fixture smoke test PASS（advisory 觸發 ×2、不觸發 ×1、既有 block 語意迴歸 ×2）
14. [x] `invariants.md` INV-GIT-005 CHECK 改為 `python3 scripts/verify-branch-base.py`、HOOK 欄位更新為 guard advisory + code-reviewer（+ invariants_zh.md 同步）
15. [x] `CLAUDE.md` Quick Commands + 文件地圖行加 verify-branch-base（+ CLAUDE_zh.md 工具列同步）

### Phase D — 收尾
16. [x] 全量驗收 9/9 PASS（§5 acceptance block）+ fresh-context read-back 驗收 10/10 PASS（code-reviewer/sonnet，含兩 hook 實跑）
17. [x] ERRORS.md 課題條目補「已解決→F-004」註記（idle 與 checkout 兩條；易變狀態條文在未合併的 PR #17 分支上，master 無此條——PR #17 合併後由週審補註記或逕刪，見 §8 Q1）；feature-list.json 已登記 F-004
18. [ ] 開 PR、CI 綠、回填 Linked PR

## 5. Verification Strategy

```acceptance
lint-plan: python3 scripts/execplan-lint.py docs/plans/active/F-004-retro-triple-fix.md
budget: python3 scripts/context-budget.py --tier strong
mirror: python3 scripts/check-mirror-parity.py
doc-refs: python3 scripts/check-doc-refs.py
hook-coupling: python3 scripts/check-hook-doc-coupling.py
idle-in-packs: grep -l "idle" .claude/tiers/strong.md .claude/tiers/mid.md .claude/tiers/light.md
no-pr-retro-in-errors: grep -c "\[PR_RETRO\]" docs/learnings/ERRORS.md expect-fail
inv-git-005-check: grep "verify-branch-base" docs/architecture/invariants.md
verify-tool-selftest: python3 scripts/verify-branch-base.py --self-test
```
- Manual: smoke test（§4 步驟 10 / 12 / 13）的實跑輸出貼入 §6

## 6. Progress Log
- [2026-08-03] dev 分支 feat/f-004-retro-triple-fix 自 master(e0f379d) 切出並驗證基底；ExecPlan 建立
- [2026-08-03] dev Phase A 完成：tier pack 骨架 + model-dispatch §6（en/zh）+ handoff-protocol idle 場景；budget 13988/14000、mirror-parity 0 ERROR
- [2026-08-03] dev Phase B 完成：PR_RETRO 遷移至 state/retro-reminders.jsonl；smoke test 三情境 PASS 且抓出一個殘留呼叫；§6 精簡後 rules 576/600 行回到預算內
- [2026-08-03] dev Phase C 完成：verify-branch-base.py（self-test 抓到並修正 fork==tip 誤判）；spike 確認 additionalContext 為唯一有效管道；guard advisory + INV-GIT-005 機械化 + 文檔同步

## 7. Decision Log
- DEC-1: 遷移範圍採選項 A（只遷 PR_RETRO），使用者 2026-08-03 裁定——一次性 harvest 留 ERRORS.md 供週審，避免改造週審與 pr-retro skill
- DEC-2: 三課題合併單一 ExecPlan F-004，使用者 2026-08-03 裁定
- DEC-3: 課題 2 注入點為 tiers/src + 重建（rules 檔僅作全文參考）——F-003 後 rules 不再自動載入，寫錯層等於沒寫（Sonnet plan-review 確認）
- DEC-4: verify-branch-base 演算法棄用「merge-base == HEAD」改用 fork-point ancestor 檢查（Sonnet plan-review 指出誤報情境）
- DEC-5: hook 警告管道 spike 結論（2026-08-03 本 session 實測，方法：guard 加臨時分支對 SPIKE_F004_MARKER 同時發射三管道後實跑）——`hookSpecificOutput.additionalContext` 以 system-reminder 形式**到達模型 context**；`permissionDecisionReason` 與 exit 0 純 stderr **皆未到達**。故 B 方案採 additionalContext JSON 形式實作，非原計畫的 stderr（原計畫的 stderr 方案經證實無效，Sonnet 審查的質疑成立）

## 8. Open Questions
- Q1（非阻斷，交接給週審）：「易變狀態」課題的 ERRORS.md 條文只存在於 PR #17（chore/session-wrapup）分支，master 上沒有；F-004 已解決其描述的問題本身。PR #17 與本 PR 先後合併時 ERRORS.md Pending Review 區可能衝突——後合併者以「保留人寫課題、移除 PR_RETRO harvest 區塊」為解衝突原則，並替該條補上「已由 F-004 解決」註記

## 9. Handoff Manifest
- Next agent: dev（main conversation 續行 Phase A）
- Required reading before resuming: 本檔 + /Users/a17/.claude/plans/refactored-inventing-moler.md（v2 計畫全文）
- Current state marker: [HANDOFF: dev]
