# {{PROJECT_NAME}} — 累積教訓 (Lessons Learned)

> **角色**：本檔為 harness 體系的長期記憶，承接原 `CLAUDE.md` 的「累積教訓」區段。
> **總數**：3 條（seed lessons — 採用此模板時通用教訓）
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
| Architecture | 1 | INV-ARC-* |
| Build / Dependencies | 0 | INV-BLD-* |
| Hooks / Harness | 1 | INV-HOOK-* |

---

## Pending Review

> 此區由 `stop-retro-logger.py` 自動 append 新 lesson candidate（Phase D 後）。
> 人類於每週收尾時手動 review，promote 到下方 `## Active Lessons`，或直接刪除無關的 noise。

_(空)_

---

## Active Lessons

> 依日期 descending 排列，分類標記在中括號中。

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
