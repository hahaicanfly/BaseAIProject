# {{PROJECT_NAME}} — 累積教訓 (Lessons Learned)

> **角色**：本檔為 harness 體系的長期記憶，承接原 `CLAUDE.md` 的「累積教訓」區段。
> **總數**：7 條（3 條 seed + 4 條 2026-07-04 harness 制度化 session 實戰教訓）
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
| Architecture | 2 | INV-ARC-* |
| Build / Dependencies | 0 | INV-BLD-* |
| Hooks / Harness | 4 | INV-HOOK-* |

---

## Pending Review

> 此區由 `stop-retro-logger.py` 自動 append 新 lesson candidate（Phase D 後）。
> 人類於每週收尾時手動 review，promote 到下方 `## Active Lessons`，或直接刪除無關的 noise。

（空 — 2026-07-04 週審已清空：PR_RETRO 提醒以手動 retro 處理，教訓 promote 至下方；hash f18510c79c 已記入 state/retro-hashes.jsonl 帳本，不會重生）

### [2026-07-07] 觸發線量測把 CLAUDE.md 一起算入 rules 總量，誤報 663>600 超線
- 情境：round-4 吸收機制後檢查 harness-maintenance §5 的 rules 600 行觸發線
- 錯誤：統計指令寫成 `wc -l CLAUDE.md .claude/rules/*.md`，把 84 行的 CLAUDE.md 算進 rules 總量，回報 663>600；實際 rules 只有 579，未破線。使用者基於錯誤數字核可了降級提案（後已重問並確認照做）
- 教訓：對照觸發線前先核對量測範圍與觸發線定義逐字一致（§5 寫的是「`.claude/rules/*` 總量」，不含 CLAUDE.md——CLAUDE.md 有自己獨立的 100 行線）
- 建議去向：留在 ERRORS

### [2026-07-07] 模板抽取時 10 個 skill 被靜默大綱化，其中 2 個標 stub、8 個無任何標記
- 情境：使用者發現多個 skills 內容空泛，回查母專案 Menu-Android 比對
- 錯誤：抽取模板時 10 個 SKILL.md 從 97-394 行砍到 31-47 行（如 security-audit 302→40），附檔（security-audit references ×4、ui-ux-pro-max scripts+data ×27）完全遺漏；僅 frontend-design/ui-ux-pro-max 標了 stub，其餘 8 個看起來像完整 skill，實為空殼——「文件說有能力 ≠ 有能力」的 skill 版
- 教訓：抽取/移植文件集時產出「來源 vs 目標行數對照表」附在 commit，行數低於來源 70% 的每一檔必須標註原因（刻意精簡/待補/stub）；無標記的縮水視為遺漏
- 建議去向：留在 ERRORS；若 fork 流程文件化，把「對照表」寫進 NEW-PROJECT-VALIDATION.md 檢查項

<!-- harvest:5fbf09ba9a -->
- [2026-07-21T15:04:20+0000] [PR_RETRO] **本 session 有 6 個 git commit，建議執行 `/pr-retro` 萃取教訓**
  Session: 645b493e-20af-4689-9546-e5ddba056a8f






<!-- harvest:8056eb8b94 -->
- [2026-07-22T15:46:35+0000] [PR_RETRO] **本 session 有 11 個 git commit，建議執行 `/pr-retro` 萃取教訓**
  Session: 077d3a3f-6205-409d-99de-bf82c10d766e
  ↳ 2026-07-23 /last-word 已完成本 session（PR #2+#3, 共 20 commits）的 retro：教訓見下方兩條 2026-07-23 條目；同 session 較早的 count=2/4 過時提醒與已解決的 C2 驗收三條目（VERIFY_FAILED/PROTOCOL_VIOLATION/ACCEPTANCE_FAIL，全文存 docs/reviews/2026-07-22-f001-phase-c2.md 與 commit 29b6663 訊息）已清理

### [2026-07-23] 提案:harness-maintenance §6 增設「Standing Rule」第三類品質閘門(該檔 §8 為 Red tier 不得自行修改,依規記錄於此送人審)
- ↳ 2026-07-23 人審裁決:同意採納,條文已寫入 harness-maintenance.md §6 第三類「Standing Rule」閘門(EN/zh 鏡像與 README 品質關卡列同步);提案全文見 git 歷史。本條已結案,下次週審可逕行刪除

### [2026-07-23] SubagentStop 的 transcript_path 指向主對話——hook payload 語意必須實證,不可從文件或直覺推定
- 情境:PR #2 的 missing-marker 哨兵讀 payload 的 transcript_path 判定子代理結尾,造成系統性誤報(主對話文字被判違規)與漏報,已污染生產 ERRORS.md
- 教訓:SubagentStop 的子代理輸出在 `agent_transcript_path` 欄位(官方 hooks 文件未記載;claude-code-guide 查文件還猜錯方向);修法前先在 hook 內 dump 一次真實 payload 再寫邏輯。同場加映:有 transcript 檔不存在的「幻影中間 stop」要跳過、最終 stop 偶有寫入競態要有界重試、每個子代理各觸發一次所以去重 hash 必含 agent_id、structured-output 型代理無結尾文字要豁免
- 建議去向:留在 ERRORS;機械防護已落地(stop-retro-logger 缺欄位即跳過並記 no-agent-transcript-*)

### [2026-07-23] CI 閘門首跑掃到自己:掃描器必須豁免自身與引用性內容;Actions 連註解裡的 ${{ }} 都會求值
- 情境:harness-gates 首次實跑兩個 job 全掛——secret-scan 的 print-洩漏正則命中工作流自己的 `print("secret-scan: FAIL")`(job 名含 secret);placeholder-gate 的天真 `{{` 匹配命中 Actions 表達式語法、佔位符「偵測器」的字面字串、文件反引號引用;修復時註解裡寫了字面空表達式,又造成 workflow 解析 0 秒失敗(一般 YAML 驗證器驗不出,只有 Actions 表達式層會拒絕)
- 教訓:(a) 內容掃描類閘門設計時先問「這條規則掃到自己的實作/文件引用時會怎樣」,豁免面(路徑範圍、code-span 剝除、語法前綴)要跟規則一起設計;(b) 修 CI 後除了 YAML lint 還要看 Actions 實跑(或用 actionlint),0 秒失敗=workflow 檔問題;(c) 負向測試不可省——豁免加寬後要證明真違規仍會被抓
- 建議去向:留在 ERRORS;若未來引入 actionlint 可將 (b) 機械化為 CI job

## Active Lessons

> 依日期 descending 排列，分類標記在中括號中。

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
