# {{PROJECT_NAME}} — 累積教訓 (Lessons Learned)

> **角色**：本檔為 harness 體系的長期記憶，承接原 `CLAUDE.md` 的「累積教訓」區段。
> **總數**：18 條 Active（7 條原有 + 11 條 2026-07-29 週審 promote）
> **格式約定**：`- [YYYY-MM-DD] [<分類>] 錯誤描述 → 正確做法`
> 每次 AI 犯錯被糾正後，**必須**主動提議追加到 `## Pending Review`（由人類週審 promote 到 `## Active Lessons`）。
> `stop-retro-logger.py`（Phase D 啟用後）會自動把 session 內的 `[VERIFY_FAILED:*]` 收割到 Pending Review 區。

---

## 分類索引 (Category Index)

| 分類 | 對應條目數 | 對應 invariants.md |
|------|-----------|---------------------|
| Security / Auth | 0 | INV-SEC-* |
| API / Data Models | 0 | INV-API-* |
| Testing | 0 | INV-TEST-* |
| Git / Branch / PR | 1 | INV-GIT-* |
| Architecture | 6 | INV-ARC-* |
| Build / Dependencies | 0 | INV-BLD-* |
| Hooks / Harness | 11 | INV-HOOK-* |

---

## Pending Review

> 此區由 `stop-retro-logger.py` 自動 append 新 lesson candidate（Phase D 後）。
> 人類於每週收尾時手動 review，promote 到下方 `## Active Lessons`，或直接刪除無關的 noise。
> 週審提醒（/pr-retro 待辦）自 F-004 起改存 `state/retro-reminders.jsonl`（見 `state/SCHEMA.md` §3f），不再出現在本區。

（空 — 2026-07-04 週審已清空：PR_RETRO 提醒以手動 retro 處理，教訓 promote 至下方；hash f18510c79c 已記入 state/retro-hashes.jsonl 帳本，不會重生）

### [2026-07-29] retro | PR #14 feat/tiered-harness

以下三條是 PR #14 合併後 `/pr-retro` 分類分析的產出。本輪多數教訓已於過程中即時記錄並 promote，這三條是**當時沒被記下來的**。

### [2026-07-29] 子 agent 進入 idle 但沒回報，被誤判成「交件失敗」
- 情境：三個 fresh-context 查核 agent 派出後，只收到 idle 通知、沒有報告內容。我向使用者回報「委派的 agent 沒交報告」，改用機械腳本自行取證；兩次催收後三份報告全數送達，且指出 4 個真實 FAIL
- 錯誤：「還沒回報」與「回報失敗」是兩件事，我把前者當成後者，並且**已經對使用者說出口**。雖然改走機械驗證的產出本身有價值，但那是誤判之後的補救，不是當下的最佳選擇
- 教訓：agent 完成訊號不可靠時，先用 `SendMessage` 明確催收並等待，再判定失敗；在真的確認失敗之前，不要對使用者敘述成失敗。附帶：機械腳本與 agent 判斷是互補而非替代——本輪機械腳本抓到內容守恆，agent 抓到「路由檔沒有起手指示」這種只有讀者才看得出來的問題
- 建議去向：留在 ERRORS
- ↳ 2026-08-03 已由 **F-004** 制度化：催收協議進 tier pack 注入層（`.claude/tiers/src/00-core-criteria.md`）+ `model-dispatch.md` §6 全文版 + `handoff-protocol.md` idle 場景（`subagent-timeout` 標記）。本條已結案，下次週審可逕行刪除

### [2026-07-29] ExecPlan §4 勾選欄與 §6 進度紀錄可以長期互相矛盾，沒有任何閘門在看
- ↳ 2026-07-29 已升格為 **`INV-ARC-002`**（`docs/architecture/invariants.md`），機械化落在 `scripts/execplan-lint.py` 的 E7／W2 檢查項，已進 CI 與 acceptance。本條已結案，下次週審可逕行刪除

### [2026-07-29] `git checkout master && git checkout -b X` 前半失敗、後半照跑，分支從錯誤基底切出
- 情境：收尾時要從 master 切 `chore/f-003-closeout`。`git checkout master` 因 hook 自動更新的 ERRORS.md 未提交而失敗，但同一個 Bash 呼叫裡後續的建分支指令仍然執行，結果分支是從 `feat/tiered-harness` 切出來的（即使加了 `set -e`）
- 錯誤：`INV-GIT-005` 要求新分支必須從 master 切出，而這個違規**沒有任何機制會發現**——分支建立成功、沒有錯誤訊息，只有主動去查基底才看得到
- 教訓：`git checkout -b` 之後立刻驗證基底（`git log --oneline -1` 或與 `origin/master` 比對 tree），不要相信指令串的成功假象。本次是靠主動查證發現並修正（`git checkout -B <branch> origin/master`）
- 建議去向：留在 ERRORS；可機械化為 PreToolUse 對 `git checkout -b` 的 sentinel 提示，但會增加 Red-tier 改動，先送人審
- ↳ 2026-08-03 已由 **F-004** 機械化：`scripts/verify-branch-base.py`（commit ownership 演算法 + `--self-test`）+ guard 對 checkout -b / switch -c 的 additionalContext advisory（spike 證實為唯一有效 exit-0 管道），INV-GIT-005 的 CHECK 欄位已可執行。本條已結案，下次週審可逕行刪除

<!-- harvest:2eba92ba59 -->
- [2026-07-24T01:18:37+0000] [PROTOCOL_VIOLATION] **invalid handoff target 'acceptance PASS'**
  ```
  tion lines, `ERRORS.md:107-110`) ahead of the `## Active Lessons` header — no other lines touched.

Non-blocking suggestion: consider updating the acceptance-criteria snapshot timestamp when re-running this review later, since the hook continues to refresh the live entry.

[HANDOFF: acceptance PASS]
  ```

<!-- harvest:3265e9b964 -->
- [2026-07-24T02:36:31+0000] [UNCONFIRMED] **Replit Plan Mode是否支援計劃內逐步驟重排(僅查到「可見可審」,未查到重排功能證據)**
  ```
  。
5. 反例:Claude Code的Plan Mode雖是最貼近本專案六階段的硬性關卡設計,但執行呈現仍以終端/diff為主,證明「計劃關卡」與「非技術友善執行呈現」是兩個需分開設計的問題。

`[UNCONFIRMED: Replit Plan Mode是否支援計劃內逐步驟重排(僅查到「可見可審」,未查到重排功能證據)]`

<!-- harvest:9afdc30531 -->
- [2026-07-24T08:45:50+0000] [UNCONFIRMED] **Grok Build 官方 headless flag 語法**
  ```
  rok-oauth)
**Partial**:官方文件未直接列出 headless/`-p` flag 語法,hooks 相容性來自第三方文件(Hermes Agent)非 xAI 一手文件,標記 `[UNCONFIRMED: Grok Build 官方 headless flag 語法]`。
另有**社群版** `superagent-ai/grok-cli`(3.3k★,活躍,2026-07-06 仍在更新)早於官方版存在,MCP 支援 + `-p/--prompt` 非互動模式已確認。[repo](https://github.com/superagent-ai/grok-cli) / 
  ```

<!-- harvest:c26ac823ed -->
- [2026-07-24T08:45:50+0000] [UNVERIFIED_CITATION] **1 cited URL(s) never fetched/observed in-session**
  ```
  https://forum.cursor.com/t/cursor-cli-the-non-interactive-mode-cannot-be-used/143045
  ```

<!-- harvest:4487f40e9a -->
- [2026-07-28T09:38:29+0000] [VERIFY_FAILED] **D3 en/zh heading+table parity gaps and D4 one newly-introduced check-doc-refs.py ERROR in CLAUDE_zh.md:30**
  ```
  g docs/INDEX_zh.md headings and the CLAUDE_zh.md mirrors row for parity, even though pre-existing.

[VERIFY_FAILED: D3 en/zh heading+table parity gaps and D4 one newly-introduced check-doc-refs.py ERROR in CLAUDE_zh.md:30]
  ```

## Sources
- https://lovable.dev/blog/versioning-with-lovable-two-point-zero
- https://lovable.dev/faq/projects/version-history
- htt
  ```

## Active Lessons

> 依日期 descending 排列，分類標記在中括號中。

- [2026-07-29] [Hooks / Harness] 一條防線禁止的字串，正好是另一個 hook 賴以運作的字串 → 寫防線時要問「這條規則套在模板自己身上成不成立」，不是只問「套在使用這個模板的專案上成不成立」
  - **Why**：`placeholder-gate` 禁止新增 `{{`，但 BaseAIProject 就是模板，產出未填槽位正是它的本分；而 `session-activation-check.py` 又靠字面 `{{fill in` 判斷槽位未填。照 CI 的意思改字串會讓閘門變綠、同時靜默關掉每個 session 的活化提醒——拿看得見的紅燈換看不見的破洞
  - **How to apply**：閘門加窄門豁免並附負向測試（`{{TODO}}` 同行仍被抓）；hook 對文件的字面依賴一律加 `# COUPLING:` 宣告，由 `scripts/check-hook-doc-coupling.py` 強制

- [2026-07-29] [Hooks / Harness] 掃描器不區分「指令要執行這個東西」與「文字要描述這個東西」，同一家族第四次，這次真的擋下合法操作 → 內容掃描類防線設計時，豁免面要跟規則一起設計，而不是等誤報出現才補
  - **Why**：前三次（CI 閘門掃到自己、遙測收割器收到引用標記、check-doc-refs 把範例路徑當真）都只是噪音，於是都沒被機械化；第四次是寫 README 的 hooks 職責表——那張表按定義就得寫出 guard 擋什麼——被 guard 自己擋下
  - **How to apply**：`pre-tool-use-guard.py` 現在對寫入資料槽（`cat >`／`tee`／`git commit -F -`／`gh --body-file -`）的 heredoc body 不做指令掃描；直譯器讀取的 heredoc（`bash <<`、`python3 - <<`、任何帶 pipe 的）絕不豁免。依 security.md 用允許清單而非封鎖清單，擴充清單時必須同步擴充負向測試

- [2026-07-28] [Architecture] 英文正典改了、`_zh` 鏡像沒跟著改，於是中文讀者看到一個已被拆除的機制長達 8 個 commit → 改一份有鏡像的檔案，鏡像要在**同一個 commit** 內一起改
  - **Why**：現有閘門攔不到——`check-doc-refs.py` 查得出路徑存不存在，查不出「這句話描述的機制還在不在」。分兩次做等於承諾一個不會兌現的 TODO
  - **How to apply**：`scripts/check-mirror-parity.py` 比對每組鏡像的章節數、子章節數與表格列數（跨語言無法比文字，但比得了結構），ERROR 即 acceptance 失敗

- [2026-07-28] [Hooks / Harness] 驗收 agent 把難驗的準則自行換成好驗的近似物，然後回報原準則 PASS → 驗收報告的 PASS/FAIL 要連同「它實際用了什麼判準」一起讀
  - **Why**：委派時指定的是「逐條說明每條規則現在住在哪」，子 agent 自行改判成「檔案有沒有被刪」——照那個標準只要不刪檔就必然 PASS，等於完全沒驗。照單全收就會讓 5 條規範性規則靜默消失在一次號稱「只搬不刪」的重構裡
  - **How to apply**：委派時要求逐項列舉而非只給結論（本次正是這個要求逼出那份清單才撈回 5 條）；收到 PASS 先看證據形態對不對，再看結論

- [2026-07-28] [Hooks / Harness] 官方文件說 hook payload「optionally 帶 model 欄位」，實際完全不存在，同一失效家族第三次 → hook payload 的欄位一律以實測為準，文件只當線索
  - **Why**：前兩次是 SubagentStop 的 `transcript_path` 實為 `agent_transcript_path`；本次一批就抓到兩處（SessionStart 無 `model`、InstructionsLoaded 欄位名全錯）。照文件寫完才發現不對的代價，遠高於先實測
  - **How to apply**：新 hook 上線前先掛一個 20 行的 dump hook + 跑一次巢狀 `claude -p`，把真實 payload 印出來再寫邏輯（已列入 `harness-maintenance.md` §4）

- [2026-07-28] [Hooks / Harness] 把「帳本是空的」直接當成「採收器壞了」，差點修一個沒壞的東西 → 空帳本至少有三種成因（採收器壞、發射端沒發、輪替清掉），區分它們只需一次 end-to-end 測試
  - **Why**：0 筆是觀察到的現象，「採收器壞了」是未經驗證的推論，計畫書把兩者寫成同一件事。照著執行會去改一個功能正常的 Red-tier hook
  - **How to apply**：「不要相信任何未經黑箱測試的防禦」的鏡像同樣成立——不要相信任何未經黑箱測試的「壞掉」診斷；另外測試失敗時先驗證 fixture，寫錯的 fixture 造成的假陰性和真的壞掉現象一模一樣

- [2026-07-28] [Architecture] 把 SKILL.md 拆檔當成「降低常駐用量」的手段，但 skill 本體從來就不常駐 → 談 token 節省前先問「這段文字是什麼時候進 context 的」
  - **Why**：常駐（system prompt／hook 注入）、觸發時載入（skill body、參考檔）、完全不進（純人類文件），三者的節省手段與量測方式都不同。混在一起會做出量不到成效的工作
  - **How to apply**：拆 SKILL.md 仍然值得做，但效益歸在「單次調用少載多少」，不要掛在常駐預算指標下；常駐預算由 `INV-ARC-001` 與 `scripts/context-budget.py` 獨立把關

- [2026-07-23] [Hooks / Harness] `SubagentStop` 的 `transcript_path` 指向主對話，不是子代理 → hook payload 語意必須實證，不可從文件或直覺推定
  - **Why**：missing-marker 哨兵據此判定子代理結尾，造成系統性誤報（主對話文字被判違規）與漏報，已污染生產 ERRORS.md
  - **How to apply**：子代理輸出在 `agent_transcript_path`；同場加映——幻影中間 stop 要跳過、最終 stop 有寫入競態要有界重試、去重 hash 必含 `agent_id`、structured-output 型代理無結尾文字要豁免

- [2026-07-23] [Hooks / Harness] CI 閘門首跑掃到自己的實作與文件引用 → 內容掃描類閘門設計時先問「這條規則掃到自己會怎樣」，豁免面要跟規則一起設計
  - **Why**：secret-scan 的正則命中工作流自己的 `print("secret-scan: FAIL")`；placeholder-gate 的天真 `{{` 匹配命中 Actions 語法、偵測器的字面字串、文件反引號引用。此後又復發兩次（check-doc-refs 誤判、guard 誤攔）
  - **How to apply**：豁免面（路徑範圍、code-span 剝除、語法前綴、資料槽 vs 可執行段）與規則同時設計；修完 CI 除了 YAML lint 還要看 Actions 實跑，0 秒失敗＝workflow 檔問題；負向測試不可省

- [2026-07-23] [Hooks / Harness] 遙測收割器把報告中「引用」的示範標記當成真實事件寫入帳本 → 收割器必須區分真實發出的標記與文件中引用的範例
  - **Why**：`rule-events.jsonl` 帳本因此首次建立，首筆即假事件；被污染的遙測比沒有遙測更糟，因為它看起來像資料
  - **How to apply**：包在 code span／fence 裡的標記一律豁免（`stop-retro-logger.py` 已落地）

- [2026-07-07] [Architecture] 量測前沒核對「單位」與「範圍」兩者是否與對照標的一致，同一家族兩次 → 回報任何量測數字前，先確認單位與範圍都與觸發線的字面定義一致
  - **Why**：第一次把 CLAUDE.md 算進 rules 總量，誤報 663>600；第二次用 `wc -c`（bytes）當字元數，34,786 實為 32,739（中文 UTF-8 佔 3 bytes）。使用者曾基於錯誤數字做過裁決
  - **How to apply**：`wc -c`(bytes)／`wc -m`(chars)／`len()`(chars) 對 CJK 結果不同；`scripts/context-budget.py` 一律以 Unicode 字元計並在 `budget.json` 明寫 not bytes

- [2026-07-07] [Architecture] 抽取模板時 10 個 SKILL.md 從 97-394 行被靜默砍到 31-47 行，附檔全失，其中 8 個看起來像完整 skill → 抽取／移植文件集時產出「來源 vs 目標行數對照表」附在 commit
  - **Why**：「文件說有能力 ≠ 有能力」的 skill 版；沒有標記的縮水看起來和刻意精簡一模一樣
  - **How to apply**：行數低於來源 70% 的每一檔必須標註原因（刻意精簡／待補／stub）；無標記的縮水視為遺漏

- [2026-07-04] [Hooks / Harness] 驗收 subagent 超出指派範圍執行 `git checkout --` 與 `rm` 未追蹤檔案，誤刪使用者檔案（幸主對話 context 留有全文得以重建） → 派工 prompt 通用規範必須明文禁止對非指派檔案執行任何還原/刪除指令；驗收類 agent 原則上唯讀
  - **Why**：「只改指派檔案」的正面表述擋不住「為了測試而清理現場」的合理化；破壞性指令需要顯式黑名單
  - **How to apply**：delegation-templates.md 通用規範已加黑名單；未追蹤的使用者檔案不受 git 保護，刪除即永久

- [2026-07-04] [Hooks / Harness] hooks 部署後從未實測，雙重失效（無執行權限 + guard 用 exit 1）長期無人發現 → 任何 hook 新增/修改後必須跑黑箱煙霧測試：block 情境期望 exit 2、pass 情境期望 exit 0
  - **Why**：Claude Code hook 協議中 exit 1 只是警告、指令照跑；「文件宣稱有防線」與「防線存在」是兩回事，唯一的證據是實測 exit code
  - **How to apply**：照 `.claude/protocols/harness-maintenance.md` §4 的煙霧測試指令；fork 模板到新專案時列入 `docs/harness/NEW-PROJECT-VALIDATION.md` Step 1

- [2026-07-04] [Hooks / Harness] dedup hash 把 timestamp 算進輸入 → 永不判重，ERRORS.md 被同主體重複寫入 59 次 → hash 輸入只放事件本質欄位（類型/主體/來源），時間只留顯示用
  - **Why**：教訓檔被 noise 灌爆後，模型會停止信任並停止閱讀它，整條「踩坑→教訓→規則」管線壞死
  - **How to apply**：寫任何去重邏輯時檢查 hash 輸入清單；本次修法見 `stop-retro-logger.py:282-289` 註解

- [2026-07-04] [Architecture] 同一事實（模型分派表/agent 名單/review 格式）在多檔各存全文 → 9 處矛盾，弱模型隨機採信 → 每類事實指定唯一正典檔，其他位置只准引用不准另列全文
  - **Why**：複本必然各自演化；弱模型遇矛盾不會停下查證，行為因此不可預測
  - **How to apply**：正典層級表在 `CLAUDE.md`；發現複本即刪、留引用；`AI-TEAM-REGISTRY.md` 一律由 frontmatter 重生成不手改

- [2026-05-28] [Hooks / Harness] `QUICK_CHECKS` 空陣列讓 post-edit-lint 形同虛設 → 採用模板後第一件事是把專案的 INV-SEC/INV-ARC patterns 填入，否則 hook 掃不到任何問題
  - **Why**：BaseAIProject 初始化時 QUICK_CHECKS=[] 是為了讓模板通用，但實際部署時若不填充則 D3 分數只有 17/20，且安全漏洞無法被即時攔截
  - **How to apply**：每個新專案採用模板後，在 Phase 2 把 INV-SEC-001/002 patterns 填入 QUICK_CHECKS，再根據技術棧加入 INV-ARC/INV-API checks

- [2026-05-28] [Git / Branch / PR] AI 完成開發後沒有 `/pr-retro`，教訓沉入聊天歷史 → 每次 merge 後必須執行 `/pr-retro` 或依賴 `stop-retro-logger` 自動觸發收割
  - **Why**：SkillOpt 論文的核心訓練信號來自 failure trajectories；若不系統性收割，所有 PR 的改進機會都浪費掉，ERRORS.md 永遠空著
  - **How to apply**：在 `/last-word` 的 Step 3 或 session 結束前，確認本 session 是否有 git commit 活動，若有則執行 `/pr-retro`

- [2026-05-28] [Architecture] 不填 ExecPlan 就直接開始實作 → 複雜任務（跨 module / 涉及 API 變更）必須先有 ExecPlan §1-§5，才能進入 feat/ branch
  - **Why**：沒有 §5 Verification Strategy 就沒有 validation gate；沒有 gate 的實作在 review 時沒有標準，往往需要多輪修改
  - **How to apply**：ExecPlan 的觸發條件在 `docs/plans/PLANS.md §1` 中定義；bug fix < 3 檔案才可免 ExecPlan

---

## 引用此檔的位置

- `CLAUDE.md`：在累積教訓區塊以一行指標引用本檔
- `docs/architecture/invariants.md`：每條 invariant 引用此檔的對應 lesson
- `.claude/hooks/stop-retro-logger.py`（Phase D）：每次 SubagentStop / Stop 時 append 到 `## Pending Review`
