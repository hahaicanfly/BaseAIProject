# SESSION-HANDOFF — 2026-07-28

> Produced by /last-word. After `/clear`, read this file to resume; once resumption is complete this file may be deleted or will be overwritten by the next /last-word.

## Handoff prompt (paste directly to resume)

I'm working on **F-003 — Tiered Harness (依模型等級分層的 harness 架構)**（ExecPlan: `docs/plans/active/F-003-tiered-harness.md`）。

**Completed（§6 Progress Log 最新條目）:**
- Phase 0：可執行閘門落地——`.claude/tiers/budget.json`（3 個可切換模式）、`scripts/context-budget.py`、CLAUDE.md Quick Commands 填入 4 條 harness 自檢指令。原計畫步驟 5「修復遙測管線」經實測**證偽**（採收器功能正常，缺口在發射端），未動該 Red-tier hook。
- Phase 1：實測確認主對話模型在第一次回應前**不可觀測**（SessionStart / InstructionsLoaded / UserPromptSubmit payload 與 env 皆無 `model`），故架構定為「主對話宣告 + 事後驗證，子 agent 真偵測」。建立 `model-map.json`。
- Phase 2：三份累加來源片段 + `build-tier-packs.py` 生成三個 pack；6 份規則檔降級 `always: false` 原地保留；CLAUDE.md「Standing Rules」改寫。**strong 常駐量 635 行/33,164 字元 → 244 行/13,420 字元（−61%）**，mid −47%，light −34%。
- Phase 3 步驟 18-19：`SubagentStart` 動態分層 hook + 委派模板去重複。
- 獨立 read-back 查核完成，並據其附帶清單補回 **5 條被重構漏掉的規範性規則**。
- acceptance-run **12/12 PASS**；三個 hook smoke test 共 17 情境全通過；巢狀 `claude -p` 真實 session 端對端驗證通過。

**Remaining（§4 未打勾步驟）:**
- 步驟 20：拆分 8 個 >150 行的 SKILL.md（ui-ux-pro-max 394、frontend-design 281、pr-review-cycle-mob 190、spectra-amplifier 189、tdd-workflow 184、beautiful-mermaid 176、feature-pipeline 171、gen-app-map 168）為「SKILL.md 路由 ≤80 行 + references/」，比照既有 `security-audit` 結構（Yellow tier）
- 步驟 21：更新 `agent_docs/AI-TEAM-REGISTRY.md`、`docs/INDEX.md`、CLAUDE.md 文件地圖
- 步驟 22：Phase 3 完成後再跑一次全量 read-back
- 步驟 23：更新 `docs/harness/LETTER-TO-FUTURE-SESSIONS.md` §3 交接清單

**Scope Baseline（copied from ExecPlan §1）:**
- target user = fork 本模板的新產品開發專案，主對話與子 agent 涵蓋 Haiku / Sonnet / Opus / Fable 四級
- success metric = 可切換模式的預算配置檔；預設 `balanced` 下 strong ≤250 行 / ≤14,000 字元、mid ≤24,000 字元；light 內容無語意遺失
- trigger condition = 使用者裁定採用分層路線後啟動
- confirmation source = 使用者 2026-07-28 原話「預期要對不同模型等級做不同的 harness 框架設計，等未來基礎模型能力提升才會收斂」+「其餘的都可以依照分析結果進行優化調整」
- **v2 (2026-07-28)**：門檻改為可調式配置（DEC-5）；子 agent 分層改動態（DEC-8）。來源：使用者「成功門檻做成可調式 -> 可選模式」「子 agent 也動態分層」

**Current marker:** `[HANDOFF: dev]`

**Pickup SOP:**
1. 讀 ExecPlan §3 Constraints + §9 Handoff Manifest + §7 DEC-1~11
2. 讀 `.claude/tiers/README.md`（分層機制、偵測優先序、已知限制）
3. 確認分支為 `feat/tiered-harness`
4. 從 §4 步驟 20 開始

**必知事項:**
- 本次改動**要開新 session 才生效**。續作時應已在新 session，主對話會收到 tier pack——順便實地檢驗注入品質與可讀性。
- 本機殘留 `HARNESS_TIER=mid`（Phase 1 探測所致，設定會即時生效但取消需開新 session）。若新 session 顯示 tier=mid 而非預期的 strong，先查此變數。
- tier pack 是**生成物**，永遠不要直接編輯 `.claude/tiers/{strong,mid,light}.md`；改 `src/` 片段後跑 `python3 scripts/build-tier-packs.py`。acceptance 的 `packs-fresh` 會擋住漂移。
- 授權範圍：使用者已同意「進行測試時可委派子 agent」。skill 拆檔屬實作，**不在該授權範圍**，需先確認。

**Related info:**
- Branch: `feat/tiered-harness`（latest commit: 2bbd863，領先 master 8 個 commit，**未推送、未開 PR**）
- Linked PR: 尚未開立
- Related invariants: INV-GIT-002 / INV-GIT-005 / INV-SEC-003
- 待人審 invariant 候選：常駐層預算上限（已由 `context-budget.py` 機械化）可升格 **INV-ARC-001**

## This session's archive summary
- invariants.md 新增：0（1 項候選待人審——invariants.md 屬 Red tier）
- ERRORS.md Pending Review 新增：3 則（hook payload 文件第三次不符、空帳本≠採收器壞掉、驗收 agent 自我放寬判準）+ 1 則 Recurred（bytes/chars 單位誤植，併入 2026-07-07 量測條目）
- ExecPlan 更新：F-003（§6 Progress Log ×6 條、§7 Decision Log DEC-1~11、§8 Q1-Q7、§9 Handoff Manifest 全面改寫）
- state/feature-list.json：F-003 verification 三項轉 true
