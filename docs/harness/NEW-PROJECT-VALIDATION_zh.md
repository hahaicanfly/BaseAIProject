# 新專案 Harness 驗收流程（Canary Walkthrough）

> **角色**：fork 本模板後，用一個約 30 分鐘、無實際業務價值的 canary 任務，走完 harness 的關鍵環節，證明「有 hook/protocol 檔案」≠「真的運作」。
> **依據**：改寫自一次真實專案的 10-phase harness 遷移 dogfood 實錄（過程中發現 2 個 hook bug）。已抽掉該專案的技術棧細節，只留可複用的驗收動作。
> **原則**：每步都要有**可觀察**的通過判準（檔案內容、指令輸出、退出碼），不接受「應該有跑」的口頭確認。

## 何時執行

Fork 模板建好新 repo、`{{BUILD_CMD}}` 已可跑通、CLAUDE.md 佔位符已填、`.claude/hooks/*.py` 已依專案技術棧填入 `QUICK_CHECKS` 之後，正式開發前先跑本流程一次。之後每次調整 hooks/protocols（黃/紅級變更）也應重跑對應步驟。

## 前置檢查

- [ ] `{{BUILD_CMD}}` 執行成功（專案自己的 build/lint/test 指令，取代此佔位符）
- [ ] `git branch --show-current` 確認不在 master/main
- [ ] `.claude/hooks/settings.json`（或 `.claude/settings.json`）已註冊要用的 hooks

---

## Step 1 — Hooks 煙霧測試

**動作**：依 `.claude/protocols/harness-maintenance.md` §4 的煙霧測試程序，對 `pre-tool-use-guard.py`（或專案等效 enforce hook）跑一次 block 案例與一次 pass 案例：

```bash
python3 -c "import json,subprocess; h='.claude/hooks/pre-tool-use-guard.py'; \
print(subprocess.run([h],input=json.dumps({'tool_name':'Bash','tool_input':{'command':'ca'+'t .e'+'nv'}}),capture_output=True,text=True).returncode)"
```

**通過判準**：
- block 案例退出碼為非 0（依專案定義，通常 `2`）
- 把 command 換成 `ls -la` 後退出碼為 `0`
- 不要用 `git commit` 當測資（只在 master/main 上 block，在 feat 分支恆為 0，會誤判 hook 失效）

---

## Step 2 — 開 feat 分支走一次最小 ExecPlan / Plan Mode

**動作**：從 master 開 `feat/canary-<date>` 分支，依 `docs/plans/PLANS.md` §2 建一份最小 ExecPlan `docs/plans/active/F-CANARY-<date>.md`（可以只做一個無害的假變更，例如新增一行註解），或改用 Plan Mode 走一次同等流程。

**通過判準**：
- ExecPlan 檔案含 §1 Goal ～ §9 Handoff Manifest 全部 9 段（順序符合 `PLANS.md` §2）
- `Status` 欄位隨流程從 `todo` → `in_progress` → `done` 有更新
- 至少 1 個 commit 引用該 ExecPlan 檔名或 F-id

---

## Step 3 — 派一次 subagent 驗證 handoff marker 與回報合約

**動作**：用 Task/Agent 工具派一個 sub-agent（任一角色，例如 `code-reviewer` 或通用 dev agent）完成 Step 2 的假變更，要求其 final response 依 `.claude/protocols/handoff-protocol.md` 結尾。

**通過判準**：
- sub-agent 的最終回應**最後一行**是 `[HANDOFF: <target>]` / `[VERIFY_FAILED: <reason>]` / `[HUMAN_ATTENTION_REQUIRED: <reason>]` 三者之一
- `<target>` 是 handoff-protocol.md 表列的合法值之一（非捏造角色名）
- 若沒有任何 marker → 視為 protocol violation，直接進 Step 5（不需另外造錯）

---

## Step 4 — 觸發一次 code-review skill

**動作**：對 Step 2/3 產生的 diff 執行 `/code-review`（或直接照 `.claude/skills/code-review/SKILL.md` 步驟手動走一次）。

**通過判準**：
- 輸出符合 SKILL.md 定義格式：含 `Blockers / Warnings / Suggestions / Praise` 四段與 `Decision`
- 結尾同樣有合法 `[HANDOFF: ...]` marker
- Review 內容至少引用 1 條 `docs/architecture/invariants.md` 的 INV-id（證明 reviewer 真的讀了 constraints，不是空泛評論）

---

## Step 5 — 故意犯一個小錯，驗證 ERRORS.md 管線

**動作**：刻意違反一條已知 invariant（例如在 master 上跑一次會被擋的操作、或寫一個明知會被 hook 標記的檔案），觀察錯誤是否真的被記錄。

**通過判準**：
- `docs/learnings/ERRORS.md` 的 `## Pending Review` 節新增一條，格式含「情境 / 錯誤 / 教訓 / 建議去向」四欄（依 `harness-maintenance.md` §3）
- 若專案有 sentinel hook（如 stop-retro-logger 等效物），對應的 `state/*.jsonl` 也應出現這次事件
- 手動確認新條目**不是**重複既有主題；若同主題已存在，改為在舊條目加 `再犯：YYYY-MM-DD`

---

## Step 6 — 檢查團隊名單與 frontmatter 一致

**動作**：比對 `agent_docs/AI-TEAM-REGISTRY.md` 表列的 agent/model/tools，與 `.claude/agents/*.md` 逐檔 frontmatter（`model` / `tools` 欄）。

**通過判準**：
- 逐一 agent 的 `model` 欄與 REGISTRY 表格一致，0 矛盾
- REGISTRY 檔頭聲明的正典來源（frontmatter 為準）沒有被表格內容反過來覆蓋
- Agent 數量與 REGISTRY 標題（如「Agents — N」）計數相符
- 有矛盾 → 依 `harness-maintenance.md` 檔案分級：REGISTRY.md 屬黃級可直接修並重生成；frontmatter 本身若要改則走該 agent 檔的分級規則

---

## 總結驗收表

| # | 環節 | 判準（可觀察） |
|---|------|---------------|
| 1 | Hooks 煙霧測試 | block 案例非 0、pass 案例為 0 |
| 2 | ExecPlan / Plan Mode | 9 段齊全、Status 有推進、有對應 commit |
| 3 | Subagent handoff | 結尾為合法三種 marker 之一 |
| 4 | code-review skill | 四段輸出格式 + 引用 INV-id + 合法 marker |
| 5 | ERRORS.md 管線 | Pending Review 新增合規格式條目（或 jsonl 事件） |
| 6 | REGISTRY 一致性 | agent 數量/model 欄與 frontmatter 0 矛盾 |

## 清理

Canary 完成後：假變更 revert 或保留成本次驗收證據存檔於 `docs/plans/completed/`；不需要的 feat 分支可刪除（非 master，非強制保留）。

`[HANDOFF: human-approval]`
