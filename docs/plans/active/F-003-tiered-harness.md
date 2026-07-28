# ExecPlan: F-003 — Tiered Harness (依模型等級分層的 harness 架構)

| Field | Value |
|------|-----|
| Status | in_progress |
| Owner Agent | dev (main conversation) |
| Branch | feat/tiered-harness |
| Created | 2026-07-28 |
| Last Updated | 2026-07-28 |
| Linked PR | (filled in at merge time) |

## 1. Goal

把目前「單一份、為弱模型設計、全量常駐」的 harness，改造成**依主對話模型等級載入不同重量規則**的分層架構：強模型（Opus / Fable）拿到輕量判準，弱模型（Haiku / Sonnet）維持現有完整 SOP；規則內容以**搬遷為主、刪除為輔**，讓同一份模板同時服務兩代模型能力。可量測成果：預算門檻做成**可切換模式的配置檔**（非硬編），預設 `balanced` 模式下 strong tier 常駐注入量從 627 行 / 32,739 字元降到 ≤250 行 / ≤14,000 字元、mid ≤24,000 字元（單位一律為 **Unicode 字元數**，非位元組；中文在 UTF-8 佔 3 bytes，字元數較接近 token 數）；使用者可依實際體驗切換模式或直接改數值而不需改動任何程式碼；且 light tier 可得的規則內容經逐條對照證明無語意遺失。

Non-Goals / Out of Scope:
- **不精簡 agent / skill roster**——使用者 2026-07-28 明確指示「內含的 agents skills 調用次數少是正常現象」，`state/delegations.jsonl` 的分佈不得作為刪減依據；本計畫不刪任何 agent 或 skill。
- 不修改 hooks 的攔截語意（INV-GIT-* / INV-SEC-* 的 block 條件與 exit code 一律不動）；本計畫只**新增** SessionStart / SubagentStart 的注入邏輯，且兩者皆為 sentinel（一律 exit 0，不阻斷）。
- 不改寫 `docs/architecture/invariants.md` 既有條目；新增 INV-ARC-001（常駐層預算）留待 Phase 3 後以獨立提案送審。
- 不翻譯或改寫 `*_zh.md` 鏡像的既有譯文，僅在檔案結構變動時跟隨調整路徑。
- 不做 auto-memory 與 ERRORS.md 的職責重劃（原分析 F 軸）——依賴本計畫的分層結果，另開 ExecPlan。
- 不引入任何新的第三方依賴；所有新腳本限用 Python 3 標準庫。

Clarify-first: 2/4 fields missing → asked & confirmed 2026-07-28。原始請求缺 success metric 與 non-goals，經使用者回覆「會使用模板的 agents & ai models 不會只有高階模型…因此預期要對不同模型等級做不同的 harness 框架設計」補齊方向與非目標；§8 的 Q1–Q4 已於同日全數裁決，success metric 據以定案（見 Scope Baseline v2）。

Scope Baseline: target user=fork 本模板的新產品開發專案，其主對話與子 agent 涵蓋 Haiku / Sonnet / Opus / Fable 四級 / success metric=strong tier 常駐量 ≤250 行且 light tier 內容無語意遺失（詳見 §5） / trigger condition=使用者裁定採用分層路線後立即啟動 / confirmation source=使用者 2026-07-28 原話「預期要對不同模型等級做不同的 harness 框架設計，等未來基礎模型能力提升才會收斂」+「其餘的都可以依照分析結果進行優化調整」。
- v2 (2026-07-28): success metric 改為**可調式**——門檻不再是固定驗收值，而是 `.claude/tiers/budget.json` 的模式配置，預設 `balanced` 沿用原數值；成功定義同時要求「模式可切換且切換後驗收仍可執行」。子 agent 分層由靜態改為**動態**（SubagentStart hook）。來源：使用者原話「成功門檻做成可調式 -> 可選模式…也可依照實際體驗切換或改數值」「子 agent 也動態分層」。

## 2. Context

- 觸發來源：Anthropic 官方文章 *The New Rules of Context Engineering for Claude 5 Generation Models*（2026）指出對 Opus 5 / Fable 5 移除 80%+ system prompt 無效能損失，並提出六項轉向：規則→判準、範例→介面設計、前置→漸進揭露、重複→單一來源、手動記憶→auto-memory、簡單規格→高保真參照。
- 本專案的設計前提與之相反：`docs/harness/DIAGNOSIS.md` §IV 明文將 harness 定位為「把弱模型執行品質拉近強模型」。兩者並非互斥，缺的是**分層**。
- `agent_docs/TECHNICAL-REFERENCE.md` 目前仍為未活化模板（全檔為未填佔位符），依 CLAUDE.md「Activation Status」略過，本計畫不引用其章節錨點。
- 受影響模組：`CLAUDE.md`、`.claude/rules/*.md`（7 檔）、`.claude/hooks/session-activation-check.py`、`.claude/settings.json`（新增 SubagentStart 掛載）、`.claude/templates/delegation-templates.md`、`.claude/skills/*/SKILL.md`（>150 行者）、`scripts/`、新增 `.claude/tiers/`。
- 相關前例：F-001（harness 可驗證性批次）建立了 `scripts/acceptance-run.py` 與 `state/acceptance/` 證據鏈，本計畫沿用同一驗收機制。
- 已完成的技術前提調查（2026-07-28 主對話實測）：
  - SessionStart hook 的 stdout **會注入 context**（`session-activation-check.py` docstring 自述，且本 session 開場實際觀察到注入結果）——這是分層注入的載體。
  - 主對話模型可從 `~/.claude/settings.json` 的 `model` 欄位讀取（實測值 `opus[1m]`），且 `/model` 指令會寫回該檔。
  - 環境變數中**無** `CLAUDE_MODEL`；存在 `CLAUDE_EFFORT`、`CLAUDE_CODE_SESSION_ID` 等。
- 官方 hooks 文件查證結果（2026-07-28，https://code.claude.com/docs/en/hooks），三項對本計畫具決定性：
  - **只有 `SessionStart` 的 payload 會帶 `model` 欄位，且官方明文「不保證存在」（optional）**；其餘所有 hook event 的 payload 都不含模型資訊。官方同時確認無 `$CLAUDE_MODEL` 環境變數（與上述實測一致）。→ 這使 §3 的 fallback 鏈成為必要設計而非防禦性冗餘，並讓 Phase 1 spike 的目標從「是否存在」收斂為「本環境實際是否帶此欄位」。
  - **`SubagentStart` hook 存在**：於子 agent 生成時觸發，matcher 為 agent 名稱（如 `Explore`、`security-reviewer`），payload 含 `agent_type` 與 `agent_id`，輸出支援 `hookSpecificOutput.additionalContext` 注入。屬「context only」事件，**無法阻斷生成**（exit 2 僅顯示 stderr）。→ 子 agent 動態分層可行；且因其 payload 不含模型，tier 需由 `agent_type` 反查 `.claude/agents/<name>.md` frontmatter 的 `model` 欄位決定。
  - `SessionStart` 同樣支援 `hookSpecificOutput.additionalContext`（較現行純 stdout 注入更明確），注入時機為第一個 prompt 之前。
- **已知限制（非缺陷，需寫入文件）**：tier 於 session 開始時決定一次；session 中途以 `/model` 切換模型**不會**重新注入 tier pack。`/model` 會寫回 `~/.claude/settings.json`，故下一個 session 才生效。

## 3. Constraints

- `INV-GIT-002`（禁止直接 commit 到 master/main）、`INV-GIT-005`（新分支必須從 master 切出）：全程在 `feat/tiered-harness` 上作業。
- `INV-SEC-003`（敏感檔不得進 staging）：新增腳本不得讀寫 `.env` 或任何 secret 路徑。
- `.claude/protocols/harness-maintenance.md` §1 檔案分級：本計畫觸及的 `CLAUDE.md`、`.claude/rules/*.md`、`.claude/hooks/*.py` 全屬 **Red tier**——每次改動前需備份（或確保工作區乾淨、由 git 當還原點），改後需 fresh-context read-back；hook 改動另需 §4 smoke test 的 block/pass 雙情境驗證。使用者於 2026-07-28 對話中的授權適用 Red-tier 例外條款，但備份與驗證程序不豁免。
- `.claude/agents/*.md`、`.claude/skills/`、`.claude/templates/` 屬 **Yellow tier**：備份 → 改 → fresh-context read-back。
- 變更影響評估對照 `docs/architecture/domains.md`：本計畫屬 harness 內部調整，不觸及任何產品程式碼路徑。
- **Fail-safe 硬規則**：tier 偵測失敗、無法讀取、或回傳非預期值時，一律 fallback 到最保守的 light tier（全量載入）。漏載規則的風險高於多載規則。

## 4. Step-by-step Plan

### Phase 0 — 建立可執行閘門與量測基準（本 repo 目前零可執行驗證）

1. [ ] 確認基線：於乾淨工作區記錄常駐層現況數值（行數、字元數）寫入 §6，作為後續 diff 的對照點
2. [ ] 新增預算配置檔 `.claude/tiers/budget.json`：定義**可切換模式**，每個模式給三個 tier 各一組 `max_lines` / `max_chars`。內建至少三檔（`strict` / `balanced`（預設） / `generous`），`balanced` 沿用 strong 250 行 / 14,000 字元、mid 24,000 字元、light 不設上限。含 `active_mode` 欄位供使用者一行切換，數值亦可直接覆寫（Q1 裁決）
3. [ ] 新增 `scripts/context-budget.py`：計算指定 tier 的實際行數與字元數並與配置比對，超標時 exit 非零並列出各檔佔比。門檻**一律讀 `budget.json`**，不硬編；`--max-chars` 僅作為臨時覆寫。另提供 `--self-test`（驗證 tier 偵測與配置解析）與 `--list-modes`
4. [ ] 填寫 `CLAUDE.md` Quick Commands 區塊：本 repo 為文件型專案，build/lint/test 對應 `execplan-lint.py` / `check-doc-refs.py` / hook smoke test 與 `context-budget.py`（Red tier，需備份）
5. [x] ~~修復規則遙測管線~~ → **改為：查證管線並定位真正缺口**。原假設「採收器壞掉」經 end-to-end 測試證偽：以合格 fixture 餵入 `stop-retro-logger.py`，`RULE_FIRED` 與 `ESCALATION` 兩類標記皆正常寫入 `state/rule-events.jsonl`。真正缺口在**發射端**——模型幾乎從不主動輸出這些標記，故帳本恆空。因採收器無需修改，本步驟不動 Red-tier 檔案；發射端的補救方案見 §8 Q6
6. [ ] 驗收 Phase 0：`context-budget.py` 對現況執行必須 FAIL（證明門檻有效）；切換 `active_mode` 後門檻確實改變（證明可調式生效）；遙測修復後**立即進入 Phase 1，不設觀察期**（Q3 裁決）

### Phase 1 — Spike：確定 tier 偵測機制

7. [ ] 實測本環境 SessionStart hook 收到的原始 payload 是否實際帶 `model` 欄位（官方標示為 optional）：暫時性地將 `read_stdin_json()` 結果完整寫入 `state/` 一次性樣本檔後移除該暫時程式碼
8. [ ] 依實測結果確定偵測來源優先序並寫入 §7 DEC-4：(a) SessionStart payload 的 `model` → (b) `~/.claude/settings.json` 的 `model` → (c) fallback light tier
9. [ ] 定義 tier 對照表 `.claude/tiers/model-map.json`：`opus*` / `fable*` → strong；`sonnet*` → mid；`haiku*` → light；未知或缺值 → light。存為獨立資料檔（非硬編在 hook 內），未來模型世代更新時無需改程式
10. [ ] 決定子 agent 的 tier 判定法：`SubagentStart` payload 只有 `agent_type`、不含模型，故由 `agent_type` 反查 `.claude/agents/<name>.md` frontmatter 的 `model` 欄位 → 套用同一張 `model-map.json`。**三個邊界情境必須明確定義**：(i) frontmatter 無 `model`（繼承主對話）→ 沿用當前 session tier；(ii) 內建 agent（`Explore` / `general-purpose` / `Plan`，無對應檔案）→ light；(iii) 檔案讀取失敗 → light
11. [ ] 驗收 Phase 1：以偽造的 model 值餵入偵測函式，確認回傳 strong/mid/light；餵入空值、亂碼、不存在的 agent_type，確認全數回傳 light

### Phase 2 — 建立 tier packs 並執行常駐層搬遷

12. [ ] 建立 `.claude/tiers/{strong,mid,light}.md` 三份 tier pack，以及三者共用的常駐核心
13. [ ] 重劃常駐層：`.claude/rules/` 僅保留「每個 session 第一個決策就需要」者（初步判定：`security.md` + CLAUDE.md 決策樹），其餘 5 檔的 `always: true` 降級，內容依重量搬入對應 tier pack
14. [ ] 語氣分層改寫：`judgment-rubrics.md` §7（Red Flags 話術表）、§2.5（gate-softening 禁令）、literal-text clause 等**防禦性條款移入 light/mid pack**；strong pack 只保留「可觀測訊號 → 動作」骨架。此步為搬遷非刪除
15. [ ] 白話註解外移（Q2 裁決）：常駐層內嵌的 26 處「白話:」註解全部搬到 `docs/PLAIN/`；**light 與 mid pack 於對應段落保留一行引用路徑提示**（指向 `docs/PLAIN/` 的具體檔案與錨點），strong pack 不含此提示
16. [ ] 改寫 `session-activation-check.py`（或新增獨立 hook）：依 Phase 1 的偵測結果，以 `hookSpecificOutput.additionalContext` 注入對應 tier pack（優於現行純 stdout）。維持 sentinel 性質，一律 exit 0（Red tier，需 smoke test）
17. [ ] 驗收 Phase 2：三個 tier 分別跑 `context-budget.py` 對照 `balanced` 模式門檻；light 不設上限但需以逐條對照表證明涵蓋現有 7 檔全部條款

### Phase 3 — 子 agent 動態分層與 skill 漸進揭露

18. [ ] 新增 `.claude/hooks/subagent-tier-inject.py` 並掛載到 `settings.json` 的 `SubagentStart`（matcher `.*`）：依步驟 10 的判定法決定 tier，以 `additionalContext` 注入對應 pack。**sentinel 性質，所有路徑 exit 0**——此事件無法阻斷生成，且注入失敗不得影響子 agent 運作（Q4 裁決；Red tier，需 smoke test）
19. [ ] `.claude/templates/delegation-templates.md` 同步調整：說明 SOP 摘要已由 SubagentStart 自動注入，委派 prompt 不需重複附帶（避免與官方「重複→單一來源」原則相悖，也避免雙重注入）
20. [ ] 拆分 >150 行的 SKILL.md：`ui-ux-pro-max`(394)、`frontend-design`(281)、`pr-review-cycle-mob`(190)、`spectra-amplifier`(189)、`tdd-workflow`(184)、`beautiful-mermaid`(176)、`feature-pipeline`(171)、`gen-app-map`(168) 共 8 檔，改為 SKILL.md 路由（≤80 行）+ `references/*.md`，比照既有 `security-audit` 結構（Yellow tier）
21. [ ] 更新 `agent_docs/AI-TEAM-REGISTRY.md`、`docs/INDEX.md`、`CLAUDE.md` 文件地圖以反映新結構；並在 `CLAUDE.md` 記載「tier 於 session 開始時決定一次，中途 `/model` 切換需開新 session 才生效」此一已知限制
22. [ ] 全量 read-back 驗收：fresh-context agent 逐項比對「搬遷前後語意無遺失」，並確認所有引用路徑存在
23. [ ] 更新 `docs/harness/LETTER-TO-FUTURE-SESSIONS.md` §3 交接清單與 `docs/learnings/ERRORS.md`（Green tier）

## 5. Verification Strategy

```acceptance
plan-lint: python3 scripts/execplan-lint.py docs/plans/active/F-003-tiered-harness.md
doc-refs: python3 scripts/check-doc-refs.py
budget-strong: python3 scripts/context-budget.py --tier strong
budget-mid: python3 scripts/context-budget.py --tier mid
modes: python3 scripts/context-budget.py --list-modes
tier-detect: python3 scripts/context-budget.py --self-test
guard-block: python3 -c "import json,subprocess;h='.claude/hooks/pre-tool-use-guard.py';import sys;sys.exit(0 if subprocess.run([h],input=json.dumps({'tool_name':'Bash','tool_input':{'command':'ca'+'t .e'+'nv'}}),capture_output=True,text=True).returncode==2 else 1)"
subagent-inject: python3 -c "import json,subprocess,sys;h='.claude/hooks/subagent-tier-inject.py';r=subprocess.run([h],input=json.dumps({'hook_event_name':'SubagentStart','agent_type':'security-reviewer','agent_id':'t1'}),capture_output=True,text=True);sys.exit(0 if r.returncode==0 and 'additionalContext' in r.stdout else 1)"
subagent-fallback: python3 -c "import json,subprocess,sys;h='.claude/hooks/subagent-tier-inject.py';r=subprocess.run([h],input=json.dumps({'hook_event_name':'SubagentStart','agent_type':'no-such-agent','agent_id':'t2'}),capture_output=True,text=True);sys.exit(0 if r.returncode==0 and 'light' in r.stdout else 1)"
budget-negative: python3 scripts/context-budget.py --tier light --max-chars 100 expect-fail
```

- 門檻來源：`budget-strong` / `budget-mid` 不帶 `--max-chars`，門檻一律由 `.claude/tiers/budget.json` 的 `active_mode` 決定——驗收因此跟著使用者選定的模式走，切換模式不需改動本 acceptance 區塊（Q1 裁決的機械化體現）。
- Manual golden path：(1) 於 `~/.claude/settings.json` 分別設為 opus / sonnet / haiku 各開一次新 session，確認 SessionStart 注入的 tier pack 正確且分量遞增；(2) 刻意將 model 欄位改為亂碼，確認 fallback 到 light tier 而非崩潰或空注入；(3) 於同一 session 分別委派給 `security-reviewer`（frontmatter opus → strong）與 `qa-engineer`（sonnet → mid），確認子 agent 收到的 pack 不同；(4) 切換 `budget.json` 的 `active_mode` 為 `strict`，確認 `context-budget.py` 門檻隨之改變。
- 語意無遺失證明：Phase 2 完成後，對「搬遷前 7 檔全文」與「light tier pack + 保留的常駐檔」做條款層級對照表，逐條標記 kept / moved-to-<tier> / deleted；deleted 項需逐條列出理由供人審。
- 依 `model-dispatch.md` §5，本計畫的驗收不得自證：Phase 2 與 Phase 3 的 read-back 由 fresh-context agent 執行。

## 6. Progress Log

- [2026-07-28 --:--] main-conversation 建立 ExecPlan；基線實測：常駐層 = CLAUDE.md 90 行 + rules 7 檔 537 行 = 627 行 / 34,786 **bytes**；agent+skill description 8,722 bytes；`state/rule-events.jsonl` 0 筆；skills 17 個中 14 個為單檔。
- [2026-07-28 --:--] dev 基線單位修正：初次記錄的 34,786 來自 `wc -c`（位元組），非字元。實測字元數為 **32,739**（中文於 UTF-8 佔 3 bytes）。`context-budget.py` 一律以 Unicode 字元計——對中文而言字元數較接近 token 數。門檻比例實質不變（14,000/32,739 ≈ 43%），Q1 裁決不受影響。
- [2026-07-28 --:--] dev Phase 0 步驟 4-6 完成：CLAUDE.md Quick Commands 填入 4 條 harness 自檢指令、產品層 build/test/lint 佔位符保留供 fork 使用；`session-activation-check.py` 警語修正（原句「未填 Quick Commands 前本 repo 沒有任何可執行驗證閘門」在閘門建立後已成假敘述），smoke test 3 情境 exit 0（正常 / 非 JSON / 空 stdin）。步驟 5 假設證偽，見下。
- [2026-07-28 --:--] dev **Phase 0 發現：遙測管線未壞**。以合格 fixture 對 `stop-retro-logger.py` 做 end-to-end 測試，`RULE_FIRED` 與 `ESCALATION` 皆正確寫入 `rule-events.jsonl`；帳本恆空的成因在發射端而非採收端。測試資料已清除，採收器一行未改。教訓記入 ERRORS.md，後續方案記為 §8 Q6。
- [2026-07-28 --:--] dev Phase 0 步驟 1-3 完成：切出 `feat/tiered-harness`、feature-list.json 新增 F-003、建立 `.claude/tiers/budget.json`（3 模式）與 `scripts/context-budget.py`。`--self-test` 5 checks 0 failed；`--list-modes` 正常；三個 tier 目前皆解析到同一組 8 檔 627 行 / 32,739 字元（tier pack 尚未建立，屬 Phase 2 前的預期狀態）。

## 7. Decision Log

- DEC-1: 採「分層」而非「瘦身」路線——使用者 2026-07-28 裁定模板需同時服務 Haiku/Sonnet 與 Opus/Fable，「等未來基礎模型能力提升才會收斂」。因此弱模型防禦條款一律降級保存，不刪除。
- DEC-2: tier pack 以 SessionStart hook 的 `additionalContext` 注入，而非新增 `always: true` 規則檔——後者是全域的，機制上無法依模型分流。
- DEC-3: 偵測失敗一律 fallback light tier（全量）——漏載規則的風險高於多載規則的 token 成本。官方文件確認 `model` 欄位為 optional，此 fallback 為必要設計。
- DEC-4: (Phase 1 步驟 8 後填入) tier 偵測來源的最終優先序。
- DEC-5: 預算門檻採**配置檔 + 可切換模式**而非固定驗收值（Q1 裁決）。理由：分層的最適門檻無法先驗得知，需依實際體驗調整；把門檻外部化後，調整不需改程式也不需改 acceptance 區塊。代價是驗收結果依賴 `active_mode`，故 §5 明列門檻來源以免日後誤讀。
- DEC-6: 白話註解外移 `docs/PLAIN/`，但 light/mid pack 保留**引用路徑提示**、strong pack 不保留（Q2 裁決）。理由：非技術使用者的可讀性需求與弱模型的規則需求高度重疊，兩者共用同一 tier；strong tier 的讀者不需要這層鷹架。
- DEC-7: 遙測修復後**不設觀察期**，直接進 Phase 2（Q3 裁決）。代價：無法以「哪條規則真的改變過行為」的資料驅動搬遷取捨，Phase 2 的分層判斷改以「是否為每個 session 第一個決策所需」的既有判準為準（LETTER §I.3）。遙測資料轉為事後驗證用途。
- DEC-8: 子 agent 採 `SubagentStart` hook 動態注入，而非委派模板靜態附帶（Q4 裁決）。理由：官方文件確認該 hook 存在且支援 `additionalContext`；動態方案讓 tier 隨 agent frontmatter 自動生效，新增 agent 時無需同步維護委派模板。因該事件 payload 不含模型，tier 改由 `agent_type` 反查 frontmatter 決定。

## 8. Open Questions

- Q1 (resolved 2026-07-28): 門檻改為可切換模式的配置檔，預設 `balanced` 沿用原提案數值 → 見 DEC-5、Phase 0 步驟 2。
- Q2 (resolved 2026-07-28): 白話註解外移 `docs/PLAIN/`，light/mid tier 保留引用路徑提示 → 見 DEC-6、Phase 2 步驟 15。
- Q3 (resolved 2026-07-28): 修完遙測直接進 Phase 2，不設觀察期 → 見 DEC-7、Phase 0 步驟 6。
- Q4 (resolved 2026-07-28): 子 agent 動態分層，以 `SubagentStart` hook 實作 → 見 DEC-8、Phase 3 步驟 18。
- Q6 (open, 非阻斷, 2026-07-28 Phase 0 發現): 規則遙測的採收器功能正常，但**發射端**失效——模型幾乎不主動輸出 `[RULE_FIRED:]` / `[RULE_SKIPPED:]`，因為該指示只是 `clarify-first.md` §1 與 `model-dispatch.md` §4 的括號附註，既無提醒也無強制。兩條路：(a) 把標記要求寫得更醒目——但那等於往常駐層加料，與本計畫方向直接衝突；(b) 放棄自陳式標記，改由可觀測行為反推（`delegation-ledger.py` 已用 regex 從委派 prompt 反推「三要素」是否齊備，同一手法可用 `AskUserQuestion` 工具呼叫反推 clarify-first 是否觸發）。**本計畫不處理**——超出 F-003 範圍，且 DEC-7 已將遙測定位為事後驗證用途。建議另開 ExecPlan 走 (b)。
- Q5 (open, 非阻斷): tier 只在 session 開始時決定一次，中途 `/model` 切換不會重新注入（官方機制限制，見 §2）。目前處理方式是寫進文件告知使用者。若日後認為此限制影響實際體驗，可評估以 `UserPromptSubmit` hook 週期性重檢——但那會在每輪對話增加成本，本計畫不採用。

## 9. Handoff Manifest

- Next agent: 人類審核者（lifecycle stage [3]：核准 §1–§5 後才切分支、status 改 in_progress）
- Required reading before resuming: `docs/plans/active/F-003-tiered-harness.md`（本檔）、`docs/harness/DIAGNOSIS.md` §IV、`.claude/protocols/harness-maintenance.md` §1 與 §4、`CLAUDE.md`「Canon Hierarchy」
- Current state marker: [HANDOFF: human-review]
