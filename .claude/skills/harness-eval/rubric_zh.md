# Harness Eval — 計分矩陣（Rubric）

> **版本**：v1.0（SkillOpt 論文加入 D8 後首版）
> **更新策略**：當 harness-eval 跑過 3 個以上真實 repo 並收集反饋後，升版調整權重。

---

## 計分矩陣

### D1 — Constitutional Layer（滿分 15）

| 檢查項 | 分值 | 計分邏輯 |
|--------|------|---------|
| `CLAUDE.md` 存在且 > 100 字 | 3 | 有=3，空殼=0 |
| 有角色定義區段 | 2 | 有=2 |
| 有 Token 預算策略（3層讀取或等效說明） | 3 | 有=3，提到但不完整=1 |
| 有隱私/禁讀規則 | 2 | 有=2 |
| `.claude/rules/` 數量 | 5 | 0個=0, 1-2個=2, 3-4個=3, 5+個=5 |

### D2 — Agent Coverage（滿分 10）

| 檢查項 | 分值 | 計分邏輯 |
|--------|------|---------|
| `.claude/agents/` 存在 | 2 | 有=2 |
| agent 數量 | 4 | 0=0, 1-3=1, 4-7=2, 8-11=3, 12+=4 |
| 核心 5 人齊全（pm+architect+tech-lead+security+qa） | 4 | 每人 0.8 分，取整 |

### D3 — Hook System（滿分 20，最高權重）

| 檢查項 | 分值 | 計分邏輯 |
|--------|------|---------|
| `pre-tool-use-guard.py` 存在 | 4 | 有=4 |
| `post-edit-lint.py` 存在 | 3 | 有=3 |
| `pre-compact-snapshot.py` 存在 | 2 | 有=2 |
| `stop-retro-logger.py` 存在 | 2 | 有=2 |
| `settings.json` 中 4 個 hooks 皆已註冊 | 3 | 全部=3, 部分按比例 |
| `post-edit-lint.py` 中 `QUICK_CHECKS` 非空 | 3 | 有實際 pattern=3, 空陣列=0 |
| `pre-tool-use-guard.py` 有 enforce 邏輯 | 3 | 真正阻擋=3, pass-through=0 |

### D4 — Invariants INV-\*（滿分 15）

| 檢查項 | 分值 | 計分邏輯 |
|--------|------|---------|
| `docs/architecture/invariants.md` 存在 | 3 | 有=3 |
| `INV-GIT-*` 規則已定義（≥2條） | 3 | ≥2=3, 1條=1, 0=0 |
| `INV-SEC-*` 規則有實際 pattern（非 TODO） | 4 | 有實際 grep pattern=4, 只有 TODO=1, 無=0 |
| 專案特定 INV 規則（非 GIT/通用） | 5 | ≥3條=5, 1-2條=2, 0=0 |

### D5 — ExecPlan System（滿分 10）

| 檢查項 | 分值 | 計分邏輯 |
|--------|------|---------|
| `docs/plans/PLANS.md` 存在且非純模板 | 2 | 有=2 |
| `docs/plans/active/` + `completed/` 存在 | 2 | 兩者都有=2, 一個=1 |
| 有過 ≥1 個 completed ExecPlan（.md 非 .gitkeep） | 4 | 有=4, 只有 active=1, 全空=0 |
| `execplan-lifecycle.md` 存在 | 2 | 有=2 |

### D6 — Memory & Retro Loop（滿分 15）

| 檢查項 | 分值 | 計分邏輯 |
|--------|------|---------|
| `docs/learnings/ERRORS.md` 存在 | 2 | 有=2 |
| `ERRORS.md` Active Lessons 非空（有實際 lesson） | 5 | ≥3條=5, 1-2條=2, 空=0 |
| `state/SCHEMA.md` 存在 | 2 | 有=2 |
| `state/` 有 `.gitignore` | 2 | 有=2 |
| `state/` 有實際 runtime 資料（jsonl 或 session-handoffs/） | 4 | 有資料=4, 空目錄=0 |

### D7 — Skills & Commands（滿分 10）

| 檢查項 | 分值 | 計分邏輯 |
|--------|------|---------|
| `.claude/skills/` 存在 | 1 | 有=1 |
| skill 數量 | 3 | 0=0, 1-3=1, 4-7=2, 8+=3 |
| 有實質內容的 skill（非純 stub，> 100 字且有具體步驟） | 4 | ≥3個=4, 1-2個=2, 0=0 |
| `/last-word` command 存在 | 2 | 有=2 |

### D8 — SkillOpt Loop Readiness（滿分 5）

| 檢查項 | 分值 | 計分邏輯 |
|--------|------|---------|
| hook 有 jsonl 記錄機制（rollout evidence） | 2 | `hook-events.jsonl` 格式存在=2 |
| `ERRORS.md` 有雙區結構（Pending Review + Active Lessons） | 2 | 雙區齊全=2, 只有一區=1 |
| 有 skill update 觸發定義（何時改哪個文件） | 1 | 有=1（在 protocol 或 CLAUDE.md 中明確） |

---

## 等級計算

| 總分 | 等級 | 標籤 |
|------|------|------|
| 0–20 | L0 | No Harness |
| 21–40 | L1 | Basic |
| 41–60 | L2 | Structured |
| 61–80 | L3 | Process-Aware |
| 81–95 | L4 | Self-Monitoring |
| 96–100 | L5 | SkillOpt-Ready |

---

## Rubric 演進記錄

| 版本 | 日期 | 變更摘要 |
|------|------|---------|
| v1.0 | 2026-05-28 | 初版，整合 SkillOpt D8 維度 |
