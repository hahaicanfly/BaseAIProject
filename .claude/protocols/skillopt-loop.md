# SkillOpt Loop Protocol

> ⚠ 狀態：未接線設計草案（design draft, not wired）。無任何 hook/cron 實際執行本迴圈；不得被其他文件當作生效規則援引。是否接線或刪除，待人類決定。

> **角色**：定義 Harness 系統的「自我改善迴圈」——如何把 PR 中的 failure signal 轉化為更好的 skill document。
> **理論依據**：SkillOpt: Optimizing Agent Skills as External Text State（Microsoft Research 等機構，2026-05）【未確認：無法驗證此來源存在】
> **核心洞察**：Agent skill document = 凍結模型的可訓練外部狀態，用 MLOps 紀律訓練文字而非模型權重。

---

## 系統架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                     SkillOpt Loop                               │
│                                                                 │
│  ┌────────────┐   rollout    ┌──────────────────────────────┐   │
│  │  PR / Task │─evidence──▶  │  pr-review-cycle-mob         │   │
│  │  執行      │             │  (scored trajectories)       │   │
│  └────────────┘             └──────────────┬───────────────┘   │
│                                            │ fail signals       │
│                                            ▼                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  pr-retro  （minibatch reflection）                      │    │
│  │  ・Case A: 再次觸發 existing lesson                      │    │
│  │  ・Case B: 新 lesson → Pending Review                   │    │
│  │  ・Case C: skill doc edit candidate                     │    │
│  │  ・Case D: INV-* candidate                              │    │
│  └────────────────────────────┬────────────────────────────┘    │
│                               │ candidates                      │
│                               ▼                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ERRORS.md Pending Review  （rejected-edit buffer）      │    │
│  └────────────────────────────┬────────────────────────────┘    │
│                               │ 人類週審（validation gate）      │
│                               ▼                                 │
│  ┌──────────────┐    ┌────────────────────┐                     │
│  │ ERRORS.md    │    │ .claude/agents/    │                     │
│  │ Active       │    │ .claude/skills/    │（epoch-wise update） │
│  │ Lessons      │    │ invariants.md      │                     │
│  └──────────────┘    └────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 迴圈參與者與職責

| 角色 | 工具/Skill | SkillOpt 元件 |
|------|-----------|--------------|
| PR 執行 + Hook | `pre-tool-use-guard` / `post-edit-lint` | rollout + scoring |
| 梯級審查 | `pr-review-cycle-mob` | scored trajectories |
| 教訓萃取 | `pr-retro` | minibatch reflection |
| 候選收集 | `ERRORS.md Pending Review` | rejected-edit buffer |
| 人類週審 | 每週日晚，手動 promote | validation gate |
| 文件更新 | 直接編輯 `.claude/agents/*.md` / `invariants.md` | bounded text edit |

---

## 學習率（Textual Learning Rate）

每週週審時，**最多** promote 以下數量的 lesson：

| 週 lesson 數 | 最多 promote | 類比 |
|-------------|-------------|------|
| 1–3 個 | 全部 | learning rate = 1.0 |
| 4–7 個 | 3–4 個 | learning rate = 0.5 |
| 8+ 個 | 3 個 | learning rate = 0.3（防 catastrophic forgetting） |

**原則**：寧可慢慢學，不要一次大改 skill docs 讓系統震盪。
**優先**：promote 有 Case D（可機械驗證）的 lesson，次之 Case C，再次 Case B。

---

## Validation Gate（如何判斷一個 lesson 值得 promote）

Promote 前問以下 3 個問題：

1. **可重現性**：這個錯誤是否在 ≥2 個不同 PR/session 中出現過？
   - 是 → promote，優先度 HIGH
   - 否（只出現一次）→ 留在 Pending Review 再觀察一週

2. **可預防性**：加上這個 lesson/INV 後，下次能在 pre-tool-use-guard 或 post-edit-lint 攔截嗎？
   - 是 → 同步更新 `invariants.md` + hook 的 `QUICK_CHECKS`
   - 否 → 只加到 ERRORS.md Active Lessons（作為 LLM reviewreference）

3. **無副作用**：這個 lesson 是否可能造成誤報（false positive）而阻礙正常工作流？
   - 可能有誤報 → 先不 promote，縮窄 pattern 後再評估

---

## Protected Regions（epoch-wise slow update）

以下文件的以下區段是 **protected**，不得由週審之外的方式修改：

| 文件 | Protected 區段 | 原因 |
|------|--------------|------|
| `CLAUDE.md` | `## 硬防線` | 核心安全約束，不能頻繁變動 |
| `docs/architecture/invariants.md` | `INV-GIT-*` | Git 規則已穩定，輕易改動風險大 |
| `.claude/hooks/pre-tool-use-guard.py` | enforce 邏輯 | 誤改可能導致安全漏洞 |

Protected region 的修改必須經過 ADR（`docs/decisions/ADR-NNNN-*.md`）。

---

## Rejected-Edit Buffer 格式（ERRORS.md Pending Review）

每條 Pending Review 必須用以下格式，方便週審時快速決策：

```
### [YYYY-MM-DD] [分類] [Case B/C/D]
**觸發 PR**：feat/xxx 或 session 日期
**問題**：[一句話描述]
**根本原因**：[為什麼發生]
**候選動作**：
  Case B: - [日期] [分類] 描述 → 正確做法
  Case C: [SKILL_EDIT_CANDIDATE] 文件+段落+改法
  Case D: INV-[NS]-[NNN] CHECK: [grep] HOOK: [hook名]
**可重現次數**：1（首次）
**週審決定**：□ Promote  □ Reject  □ 再觀察
```

---

## SkillOpt Readiness Checklist

當 `/harness-eval` 的 D8 分數 < 5 時，按以下順序補齊：

- [ ] `state/hook-events.jsonl` 有 rollout evidence（hooks 有在記錄）
- [ ] `ERRORS.md` 有 Pending Review + Active Lessons 雙區
- [ ] `pr-review-cycle-mob` 已定義 cascade 評分標準
- [ ] `pr-retro` 能自動觸發（stop-retro-logger 整合）
- [ ] 至少 1 次人類週審記錄（知道流程跑通了）

D8 = 5 分 → Harness 達到 Level 5 SkillOpt-Ready。

---

## 引用此檔的位置

（尚無任何檔案引用本協議）
