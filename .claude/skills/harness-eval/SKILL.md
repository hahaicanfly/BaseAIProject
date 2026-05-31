# Skill: harness-eval

> **用途**：掃描目標 repo，輸出 Harness Engineering 成熟度分數（0–100）、各維度缺口清單、優先改善建議。
> **觸發**：`/harness-eval [repo_path]`（省略 path 則預設為當前工作目錄）
> **輸出**：Maturity Report — 分數卡 + 改善路線圖

---

## 執行步驟

### Step 0：定位目標 repo

確認以下路徑存在，否則報錯並中止：
- `CLAUDE.md` 或 `.claude/`（任一即可視為有 harness 意圖）

### Step 1：讀取 rubric

讀 `.claude/skills/harness-eval/rubric.md`，取得 8 個維度的評分標準。

### Step 2：逐維度掃描

**D1 — Constitutional Layer（CLAUDE.md + rules/）**
- [ ] `CLAUDE.md` 是否存在且非空
- [ ] 是否有角色定義（`## 角色` 或 `## Role`）
- [ ] 是否有 Token 預算策略（3 層讀取或等效）
- [ ] 是否有隱私規則 / 禁讀區
- [ ] `.claude/rules/` 目錄中 rules 數量（0/1-2/3-5/5+）

**D2 — Agent Coverage**
- [ ] `.claude/agents/` 存在
- [ ] agent 數量（0/1-3/4-7/8-11/12+）
- [ ] 核心 5 人是否齊全：pm、architect、tech-lead、security-reviewer、qa-engineer

**D3 — Hook System（最高權重）**
- [ ] `pre-tool-use-guard.py` 存在
- [ ] `post-edit-lint.py` 存在
- [ ] `pre-compact-snapshot.py` 存在
- [ ] `stop-retro-logger.py` 存在
- [ ] `.claude/settings.json` 中 hooks 是否對應 `PreToolUse`、`PostToolUse`、`PreCompact`、`Stop`
- [ ] `post-edit-lint.py` 中 `QUICK_CHECKS` 是否有實際填入（非空陣列）
- [ ] `pre-tool-use-guard.py` 是否有 enforce 邏輯（非 pass-through）

**D4 — Invariants（INV-\*）**
- [ ] `docs/architecture/invariants.md` 存在
- [ ] `INV-GIT-*` 規則已定義
- [ ] `INV-SEC-*` 規則已定義（含實際 pattern，非 template TODO）
- [ ] 專案特定 INV 規則數量（0/1-2/3+）
- [ ] `post-edit-lint.py` 中是否引用 INV-id

**D5 — ExecPlan System**
- [ ] `docs/plans/PLANS.md` 存在
- [ ] `docs/plans/active/` + `docs/plans/completed/` 目錄存在
- [ ] 有過至少 1 個 completed ExecPlan（否則 "未曾啟用"）
- [ ] `.claude/protocols/execplan-lifecycle.md` 存在

**D6 — Memory & Retro Loop**
- [ ] `docs/learnings/ERRORS.md` 存在
- [ ] `ERRORS.md` 的 Active Lessons 非空（有實際 lesson）
- [ ] `state/SCHEMA.md` 存在
- [ ] `state/` 有 `.gitignore`（防止 jsonl 入版控）
- [ ] `state/hook-events.jsonl` 或 `session-handoffs/` 有實際資料（代表系統曾真實運行）

**D7 — Skills & Commands**
- [ ] `.claude/skills/` 目錄存在
- [ ] skill 數量（0/1-3/4-7/8+）
- [ ] 關鍵 skill 是否有實質內容（非純 stub）：code-review、multi-agent-review 任一
- [ ] `.claude/commands/last-word.md` 存在（session hygiene）

**D8 — SkillOpt Loop Readiness**（SkillOpt 論文標準）
- [ ] 有 rollout evidence 收集機制（hook 記錄執行結果到 jsonl）
- [ ] 有 validation gate 概念（改 skill 前後能比較效果）
- [ ] `ERRORS.md` 結構符合：Pending Review → Active Lessons 雙區（rejected-edit buffer + epoch update）
- [ ] 是否定義了 skill update 觸發條件（何時更新哪個 agent/skill 文件）

### Step 3：計算分數

參閱 `rubric.md` 中的計分矩陣，加總各維度得分，標準化為 0–100。

### Step 4：產出報告

輸出格式：

```
## Harness Maturity Report — [repo_path]
**日期**：[今天]
**總分**：XX / 100 → Level N [等級名稱]

### 分數卡
| 維度 | 得分 | 滿分 | 評語 |
|------|------|------|------|
| D1 Constitutional | X | 15 | ... |
| D2 Agents         | X | 10 | ... |
| D3 Hooks          | X | 20 | ... |
| D4 Invariants     | X | 15 | ... |
| D5 ExecPlan       | X | 10 | ... |
| D6 Memory/Retro   | X | 15 | ... |
| D7 Skills/Cmds    | X | 10 | ... |
| D8 SkillOpt Ready | X |  5 | ... |

### 缺口清單（依優先度排序）
1. [HIGH] ...
2. [MED] ...
3. [LOW] ...

### 最小改善路徑（3 步）
1. ...
2. ...
3. ...

### SkillOpt Readiness 指數
[是否具備自動改善能力的前提條件分析]
```

### Step 5：寫回 Atlas/QA（若在 Life-Vault 環境）或寫到 docs/

- 若 `Atlas/QA/` 存在 → 寫入 `Atlas/QA/[日期]-harness-eval-[repo-slug].md`
- 否則 → 輸出到 `docs/harness-eval-[日期].md`

---

## 成熟度等級定義

| 等級 | 分數 | 名稱 | 特徵 |
|------|------|------|------|
| 0 | 0–20 | No Harness | 無 CLAUDE.md 或只有空殼 |
| 1 | 21–40 | Basic | 有 CLAUDE.md + 少量 rules，無 hooks |
| 2 | 41–60 | Structured | 有 agents + hooks（至少 guard），有 INV-GIT-* |
| 3 | 61–80 | Process-Aware | ExecPlan 曾實際使用，ERRORS.md 有 lessons |
| 4 | 81–95 | Self-Monitoring | 全 8 hooks 運行，INV-* 有專案規則，retro loop 運轉中 |
| 5 | 96–100 | SkillOpt-Ready | D8 完整，skill doc 有版本歷史，validation gate 定義完成 |

---

## 注意事項

- 掃描只讀不寫（除了最後的 report 輸出）
- 掃描時間應在 2 分鐘內完成（不要讀大型原始碼）
- 重點看結構與配置，不評估 skill/agent 內容品質（那是 skill-quality-review 的任務）
