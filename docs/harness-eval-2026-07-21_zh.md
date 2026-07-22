## Harness 成熟度報告 — /Users/a17/AIproject/BaseAIProject
> 本檔為 docs/harness-eval-2026-07-21.md 的繁體中文鏡像(2026-07-22 同步)。
**日期**: 2026-07-21
**總分**: 90 / 100 → Level 4 [Self-Monitoring]

Rubric 交叉核對(`.claude/skills/harness-eval/rubric.md`):八個維度的分數皆依 rubric 自身的計分表重新推導,結果完全吻合(D1 3+1+3+2+5=14, D2 2+4+4=10, D3 4+3+2+2+3+3+3=20, D4 3+3+4+0=10, D5 2+2+0+2=6, D6 2+5+2+2+4=15, D7 1+3+4+2=10, D8 2+2+1=5)。有一處判斷值得標註,但非錯誤:rubric 中 D1 的「角色定義」一項僅寫明 `present=2`,並未明訂部分給分條款;本次掃描對「雖已存在但被拆分在未填的 `{{tagline}}`/`{{Tech Stack}}` 佔位符中、且採行為(而非身份)框架」的段落給了 1/2 分。這與 rubric 在其他地方處理部分給分的方式一致(例如 D4 的 `TODO only=1`),因此維持此評分,不予進位到 2 分。總分 = 90,落在 L4(81–95)「Self-Monitoring」區間,低於最高層級 L5「SkillOpt-Ready」區間(96–100)一級。

### 評分卡

| 維度 | 分數 | 滿分 | 說明 |
|---|---|---|---|
| D1 — Constitutional Layer | 14 | 15 | 確實精簡、採分層閱讀設計的 CLAUDE.md,具備真實可用的正典層級衝突規則與 6 個實質性規則檔;扣 1 分是因為角色/標語欄位(CLAUDE.md:3, :79-81)仍是未填寫的 `{{placeholder}}`——依其自身的 Activation Status 規則,本 repo 屬於尚未 fork 啟用的樣板(template)。 |
| D2 — Agent Coverage | 10 | 10 | 共 14 個 agent 檔案(核心 5 個之外還有 9 個),核心 5 種角色(pm/architect/tech-lead/security-reviewer/qa-engineer)皆已透過檔名與 frontmatter 的 `name:` 雙重確認。涵蓋率完整;但沒有任何機制強制執行決定「何時該用」這些 agent 的調度紀律(這部分僅是 model-dispatch.md 中的文字規範)。 |
| D3 — Hook System | 20 | 20 | 全部 4 個 hook 皆存在,並已在 settings.json 中接好;`pre-tool-use-guard.py` 的 exit-2 強制邏輯已確認在 `state/hook-events.jsonl` 中真實觸發過(17 筆實際的 `enforced_block` 事件,例如一次被阻擋的 `cat .env`)。是本 repo 中最強的維度——屬機制性,而非僅止於文字規範。 |
| D4 — Invariants | 10 | 15 | GIT(5 條規則)與 SEC(具真實 grep pattern)命名空間穩固且滿分;專案專屬廣度得分為 0/5——INV-TEST/API/ARC/BLD 全部都是未填寫的 `> Fill in project X invariants.` 佔位符,與尚未 fork 啟用的樣板狀態一致。 |
| D5 — ExecPlan System | 6 | 10 | PLANS.md(9 節規格)與 10 階段生命週期文件設計良好、拿到滿分;「≥1 個已完成的 ExecPlan」一項全數 4 分皆失分,因為 `docs/plans/active/` 與 `completed/` 內除了原始的 `.gitkeep` 之外空無一物——此系統在本 repo 的 git 歷史中從未被實際使用過。 |
| D6 — Memory & Retro Loop | 15 | 15 | ERRORS.md(6 條真實、有日期的經驗教訓)、SCHEMA.md、`state/.gitignore`,以及 1518 行真實的 hook-events.jsonl 紀錄(18 天、3 個 hook,含一筆真實的 `enforced_block`)皆齊備——是本 repo 中最強的證據,證明此迴圈已在正式環境中端到端跑過,而不只是停留在紙上。 |
| D7 — Skills & Commands | 10 | 10 | 共 17 個 skill 目錄(8+ 級),關鍵 skill(code-review 72 行、multi-agent-review 137 行)內容具體、非空殼,`/last-word` 是真實的 8 步驟工作流程。「觸發時機是否正確」仍依賴文字判斷(這是 Skill 機制本身的固有特性,此處不因此扣分)。 |
| D8 — SkillOpt Loop Readiness | 5 | 5 | jsonl 上線紀錄是真實且機制性的(由 hook 實際寫入,而非僅止於文件描述);ERRORS.md 的 Pending Review + Active Lessons 雙結構確實有內容填入;skill 更新的觸發條件(pr-retro 的「Case C」)已明確定義。此迴圈屬於「蒐證並由人類把關」性質,而非封閉式自動優化器——這在此成熟度區間屬於預期表現,不因此扣分。 |
| **總分** | **90** | **100** | |

### 缺口清單(依優先順序)

**[HIGH]**
1. 本 repo 仍是尚未 fork 啟用的樣板——`CLAUDE.md:1` 字面上就寫著 `{{PROJECT_NAME}}`,`invariants.md:1` 的標題是 `{{PROJECT_NAME}} — Mechanically Verifiable Invariants`;依該檔自身的 Activation Status 規則,這限制了 D1/D4「憲法層」內容在實務上能有多大意義。
2. 沒有任何機制性關卡能阻擋缺乏驗證證據卻聲稱「已完成」的說法——judgment-rubrics.md §2/§5 與 model-dispatch.md §5(「絕不可自我認證」)都只是文字規範;`pre-tool-use-guard.py`(唯一具強制模式的 hook)完全不知道交付物是否曾被驗證過。
3. ExecPlan + review-protocol 這套機制——原本設計來作為持久、結構化驗證紀錄的歸屬地——從未被實際演練過:`docs/plans/active/` 與 `completed/` 只有 `.gitkeep`,`state/feature-list.json` 在磁碟上並不存在。完全沒有證據顯示這個樣板會被填入真實資料,而不是一直維持空殼狀態。
4. 依 plan-first.md 自身列出的 <20 行/單一檔案/已定位 bug 修復等例外規則,絕大多數真實任務根本不需要任何驗證證據產出物——對這些任務而言,「我是否驗證過」全憑模型在對話中怎麼說。
5. CLAUDE.md 的正典決策樹(唯一有文件記載的進入點)沒有針對需求釐清/範圍界定設置 Step 0——它會從「收到目標」直接路由進入 ExecPlan 或 Plan Mode。
6. pm agent 與 spectra-amplifier skill(唯二能產出範圍/驗收標準(AC)明確性的兩項工具)都是關鍵字/選用觸發——沒有任何機制會把一句模糊的請求導向其中任一者,一個普通的請求可以完全繞過這兩者。
7. 全部 14 個 agent 都以 `context_firewall:true`(非互動式子代理)運作——因此書面的「Open Questions」欄位永遠無法作為即時來回釐清的關卡;等到有人讀到它時,草擬工作早已建立在未經驗證的假設之上。
8. 完全沒有任何專案專屬的不變量規則存在——`invariants.md` 中的 INV-TEST/API/ARC/BLD 命名空間全部都是未填寫的 `> Fill in project X invariants.` 佔位符(D4 在此項得分為 0/5)。

**[MED]**
9. `.claude/rules/` 下 6 個檔案中大多數只是政策性文字,背後沒有機制性關卡——只有與 `pre-tool-use-guard.py` 正規表示式規則重疊的 security/git-guard 子集才真正被強制執行;model-dispatch 的分級、judgment-rubrics 的升級機制、plan-first、cost-optimization 全都仰賴自律遵守。
10. 沒有任何機制強制主對話依 model-dispatch.md 自身的規範,實際委派給 pm/architect/security-reviewer/qa-engineer——調度紀律仍是自我約束的文字規範(D2 的涵蓋率滿分;但 D2 的*使用*並未被強制執行)。
11. `handoff-protocol.md:19` 誇大了 `stop-retro-logger.py` 實際的能力——它宣稱缺漏或格式錯誤的結尾標記會被「標記出來(flagged)」,但該 hook 的 `MARKER_RE` 只會比對*確實存在*的標記;完全沒有偵測「不存在」的程式碼路徑,而且 `[HANDOFF:*]` 根本從未被解析過。這是一處文件與實作不一致,而且是攸關稽核軌跡(audit-trail)敘事核心的宣稱。
12. 新鮮上下文驗收審查(fresh-context acceptance review,model-dispatch.md §5 / delegation-templates.md §6)設計良好,對文件與程式碼一視同仁地涵蓋,但沒有觸發關卡,也沒有留存要求——其 PASS/FAIL 判決可能隨著子代理短暫的上下文一起消失。
13. `review-protocol.md` 針對 Code/Security/QA 審查者有詳細檢查清單,但對非程式碼交付物(設計文件、PRD、報告)則完全沒有——在協定定義層級,驗證隱含地被限定為只涵蓋程式碼/測試。
14. INV-GIT-001、INV-GIT-005,以及整個 TEST/API/ARC/BLD 命名空間,標註的都是 `HOOK: manual review` 或根本沒有 hook——純屬文字規範、未被強制執行,與具備機制性關卡的 INV-GIT-002/003/004 及 INV-SEC-* 明顯不同。
15. ExecPlan 生命週期中唯一針對模糊性的結構性檢查點(plan-reviewer 第 3 階段的「Open Questions 未解決」檢查),只會在 Phase 1(pm 需求分析)與 Phase 2(architect 設計)已經把請求轉化為具體決策*之後*才觸發——屬於被動且延後的檢查,而非事前關卡。
16. `docs/plans/PLANS.md` §2 的 9 節式 ExecPlan 樣板中,沒有專屬的 Non-Goals/Out-of-Scope 欄位——即使是完全符合 rubric 規範的 ExecPlan,也不需要說明排除了哪些內容。(只有 feature-pipeline 的 Stage-1 包裝層有 Included/Excluded 欄位,但這並非基礎規格的一部分。)
17. judgment-rubrics.md §3 的模糊性斷路機制純屬被動反應式(要等到任務進行中「注意到有兩種合理解讀」才會觸發)——沒有任何規則要求在工作開始前主動進行事前模糊性掃描。
18. 完全找不到任何客觀、可檢核的 Signal→Action 判準,用來判斷「這個請求夠模糊、需要澄清」相對於「範圍已經明確、可以直接進行」——judgment-rubrics.md 中其他每一個判斷點都有這樣的判準;唯獨這個決策點沒有。
19. ExecPlan 生命週期中的兩個「人類審查者關卡」檢查點(`execplan-lifecycle.md:69`、`:111`)僅靠文字規範/agent 自律遵守來執行——唯一會碰到 ExecPlan 的 hook(`pre-compact-snapshot.py`,透過 `_lib.py:116`)只是被動地讀取目前作用中計畫的路徑以供 session 快照使用;它並不把關任何事情。

**[LOW]**
20. 儘管 `hook-events.jsonl` 已有 1518+ 行的活動紀錄,`state/session-handoffs/` 卻是空的——`pre-compact-snapshot.py` 的快照寫入功能與 `/last-word` 流程,在本 repo 的實際使用中似乎從未產生過持久性產出物;有可能是靜默失敗(該 hook 只把寫入失敗記錄到 jsonl,從未真正顯現出來),但兩種可能性目前都未經驗證。
21. 即使是(目前尚未使用的)ExecPlan 樣板,其 §5 驗證策略也只要求列出指令字串(例如「Build: `[build command]`」),而不要求貼上實際輸出——因此即便 ExecPlan 被完整使用,審查時仍可能僅憑一個沒有實證支撐的 ✓ 就通過。
22. `INV-SEC-003` 的 git-add 機密檔案防護有一個自行記載在文件中的盲點(`pre-tool-use-guard.py:94-99`):它無法攔截 `git add -A`/`git add .` 這種不小心把機密檔案一併掃進去的情況,只能抓命令列上直接寫出的字面檔名。
23. 本專案自身的規則/協定中,並沒有任何地方強制要求針對模糊請求採用等同於 `AskUserQuestion` 的模式——這種模式存在於更廣泛的 skill 生態系中(例如通用的 `deep-research` skill 就有「若範圍不明確,詢問 2-3 個釐清問題」的做法),但尚未被採納進這個 harness 自身「從想法到計畫」的流程中。
24. D8 的 SkillOpt 迴圈屬於蒐證並由人類把關性質,而非封閉迴圈的自動優化器——目前沒有任何機制會自動讀取 `hook-events.jsonl` 來提議或套用 skill 修改;必須由人類/agent 手動執行 pr-retro 的 Case C。

### 重點深入探討(1):輸出可驗證性 / 可稽核軌跡 / 回滾(Rollback)

**目前已具備的**
- **硬性強制執行(Hard-enforced)**:`pre-tool-use-guard.py`(`.claude/hooks/pre-tool-use-guard.py`)是唯一會以 exit-2 方式阻擋操作的 hook——它會阻止直接提交到 master、對 master 執行 force-push/reset-hard、讀取 `.env`/機密檔案、`curl|sh`、`rm -rf /|~`。附帶效果是它從結構上讓程式碼變更具備回滾安全性(所有東西都被強制走 feature branch + PR,因此可還原)——但它完全沒有說明變更是否*正確*,只保證了它*可還原*。
- **硬性強制執行(部分)**:`stop-retro-logger.py` 把標記收割進 `ERRORS.md` 的功能確實有效運作——在 `docs/learnings/ERRORS.md` 中已確認有 2026-07-04/07-07 的真實、有日期的條目——但它只能偵測到 transcript 中*確實存在*的標記;它沒有偵測標記*不存在*的邏輯,這與 `handoff-protocol.md:19` 宣稱缺漏標記會被「標記出來(flagged)」的說法相矛盾。
- **軟性政策(Soft-policy)**:`post-edit-lint.py` 的 INV-SEC-001/002 掃描(依其自身 docstring,僅作哨兵提示、從不阻擋)、`model-dispatch.md` §5「驗證絕不可自我認證」的規則,加上 `delegation-templates.md` §6 的新鮮上下文驗收審查樣板(這是唯一一個把文件與程式碼一視同仁視為可驗證的機制——但完全是選用性質且不具留存性)。
- **僅止於文件記載(Documented-only)**:`review-protocol.md` 的結構化驗證結果表(僅涵蓋程式碼/PR 範圍,沒有對應的文件版本);`pre-compact-snapshot.py` 的 session 快照設計(已在 settings.json 中接好,但 `state/session-handoffs/` 是空的——從未產出過真實的產出物);整套 ExecPlan §5/§6/§7/§9 驗證證據機制,以及 `state/feature-list.json` 的驗證 schema(兩者皆從未被實際實例化過——`docs/plans/active/` 與 `completed/` 只有 `.gitkeep`);`/last-word` 產出 SESSION-HANDOFF.md 的機制(CLAUDE.md 稱其為「硬性關卡」,但沒有任何 hook 會檢查它是否真的執行過或驗證其內容)。

**缺口(依排序)**
1. [HIGH] 沒有任何機制性關卡能阻擋缺乏驗證證據卻聲稱完成的說法——唯一具強制模式的 hook 完全不知道驗證狀態。
2. [HIGH] ExecPlan/review-protocol 機制從未被實際演練過——在本 repo 中的部署狀態百分之百仍屬理想願景。
3. [HIGH] 大多數真實任務(依 plan-first.md 自身的例外規則)完全不需要任何必要的驗證產出物。
4. [MED] `handoff-protocol.md:19` 誇大了 `stop-retro-logger.py` 實際的能力(文件與實作不一致)。
5. [MED] 新鮮上下文驗收審查沒有觸發關卡,也沒有留存要求。
6. [MED] `review-protocol.md` 對非程式碼交付物沒有審查者檢查清單。
7. [LOW] 即使被使用,ExecPlan §5 也只要求指令字串,不要求貼上實際輸出。
8. [LOW] INV-SEC-003 的 git-add 防護無法攔截 `git add -A` 把機密檔案一併掃進去的情況。
9. [LOW] `pre-compact-snapshot.py` 的安全網看似未被使用/未經驗證——呼應了 ERRORS.md(2026-07-04)中已記載過的「已部署但從未做過 smoke test」的舊教訓。

**具體提案**
- **在 `stop-retro-logger.py` 中加入缺漏標記哨兵(missing-marker sentinel)**——擴充現有的 transcript 解析流程,額外檢查最後一個 assistant 文字區塊是否以必要的標記結尾;若沒有(且該 session 的 `tool-calls.jsonl` 顯示有編輯活動),就記錄一筆 `result="missing_marker"` 事件,並附加到 `ERRORS.md` Pending Review 底下新增的「Protocol Violations」類別中。維持哨兵性質(不阻擋)。*接入點*:`.claude/hooks/stop-retro-logger.py`,已在 settings.json 中接到 Stop/SubagentStop。*工作量*:小(約半天)。
- **`state/verifications.jsonl` + Stop 時交叉核對**——建立一個強制性的輕量紀錄格式 `{ts, session_id, task, deliverable_files[], verifier, evidence, pass_bool}`,每次聲稱「完成」時都應附加一筆;在 Stop 時由哨兵機制將該 session 的 tool-calls 與 verification-log 條目交叉核對,若有編輯活動卻完全沒有驗證紀錄,就在 ERRORS.md 中標記此缺口。*接入點*:新增 `state/verifications.jsonl`(schema 加入 `state/SCHEMA.md`)、`stop-retro-logger.py` 或其同級 hook 中的邏輯、`judgment-rubrics.md` §2 與 `model-dispatch.md` §5 的文件更新。*工作量*:中(約 1 天)。
- **在 `review-protocol.md` 中新增文件/報告審查者檢查清單**——比照現有 Code/Security/QA 各節,新增一份針對非程式碼交付物的檢查清單,要求在文件被標記為已審查之前,必須引用一次新鮮上下文驗收審查的 PASS/FAIL 結果;並在 judgment-rubrics.md §2(「真正完成」)中新增第 6 條判準。*接入點*:`.claude/protocols/review-protocol.md`(新增章節)+ `.claude/rules/judgment-rubrics.md` §2。*工作量*:小(僅文件層面)。
- **INV-VERIFY-001 + 配套的 GitHub Actions 檢查**——新增一條不變量規則,要求每個 PR 都必須連結一份 ExecPlan,且其 §7 決策紀錄與 §5 驗證策略皆非空殼(需有實際貼上的輸出,而非只有指令字串),透過 `.github/workflows/harness-gates.yml` 這個 CI 關卡強制執行(本地 hook 無法把關 PR 合併)。*接入點*:`docs/architecture/invariants.md`(新增 INV-VERIFY-001)+ 新的 workflow 檔案 + `review-protocol.md` 的 Code Reviewer 檢查清單。*工作量*:中(約 1 天,而且因目前尚無真實 ExecPlan 存在,還需要先產生第一份真實 ExecPlan 才能測試)。
- **`pre-compact-snapshot.py` 自我檢查**——若 hook-events.jsonl 顯示有嘗試寫入快照,但 `state/session-handoffs/` 的檔案數量少於預期,就記錄一筆獨立的警告事件,讓這類靜默失敗能被自動抓到,而不必仰賴人類發現一個空目錄。*接入點*:`.claude/hooks/pre-compact-snapshot.py` 或 `stop-retro-logger.py`。*工作量*:小(數小時)。

### 重點深入探討(2):規劃前的需求釐清

**目前已具備的**
- **軟性政策(Soft-policy)**:`pm` agent(`.claude/agents/pm.md`)會產出帶有「Open Questions」欄位的需求文件,但它是關鍵字觸發(需求/PRD/用戶故事/功能),而且因為它是以非互動式子代理(`context_firewall:true`)方式執行,無法在任務進行中暫停下來真正詢問使用者——Open Questions 只是一份延遲呈現的書面產出物,而非即時關卡。`judgment-rubrics.md` §3 的模糊性斷路機制確實存在,但純屬被動反應式——只有在任務進行中已經注意到模糊性時才會觸發。`plan-reviewer` 第 3 階段的「Open Questions 未解決」檢查(`execplan-lifecycle.md`)是唯一觸及模糊性的結構性檢查點,但它是在需求(Phase 1)與架構(Phase 2)草擬都已完成*之後*才觸發。
- **僅止於文件記載(Documented-only)**:`spectra-amplifier`(harness 中界定範圍最完整的工具——具備明確的 Out-of-Scope 欄位、Given/When/Then 驗收標準)被定位為「建議使用(Recommended)」,而非必要;而且在 CLAUDE.md/plan-first.md/execplan-lifecycle.md/PLANS.md 中,完全沒有任何地方把它列為任何事項的前置條件。CLAUDE.md 的決策樹與 plan-first.md 工作流程第 1 步(「分析任務需求」)都沒有提供結構化方法,也沒有指向這兩項工具中的任何一個。
- **硬性強制執行(Hard-enforced)**:無。這個 harness 中沒有任何地方存在會機制性強制在規劃開始前執行釐清步驟的機制。

**缺口(依排序)**
1. [HIGH] CLAUDE.md 的正典決策樹——每個 session 都被要求查閱的唯一有文件記載的進入點——沒有針對範圍/需求釐清設置 Step 0。
2. [HIGH] pm agent 與 spectra-amplifier 都是關鍵字/選用觸發;沒有任何機制會把一句模糊的請求導向其中任一者。
3. [HIGH] Agent 都以非互動式子代理(`context_firewall:true`)方式運作,因此 Open Questions 欄位無法作為即時釐清迴圈——等到有人讀到它們時,草擬工作早已建立在假設之上。
4. [MED] `PLANS.md` §2 的 9 節式樣板沒有專屬的 Non-Goals/Out-of-Scope 欄位。
5. [MED] 唯一的結構性模糊性檢查(plan-reviewer 第 3 階段)是在兩個草擬階段都已發生*之後*才觸發。
6. [MED] judgment-rubrics.md §3 的模糊性觸發條件純屬被動反應式;不存在對應的主動事前檢查機制。
7. [MED] 沒有客觀的 Signal→Action 判準能區分「夠模糊、需要澄清」與「範圍已明確」——judgment-rubrics.md 中其他每一個判斷點都有這樣的判準;唯獨這一個沒有。
8. [LOW] 本專案自身的規則/協定中,並未強制要求採用等同於 `AskUserQuestion` 的模式(在通用的 `deep-research` skill 中已有先例,但尚未被本專案採納)。

**具體提案**
- **CLAUDE.md 決策樹 Step 0:釐清範圍**——在現有 5 步驟決策樹之前插入 1-2 行的步驟:若輸入是一個原始目標(尚未界定範圍),就先執行一次釐清流程(可透過互動方式,或透過 pm/spectra-amplifier),並在繼續之前取得使用者對範圍的明確確認。*接入點*:`CLAUDE.md`「Decision Tree Before Acting」章節,置於目前的 step 1 之前(須維持在該檔案自我設限的 ≤100 行預算內——需在別處刪減)。*工作量*:小(<10 行)。
- **新增常駐規則 `.claude/rules/clarify-first.md`**——以與 judgment-rubrics.md 相同的格式定義一個可觀察的 Signal→Action 觸發條件(例如:若 {目標使用者、成功指標、明確邊界、具體觸發條件} 中缺少 2 項以上就觸發),並規定釐清工作必須在主對話中進行(而非在 `context_firewall:true` 的子代理內),且須在進入 Plan Mode/ExecPlan 之前完成。*接入點*:新檔案,登記在 CLAUDE.md 的「Standing Rules」清單中,與現有 6 條並列。*工作量*:中(約 60-80 行的檔案,以 judgment-rubrics.md 為範本)。
- **將 `plan-first.md` 步驟 1 接上 `clarify-first.md`**——把目前僅一行的「分析任務需求」步驟改寫,明確套用新的訊號檢查清單,並要求在草擬之前先確認範圍。*接入點*:`.claude/rules/plan-first.md`,Workflow 章節,步驟 1。*工作量*:小(<10 行)。
- **新增 Non-Goals/Out-of-Scope 作為必填欄位**——加入 `PLANS.md` 的樣板與 `pm.md` 的 Output Format 中(目前只有 feature-pipeline 的 Stage-1 包裝層有 Included/Excluded 欄位)。*接入點*:`docs/plans/PLANS.md` §2 + `.claude/agents/pm.md` Output Format。*工作量*:小至中(2-3 處協調一致的編輯,各 <20 行)。
- **強化 `execplan-lifecycle.md` Phase 1 的退出條件**——要求必須「Goal 已填寫 且 Non-Goals 已陳述 且(若 clarify-first.md 已觸發)引用使用者確認內容」,才允許交接給 architect。*接入點*:`.claude/protocols/execplan-lifecycle.md`,Phase 1 — PROPOSED,Exit 那一行。*工作量*:小(<10 行)。
- **plan-reviewer 稽核「釐清紀錄」的存在,而不只是 Open Questions**——由於釐清品質本身是一種判斷(依 judgment-rubrics §6,無法用 hook 機制化),延伸 plan-reviewer 第 3 階段的檢查清單,驗證是否存在一份釐清紀錄(訊號未觸發+原因,或訊號已觸發+確認連結)——這是一種與 model-dispatch.md §5 的新鮮上下文審查模式一致的事後稽核軌跡。*接入點*:`.claude/agents/plan-reviewer.md` 檢查清單 + `PLANS.md` 樣板 §8 附近。*工作量*:中(涉及兩個檔案,且依 harness-maintenance.md 需要一輪觸發測試)。

### 最小改善路徑(3 個步驟)

1. **CLAUDE.md 決策樹 Step 0 + `clarify-first.md`**——整份報告中成本最低、槓桿效益最高的修正:對每個 session 都被要求閱讀的唯一檔案做一次 <10 行的編輯,即可補上深入探討(2)中排名最前的缺口(合併清單中的缺口 #5-#7),且完全不需碰觸任何 hook 或 agent 行為。*涉及檔案*:`CLAUDE.md`、新增 `.claude/rules/clarify-first.md`。
2. **在 `stop-retro-logger.py` 中加入缺漏標記哨兵**——對一個已載入、已接好線的 hook 進行約半天工作量的新增(不需變更 settings.json),讓 `handoff-protocol.md:19` 現有的宣稱從理想願景變成真實情況,並開始產出第一個關於「驗證/交接證據缺失」的機制性訊號(合併清單中的缺口 #2、#11)。*涉及檔案*:`.claude/hooks/stop-retro-logger.py`。
3. **在 `PLANS.md` + `pm.md` 中新增 Non-Goals/Out-of-Scope 欄位**——一次小型、僅涉及文件的編輯(2-3 個檔案,各 <20 行),為唯一真正具備實質結構的工作流程路徑(ExecPlan)補上範圍邊界的缺口,由於不涉及任何程式碼/hook 變更,實作風險幾乎為零。*涉及檔案*:`docs/plans/PLANS.md` §2、`.claude/agents/pm.md` Output Format。

### SkillOpt 就緒度指標

D8 拿到乾淨的 5/5,但就質性圖像而言,這屬於「蒐證並由人類把關」,而非「封閉迴圈自動優化」——這正是 L4(Self-Monitoring)而非 L5(SkillOpt-Ready)所預期的表現。rubric 的三項檢查全部真實且具機制性:`hook-events.jsonl` 確實是由 `_lib.py` 的 `append_jsonl()`/`log_event()`,從三個不同的 hook 真實寫入的(1500+ 行真實紀錄,時間範圍 2026-07-04 → 2026-07-21,結果類型具真實多樣性,包含 16 筆 `enforced_block` 事件);`ERRORS.md` 的 `## Pending Review` 與 `## Active Lessons` 兩部分都填有真實、有日期、非佔位符的條目;而 `pr-retro/SKILL.md` 的「Case C」明確定義了何時應該編輯 skill/agent 檔案的觸發條件,並透過 `ERRORS.md` Pending Review 進行導流。距離下一個層級還缺什麼:目前沒有任何機制會讀取 `hook-events.jsonl` 來自動呈現或提議 skill 修改——必須由人類/agent 自行注意到模式,並手動執行 pr-retro 的 Case-C 路徑;也沒有接入 CI 的自動化「修改前/修改後觸發率驗證」迴圈(`skill-creator-plus/references/eval-loop.md` 與 `harness-maintenance.md` §6.3 中雖有手動派發並比對的流程,但僅是文字指引,並未腳本化)。上線遙測(rollout-telemetry)的基礎確實穩固——通往 L5 的差距完全在於將「記錄 → 決策 → 編輯 → 驗證」這個迴圈自動化,而不在於記錄本身。
