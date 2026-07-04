---
name: pr-retro
description: 每次 PR merge 後自動萃取教訓並寫入 ERRORS.md Pending Review，驅動 skill 文件持續優化；當 PR 合併後或使用者提及「複盤」「retro」時觸發。
---

# Skill: pr-retro

> **用途**：每次 PR merge 後自動萃取教訓，寫入 ERRORS.md Pending Review，驅動 SkillOpt 式的 skill document 持續改善。
> **觸發**：`/pr-retro [PR 描述 / review log / diff 摘要]`（或由 stop-retro-logger 自動調用）
> **角色定位**：SkillOpt 論文中的 "minibatch reflection + rejected-edit buffer 寫入器"

---

## 核心概念：PR 是最好的 Training Signal

每個 PR 都是一次完整的 rollout：
- **成功的 PR** = 正向 example（知道什麼有效）
- **被 Review 攔截的問題** = 負向 example（知道什麼不該做）
- **需要多次修改才通過的 PR** = 高信號 training data

pr-retro 的任務：把這些 signal 轉化成 ERRORS.md 的候選 lesson。

---

## 執行步驟

### Step 1：收集 PR 上下文

需要以下任一輸入：
- git diff（`git diff main...HEAD` 或 PR diff）
- PR review 意見（若有 code review 輸出）
- `pr-review-cycle-mob` 的 Cascade 報告
- ExecPlan §6 Progress Log 中的 `[VERIFY_FAILED:*]`

若無任何輸入，讀 `state/hook-events.jsonl` 最近 N 筆記錄。

### Step 2：分析失敗模式

對每個被 Flag / Block / VERIFY_FAILED 的條目，分析：

```
問題描述：[發生了什麼]
根本原因：[為什麼會發生]
觸發 INV：[對應哪條 INV-*，若無對應 → 候選新增]
修復方式：[怎麼解決]
預防措施：[下次如何避免]
```

### Step 3：分類處理

**Case A：對應現有 ERRORS.md lesson（再次觸發）**
- 在 ERRORS.md 的對應 lesson 後 append：`  ↩ [日期] 再次觸發於 [PR slug]`
- 考慮是否將此 lesson 升級為 INV-* 規則

**Case B：新模式（未見過的錯誤）**
- 產生候選 lesson：
  ```
  - [YYYY-MM-DD] [分類] 問題描述 → 正確做法
  ```
- append 到 `docs/learnings/ERRORS.md` 的 `## Pending Review`

**Case C：涉及 skill doc 需要更新**
- 若問題根因是某個 agent/skill 的指引不足或有誤
- 產生具體的 skill doc edit 建議：
  ```
  [SKILL_EDIT_CANDIDATE]
  目標文件: .claude/agents/xxx.md
  操作: replace
  位置: [描述在文件的哪個段落]
  原文: [摘錄]
  建議改為: [改後版本]
  原因: [為什麼]
  ```
- 寫入 ERRORS.md Pending Review（待人類週審時決定是否 apply）

**Case D：需要新增 INV-* 規則**
- 若此問題可以寫成 grep pattern 來機械驗證
- 產生候選 INV：
  ```
  INV-[NS]-[NNN]  [一句話規則]
    CHECK    [grep 指令]
    HOOK     post-edit-lint.py
    SOURCE   [來源日期]
  ```
- 寫入 ERRORS.md Pending Review，人類週審後 promote 到 invariants.md

### Step 4：產出 Retro Report

```
## PR Retro Report — [PR slug / 日期]

### 本次 PR 統計
- 變更檔案：N
- Review 輪次：N
- L1 Flags：N, L2 Blocks：N, L3 Criticals：N

### 新增候選 Lessons（Case B）
[列出]

### 再次觸發的 Lessons（Case A）
[列出]

### Skill Doc Edit 候選（Case C）
[列出 SKILL_EDIT_CANDIDATE]

### 新增 INV-* 候選（Case D）
[列出]

### 本 PR 品質分數（0-10）
[基於 review 輪次、flag 數量的簡單計算]
```

### Step 5：自動更新追蹤

- append 到 `docs/learnings/ERRORS.md` `## Pending Review`：`## [日期] retro | [PR slug]`
- 若 Case B/C/D 有內容 → 在 session 末段提醒人類「週審 ERRORS.md 有 N 條 pending」

---

## 與 SkillOpt 的對應

| pr-retro 動作 | SkillOpt 元件 |
|--------------|---------------|
| 收集 Flag/Block | rollout evidence |
| Case B → Pending Review | rejected-edit buffer |
| 人類週審 promote | epoch-wise slow update |
| Case C → skill edit | bounded text edit（人工核可版） |
| Case D → INV candidate | validation gate 強化 |

---

## 與 stop-retro-logger 的關係

`stop-retro-logger.py` 僅在 session 結束時 append 一則執行提醒（純文字 reminder），**不會**執行 Case A/B/C/D 的分類分析。分類分析必須由人工觸發本 skill（`/pr-retro`）才會發生。

詳見 `.claude/hooks/stop-retro-logger.py` 的 `# PR_RETRO_HOOK` 標記。
