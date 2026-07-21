# {{PROJECT_NAME}} — Agent 操作地圖

> {{PROJECT_TAGLINE}}
> 本檔是**路由中心**（≤100 行）：只放採信順序、決策樹與最高頻硬規則，詳情追引用檔。
> 2026-07-04 由 503→125→本版重寫，舊版在 `CLAUDE.md.bak`，重寫依據見 `docs/harness/DIAGNOSIS.md`。

## 啟用狀態（fork 本模板的新專案先讀這節）

- 任何檔案若仍含 `{{佔位符}}` = **未啟用**：跳過它，不要照做、不要編造內容補洞。
- `agent_docs/TECHNICAL-REFERENCE.md` 填實後（無佔位符）→ 恢復「任務前必讀」地位；未填實 → 跳過。

## Quick Commands

```bash
# {{填入專案建構/測試/lint 指令}} ← fork 後第一批必填（可執行驗證指令是成功率最大槓桿）；環境初始化範本：.claude/templates/init.sh.template
git branch --show-current   # 動手前確認不在 master/main
```

## 正典層級（文件互相矛盾時，依此順序採信）

1. 模型與工具分派 → 以 `.claude/agents/*.md` 的 frontmatter 為準
2. Review 流程與輸出格式 → 以 `.claude/protocols/review-protocol.md` 為準
3. Agent / Skill 名單 → 以 `agent_docs/AI-TEAM-REGISTRY.md` 為準（該檔由 frontmatter 生成，重生成方式見其檔頭）
4. Git / 安全硬規則 → 以 `docs/architecture/invariants.md` 為準

遇到矛盾：按上表採信，並把矛盾記入 `docs/learnings/ERRORS.md`，不要停下來糾結。

## 動手前決策樹（唯一入口）

0. 範疇/需求不清（下列 4 項缺 2 項以上：目標用戶、成功指標、明確邊界/非目標、觸發條件）→ 先在主對話釐清，才進 ExecPlan 或 Plan Mode（詳見 `.claude/rules/clarify-first.md`）
1. 跨模組 / API 變更 / 大規模重構 → 建 ExecPlan（`docs/plans/active/`，規格見 `docs/plans/PLANS.md`），**等人類核可**
2. 其餘非瑣碎任務（新功能、多檔修改、刪檔）→ Plan Mode 提計劃，同意後執行
3. 單檔 < 20 行、已定位的 bug 修復、格式調整 → 直接做
4. 驗收條件無法機械化（品味／商業判斷）→ 產出候選＋trade-off 交人選（judgment-rubrics §6），不進實作迴圈
5. 永遠適用：改檔前必先 Read；未經驗證不得宣稱完成

## 常駐規則（`.claude/rules/` 自動載入，不必重複讀）

security ／ model-dispatch（模型調度與派工）／ judgment-rubrics（升級·完成·熔斷·換路判準）／ clarify-first（進 ExecPlan/Plan Mode 前的主動範圍確認）／ plan-first ／ parallel-worktree ／ cost-optimization（modularity 已降非常駐 → `agent_docs/modularity.md`）

- 派工 prompt 模板：`.claude/templates/delegation-templates.md`
- Harness 檔案怎麼安全地改：`.claude/protocols/harness-maintenance.md`

## 硬防線

`pre-tool-use-guard.py`（enforce，已實測）以 exit 2 阻斷：master/main 上 commit、force-push master/main、`reset --hard origin/master|main`、讀 `.env` 等密檔、`curl|sh`。全文見 `docs/architecture/invariants.md`。

NEVER：硬編碼 secrets ／ commit 敏感檔（`.env`、`*.keystore`…）／ 猜 API 簽名 ／ 加未要求的功能抽象 ／ 跳過 lint/test 宣稱完成。

## 交接與 Session 管理

- Sub-agent final response 必含 `[HANDOFF:*]` / `[VERIFY_FAILED:*]` / `[HUMAN_ATTENTION_REQUIRED:*]`（規範：`.claude/protocols/handoff-protocol.md`）
- 階段完成且 context 用量 >50% → `/last-word` 產出 `SESSION-HANDOFF.md` → `/clear` → 新 session 讀檔續接
- 踩坑教訓 append 到 `docs/learnings/ERRORS.md`（格式見 harness-maintenance.md）；重複出現且可機械化者，升級寫進 `invariants.md`

## 文件地圖

| 需要什麼 | 去哪裡 |
|---------|--------|
| 文件總索引 | `docs/INDEX.md` |
| 當前架構（填實後必讀） | `agent_docs/TECHNICAL-REFERENCE.md` |
| 團隊名單、模型分派、skills | `agent_docs/AI-TEAM-REGISTRY.md` |
| 多代理協作模式 | `agent_docs/multi-agent-guide.md` |
| ExecPlan 10 階段生命週期 | `.claude/protocols/execplan-lifecycle.md` |
| Harness 診斷書／給未來 session 的信 | `docs/harness/` |
| UI 三階段流程 | `.claude/uiux/WORKFLOW.md` |
| Runtime state 格式 | `state/SCHEMA.md` |

## Communication Style

繁體中文回應；代碼註解可英文；commit message 英文、`type(scope)` 格式、一功能一 commit、嚴禁直接 commit master（feat/<slug> 開分支 + PR）。精簡、技術準確、無 emoji（除非用戶要求）。

```
✓ 完成：[具體做了什麼]
→ 下一步：[接下來要做什麼]
⚠ 注意：[需要用戶知道的風險或問題]
```

## Tech Stack ／ Project Relations

{{未填 = 未啟用，跳過本節}}

## Antigravity (agy) 橋接

agy agent：先讀 `GEMINI.md`。`.claude/agents/*.md` 與 `.claude/skills/*/SKILL.md` 規則完整適用於 agy；Python hooks 在 agy 環境不自動執行，須手動遵守等效規則（尤其 invariants 的 INV-GIT-*）。
