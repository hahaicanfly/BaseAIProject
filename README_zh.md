# BaseAIProject — AI Harness Engineering 基礎模板

https://hahaicanfly.github.io/BaseAIProject/share/ai-journey-story/

> [English](README.md) | 繁體中文
> **不是工程師？** 從 [`docs/PLAIN/START-HERE_zh.md`](docs/PLAIN/START-HERE_zh.md) 開始 —— 一樣的流程，沒有術語，什麼都不用背。

## 這是什麼（30 秒版）

一份可以直接 fork 的 **Claude Code AI 開發治理模板**。它把「怎麼派工、怎麼驗證、怎麼防失控、怎麼累積教訓」變成模型真的會讀的檔案、以及真的會觸發的 hook —— 讓 AI 在沒有人盯著每一步的情況下，也能產出穩定、可驗證、不失控的結果。

你會拿到：**14 個專職 agent**、**17 個觸發式 skill**、**橫跨 8 個事件的 10 個 hook**（1 個會攔截、9 個只觀察）、**3 份依模型分層的規則 pack**、**7 支讓宣稱可被查證的腳本**、**9 條硬性 invariant**，以及一條把錯誤變成強制規則的教訓管線。

**三步上手：**

1. **Fork 後填實** —— 替換 `{{PROJECT_NAME}}` 這類佔位符，把你的 build/test/lint 指令填進 `CLAUDE.md` Quick Commands（環境初始化範本：`.claude/templates/init.sh.template`）。可執行的驗證指令是成功率最大的單一槓桿。
2. **啟用防線** —— `chmod +x .claude/hooks/*.py`，然後照 `.claude/protocols/harness-maintenance.md` §4 跑煙霧測試。攔截情境**和**放行情境都要測。
3. **試車驗收** —— 照 `docs/harness/NEW-PROJECT-VALIDATION.md` 用一個 30 分鐘的小任務走完整流程（開分支 → 計畫 → 派工 → 審查 → 寫回教訓）。這一趟過了，才算能真的拿來用。

語言慣例：AI 會讀的制度檔一律是**英文正典**；給人看的繁體中文版放在同目錄的 `_zh` 檔，或鏡像在 `agent_docs/zh/`。

---

## 這個專案解決什麼問題

AI 主導的開發有三種失效模式。每一種都配一道實體防線，而不是一句勸告。

| 失效模式 | 對應的防線 |
|---|---|
| **文件說的 ≠ 事實** —— 規則寫了但從沒執行、防線部署了但從沒真的觸發 | hook 一律黑箱煙霧測試；每個引用都驗證存在；驗收由全新 context 執行 |
| **弱模型失焦** —— 文件互相矛盾，採信哪一份全憑運氣 | 正典層級（每類事實只有一個來源，其餘只能引用）；觸發詞互斥設計 |
| **知識蒸發** —— 教訓沉進聊天記錄，同一個坑踩三次 | 教訓管線：踩坑 → `ERRORS.md` → 人審 promote → 機械化成 invariant + guard |

## 核心設計哲學

1. **指揮官不下場幹活。** 主對話只負責決策、拆解、派工、裁定驗收、跟你溝通。大量讀檔、掃 repo、查資料一律交給子 agent，回報只帶結論與 `file:line`，不貼原文。
2. **驗收不得自證。** 實作者無權宣告自己的產出通過。一律由全新 context 的 agent 做回讀、真的把測試跑起來、或給出獨立的第二意見。
3. **常駐層是預算，而且這個預算是被強制執行的。** 每個 session 會載入什麼，由 `INV-ARC-001` 設上限、由 `scripts/context-budget.py` 量測。往常駐層加一行，現在會有一個數字跟著。
4. **判斷力外化。** 何時升級模型、什麼才算做完、何時該停下來問、什麼訊號代表走錯路 —— 全部寫成「可觀察訊號 → 動作」並附正反例，讓弱模型照本執行。
5. **誠實條款。** 品味、模糊的商業判斷、沒有事實可對照的長推理鏈，是弱模型會垮掉的地方。制度為每一種都指定了出口（給候選讓人選、標為未確認、找第二意見），而不是硬撐。

## 能力總覽

| 子系統 | 規模 | 一句話 |
|---|---|---|
| 規則投遞 | 3 份 tier pack + 1 份全域常駐規則 | 規則份量對齊執行模型；`security.md` 每個 tier 都載入 |
| 虛擬團隊 | 14 個 agent（4 opus + 10 sonnet） | 職責互斥；模型分派以 frontmatter 為正典 |
| Skills | 17 個 | 觸發式工作流；最大的幾個改走 `references/` 而非整份載入 |
| Hooks | 橫跨 8 個事件的 10 個 + 2 個共用模組 | 1 個 enforce（exit 2，攔截經實測）+ 9 個 sentinel |
| Protocols | 5 份 | ExecPlan 生命週期、交接標記、審查 SOP、harness 維護、1 份未接線草案 |
| 機械閘門 | 9 支腳本 + 6 job CI | 8 支檢查 + 1 支唯讀翻譯器；`harness-gates.yml` 每個 PR 重跑 |
| 硬規則 | 9 條 invariant | 5 git + 3 security + 1 architecture，每條都有 CHECK 指令與負責的 hook |
| 狀態帳本 | 8 個 JSONL + 2 個 JSON + 2 個子目錄 | 派工、驗收結果、規則命中率不隨 session context 消失（`state/SCHEMA.md`） |
| 知識系統 | 5 層 | 教訓／硬規則／ADR／session 快照／原生記憶，各有各的權限 |

## 各子系統

### 1. 指令與派工層

- **`CLAUDE.md`（93 行路由中心）** —— 正典層級、硬防線摘要、文件地圖。超過 100 行就強制精簡。
- **`.claude/rules/model-dispatch.md`** —— 可用的模型層級、派工三要素（目標與動機／驗收標準／回報格式，缺一就別派）、升級路徑（同一模型連續失敗兩次 → 升級一次 → 再失敗 → 熔斷問人）、回報契約（≤40 行；長產物寫檔、回報只給路徑）、驗收邊界（FAIL 只能引用可機械檢查的判準，風格意見進非阻斷欄）。
- **`.claude/rules/judgment-rubrics.md`** —— 七節可觀察判準，每節附正反例：何時升級、什麼算做完（含禁止放寬閘門）、何時熔斷（含無改善偵測 —— 連續兩輪 FAIL 集合相同就停）、走錯路的訊號、品質底線、能力極限，以及一張合理化話術對照表。
- **`.claude/templates/delegation-templates.md`** —— 六份派工模板，每份都帶範圍宣告（可讀／可寫／禁區／終止條件）與破壞性指令黑名單。
- **`.claude/commands/guided-start.md` + `scripts/translate-acceptance.py`** —— 給非技術需求的自然語言入口，加上一支事後把驗收證據翻成白話的唯讀腳本。

### 2. 分層規則投遞

同一份模板要服務 Haiku 到 Fable。弱模型需要明確流程，強模型給判準和判斷空間反而做得更好。所以常駐規則被組建成三份累加的 pack，session 開始時注入對的那一份。

| Tier | 模型 | 內含 |
|---|---|---|
| `strong` | Opus、Fable | 只有判準 —— 訊號 → 動作，不附範例 |
| `mid` | Sonnet | strong + 完整範例、品質底線、回報契約 |
| `light` | Haiku、任何未知 | mid + 防線：合理化話術表、硬性禁令、worktree 隔離 |

- **pack 是生成物**，絕不手寫 —— 改 `.claude/tiers/src/` 的片段後跑 `scripts/build-tier-packs.py`。pack 與來源不同步，acceptance 就會擋下來。
- **主對話的 tier 是宣告的，子 agent 的是偵測的。** 第一次回應前沒有任何 hook 看得到模型，所以由 `.claude/settings.json` 的 `HARNESS_TIER` 宣告（出廠值 `auto` = 交給猜測）。子 agent 的 `SubagentStart` payload 帶 `agent_type`，tier 直接從該 agent 的 frontmatter 判定。第二輪起 `tier-drift-check.py` 會把宣告值與真實 model id 對照，不符就更正。
- **任何未知一律落到 `light`** —— 多載規則只花 token，少載規則會出錯。
- **6 份非常駐規則檔原地保留**，作為附完整範例的全文參考。邊界情況需要查判準背後的理由時再讀。細節見 `.claude/tiers/README.md`。

### 3. 虛擬團隊（14 個 agent）

**Opus ×4**，保留給沒有標準答案的取捨：`architect`（系統設計、ADR）、`pm`（需求、優先級）、`security-reviewer`（安全稽核）、`plan-reviewer`（計畫審查）。

**Sonnet ×10**，負責清單型與模板化工作：`code-reviewer`（PR 把關 —— 唯一的 Decision 出口）、`qa-engineer`、`tech-lead`（重構顧問，**不**做 PR 把關）、研究三人組（`data-analyst` 量化 KPI、`market-researcher` 市場與消費者、`competitive-analyst` 競品逐項比較，觸發詞互斥）、`uiux-agent`（三階段入口）與 `ui-ux-designer`（Phase 3 產出）、`techdebt-scanner`、`workflow-optimizer`。

四個審查類 agent 透過 `review-protocol.md` 共用同一套輸出詞彙（Blocker／Warning／Suggestion + Pass／Block／Conditional Pass）。名冊以 `agent_docs/AI-TEAM-REGISTRY.md` 為正典，由 frontmatter 重新生成 —— 禁止手改個別欄位。

### 4. Skills（17 個）

- **開發流程** —— `feature-pipeline`（端到端）、`tdd-workflow`、`spectra-amplifier`（幫單薄的 PRD 補上驗收標準）
- **審查三人組**，觸發詞互斥 —— `code-review`（標準單 PR）、`multi-agent-review`（高風險改動三位專家並行）、`pr-review-cycle-mob`（成本分層 cascade）
- **安全與品質** —— `security-audit`（OWASP）、`techdebt-scanner`、`harness-eval`（harness 成熟度 0–100 分）
- **知識與交接** —— `pr-retro`（merge 後萃取教訓）、`context-aggregator`（多來源交接摘要）、`gen-app-map`（技術棧無關的專案地圖）
- **Skill 工程** —— `skill-creator-plus`（取代基礎版 `skill-creator`）：意圖捕捉、重疊檢查、`validate_skill.py` 機械驗證、雙向觸發測試、eval 迭代
- **UI 與圖表** —— `beautiful-mermaid`（Mermaid → 終端 ASCII／SVG）、`ui-ux-pro-max`（設計系統生成器，含檢索腳本與設計資料庫）、`frontend-design`（設計哲學，Compose 範例附跨技術棧等價寫法）

最大的四個 skill 在 `SKILL.md` 只留一份簡短路由，內容放進 `references/`，需要時才載入。`SKILL.md` 長到 150 行以上時就照這個形狀做 —— 本體雖然不是常駐內容，但**每次被調用都要整份付費**。

### 5. 實體防線（Hooks）

| Hook | 事件 | 模式 | 職責 |
|---|---|---|---|
| `pre-tool-use-guard.py` | PreToolUse(Bash) | **enforce**（exit 2） | 攔截：直接 commit 到 master/main、force-push、`reset --hard origin`、讀取**與 git add** 機密檔、所有 `curl|sh` 變體、`rm -rf /` |
| `post-edit-lint.py` | PostToolUse(write) | sentinel | INV 樣式快掃（fork 後填 `QUICK_CHECKS`） |
| `pre-compact-snapshot.py` | PreCompact | sentinel | 把 session 快照寫進 `state/session-handoffs/` |
| `delegation-ledger.py` | PreToolUse(Task/Agent) | sentinel | 記錄每一次派工，以及有沒有附驗收標準 |
| `post-bash-commit-ledger.py` | PostToolUse(Bash) | sentinel | 把每個真實 commit 連回它的 session |
| `session-activation-check.py` | SessionStart | sentinel | 模板啟用槽位還沒填完就出聲提醒 |
| `session-tier-inject.py` | SessionStart | sentinel | 注入所宣告 tier 的規則 pack |
| `subagent-tier-inject.py` | SubagentStart | sentinel | 依該 agent 自己 frontmatter 的模型注入對應 pack |
| `tier-drift-check.py` | UserPromptSubmit | sentinel | 第二輪起比對宣告 tier 與真實 model id，不符就更正 |
| `stop-retro-logger.py` | Stop／SubagentStop | sentinel | 把 `[VERIFY_FAILED:*]` 收進 `ERRORS.md`、遙測標記收進 `state/rule-events.jsonl`；引用在 code span 裡的標記豁免；墓碑帳本防重複 |

共用模組 `_lib.py` 與 `tier_resolve.py` 由 hook import，不掛在事件上。

**用血換來的鐵律：** 任何新增或修改 hook，都必須做黑箱煙霧測試 —— 攔截情境預期 exit 2、放行情境預期 0（指令見 `harness-maintenance.md` §4）。本專案的 guard 曾經以「紙上防線」的狀態放了好幾個月沒被發現，被少了執行權限和寫錯 exit code 雙重停用。

### 6. 機械閘門

九支腳本，讓宣稱可以被當場查證，而不是被相信：

| 腳本 | 它能一槌定音的事 |
|---|---|
| `acceptance-run.py` | 執行 ExecPlan 的驗收區塊並存下證據 |
| `execplan-lint.py` | 對照 `PLANS.md` 規格檢查 ExecPlan 結構 |
| `check-doc-refs.py` | 驗證正典裡每個路徑與章節引用都存在（死引用是幻覺的餌） |
| `context-budget.py` | 量測常駐層對照 `.claude/tiers/budget.json` —— `INV-ARC-001` 背後的執行者 |
| `build-tier-packs.py` | 重建 tier pack；`--check` 在 pack 與來源漂移時失敗 |
| `check-mirror-parity.py` | 比對每份 `_zh` 鏡像與原文的章節、子章節、表格列結構——抓出仍在描述已被替換機制的鏡像 |
| `check-hook-doc-coupling.py` | hook 靠某份文件的字面字串做判斷卻未宣告該依賴時，讓它失敗 |
| `retro-status.py` | 依字面定義計算精簡觸發線的各項數字 |
| `translate-acceptance.py` | **不是閘門** —— 唯讀、永遠 exit 0，只把既有驗收證據翻成白話 |

`.github/workflows/harness-gates.yml` 在每個 PR 重跑可檢查的子集（py-compile、secret-scan、execplan-lint、mirror-parity、hook-coupling、placeholder-gate）。

### 7. 知識管理（地圖在 `docs/INDEX.md`）

```
踩坑 ──→ ERRORS.md（Pending；hook 自動收割 + 人工追加）
        │ 人類週審 promote
        ▼
   Active Lessons（含 Why + 怎麼套用）
        │ 其中可機械化者
        ▼
invariants.md（INV-*）──→ guard hook（實體攔截）
```

另外三層：`docs/decisions/ADR-*`（人類核可的架構決策）、`state/session-handoffs/`（PreCompact 自動快照）、Claude Code 原生記憶（**只准放跨 session 指標** —— 教訓全文一律走 `ERRORS.md`）。

維護權限分紅／黃／綠三級（`harness-maintenance.md`）：教訓隨時可追加，行為指引備份後可改，常駐規則與防線動之前必須先問人。

`docs/PLAIN/` 是白話衍生層，不是管線的第六站 —— 它是規則檔的唯讀翻譯。跟來源牴觸時，以來源為準。

### 8. UI/UX 三階段流程（選用）

Wireframe → Critique → Implementation，以閘門形式強制（`.claude/uiux/WORKFLOW.md`），附風格規範範本與六份 prompt 模板。沒有前端的專案可以把 `.claude/uiux/` 和兩個 UI agent 整個刪掉。

## 快速開始（fork 後五步）

1. **替換佔位符。** 搜尋 `{{PROJECT_NAME}}`、`{{PROJECT_TAGLINE}}`；填好 `CLAUDE.md` 的 Quick Commands 與 Tech Stack；照 `.claude/templates/init.sh.template` 初始化環境。還含 `{{}}` 的檔案一律視為未啟用，模型會自動跳過。
2. **最小可用填實。** `agent_docs/TECHNICAL-REFERENCE.md` 檔頭列了 5 個欄位（核心任務、技術棧四象限、頂層模組、API base URL、認證方式）。填完這些就解鎖它的「必讀」地位，其餘可以之後再補。
3. **煙霧測試 hooks。** `chmod +x .claude/hooks/*.py`，然後照 `harness-maintenance.md` §4 實測攔截與放行兩種情境。
4. **跑一次試車。** 照 `docs/harness/NEW-PROJECT-VALIDATION.md` 用一個 30 分鐘小任務走完整流程，每一步都有可觀察的判準。
5. **依技術棧客製。** 往 `invariants.md` 加 INV-SEC／INV-TEST／INV-API 規則、填 `post-edit-lint.py` 的 `QUICK_CHECKS`、填 `gen-app-map` 的掃描目標表，有前端的話再填 uiux 風格規範。如果你知道自己主要會跑哪個模型，就在 `.claude/settings.json` 設定 `HARNESS_TIER`；否則維持 `auto`。

## 目錄結構

```
BaseAIProject/
├── CLAUDE.md                  # 路由中心：正典層級、硬防線、文件地圖（≤100 行）
├── GEMINI.md                  # Antigravity (agy) agent 橋接協議
├── agent_docs/                # 詳細教學層
│   ├── AI-TEAM-REGISTRY.md    # agent/skill 正典名冊（由 frontmatter 生成）
│   ├── TECHNICAL-REFERENCE.md # 技術百科（含最小填實清單）
│   └── multi-agent-guide / modularity / security-policy / cost-optimization / code-conventions
├── docs/
│   ├── INDEX.md               # 文件索引 + 五層知識地圖
│   ├── harness/               # 診斷書、給未來 session 的信、新專案驗證流程
│   ├── architecture/          # invariants.md（INV-*）、domains.md
│   ├── decisions/             # ADR-0001 + 範本
│   ├── learnings/ERRORS.md    # 教訓管線（Pending → Active → invariants）
│   ├── PLAIN/                 # 白話層：START-HERE、CLAUDE.md 對照卡
│   └── plans/                 # ExecPlan 規格 + active/ + completed/
├── scripts/                   # 8 支機械閘門 + translate-acceptance（唯讀，非閘門）
├── .github/workflows/         # harness-gates.yml CI（6 個 job）
├── state/                     # 執行期，已 gitignore：8 個 JSONL 帳本 + acceptance/ + session-handoffs/
└── .claude/
    ├── settings.json          # hook 接線（8 個事件）+ HARNESS_TIER 宣告
    ├── tiers/                 # 3 份生成 pack + src/ 片段 + budget／model-map 配置
    ├── rules/                 # security.md（常駐）+ 6 份全文參考檔
    ├── agents/                # 14 個虛擬 agent
    ├── skills/                # 17 個 skill
    ├── protocols/             # lifecycle / handoff / review / maintenance
    ├── templates/             # 派工模板、init.sh 環境範本
    ├── hooks/                 # 10 個 hook + 2 個共用模組
    ├── commands/              # /guided-start、/last-word、/techdebt
    └── uiux/                  # UI 三階段流程（選用）
```

## 核心概念速查

| 概念 | 意思 | 正典文件 |
|---|---|---|
| 正典層級 | 文件矛盾時的採信順序：frontmatter > protocol > REGISTRY > invariants | `CLAUDE.md` |
| Tier pack | 常駐規則，份量對齊執行模型；主對話用宣告的，子 agent 用偵測的 | `.claude/tiers/README.md` |
| 常駐層預算 | `CLAUDE.md` + `security.md` + 注入的 pack 必須塞得進當前模式的上限 | `INV-ARC-001` |
| 派工三要素 | 目標與動機／驗收標準／回報格式 —— 缺一就別派 | `model-dispatch.md` |
| 驗收不得自證 | 由全新 context 的 agent 回讀、實跑、或審查 | `model-dispatch.md` §5 |
| 熔斷 | 走完整條升級路徑仍失敗 → 帶著失敗紀錄，用固定格式問人 | `judgment-rubrics.md` §3 |
| ExecPlan | 跨模組／API 改動用的 9 節計畫書，配 10 階段生命週期 | `docs/plans/PLANS.md` |
| 交接標記 | agent 的最終回應必須以 `[HANDOFF:]`／`[VERIFY_FAILED:]`／`[HUMAN_ATTENTION_REQUIRED:]` 結尾 | `handoff-protocol.md` |
| 紅／黃／綠分級 | harness 檔案的修改權限與備份要求 | `harness-maintenance.md` §1 |
| 煙霧測試 | 任何 hook 改動後，攔截與放行兩種情境都要黑箱實測 | `harness-maintenance.md` §4 |
| 範圍宣告 | 每次派工都要寫明：可讀／可寫／禁區／終止條件 | `delegation-templates.md` |
| 品質閘門 | 新增 agent／skill → 重疊審查 + 雙向觸發測試；新增常駐規則 → 要證據 + 遙測 + 90 天回審 | `harness-maintenance.md` §6 |
| 遙測標記 | 規則命中當下就地發出 `RULE_FIRED`／`RULE_SKIPPED`／`ESCALATION`，收割進 `state/rule-events.jsonl` —— 零命中的規則面臨降級 | `handoff-protocol.md` |
| 五維體檢 | Instructions／Tools／Environment／State／Feedback —— 缺一即不完整 | `harness-maintenance.md` §7 |
| Red Flags | 合理化話術對照表；違反字面就是違反精神 | `judgment-rubrics.md` §7 |

## 能力極限（誠實條款）

拆解、隔離驗證、多答案審查，能把弱模型的**執行品質**拉近高階模型，但它們修不好**目標本身對不對**。品味、模糊的商業判斷、無法驗證的長推理鏈 —— 制度給的答案是一個明確的出口（給候選讓人選、明講這需要人來決定、標註信心水準與未確認項），而不是假裝辦得到。完整清單見 `docs/harness/DIAGNOSIS.md` §4。

## 參考來源

- [Anthropic — Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Anthropic — 官方 skills repo](https://github.com/anthropics/skills)（skill-creator 方法論來源）
- [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering)（五維模型來源）
- [obra/superpowers](https://github.com/obra/superpowers)（Red Flags 反合理化與 skill-TDD 模式來源）
- [revfactory/harness](https://github.com/revfactory/harness)（量化雙向觸發測試來源）
- Addy Osmani — Loop Engineering（maker/verifier 分離、禁止放寬閘門）
- Mitchell Hashimoto — Harness Engineering
- Andy Matuschak — Evergreen Notes（知識管線設計參考）
