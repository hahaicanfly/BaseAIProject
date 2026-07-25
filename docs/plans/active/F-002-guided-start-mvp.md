# ExecPlan: F-002 — Guided-Start MVP (Tier B, non-technical accessibility)

| Field | Value |
|------|-----|
| Status | in_progress |
| Owner Agent | dev (main conversation) |
| Branch | feat/guided-start-mvp |
| Created | 2026-07-25 |
| Last Updated | 2026-07-26 |
| Linked PR | (filled in at merge time) |

## 1. Goal

為 BaseAIProject 新增縮小版 `/guided-start` 引導式入口指令與唯讀衍生工具 `scripts/translate-acceptance.py`,讓非技術背景使用者能以自然對話完成「需求收集 → 交還既有治理路由 → 驗收結果白話摘要」,中間的路由判斷與人審/執行三段完全複用既有機制、本指令不新增任何治理判準或裁決權。

Non-Goals / Out of Scope:
- 確認短語與錯誤復原機制(完整六階段的「確認執行」段落)——不在縮小版範圍。
- `.claude/commands/*.md` 的正式權限分級——harness-maintenance.md §1 表格無此列,本次類推當 Yellow tier 處理,不順帶補此 Red-tier 文件的空缺。
- README / CLAUDE.md 是否加一行指向 `/guided-start`——本次不加;`/guided-start` 是決策樹外的替代路徑,不取代現有入口。
- 雙向觸發測試法是否正式寫進 harness-maintenance.md §6 當標準方法——本次不修改 Red-tier 協議。
- `stop-retro-logger.py` 是否在寫入時多帶 `plan` 欄位以利精確 join——記入 ERRORS.md 當未來改善項,本次不做。
- 完整六階段的 `/guided-start`(人審調整、確認執行兩段)——待本次實際回饋後再決定。

Clarify-first: all 4 fields present via prior Plan Mode session plus AskUserQuestion confirmation, 2026-07-25(target user / success metric / trigger condition / non-goals 皆已於先前 Plan Mode 對話與 AskUserQuestion 中 confirmed,本次無新增待澄清項)。

Scope Baseline: target user=BaseAIProject 的非技術背景使用者 / success metric=`py_compile` 通過、以真實 F-001 fixture(`state/acceptance/F-001-harness-verifiability-batch.jsonl` + `docs/reviews/2026-07-22-f001-phase-c2.md`、`docs/reviews/2026-07-23-f001-phase-c3c4.md`)實跑輸出與原始結論一致、無對應 plan/空 jsonl 負向測試優雅降級、`check-doc-refs.py --all` 零新增 ERROR / trigger condition=使用者調用 `/guided-start` 指令 / confirmation source=使用者在對話中核准的 Plan Mode 計畫,2026-07-25。

## 2. Context

- 背景研究: `docs/research/2026-07-25-non-technical-accessibility.md` §3 定義 Tier B;PR 1(uiux 白話化 + agent 觸發詞)已合併,本 ExecPlan 為 PR 2。
- 受影響既有機制(皆為複用、不重寫):
  - Commands 慣例:仿 `.claude/commands/last-word.md`、`.claude/commands/techdebt.md`(無 YAML frontmatter、純 markdown prompt、Step 段落結構、結尾 References)。
  - 路由判準來源(本指令即時讀取、不複製):`CLAUDE.md`「Decision Tree Before Acting」、`.claude/rules/clarify-first.md` §1(4 欄位)、`.claude/rules/plan-first.md` Exceptions、`.claude/protocols/execplan-lifecycle.md`。
  - Scripts 慣例:仿 `scripts/check-doc-refs.py`、`scripts/acceptance-run.py`(各自獨立、不 import 共用模組);複用 `acceptance-run.py` 既有 Summary / expect-fail 措辭;`review-protocol.md` 燈號行與 VERDICT 行解析(需同時吃 `**VERDICT: PASS**` 粗體無路徑、與 `VERDICT: FAIL <path>` 無粗體帶路徑兩種既有格式)。
  - 資料來源 schema:`state/SCHEMA.md` §4d(`state/acceptance/<stem>.jsonl`);`state/verifications.jsonl`(無 `plan` 欄位,採檔名子字串啟發式比對)。
- Registry: `agent_docs/AI-TEAM-REGISTRY.md` Commands 表需新增 `/guided-start` 一列。
- Related ADR: 無新 ADR;上位決策見 `docs/decisions/ADR-0001-adopt-harness-engineering.md`。Related past PRs: PR 1(Tier B 第一階段,已合併)。

## 3. Constraints

- Invariants(`docs/architecture/invariants.md`,目前僅 INV-GIT-001~005、INV-SEC-001~003):
  - INV-GIT-002 / INV-GIT-001:於分支 `feat/guided-start-mvp` 提交,提交前 `git branch --show-current`,絕不直接提交 master/main。
  - INV-GIT-005:分支自最新 master 切出。
  - INV-SEC-001 / INV-SEC-002 / INV-SEC-003:`translate-acceptance.py` 全程唯讀開檔、無任何寫入路徑,不硬編 key/token,不在 print/log 輸出敏感字,不 stage 敏感檔。
  - (INV-TEST / INV-API / INV-ARC / INV-BLD 在本專案為未活化模板,不套用;不編造不存在的 INV。)
- File-tier 處理(`harness-maintenance.md` §1,本次涉及的兩類皆無正式 tier,依「有疑慮從嚴」原則類推從嚴):
  - `.claude/commands/guided-start.md`:表格未列 `.claude/commands/`,本次類推當 Yellow tier——先確保 clean git tree(或 `cp` 備份)、編輯後派 fresh-context agent read-back 驗證。其 zh 鏡像 `agent_docs/zh/commands/guided-start.md` 屬 `agent_docs/*`,明確為 Yellow tier。
  - `scripts/translate-acceptance.py`:新增檔,`scripts/` 未列於表格,同樣類推當 Yellow tier 處理(備份/驗證流程照 §4)。
  - `agent_docs/AI-TEAM-REGISTRY.md`:Yellow tier,依 §4 備份 + read-back。
  - 本次不觸碰任何 Red-tier 檔案(不改 CLAUDE.md、`.claude/rules/*`、`.claude/protocols/*`、invariants.md、hooks)。
- Domain impact: `docs/architecture/domains.md` 為未活化模板,無可對應的 change-impact 列,故不適用(不套用通用前後端分層)。
- ERRORS.md hits: 本次無既有教訓直接對應;`stop-retro-logger.py` 缺 `plan` 欄位一項將於執行時新增為 Pending Review 條目(見 §1 Non-Goals)。

## 4. Step-by-step Plan

- [ ] 1. Baseline:自最新 `master` 切 `feat/guided-start-mvp`(INV-GIT-005);確認 `git branch --show-current` ≠ master 且工作樹乾淨(Yellow-tier 依賴 clean tree 作回滾點)。確認三個 fixture 存在:`state/acceptance/F-001-harness-verifiability-batch.jsonl`、`docs/reviews/2026-07-22-f001-phase-c2.md`、`docs/reviews/2026-07-23-f001-phase-c3c4.md`。_Verify_:分支名正確、三檔 `ls` 皆在。
- [ ] 2. 撰寫 `.claude/commands/guided-start.md`(仿 `last-word.md`:無 YAML frontmatter、開場 prose + `## Step N` 段 + 結尾 `## References`)。五段內容:
  - Step 0(自動偵測接續):掃 `docs/plans/active/F-*.md`,若有進行中 ExecPlan 且對話像接續 → 跳 Step 4;不確定時明講一句問使用者確認,不靜默假設。
  - Step 1-2(需求收集):一句話覆誦已知意圖 → 即時讀取 `.claude/rules/clarify-first.md` §1 四欄位(target user / success metric / non-goals / trigger),不複製其判準 → 分批 1-2 題 `AskUserQuestion`,已知不重問;若已符合 `.claude/rules/plan-first.md` Exceptions → 跳過 Step 3 直接執行。
  - Step 3(路由防線):逐字讀取 `CLAUDE.md`「Decision Tree Before Acting」本文做路由,本指令不自帶任何判準、只翻譯呈現層 → 把控制權交還對應分支(ExecPlan / Plan Mode / 直接做),不追蹤後續進度。
  - Step 4(驗收白話):呼叫 `scripts/translate-acceptance.py`,把結果套進 `CLAUDE.md` 既有 Done/Next/Note 三行模板並連結真實證據檔路徑。
  - References:指向 `clarify-first.md` / `CLAUDE.md` / `plan-first.md` / `execplan-lifecycle.md` / `translate-acceptance.py` / `review-protocol.md`。
  - _Verify_:首行非 `---`(無 frontmatter);grep 命中 `## Step 0`、`## Step 1`、`## Step 3`、`## Step 4`、`## References`;fresh-context agent read-back(Yellow-tier)。
- [ ] 3. 撰寫中文鏡像 `agent_docs/zh/commands/guided-start.md`——與 EN 逐段對應。_Verify_:`## Step N` 段數與 EN 一致;read-back 核對無漏段/漏 References。
- [ ] 4. 撰寫 `scripts/translate-acceptance.py`(唯讀衍生工具,仿 `check-doc-refs.py`/`acceptance-run.py`、不 import 共用模組):
  - CLI:`plan`(positional,可省略取 active/ 最新 `F-*.md`)、`--review <file>`、`--json`;exit code 恆為 0;全程唯讀開檔、無寫入路徑(INV-SEC-*)。
  - acceptance:讀 `state/acceptance/<stem>.jsonl` 取每 label 最後一筆 → emoji 化 + 複用 `acceptance-run.py` 的 `Summary: N total…` 與 expect-fail 措辭(不重寫白話邏輯);無 jsonl → 明講「尚無驗收紀錄」不捏造。
  - review:讀 `docs/reviews/<file>.md` 抓 `review-protocol.md` 燈號行(🟢/🟡/🔴)與 `VERDICT` 行(需同時支援 `**VERDICT: PASS**` 粗體無路徑、與 `VERDICT: FAIL <path>` 無粗體帶路徑兩種既有格式);抓不到燈號 → 明講「此報告無白話層,以下為技術原文摘錄」。
  - join:`state/verifications.jsonl` 無 `plan` 欄 → 檔名子字串啟發式比對,找不到明確對應時明講但書;`--review` 可明確指定跳過猜測。
  - _Verify_:見 §5 acceptance block。
- [ ] 5. 更新 `agent_docs/AI-TEAM-REGISTRY.md` Commands 表新增 `/guided-start` 一列。_Verify_:grep `/guided-start` 命中該表;read-back。
- [ ] 6. 跑 §5 全部 acceptance + Manual golden path;全綠後結尾 `[HANDOFF: code-reviewer]`。

## 5. Verification Strategy

```acceptance
compile: python3 -m py_compile scripts/translate-acceptance.py
fixture-acceptance: python3 scripts/translate-acceptance.py docs/plans/completed/F-001-harness-verifiability-batch.md
fixture-review: python3 scripts/translate-acceptance.py docs/plans/completed/F-001-harness-verifiability-batch.md --review docs/reviews/2026-07-23-f001-phase-c3c4.md
fixture-json: python3 scripts/translate-acceptance.py docs/plans/completed/F-001-harness-verifiability-batch.md --json
negative-graceful: python3 scripts/translate-acceptance.py docs/plans/active/zzz-no-such-plan.md
doc-refs-plan: python3 scripts/check-doc-refs.py --file docs/plans/active/F-002-guided-start-mvp.md --strict
doc-refs-all: python3 scripts/check-doc-refs.py --all --strict
```

- 每個 fixture 路徑皆為 repo 內實存檔:F-001 plan 已歸檔於 `docs/plans/completed/`;`state/acceptance/F-001-harness-verifiability-batch.jsonl` 最後一輪(ts `2026-07-22T16:21:05Z`)四 label 全 pass;`docs/reviews/2026-07-23-f001-phase-c3c4.md` 帶 `**VERDICT: PASS**`,`docs/reviews/2026-07-22-f001-phase-c2.md` 帶 `VERDICT: FAIL <path>`(兩種 VERDICT 格式都能驗)。
- `translate-acceptance.py` exit code 恆 0,故 `fixture-*` 與 `negative-graceful` 的 PASS 語意 = 未崩潰、優雅執行(輸出內容正確性由下方 Manual 人工核對);`negative-graceful` 傳不存在的 plan → 仍 exit 0 即證明降級不崩潰,無需 expect-fail。
- `doc-refs-*` 加 `--strict` 才會在任一 ERROR 級發現時 exit 1;基線為 0 ERROR(2026-07-23 報告確認),故此二行等同「零新增 dead-ref」的機械閘門(`--file` 保 F-002 plan 自身引用、`--all` 保新 command 檔與 zh 鏡像)。
- Manual golden path:
  - G1 Step 0 接續:`active/` 有進行中 `F-*` 時觸發 → 應偵測並提議跳 Step 4(不確定時問一句確認);`active/` 無進行中 → 進 Step 1。
  - G2 需求收集:丟一句模糊需求(例「加一個匯出功能」)→ 確認即時讀 `clarify-first.md` §1 四欄位、分批 1-2 題 `AskUserQuestion`、不重問已知;符合 `plan-first` Exceptions 時跳過 Step 3。
  - G3 路由防線:確認 Step 3 逐字引用 `CLAUDE.md` Decision Tree 做路由、不自帶判準,並把控制權交還對應分支。
  - G4 驗收白話(happy path):對 F-001 fixture 跑腳本,人工核對 emoji 化摘要與 jsonl 每 label 最後一筆一致、Done/Next/Note 三行連到真實證據檔;`--review` 指向 c3c4 時正確抓 `**VERDICT: PASS**`,並因該報告無 🟢/🟡/🔴 燈號行而明講「無白話層、以下為原文」不捏造(以 c2 報告 `VERDICT: FAIL <path>` 另驗 FAIL 變體)。
  - G5 優雅降級 + 唯讀:對無對應 jsonl 的 plan、及空 jsonl(scratchpad 造)各跑一次,確認輸出但書而非崩潰/捏造;`git status` 驗收前後逐行一致(證實無寫入副作用)。
  - G6 Yellow-tier read-back:fresh-context agent 讀回 `guided-start.md`(EN+zh)與 REGISTRY 新列,逐項對照 §4。

## 6. Progress Log

- [2026-07-25 00:00] main conversation(dev):plan drafted via pm → architect → plan-reviewer pipeline(Workflow tool),assembled into this file,pending human approval(Phase 3 gate).
- [2026-07-26 00:00] main conversation(dev):使用者核准(Phase 3 human approval gate passed),開 `feat/guided-start-mvp` 分支,建立 `state/feature-list.json` 骨架(F-002, in_progress),進入 Phase 4 實作。

## 7. Decision Log

- DEC-1:採縮小版 `/guided-start`(需求收集 + 驗收白話摘要),不重寫人審調整/確認執行,因為重新實作會產生第二條治理路由來源、與 `plan-first.md`/`execplan-lifecycle.md` 既有判準分裂風險。使用者於 Plan Mode 階段以 AskUserQuestion 核准此範圍(2026-07-25)。
- DEC-2:Step 0 採自動偵測(而非要求使用者明講)是否接續進行中的 ExecPlan,使用者於 Plan Mode 階段核准(2026-07-25)。
- DEC-3:`translate-acceptance.py` exit code 恆為 0(格式轉換工具,非判定閘門),避免使其看起來擁有裁決權。

## 8. Open Questions

- Q1:`state/feature-list.json` 目前不存在(state/ 下無此檔)。Phase 4 開分支時依 `docs/plans/PLANS.md` §5 慣例需新增/更新此 ledger 條目,§4 未列出建檔步驟——留待 Phase 4 執行時視情況建立最小骨架,不在此次 Phase 1-3 起草階段處理。

## 9. Handoff Manifest

- Next agent: 使用者(human reviewer,Phase 3 approval gate)
- Required reading before resuming: 本檔全文;`docs/research/2026-07-25-non-technical-accessibility.md` §3-4;已核准的 Plan Mode 計畫(`/Users/a17/.claude/plans/mellow-pondering-sparkle.md`)
- Current state marker: [HANDOFF: human-approval]
