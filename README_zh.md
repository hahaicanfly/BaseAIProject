# BaseAIProject — AI Harness Engineering 基礎模板

https://hahaicanfly.github.io/BaseAIProject/share/ai-journey-story/

> [English](README.md) | 繁體中文

## 這是什麼（30 秒版）

BaseAIProject 是一套可直接 fork 的 **Claude Code AI 開發治理模板**：把「怎麼派工、怎麼驗收、怎麼防呆、怎麼累積教訓」寫成制度檔案——7 條常駐規則、14 個專業 agents、17 個觸發式 skills、7 個 guard hooks、4 支機械閘門腳本與對應 CI、一條教訓管線——讓 AI 在最少人工介入下穩定產出、可驗證、不失控。

**三步上手**：

1. **Fork 並填實**：全域替換 `{{PROJECT_NAME}}` 等佔位符，填入你專案的建構／測試／lint 指令（`CLAUDE.md` Quick Commands；環境初始化範本 `.claude/templates/init.sh.template`）——可執行驗證指令是成功率最大槓桿
2. **啟用防線**：`chmod +x .claude/hooks/*.py`，照 `.claude/protocols/harness-maintenance.md` §4 跑煙霧測試（block 與 pass 兩情境都要實測）
3. **Canary 驗收**：用一個 30 分鐘小任務照 `docs/harness/NEW-PROJECT-VALIDATION.md` 走完整流程（分支→計劃→派工→review→教訓寫回），全通即可正式使用

不會打指令?直接把這句貼給 Claude Code:「幫我完成專案初始化,交給它做前兩步」

語言慣例：AI 讀取的制度檔一律為**英文正典**；中文人類版在同目錄 `_zh` 後綴檔或 `agent_docs/zh/` 鏡像。以下為完整介紹。

---

> 一套可直接 fork 的 **AI 開發治理骨架**：讓 Sonnet / Haiku 等級的模型在缺乏人類逐步指揮的情況下，也能穩定、可驗證、不失控地自主產出。從 MaiNeu 實戰專案抽取，經 2026-07 Fable 5 架構 session 三輪深度制度化，再吸收外部 harness 生態研究（superpowers、learn-harness-engineering、revfactory/harness 等 7 個來源，星數與內容實地查證）的第四輪強化。

## 這個專案解決什麼問題

AI 主導開發的三大失敗模式，各有對應的物理防線：

| 失敗模式 | 本專案的解法 |
|----------|------------|
| **文件宣稱 ≠ 現實**（規則寫了沒人執行、防線部署了從未生效） | enforce hook 實測制度（黑箱煙霧測試）、引用即驗證、隔離驗收 |
| **弱模型失焦**（多份文件互相矛盾、隨機採信） | 正典層級（每類事實唯一事實源，其他只准引用）、觸發詞互斥設計 |
| **知識蒸發**（教訓沉入聊天記錄、同樣的坑踩三次） | 教訓管線：踩坑 → ERRORS.md → 人審 promote → 機械化進 invariants + guard |

## 核心設計哲學（五條）

1. **指揮官不下場**：主對話只做決策、拆解、派工、驗收；大量讀檔/掃 repo/研究一律派 subagent，回報只收結論與 `檔案:行號`。
2. **驗證不自驗**：實作者不得宣告自己通過驗收；一律派 fresh-context agent 做 read-back、實跑測試或多答案評審。
3. **常駐面即預算**：每 session 自動載入的內容（CLAUDE.md + rules）是對所有未來工作的徵稅，有明確行數上限與精簡觸發線。
4. **判斷力外化**：升級模型、判定完成、熔斷提問、換路訊號——全部寫成可觀察判準與正反例，弱模型照表執行。
5. **誠實條款**：品味決策、模糊商業判斷、無 ground truth 推理是弱模型的極限——制度明定遇到時的出口（多候選交人選、標註未確認、第二意見），不假裝能做。

## 能力總覽

| 子系統 | 規模 | 一句話 |
|--------|------|--------|
| Virtual Team | 14 agents（4 opus + 10 sonnet） | 職責互斥的專業分工，模型分派以 frontmatter 為正典 |
| Skills | 17 個 | 觸發式工作流，description 互斥設計 + 機械驗證器 |
| Hooks | 7 個 + 共用庫 | 1 個 enforce（exit 2 實測攔截）+ 6 個 sentinel |
| 常駐 Rules | 7 條（`always: true`） | 調度、判準、clarify-first、安全、成本、worktree、plan-first（模組化已降非常駐 → `agent_docs/`） |
| Protocols | 5 份 | ExecPlan 生命週期、交接 marker、review SOP、harness 維護、（1 份未接線草案） |
| 機械閘門 | 4 支腳本 + 4-job CI | `scripts/` acceptance-run / execplan-lint / check-doc-refs / retro-status；`harness-gates.yml` 對每個 PR 重跑檢查（py-compile、secret-scan、execplan-lint、placeholder-gate） |
| State 帳本 | 5 份 JSONL 帳本 | commits / delegations / verifications / rule-events / metrics-monthly——派工、驗收結果、規則命中率跨 session 存續（schema：`state/SCHEMA.md`） |
| 知識系統 | 5 層 | 教訓／硬規則／ADR／session 快照／原生 memory，各有寫讀權與流動規則 |

## 六大子系統

### 1. 指揮與調度層

- **`CLAUDE.md`（87 行路由中心）**：正典層級（文件矛盾時的採信順序）、動手前決策樹（ExecPlan vs Plan Mode vs 直接做 vs 驗收無法機械化→交人選）、硬防線摘要、文件地圖。超過 100 行觸發強制精簡。
- **`.claude/rules/model-dispatch.md`**：本機實際可用模型檔位、派工三件套（目標動機／驗收條件／回報格式，缺一不派）、升降級路徑（同模型連敗 2 次 → 升級一次 → 再敗 → 熔斷問人）、回報合約（≤40 行、長產物落檔傳路徑）、驗收邊界（FAIL 只准基於可機械檢查條件，風格意見進非阻斷建議欄）。
- **`.claude/rules/judgment-rubrics.md`**：七節可觀察判準各附正反例——何時升級、何時算真完成（含 gate-softening 禁令）、何時熔斷提問（含無改善偵測：連續 2 輪 FAIL 集合相同即熔斷）、什麼訊號該換路、品質底線、能力極限、Red Flags 合理化話術對照表（「違反字面即違反精神」）。
- **`.claude/templates/delegation-templates.md`**：搜尋／實作／重構／研究／審查／fresh-context 驗收六份派工模板，含範圍宣告（允許讀／允許寫／禁止觸碰／終止條件）與破壞性指令黑名單（禁對非指派檔案 rm / checkout / restore / clean）。

### 2. Virtual Team（14 agents）

opus ×4 保留給無標準答案的取捨：`architect`（系統設計/ADR）、`pm`（需求/優先級）、`security-reviewer`（安全審計）、`plan-reviewer`（計劃審查）。
sonnet ×10 執行 checklist 與模板化工作：`code-reviewer`（PR gating，唯一 Decision 出口）、`qa-engineer`、`tech-lead`（架構重構顧問，不做 PR gating）、研究三人組（`data-analyst` 量化KPI／`market-researcher` 市場消費者／`competitive-analyst` 競品比較，觸發詞互斥）、`uiux-agent`（三階段入口）與 `ui-ux-designer`（Phase 3 產出）、`techdebt-scanner`、`workflow-optimizer`。

四個 review 類 agent 的輸出格式統一採 `review-protocol.md` 正典詞彙（Blocker/Warning/Suggestion + Pass/Block/Conditional Pass）。名單與分派以 `agent_docs/AI-TEAM-REGISTRY.md` 為準（由 frontmatter 重生成，禁止手改單格）。

### 3. Skills（17 個）

- **開發流程**：`feature-pipeline`（端對端流水線）、`tdd-workflow`、`spectra-amplifier`（PRD 補 acceptance criteria）
- **審查三件套**（觸發互斥）：`code-review`（單一 PR 標準審查）、`multi-agent-review`（高風險三專家並行）、`pr-review-cycle-mob`（成本分級 cascade）
- **安全與品質**：`security-audit`（OWASP）、`techdebt-scanner`、`harness-eval`（harness 成熟度 0-100 評分）
- **知識與交接**：`pr-retro`（merge 後萃取教訓）、`context-aggregator`（多來源交接摘要）、`gen-app-map`（技術棧無關的專案地圖產生器）
- **Skill 工程**：`skill-creator-plus`（取代基礎版 `skill-creator`；官方 Anthropic 方法論 × 本地制度：意圖捕捉、互斥檢查、pushy description、機械驗證器 `validate_skill.py`、fresh-context 雙向觸發測試各 8-10 條、eval 迭代）
- **UI 與圖表**：`beautiful-mermaid`（Mermaid → 終端 ASCII／SVG）、`ui-ux-pro-max`（設計系統產生器，附 3 支檢索腳本＋24 份跨 13 技術棧的設計資料庫）、`frontend-design`（設計哲學指引，Compose 範例＋等價寫法標註）

> 2026-07-07 全部 skills 已從母專案補回完整內容並去專案化（抽取時 10 個曾被靜默大綱化——這個事故本身也進了教訓管線）。

### 4. 物理防線（Hooks）

| Hook | 事件 | 模式 | 職責 |
|------|------|------|------|
| `pre-tool-use-guard.py` | PreToolUse(Bash) | **enforce**（exit 2） | 攔截：master/main 直接 commit、force-push、reset --hard origin、讀取**與 git add** 敏感檔（.env/keystore/credential…）、`curl\|sh` 各變體、rm -rf / |
| `post-edit-lint.py` | PostToolUse(寫入) | sentinel | INV pattern 快掃（fork 後填 QUICK_CHECKS） |
| `pre-compact-snapshot.py` | PreCompact | sentinel | 自動寫 session 快照到 `state/session-handoffs/` |
| `delegation-ledger.py` | PreToolUse(Task/Agent) | sentinel | 記錄每次派工（含是否附驗收條件）到 `state/delegations.jsonl` |
| `post-bash-commit-ledger.py` | PostToolUse(Bash) | sentinel | 把每個真實 git commit 連結回其 session，記入 `state/commits.jsonl` |
| `session-activation-check.py` | SessionStart | sentinel | 模板活化槽位（build/test 指令、佔位符）未填時開場警示 |
| `stop-retro-logger.py` | Stop/SubagentStop | sentinel | 收割 `[VERIFY_FAILED:*]` 進 ERRORS.md、遙測標記進 `state/rule-events.jsonl`（code span／fence 內引用豁免）；墓碑帳本防重複；30/90 天 state 輪替 |

鐵律（來自實戰教訓）：**任何 hook 新增或修改後，必須跑黑箱煙霧測試**（block 情境期望 exit 2、pass 期望 0，指令在 `harness-maintenance.md` §4）——本專案的 guard 曾因無執行權限＋錯誤 exit code 雙重失效而「紙上防線」數月無人發現。

runtime hooks 之外，四支**機械閘門腳本**（`scripts/`）讓宣稱隨時可驗：`acceptance-run.py` 實跑 ExecPlan §5 驗收區塊並存證、`execplan-lint.py` 依 PLANS.md 規格檢查 ExecPlan 結構、`check-doc-refs.py` 驗證正典中每個路徑／節引用真實存在（死引用是幻覺誘餌）、`retro-status.py` 依字面定義計算 §5 精簡觸發線數字。同組檢查經 `.github/workflows/harness-gates.yml` 對每個 PR 重跑（4 jobs：py-compile、secret-scan、execplan-lint、placeholder-gate）。

### 5. 知識管理（五層，地圖見 `docs/INDEX.md`）

```
踩坑 ──→ ERRORS.md（Pending，hook 自動收割＋手動 append）
              │ 人類週審 promote
              ▼
         Active Lessons（附 Why + How-to-apply）
              │ 可機械化者
              ▼
    invariants.md（INV-* 硬規則）──→ guard hook（物理攔截）
```

另三層：`docs/decisions/ADR-*`（架構決策，人核可）、`state/session-handoffs/`（PreCompact 自動快照）、Claude Code 原生 memory（**只准存跨 session 指標**，教訓全文一律走 ERRORS.md）。維護權限採紅黃綠三級（`harness-maintenance.md`）：教訓隨時可 append、行為指引備份後改、常駐規則與防線動之前問人。

### 6. UI/UX 三階段（可選）

Wireframe → Critique → Implementation 強制閘門（`.claude/uiux/WORKFLOW.md`），配 style-spec 模板與六份 prompt 模板。無前端專案可整組刪除 `.claude/uiux/` 與兩個 UI agent。

## 快速開始（fork 後五步）

1. **替換佔位符**：全域搜尋 `{{PROJECT_NAME}}`、`{{PROJECT_TAGLINE}}`；填 CLAUDE.md 的 Quick Commands 與 Tech Stack（可執行驗證指令是成功率最大槓桿——Feedback 子系統）；環境初始化照 `.claude/templates/init.sh.template` 填實。含 `{{}}` 的檔案視為未啟用，模型會自動跳過。
2. **最小可用填寫**：`agent_docs/TECHNICAL-REFERENCE.md` 檔頭列了 5 個欄位（核心使命、技術棧四格、頂層模組、API base URL、認證方式）——填完即解鎖「任務前必讀」地位，其餘 28 個佔位符可後補。
3. **Hooks 煙霧測試**：`chmod +x .claude/hooks/*.py` 後照 `harness-maintenance.md` §4 實測 block/pass 兩情境。
4. **跑 canary 驗收**：照 `docs/harness/NEW-PROJECT-VALIDATION.md` 用一個 30 分鐘的小任務走完整流程（分支→計劃→派工→review→教訓管線），每步有可觀察判準。
5. **按技術棧客製**：`invariants.md` 補 INV-SEC/TEST/API 規則、`post-edit-lint.py` 填 QUICK_CHECKS、`gen-app-map` 填掃描目標表、（有前端）填 uiux style-spec。

## 目錄結構

```
BaseAIProject/
├── CLAUDE.md                  # 路由中心：正典層級、決策樹、文件地圖（≤100 行）
├── GEMINI.md                  # Antigravity(agy) agent 橋接協議
├── agent_docs/                # 詳版教學層（常駐 rules 的延伸內容）
│   ├── AI-TEAM-REGISTRY.md    # agents/skills 正典名單（frontmatter 生成）
│   ├── TECHNICAL-REFERENCE.md # 技術百科（含最小填寫清單）
│   └── multi-agent-guide / modularity / security-policy / cost-optimization / code-conventions
├── docs/
│   ├── INDEX.md               # 文件索引 + 五層知識地圖
│   ├── harness/               # 制度文件：診斷書、交接信、新專案驗收流程
│   ├── architecture/          # invariants.md（INV-* 硬規則）、domains.md
│   ├── decisions/             # ADR-0001 + 範本
│   ├── learnings/ERRORS.md    # 教訓管線（Pending → Active → invariants）
│   └── plans/                 # ExecPlan 規格 + active/ + completed/
├── scripts/                   # 機械閘門：acceptance-run / execplan-lint / check-doc-refs / retro-status
├── .github/workflows/         # harness-gates.yml CI（py-compile、secret-scan、execplan-lint、placeholder-gate）
├── state/                     # runtime（gitignored）：快照、hook 事件、5 份 JSONL 帳本（schema：SCHEMA.md）
└── .claude/
    ├── settings.json          # hooks 接線（6 事件）
    ├── rules/                 # 7 條常駐規則（always: true）
    ├── agents/                # 14 個 virtual agents
    ├── skills/                # 17 個 skills
    ├── protocols/             # lifecycle / handoff / review / maintenance
    ├── templates/             # 派工模板、init.sh 環境範本
    ├── hooks/                 # 7 hooks + _lib
    ├── commands/              # /last-word、/techdebt
    └── uiux/                  # UI 三階段（可選）
```

## 核心概念快速參考

| 概念 | 說明 | 正典文件 |
|------|------|---------|
| 正典層級 | 文件矛盾時的採信順序：frontmatter > 各 protocol > REGISTRY > invariants | `CLAUDE.md` |
| 派工三件套 | 目標動機／驗收條件／回報格式，缺一不派 | `.claude/rules/model-dispatch.md` |
| 驗證不自驗 | fresh-context agent 做 read-back／實跑／評審 | `model-dispatch.md` §5 |
| 熔斷 | 升降級走完仍失敗→帶軌跡問人，格式固定 | `.claude/rules/judgment-rubrics.md` §3 |
| ExecPlan | 跨模組/API 變更的 9 段計劃，10 階段生命週期 | `docs/plans/PLANS.md` |
| Handoff Marker | agent 結尾必為 `[HANDOFF:]`/`[VERIFY_FAILED:]`/`[HUMAN_ATTENTION_REQUIRED:]` | `.claude/protocols/handoff-protocol.md` |
| 紅黃綠分級 | harness 檔案的修改權限與備份驗證要求 | `.claude/protocols/harness-maintenance.md` |
| 煙霧測試 | hook 改動後 block/pass 雙情境黑箱實測 | `harness-maintenance.md` §4 |
| 範圍宣告 | 派工必附：允許讀／寫／禁觸／終止條件 | `delegation-templates.md` 通用規範 |
| 品質關卡 | 新增/改 agent 或 skill：重複審查＋雙向觸發測試＋baseline 對照；新增/擴編 standing rule：需求證據＋遙測標記＋90 天複審 | `harness-maintenance.md` §6 |
| 遙測標記 | 規則命中當下發出行內標記（`RULE_FIRED`／`RULE_SKIPPED`／`ESCALATION`），收割進 `state/rule-events.jsonl`——命中率可量測，零命中規則面臨降級 | `handoff-protocol.md`「行內輔助標記」 |
| 五維度體檢 | Instructions/Tools/Environment/State/Feedback 缺一不完整 | `harness-maintenance.md` §7 |
| Red Flags | 合理化話術對照表；違反字面即違反精神 | `judgment-rubrics.md` §7 |

## 能力極限（誠實條款）

拆解、隔離驗證、多答案評審能把弱模型的**執行品質**逼近高階模型；**目標對不對**補不了。品味與美感決策、模糊商業判斷、無法驗證的長鏈推理——制度的答案是明確的出口（多候選交人選、明說需要人類決策、標註信心與未確認），而不是假裝能做。完整清單見 `docs/harness/DIAGNOSIS.md` §四。

## 參考資料

- [Anthropic — Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Anthropic — 官方 skills repo（skill-creator 方法論來源）](https://github.com/anthropics/skills)
- [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering)（五子系統模型來源）
- [obra/superpowers](https://github.com/obra/superpowers)（Red Flags 反合理化與 skill TDD 模式來源）
- [revfactory/harness](https://github.com/revfactory/harness)（雙向觸發測試量化來源）
- Addy Osmani — Loop Engineering（maker/verifier 分離、gate-softening 禁令的理論源頭）
- Mitchell Hashimoto — Harness Engineering
- Andy Matuschak — Evergreen Notes（知識管線設計參考）
