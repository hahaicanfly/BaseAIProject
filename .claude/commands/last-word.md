主動 Context 收尾工作流。在 context usage 接近上限前，主動做一次高品質歸檔，確保下次 session 能無痛續接。

觸發時機：context usage 約 40%、使用者準備離開 session、或一個大任務階段性完成。
**硬性門檻（CLAUDE.md MUST: PHASE HANDOFF GATE）**：階段完成（功能 / Phase N / Mx）進下一任務前，若 context 用量 >50%，**必須**先跑本指令產出 `SESSION-HANDOFF.md`，再 `/clear`，然後讀檔以新 session 續接。

> **Phase D 升級**：本指令已對齊 harness 架構。教訓不再寫進 CLAUDE.md，而是分流到 `docs/learnings/ERRORS.md`、`docs/architecture/invariants.md` 與 active ExecPlan。Auto-memory 仍可保留**短期 session 狀態**，但**長期脈絡走 ExecPlan**。

---

請依照以下 8 個步驟逐一執行，每個步驟完成後簡要回報。**禁止跳步**——harness session 收尾的可審核性比速度更重要。

## Step 1: 回顧對話 + 識別 marker

回顧整個 session 的對話內容，提取四類資訊：

| 類型 | 範例 | 後續去向 |
|------|------|---------|
| **卡點 / 教訓** | 「修了一上午才發現某 bug」 | `docs/learnings/ERRORS.md` 或 `invariants.md` |
| **有效做法 / pattern** | 「抽出 base fake 一次解決所有 stub」 | 同上（標 success pattern）|
| **未完成工作** | 「F-NNN ExecPlan §4 step 3 還沒驗證」 | 對應 ExecPlan §6 + §9 |
| **Session 內主動 marker** | `[VERIFY_FAILED:*]` / `[HUMAN_ATTENTION_REQUIRED:*]` 紀錄 | 等 `stop-retro-logger.py` 自動 harvest（or 手動補） |

## Step 2: 教訓分流歸檔（取代舊 CLAUDE.md 累積教訓）

依下表把 Step 1 的 finding 寫到正確位置：

| 判斷條件 | 歸檔位置 | 操作 |
|---------|---------|------|
| 可機械驗證（grep / lint pattern 可寫） | `docs/architecture/invariants.md` | 加一條 INV-`<NS>`-`<NNN>`，標 CHECK / HOOK / SOURCE（invariants.md 屬紅級，見 `harness-maintenance.md` §1，寫入前需提示使用者確認） |
| 不可機械驗證但通用（design-level） | `docs/learnings/ERRORS.md` `## Pending Review` | 用 `<!-- harvest:HASH -->` 包，等下週 promote |
| 與**特定 feature 設計決策**有關 | 對應 `docs/plans/active/F-NNN.md` §7 Decision Log | 一行 summary + 必要時升級為 ADR |
| 已在 git commit / GitHub issue 追蹤 | **不存** | 避免重複噪音 |
| Session 一次性狀態（如「F-NNN 做到 step 3」） | Auto-memory **或** ExecPlan §6 Progress Log | ExecPlan 優先；memory 僅補無 ExecPlan 的暫態 |

**實際執行歸檔**（編輯 `docs/learnings/ERRORS.md`、`docs/architecture/invariants.md`、active ExecPlan 段落，**不要動 CLAUDE.md**）。

> CLAUDE.md 是「地圖」（≤150 行），不再是教訓堆放處。

## Step 3: ExecPlan 進度同步

對 session 中觸碰過的每一份 `docs/plans/active/F-NNN-*.md`：

1. 在 §6 Progress Log append 一行 summary（含 timestamp + agent + 一句話）
2. 在 §9 Handoff Manifest 更新 `Current state marker`：
   - 全部完成 → `[HANDOFF: code-reviewer]` / `[HANDOFF: human-pr-review]` / `[HANDOFF: done]`
   - 有 invariant 違反未修 → `[VERIFY_FAILED: <INV-id>]`
   - 卡在外部依賴 → `[HUMAN_ATTENTION_REQUIRED: <reason>]`
3. 如 status 有變更，同步 `state/feature-list.json`（若該檔存在）

如果整個 session 都不在 ExecPlan 範疇（純探索 / 純文件 / hot-fix < 3 檔案），跳過此步驟。

## Step 4: 交接 prompt → 寫入 `SESSION-HANDOFF.md`（給下一個 session）

如果 session 結束時還有未完成工作，**用 Write 工具把下列交接 prompt 寫入專案根目錄的 `SESSION-HANDOFF.md`**（覆寫舊內容，此檔為單一 session 的暫態交接區，不累積）。這是「階段交接門檻」（CLAUDE.md MUST: PHASE HANDOFF GATE）的落地產物——使用者 `/clear` 後會直接讀此檔以新 session 續接。

`SESSION-HANDOFF.md` 內容範本：

```
# SESSION-HANDOFF — <YYYY-MM-DD HH:MM>

> 由 /last-word 產出。`/clear` 後請讀本檔續接；續接完成後本檔可刪或被下次 /last-word 覆寫。

## 交接 prompt（直接貼上即可續接）

我正在進行 [F-NNN — 功能名]（ExecPlan: docs/plans/active/F-NNN-<slug>.md）。

**已完成（§6 Progress Log 最新一筆）：**
- [...]

**待完成（§4 Step 標記未打勾）：**
- [...]

**當前 marker：** [HANDOFF: <next>] 或 [VERIFY_FAILED: <INV-id>]

**接手 SOP：**
1. 讀 ExecPlan §3 Constraints + §9 Handoff Manifest
2. 確認 git branch（應為 `feat/<slug>`）
3. 從 §4 step <N> 開始

**相關資訊：**
- Branch: `feat/<slug>`（最新 commit: <hash>）
- Linked PR: #<NNN> 或 (尚未開 PR)
- 相關 invariants：INV-... / INV-...

## 本次歸檔摘要
- invariants.md 新增：INV-... × N
- ERRORS.md Pending Review 新增：N 條
- ExecPlan 更新：F-NNN（§6 + §9）
```

寫檔後在對話中回報 `SESSION-HANDOFF.md` 路徑。如果所有工作都已完成，跳過此步驟、**不產生** `SESSION-HANDOFF.md`，並改輸出「無待續事項」。

## Step 5: GitHub Issue / PR 整理

- 檢查本次 session 涉及的 GitHub issues / PR
- 確認 issue 狀態（open / closed）與實際程式碼進度一致
- 如有完成但未關閉的 issue，提醒使用者
- ExecPlan 已 merge → 從 `docs/plans/active/` 移到 `docs/plans/completed/` 並更新 `state/feature-list.json`

## Step 6: 清理 stale 內容

掃描以下三處：

| 檔案 | 清理重點 |
|------|---------|
| `docs/learnings/ERRORS.md` `## Pending Review` 區 | promote 已驗證可用的 lesson 到 `## Active Lessons`；刪除 noise |
| `docs/plans/active/` | 已停滯 > 4 週的 ExecPlan 標記 BLOCKED 或移到 completed/ + 加 Rejection Reason |
| Auto-memory | 移除 ExecPlan 已記載 / git 已追蹤的 暫態 |
| Claude Code 原生 memory（專案 memory 目錄） | 已 promote 進 ERRORS.md/invariants 的內容，從 memory 檔刪除、只留指標 |

**禁止**清理 `docs/architecture/invariants.md` —— 一條 INV 一旦立過就保留。
**禁止**動 CLAUDE.md —— 該檔已是壓縮地圖，內容由 ADR 流程管控。
保守原則：不確定是否過期 → 留著。

## Step 7: 檢查 uncommitted changes + branch

執行：
```bash
git status
git branch --show-current
```

確認：
- 沒有 staged 但未 commit 的修改
- 沒有重要的 unstaged 修改被遺忘
- 當前 branch **不為 master/main**（INV-GIT-001 / INV-GIT-002）
- 若有 uncommitted changes，**提醒使用者先 commit 再 /clear**

## Step 8: 收尾報告 + 安全 /clear 確認

完成所有步驟後向使用者回報：

```
✓ 教訓歸檔：
  - invariants.md 新增：INV-... × N
  - ERRORS.md Pending Review 新增：N 條
  - ExecPlan 更新：F-NNN（§6 + §9）

✓ Starter Prompt：[已輸出 / 不需要]

✓ Git 狀態：
  - Branch: feat/<slug>
  - Uncommitted: <檔案數>（需 commit / clean）

→ 是否可以安全執行 /clear：[YES / NO（請先處理 ...）]
```

最終以 harness marker 收尾：
- 全程無 issue → `[HANDOFF: next-session]`
- 有未解決 → `[HUMAN_ATTENTION_REQUIRED: <reason>]`

---

## 與 stop-retro-logger.py 的關係

`/last-word` 是**主動式人工收尾**；`stop-retro-logger.py`（Phase D sentinel）是**被動式自動 harvest**。兩者**互補不重複**：

| 觀察 | `/last-word` 處理 | `stop-retro-logger.py` 處理 |
|------|-------------------|------------------------------|
| `[VERIFY_FAILED:*]` 在對話中出現 | 結構化分類 + 必要時升級 invariant | 自動原文 append 到 Pending Review |
| 對話中明顯但無 marker 的 lesson | 由 agent 主動識別歸檔 | 不處理（無 marker 抓不到） |
| ExecPlan §6 / §9 更新 | 必須做 | 不做 |
| Auto-memory 清理 | 評估後執行 | 不做 |

> **建議使用順序**：先跑 `/last-word`（結構化收尾），再讓 session 自然結束（觸發 stop-retro-logger 自動 harvest 漏網 marker）。

---

## 參考

- `.claude/protocols/handoff-protocol.md` — 三種 marker 規範
- `.claude/protocols/execplan-lifecycle.md` — ExecPlan 10 階段
- `docs/plans/PLANS.md` — ExecPlan 9 段規格
- `docs/learnings/ERRORS.md` — Pending Review 區規範
- `docs/architecture/invariants.md` — INV-* 條目格式

### 自動快照 vs 本命令的分工

- `pre-compact-snapshot.py` → `state/session-handoffs/`：**自動快照**，PreCompact 時觸發，機器可讀，不需人介入。
- `/last-word` → `SESSION-HANDOFF.md`：**手動交接**，人主動觸發，含可直接貼上續接的 prompt，供下個 session 的人類/agent 讀。
- 兩者互補：自動快照保底（compact 隨時可能發生），手動交接才有結構化的續接 prompt。
