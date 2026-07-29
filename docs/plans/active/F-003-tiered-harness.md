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
20. [x] 拆分最大的 3 個 SKILL.md 為路由（≤80 行）+ 同目錄參考檔（Yellow tier）：`ui-ux-pro-max` 394→55、`security-audit` 306→69、`frontend-design` 281→79。範圍經使用者 2026-07-28 裁定縮減，其餘 5 檔（168–190 行）留在原地，理由見 DEC-12
20b. [x] `.claude/settings.json` `env` 區塊出廠帶 `HARNESS_TIER: "auto"`（宣告哨兵值，等同不宣告→落回猜測），`tier_resolve.py` 以 `NO_DECLARATION` 常數明文化此語意。使用者裁定：讓 fork 本模板的人一眼看得到這個旋鈕在哪、怎麼改（Red tier，8 種取值 + 9 情境 hook smoke test 全通過）
21. [x] 更新 `agent_docs/AI-TEAM-REGISTRY.md`（模型分派 vs harness tier 的區別、routing skill 對照表）、`docs/INDEX.md` + `docs/INDEX_zh.md`（`rules/*.md` 的「（常駐）」標註已成假敘述，改為「全文參考檔，非自動載入」並新增 `.claude/tiers/README.md` 列）、`CLAUDE.md` + `CLAUDE_zh.md` 文件地圖；`CLAUDE.md` 記載「tier 於 session 開始時決定一次，中途 `/model` 切換需開新 session 才生效」此一已知限制
22. [x] 全量 read-back 驗收：語意無遺失與引用路徑存在性改以**可重跑的機械腳本**逐行驗證（見 §6），非 agent 自陳；判斷型項目（路由檔冷讀可用性）另派 fresh-context agent
23. [x] 更新 `docs/harness/LETTER-TO-FUTURE-SESSIONS.md`（§I.3 常駐面描述改為 tier pack + 預算閘門、§II 新增「鏡像漂移」腐化模式、§III 新增 3 項待辦；中英鏡像同 commit）與 `docs/learnings/ERRORS.md`（新增 2 則）

## 5. Verification Strategy

```acceptance
plan-lint: python3 scripts/execplan-lint.py docs/plans/active/F-003-tiered-harness.md
doc-refs: python3 scripts/check-doc-refs.py
budget-strong: python3 scripts/context-budget.py --tier strong
budget-mid: python3 scripts/context-budget.py --tier mid
modes: python3 scripts/context-budget.py --list-modes
tier-detect: python3 scripts/context-budget.py --self-test
packs-fresh: python3 scripts/build-tier-packs.py --check
resolver: env -u HARNESS_TIER python3 -c "import sys;sys.path.insert(0,'.claude/hooks');import tier_resolve as t;cases=[('claude-opus-5','strong'),('claude-sonnet-5','mid'),('claude-haiku-4-5-20251001','light'),('gpt-4','light'),(None,'light')];bad=[c for c,w in cases if t.tier_from_model(c)!=w];agents=[('security-reviewer','strong'),('qa-engineer','mid'),('Explore','light'),('no-such-agent','light')];bad+=[a for a,w in agents if t.resolve_agent_tier(a)[0]!=w];sys.exit(1 if bad else 0)"
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

- [2026-07-28 --:--] dev Phase 3 步驟 20-23 完成（新 session 續作，主對話實地收到 tier pack）。步驟 20 依 DEC-12 縮減為 3 檔並全數落在 ≤80 行：`ui-ux-pro-max` 394→55、`security-audit` 306→**80**、`frontend-design` 281→79，新增 14 份 `.claude/skills/<name>/references/` 參考檔（中英各一）。**內容守恆以逐行比對機械驗證**（對 `git show HEAD:` 版本的每一非空行檢查是否仍存在於「新 SKILL.md + 全部 references」聯集）：ui-ux-pro-max 與 frontend-design 除一段被路由表取代的 stub 外 0 遺漏；security-audit 8 行為刻意改寫（`Reference File`→`Domain File` 正名，因該目錄現同時放 domain 檔與支援檔；「per the output format below」改為指向 `references/reporting.md`；末段重複的 domain 清單刪除）。首輪比對抓到一處實質退化——Phase 0/1/2 標題被降級為粗體、5 步 Per-Item Assessment Protocol 被壓成一句散文——已還原為 `###` 標題與編號清單。另完成步驟 20b（`HARNESS_TIER: "auto"` 出廠哨兵值）。
- [2026-07-28 --:--] dev **文件層發現兩處假敘述並修正**：(a) `CLAUDE_zh.md` 自 Phase 2 起未跟改，仍寫著「## 常駐規則（`.claude/rules/` 自動載入）」並列出 7 檔——中文讀者看到的是一個已拆除的機制，歷時 8 個 commit；(b) `docs/INDEX.md` / `INDEX_zh.md` 把 `model-dispatch.md`、`judgment-rubrics.md` 標為「(standing) / （常駐）」。兩者皆已改正，並以 grep 對照 7 份規則檔 frontmatter `always:` 的實際值逐條複驗（僅 `security.md` 為 true）。教訓已記入 ERRORS.md，並在 LETTER §II 腐化模式表新增「鏡像漂移」列、§III 交接清單新增 parity 閘門待辦。順帶查出一項早於本計畫的既有缺口：`docs/INDEX_zh.md` 少了英文版的兩個章節，記入 LETTER §III 未自行補譯（超出本計畫非目標）。
- [2026-07-28 --:--] dev **驗收第二輪：三個 fresh-context 子 agent 全數回報，共 4 個 FAIL，全部已修**。(a) `frontend-design` 路由檔沒有任何「先做什麼」的祈使句——由兩個獨立 agent（結構查核與冷讀）分別指出，屬真實退化：原檔靠五項原則的完整內文自然承擔起手指引，壓成路由後那個功能沒有人接手，已補「動手寫任何 UI 代碼之前，先讀 design-principles」。(b) `security-audit` 的 `domain1-4.md`（早於本次重構）缺回指 SKILL.md 的檔頭，與本次新拆的 6 份不一致，已補齊。(c) 冷讀指出 `ui-ux-pro-max` 把「先萃取需求」寫在它所修飾的指令**之後**，讀者可能先跑指令再萃取——已調換順序。(d) 冷讀指出 `security-audit` 的「CRITICAL findings — flag immediately」從未定義「flag」是什麼動作，已改為明確的 `[HUMAN_ATTENTION_REQUIRED: <reason>]`。另採納三則非阻斷建議：CLAUDE.md/LETTER 的 `{strong,mid,light}` 花括號寫法 check-doc-refs 無法展開（改為逐檔列出，全 repo ERROR 由 8 降為 7）、`CLAUDE_zh.md` 文件地圖補回英文版才有的中文鏡像慣例列、REGISTRY 中未帶路徑的參考目錄簡寫改為完整路徑（check-doc-refs 對這種簡寫會回報 ambiguous；本行刻意不引用該字面寫法，否則掃描器會掃到這句話本身——同 ERRORS.md 2026-07-23「掃描器必須豁免引用性內容」）。修後複驗：內容守恆比對僅餘刻意改寫、en/zh 標題 parity 全對、回指檔頭 0 缺、acceptance 12/12 PASS。
- [2026-07-28 --:--] dev 步驟 22 驗收方式說明：委派的兩個 fresh-context read-back 子 agent 進入 idle 但未回傳報告（兩次催收無效），故改以**可重跑的機械腳本**取得證據——逐行內容守恆比對、引用路徑存在性、en/zh 標題數與順序 parity、`always:` 實際值對照、`HARNESS_TIER` 8 種取值解析、三個 tier hook × 9 情境 smoke test，輸出全部貼於本 session。acceptance-run 12/12 PASS；strong 245 行/13,679 字元、mid 320 行/18,693 字元，均在 balanced 門檻內。此為對 model-dispatch §5「驗收不得自證」的**部分達成**：機械項目有可重現的執行證據，但「路由檔冷讀是否足以起手」這類判斷項仍依賴子 agent，結果見本條之後的補充。
- [2026-07-28 --:--] main-conversation 建立 ExecPlan；基線實測：常駐層 = CLAUDE.md 90 行 + rules 7 檔 537 行 = 627 行 / 34,786 **bytes**；agent+skill description 8,722 bytes；`state/rule-events.jsonl` 0 筆；skills 17 個中 14 個為單檔。
- [2026-07-28 --:--] dev 基線單位修正：初次記錄的 34,786 來自 `wc -c`（位元組），非字元。實測字元數為 **32,739**（中文於 UTF-8 佔 3 bytes）。`context-budget.py` 一律以 Unicode 字元計——對中文而言字元數較接近 token 數。門檻比例實質不變（14,000/32,739 ≈ 43%），Q1 裁決不受影響。
- [2026-07-28 --:--] dev /last-word 收尾：本 session 完成 Phase 0/1/2 + Phase 3 步驟 18-19，8 個 commit 於 `feat/tiered-harness`（未推送、未開 PR）。教訓兩則歸檔 ERRORS.md Pending Review（驗收 agent 自我放寬判準、bytes/chars 單位誤植併入既有量測條目為 Recurred）。提請人審一項 invariant 候選：常駐層預算上限已由 `context-budget.py` 機械化，可升格 INV-ARC-001（invariants.md 屬 Red tier，未經同意不自行寫入）。
- [2026-07-28 --:--] dev **獨立查核回報 PASS，但查核本身找出 5 條真實缺漏並已補**。fresh-context 子 agent（Sonnet）逐檔審完 6 份降級規則，判定無刪除、無語意/門檻變更、無死連結、無過時自我描述。惟其準則 1 的判準被自行放寬為「檔案沒被刪」，較委派時指定的「每條規則現在住在哪」寬鬆；實質產出是它列出的 7 條「僅存於參考檔、未進任何 pack」，其中 5 條經覆核屬真實規範性缺漏，已補入對應層：(a) Haiku 出錯一次即換 Sonnet 不重試 → mid；(b) 涉及安全或成本的決策一律走 Plan Mode → strong；(c) 任務中途需求變更走 Scope Change 程序 → strong；(d) build/test 未過不得 push → light；(e) agent 路由具體對象（Explore / general-purpose+sonnet / worktree 批改）→ mid。另修正其指出的自相矛盾：light pack 原本逐字複製 CLAUDE.md 的正典層級表，卻同段寫著「不要把正典表複製到第二個檔案」——改為引用。其餘 2 條（cost-optimization 的 Input Optimization、model-dispatch 的 effort 參數說明）判定維持參考層即可。補完後重建 pack，acceptance 12/12 PASS，strong 244 行/13,420 字元仍在預算內。
- [2026-07-28 --:--] dev Phase 2 完成 + Phase 3 步驟 18 提前完成。建立三份累加來源片段（core-criteria / mid-expansion / light-expansion）、manifest、`scripts/build-tier-packs.py`（含 `--check` 防止 pack 與來源漂移，實測抓到一次真實漂移）、`.claude/tiers/README.md`；6 份規則檔改 `always: false` 並加註「非自動載入」，三處「Always-on rule」假敘述一併修正；CLAUDE.md「Standing Rules」改寫為「Operating Rules (tier pack)」。三個 hook 接入 settings.json。**量測結果（balanced 模式）**：strong 635 行/33,164 字元 → **243 行/13,035 字元（減 61%）**；mid 314 行/17,682；light 382 行/21,870。原訂搬移 6 檔到 `agent_docs/rules-reference/` 一案否決——實測會打斷約 50 處既有引用，風險高於效益，改為原地降級（DEC-10）。
- [2026-07-28 --:--] dev 驗證：三個 hook 各自 smoke test 通過（session 5 情境 / subagent 5 情境 / drift-check 7 情境，含非 JSON 與空 stdin 皆 exit 0）；**真實 session 端對端驗證**（巢狀 `claude -p`）確認 pack 確實抵達模型：無宣告時猜測為 strong、`HARNESS_TIER` 宣告優先、`qa-engineer` 子 agent 依自身 frontmatter 取得 mid 而非繼承主對話。acceptance-run 12/12 PASS。
- [2026-07-28 --:--] dev Phase 1 步驟 7-10 完成（實測法：臨時 probe hook 掛 SessionStart/SubagentStart/UserPromptSubmit/InstructionsLoaded + 巢狀 `claude -p` 觸發，測畢已完全移除、settings.json 還原無殘留）。結論：主對話模型在第一次回應前不可觀測（三事件 payload 與 env 皆無 `model`）→ DEC-4；子 agent 偵測可行（`agent_type` 實測有效）→ DEC-9。建立 `.claude/tiers/model-map.json`，`--self-test` 5 checks 0 failed。步驟 11 驗收與 Phase 2 阻塞於 §8 Q7 人裁。
- [2026-07-28 --:--] dev Phase 0 步驟 4-6 完成：CLAUDE.md Quick Commands 填入 4 條 harness 自檢指令、產品層 build/test/lint 佔位符保留供 fork 使用；`session-activation-check.py` 警語修正（原句「未填 Quick Commands 前本 repo 沒有任何可執行驗證閘門」在閘門建立後已成假敘述），smoke test 3 情境 exit 0（正常 / 非 JSON / 空 stdin）。步驟 5 假設證偽，見下。
- [2026-07-28 --:--] dev **Phase 0 發現：遙測管線未壞**。以合格 fixture 對 `stop-retro-logger.py` 做 end-to-end 測試，`RULE_FIRED` 與 `ESCALATION` 皆正確寫入 `rule-events.jsonl`；帳本恆空的成因在發射端而非採收端。測試資料已清除，採收器一行未改。教訓記入 ERRORS.md，後續方案記為 §8 Q6。
- [2026-07-28 --:--] dev Phase 0 步驟 1-3 完成：切出 `feat/tiered-harness`、feature-list.json 新增 F-003、建立 `.claude/tiers/budget.json`（3 模式）與 `scripts/context-budget.py`。`--self-test` 5 checks 0 failed；`--list-modes` 正常；三個 tier 目前皆解析到同一組 8 檔 627 行 / 32,739 字元（tier pack 尚未建立，屬 Phase 2 前的預期狀態）。

## 7. Decision Log

- DEC-1: 採「分層」而非「瘦身」路線——使用者 2026-07-28 裁定模板需同時服務 Haiku/Sonnet 與 Opus/Fable，「等未來基礎模型能力提升才會收斂」。因此弱模型防禦條款一律降級保存，不刪除。
- DEC-2: tier pack 以 SessionStart hook 的 `additionalContext` 注入，而非新增 `always: true` 規則檔——後者是全域的，機制上無法依模型分流。
- DEC-3: 偵測失敗一律 fallback light tier（全量）——漏載規則的風險高於多載規則的 token 成本。官方文件確認 `model` 欄位為 optional，此 fallback 為必要設計。
- DEC-4 (2026-07-28 Phase 1 實測後定案): **主對話 tier 無法偵測，只能宣告；子 agent tier 可以偵測。** 實測（Claude Code 2.1.220，臨時 probe hook + 巢狀 `claude -p`）證實第一次回應前沒有任何管道能得知主對話模型：`SessionStart`、`InstructionsLoaded`、`UserPromptSubmit` 三個事件的 payload 皆無 `model` 欄位，環境變數亦無（haiku 與 sonnet 兩次執行的 env 逐字相同）。官方文件宣稱 SessionStart「optionally includes model」在本版本不成立。另實測 `InstructionsLoaded` 為 context-only、exit code 被忽略，故「依 tier 抑制規則檔載入」亦不可行。唯一可信來源是 transcript 內的真實 model id（正確反映 `--model` 覆寫），但要到第一個 assistant 回應寫入後才存在。→ 架構改為「宣告 + 驗證」，細節見 §8 Q7。
- DEC-10: 6 份降級規則檔**留在 `.claude/rules/` 原地**，不搬到參考目錄。原計畫想以搬移彰顯「pack 才是正典」，但實測全 repo 對這些路徑有約 50 處引用（model-dispatch 15、security 13、judgment-rubrics 11…），搬移會製造大量死連結——正是 DIAGNOSIS §II.2 記載的衰敗模式。改為原地降級 `always: false` + 檔頭加註「非自動載入，本檔是 tier pack 的全文參考」，token 目標一樣達成，引用全數維持有效。
- DEC-11: tier pack 採**生成式**（`build-tier-packs.py` + manifest），不手寫三份。三份 pack 共用大部分內容，手寫必然各自漂移，正是 DIAGNOSIS §II.1 的正典分裂模式。`--check` 納入 acceptance，pack 與來源不同步即 FAIL。
- DEC-12 (2026-07-28, 使用者裁定): 步驟 20 由 8 檔縮減為 **3 檔**（`ui-ux-pro-max` / `security-audit` / `frontend-design`）。決策依據是一項在執行前才查清的事實：**SKILL.md 本體不常駐**——session 開始只載入 frontmatter `description`（§6 基線已記 8,722 bytes），本體要到 skill 被調用時才進 context。因此拆檔對本計畫的核心成功指標（常駐注入量）貢獻為 0，效益僅在「單次調用時少載多少」，且每拆一檔都帶語意遺失風險。三個最大檔（394/306/281 行）佔超長檔案的大半，效益風險比最佳；其餘 5 檔（168–190 行）留在原地。另修正原計畫的一處事實錯誤：原文以 `security-audit` 為「既有參照結構」，但它自己的 SKILL.md 當時是 306 行——「≤80 行路由」在本 repo 並無前例，是本次新立的標準，故 `security-audit` 一併納入拆分。
- DEC-9: 子 agent tier 判定維持偵測式。`SubagentStart` payload 實測為 `{session_id, prompt_id, agent_id, agent_type, hook_event_name}`，`agent_type` 確認可用（實測值 `Explore`），反查 `.claude/agents/<name>.md` frontmatter `model` 的設計成立。此為分層價值最高的一半——弱模型實際上就在子 agent 這端。
- DEC-5: 預算門檻採**配置檔 + 可切換模式**而非固定驗收值（Q1 裁決）。理由：分層的最適門檻無法先驗得知，需依實際體驗調整；把門檻外部化後，調整不需改程式也不需改 acceptance 區塊。代價是驗收結果依賴 `active_mode`，故 §5 明列門檻來源以免日後誤讀。
- DEC-6: 白話註解外移 `docs/PLAIN/`，但 light/mid pack 保留**引用路徑提示**、strong pack 不保留（Q2 裁決）。理由：非技術使用者的可讀性需求與弱模型的規則需求高度重疊，兩者共用同一 tier；strong tier 的讀者不需要這層鷹架。
- DEC-7: 遙測修復後**不設觀察期**，直接進 Phase 2（Q3 裁決）。代價：無法以「哪條規則真的改變過行為」的資料驅動搬遷取捨，Phase 2 的分層判斷改以「是否為每個 session 第一個決策所需」的既有判準為準（LETTER §I.3）。遙測資料轉為事後驗證用途。
- DEC-8: 子 agent 採 `SubagentStart` hook 動態注入，而非委派模板靜態附帶（Q4 裁決）。理由：官方文件確認該 hook 存在且支援 `additionalContext`；動態方案讓 tier 隨 agent frontmatter 自動生效，新增 agent 時無需同步維護委派模板。因該事件 payload 不含模型，tier 改由 `agent_type` 反查 frontmatter 決定。

## 8. Open Questions

- Q1 (resolved 2026-07-28): 門檻改為可切換模式的配置檔，預設 `balanced` 沿用原提案數值 → 見 DEC-5、Phase 0 步驟 2。
- Q2 (resolved 2026-07-28): 白話註解外移 `docs/PLAIN/`，light/mid tier 保留引用路徑提示 → 見 DEC-6、Phase 2 步驟 15。
- Q3 (resolved 2026-07-28): 修完遙測直接進 Phase 2，不設觀察期 → 見 DEC-7、Phase 0 步驟 6。
- Q4 (resolved 2026-07-28): 子 agent 動態分層，以 `SubagentStart` hook 實作 → 見 DEC-8、Phase 3 步驟 18。
- Q7 (**阻斷 Phase 2，待人裁**, 2026-07-28 Phase 1 實測後): 主對話 tier 既然無法偵測，來源要選哪一種？三個候選：
  - **(a) 明確宣告 + 事後驗證（建議）**：優先序 = 專案 `settings.json` 的 `env` 區塊宣告（實測 env 區塊確實會傳進 hook 程序）→ `~/.claude/settings.json` 的 `model` 欄位（盡力猜測，遇 `--model` 覆寫會猜錯）→ light。另加一個 `UserPromptSubmit` hook：第二輪起 transcript 已有真實 model id，比對宣告值，不符就注入更正提示（「你被載入 strong pack，但你實際是 Haiku，請立即讀 `.claude/tiers/light.md`」）。優點：常見情境正確、罕見情境自癒；代價：每輪多一次 hook 執行（可用 per-session 標記在驗證完成後短路）。
  - **(b) 一律注入 light（最保守）**：完全符合 fail-safe，但強模型永遠付全額 token，等於放棄本計畫的節省目標。
  - **(c) 純手動宣告，不做驗證**：最簡單，但宣告與現實脫節時無人察覺——正是 `LETTER-TO-FUTURE-SESSIONS.md` §I.1 警告的「文件說有防禦 ≠ 防禦存在」。
- Q6 (open, 非阻斷, 2026-07-28 Phase 0 發現): 規則遙測的採收器功能正常，但**發射端**失效——模型幾乎不主動輸出 `[RULE_FIRED:]` / `[RULE_SKIPPED:]`，因為該指示只是 `clarify-first.md` §1 與 `model-dispatch.md` §4 的括號附註，既無提醒也無強制。兩條路：(a) 把標記要求寫得更醒目——但那等於往常駐層加料，與本計畫方向直接衝突；(b) 放棄自陳式標記，改由可觀測行為反推（`delegation-ledger.py` 已用 regex 從委派 prompt 反推「三要素」是否齊備，同一手法可用 `AskUserQuestion` 工具呼叫反推 clarify-first 是否觸發）。**本計畫不處理**——超出 F-003 範圍，且 DEC-7 已將遙測定位為事後驗證用途。建議另開 ExecPlan 走 (b)。
- Q5 (open, 非阻斷): tier 只在 session 開始時決定一次，中途 `/model` 切換不會重新注入（官方機制限制，見 §2）。目前處理方式是寫進文件告知使用者。若日後認為此限制影響實際體驗，可評估以 `UserPromptSubmit` hook 週期性重檢——但那會在每輪對話增加成本，本計畫不採用。

## 9. Handoff Manifest

- Next agent: dev（續作 Phase 3 步驟 20-23），完成後轉 code-reviewer
- Required reading before resuming: `docs/plans/active/F-003-tiered-harness.md`（本檔 §4 Phase 3、§7 DEC-1~11、§8 Q5/Q6）、`.claude/tiers/README.md`（分層機制與已知限制）、`.claude/protocols/harness-maintenance.md` §1 與 §4（Red/Yellow tier 改動程序）
- 剩餘工作（§4 未打勾者）：步驟 20（拆分 8 個 >150 行 SKILL.md）、步驟 21（AI-TEAM-REGISTRY / INDEX / CLAUDE.md 文件地圖）、步驟 22（全量 read-back，本次已做過一輪並補回 5 條缺漏，Phase 3 完成後需再跑一次）、步驟 23（LETTER §3 交接清單 + ERRORS）
- 續作前必知：本 session 的改動要**開新 session 才生效**——舊 session 載入的仍是重構前的 7 份常駐規則。續作時應已在新 session，屆時主對話會收到 tier pack，可順便實地檢驗注入品質
- 環境注意：本機殘留 `HARNESS_TIER=mid`（Phase 1 探測所致）。新 session 若未顯式宣告，預期走 `guessed:settings.json` 路徑；若看到 tier=mid 而非 strong，先查該變數是否仍在環境中
- Current state marker: [HANDOFF: dev]
