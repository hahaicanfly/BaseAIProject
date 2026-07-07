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

### [2026-07-07] 模板抽取時 10 個 skill 被靜默大綱化，其中 2 個標 stub、8 個無任何標記
- 情境：使用者發現多個 skills 內容空泛，回查母專案 Menu-Android 比對
- 錯誤：抽取模板時 10 個 SKILL.md 從 97-394 行砍到 31-47 行（如 security-audit 302→40），附檔（security-audit references ×4、ui-ux-pro-max scripts+data ×27）完全遺漏；僅 frontend-design/ui-ux-pro-max 標了 stub，其餘 8 個看起來像完整 skill，實為空殼——「文件說有能力 ≠ 有能力」的 skill 版
- 教訓：抽取/移植文件集時產出「來源 vs 目標行數對照表」附在 commit，行數低於來源 70% 的每一檔必須標註原因（刻意精簡/待補/stub）；無標記的縮水視為遺漏
- 建議去向：留在 ERRORS；若 fork 流程文件化，把「對照表」寫進 NEW-PROJECT-VALIDATION.md 檢查項

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
