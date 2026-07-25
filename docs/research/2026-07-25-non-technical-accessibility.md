# BaseAIProject 非技術友善化研究

> 日期:2026-07-25
> 來源:Workflow 四階段研究(4 路內部稽核 → 3 路外部調研 → 綜合 → 9 條承重牆宣稱對抗性查證)
> 範圍界定:**不是**另建 GUI app(那個方向〔精靈工作室〕已確定移到另一個獨立專案);這次研究如何在**現有 CLI / Claude Code 對話介面內**,讓非技術背景用戶也能「學會使用」「檢驗輸出」「驗證成果」,同時不拆除現有 harness 的治理與品質機制(ExecPlan 人審、hooks 安全閘、驗收流程)。
> 狀態:研究定稿,經 plan-reviewer 批判;§7 開放問題待人類裁決

## 1. 根本診斷:單一根因,四種外顯

四份內部稽核(入口術語、上手路徑、驗證呈現、agent/skill 暴露)不是 20 個互不相關的問題,而是同一個結構性根因在四個地方的外顯:

> **同一份文件同時扮演「AI 的可機械執行規則」與「人類唯一可讀介面」兩種角色,而在精確度與可讀性衝突時,現行文件全部倒向精確度那一邊,人類讀者被留在術語牆外。**

治理機制本身(ExecPlan 人審、Plan Mode、hooks 安全閘)沒有被稽核指出設計缺陷——問題出在**呈現層缺口**,不在治理邏輯。四種外顯:

- **入口端**:README 的上手步驟本身就是對人類下達的 shell 指令(全域替換 `{{PROJECT_NAME}}`、`chmod +x`),全庫找不到一句「這件事你可以直接叫 Claude Code 做」。CLAUDE.md 的 Activation Status 段落明講是寫給 AI 看的行為規則,卻被 README 當成人類上手的第一站。
- **判斷端(最嚴重,因為是每個任務的必經之路)**:CLAUDE.md 決策樹第一個分岔(`CLAUDE.md:30`、`plan-first.md:11/13`)要求人類判斷「該走 ExecPlan 還是 Plan Mode」,但兩詞只互相指向對方定義,形成無起點的循環術語牆。`parallel-worktree.md` 直接貼原始 git 指令(worktree/rebase/reset --hard)不解釋差異與風險,是同一根因的另一種外顯。
- **出口端**:驗收證據(`docs/reviews/*.md`、`state/*.jsonl`)全篇技術代號,人類唯一可解讀的往往只有最後一行「VERDICT: PASS」。CLAUDE.md 唯一設計來給人類看的 ✓/→/⚠ 模板(`CLAUDE.md:76-78`)完全 unenforced(`handoff-protocol.md` 明載主對話的 Stop 事件不受 hook 檢查),且未連結任何實際證據檔——是「意圖良好但沒有機制保證存在」的孤兒設計。
- **分派端(圖景較複雜)**:harness 其實已有部分良好設計——主對話被規則禁止親自做重活、多數 skill 靠白話意圖自動觸發、交接標記對一般對話不可見。但設計意圖沒有貫徹到底:`.claude/uiux/WORKFLOW.md` 教的「快速上手」反而是打 `@agent`/斜線語法;近似 agent(market-researcher/data-analyst/competitive-analyst)靠 TAM/SAM/SOM、KPI、SWOT 等術語互斥分工,講錯詞可能靜默分派錯誤且無提示。

## 2. 設計原則(源自外部研究,經查證修正)

1. **不稀釋 AI 版規則本文的精確度**——依 Diátaxis 的 Reference/Explanation 分工,規則檔本文(`.claude/rules/*.md`、`CLAUDE.md`)維持給 AI 的機械判準不變,另建白話衍生層(首次術語就地一句話註解 + 獨立索引),不把兩種讀者需求合併進同一份文件裡稀釋精確度。
2. **澄清/確認/人審永遠留在主對話層或 slash command,不可委派給子 agent**——查證確認:AskUserQuestion 工具確實不能在 Task/Agent 工具產生的子 agent 內呼叫;但**需修正**一點——子 agent 對需許可的工具呼叫並非「一律自動拒絕」,前景(foreground)模式子 agent 的權限提示會轉發給使用者,只有 `dontAsk`/背景模式才會靜默拒絕。核心結論不變:六階段中「需求梳理」「人審調整」「確認執行」三個需要真人即時回應的節點,仍必須設計在主對話層直接呼叫 AskUserQuestion/Plan Mode,不能包在委派出去的子任務裡——這與本專案 `clarify-first.md` §2 既有規則一致。
3. **分流放在文件或流程的第一個決策點**,而非期待讀者線性讀完再自行判斷該不該啃這份文件(Stripe API 文件「不是開發者?→」模式);術語第一次出現處就地一句話解釋,不建一份要額外讀的集中詞彙表(plainlanguage.gov 原則,經查證屬實)。
4. **驗證/驗收輸出採「結論置頂 + 單句總裁決/燈號 + 技術代號括號保留」三段式呈現**,原始 JSONL 與 Decision 表不修改、不竄改,白話層是從同一機器可讀來源衍生的附加產物。**驗證方式需拆成兩種,不可混為一談**(plan-reviewer 批判後修正):
   - **機械可查(可判 FAIL,遵循 `review-protocol.md` §5 與 `judgment-rubrics.md` 的既定原則——FAIL 只能基於機械可檢項)**:忠實度檢查,即白話摘要陳述的結論是否與技術版 Decision/VERDICT 一致(例如白話層說「安全可接受」但技術版是 FAIL,這是可機械比對的事實矛盾,fresh-context agent 可以且應該判 FAIL);以及覆蓋率檢查(稽核清單列出的術語是否每個首次出現處都有註解,可用腳本/grep 驗證存在性)。
   - **主觀判斷(不可判 FAIL,只能列入非阻斷 Suggestions)**:「這樣寫算不算夠白話」「這句話讀起來順不順」——這是文字風格/taste 判斷,依 `judgment-rubrics.md` §6 屬弱模型做不好、也不該假裝能機械認定的能力邊界,不得成為擋下白話層上線的閘門。
   - 兩者都沿用 harness 既有「驗證不可自證」原則(由非撰寫者的 fresh-context agent 檢查),但只有前者能真正「擋下」不合格的白話層。
5. **風險分級確認取代齊頭式 y/n 或齊頭式全自動**:低風險可選擇性確認,高風險/不可逆動作前設置人審檢查點並要求非平凡輸入,互動模式不可是唯一入口(需保留非互動路徑)——這是呈現層改動,不拆除 ExecPlan/Plan Mode 既有人審機制本身。(註:「監督強度應對應風險高低」這條原則本身合理且與 clig.dev 的風險分級一致,但**引用來源需修正**——查證發現 Anthropic《Building Effective Agents》原文只提到「在檢查點暫停等待人類回饋」,沒有「不可逆」與「風險分級」的字眼,原始歸因張冠李戴,類似論述實際見於另一篇文章。此設計原則保留,但不應再引用該文章作為出處。)
   **適用範圍限縮(plan-reviewer 批判後修正)**:clig.dev 查證確認的「要求輸入非平凡字串」模式,其證據基礎是**破壞性/不可逆操作**(如刪除、force push);它本身就是刻意設計的摩擦,不是為「常規人審關卡」設計的。本文件不應把它外推成非技術用戶日常會遇到的一般確認機制——只用在 ExecPlan/PR 這類真正高風險、不可逆的節點,其餘一律維持較輕量的確認方式。且確認短語必須設計錯誤復原路徑(見 §3 Tier B/C 的更新)。
6. **先給極簡摘要索引,細節按需展開**(progressive disclosure):不要求非技術使用者一次啃完百行規則檔,讓摘要成為預設可見層、完整規則檔成為按需點入的深層。

## 3. 分層提案

### Tier A:文件層快贏(每項 effort S,近乎零風險)

| 提案 | 具體做法 | 解決的障礙 |
|---|---|---|
| 六份規則檔術語內嵌白話註解 + 一行摘要 | 在六份 `.claude/rules/*.md`(plan-first、clarify-first、judgment-rubrics、model-dispatch、parallel-worktree、security)的標題與現有引言之間插入一句斜體白話摘要;對 circuit-break、gate-softening、context_firewall、invariant 等術語,僅在首次出現處加括號白話註解。這些檔案沒有行數上限,不與 progressive disclosure 原則衝突。不改動任何可執行判準文字本身 | 入口術語稽核的 blocking/major 項(`plan-first.md:11/13`、`clarify-first.md:22/29/36`、`judgment-rubrics.md:19/57`、`model-dispatch.md:14/22/31/48`) |
| CLAUDE.md **不內嵌**,改用外部一頁式對照卡 | plan-reviewer 批判後修正:CLAUDE.md 自訂「routing hub ≤100 lines」硬限制(`CLAUDE.md:2`),內嵌註解會撐大它,且直接違反設計原則 6(progressive disclosure——摘要為預設層、細節按需展開)。改法:新增一份極簡的 `docs/PLAIN/claude-md-crib-sheet.md`(≤20 行,先於 Tier C 完整版 `docs/PLAIN-INDEX.md` 存在,作為其第一塊拼圖),只解釋 CLAUDE.md 決策樹裡最卡關的幾個詞(ExecPlan、Plan Mode 的差異——用一句話講清楚「小改動直接做,大改動/跨模組要先寫計劃給你看過再做」);CLAUDE.md 本文加一行連結指向它,不擴充本文行數 | 入口術語稽核的 `CLAUDE.md:21/24/30/31-32/39/52/73/87` 各項(修正原引用 `CLAUDE.md:30` 為 clarify-first 判準所在行,ExecPlan/Plan Mode 實際分岔在 `CLAUDE.md:31-32`) |
| `parallel-worktree.md` 白話化 + 入口分流句 | 開頭加一句白話定義(worktree = 同時開好幾個獨立資料夾工作),git 指令旁加白話風險註解(stash 可復原 vs reset --hard 永久丟棄)。README/CLAUDE.md 各加一句「不會下指令?直接把這句貼給 Claude Code:『幫我完成專案初始化,交給它做前兩步』」 | `parallel-worktree.md:11/36/53`;`README.md:13/14/117`、`CLAUDE.md:7-10` |
| 修正假成功訊息與文件自相矛盾 | `init.sh.template` 偵測到佔位符未填時,改印「⚠ 尚未設定,不代表通過」取代目前無條件印出的 `init OK`;`docs/INDEX.md` 補上實際專案名稱(先解除自身未活化狀態);`harness-maintenance.md` 已自述讀者是 AI(第3行),只需**補一句人類導向句**指向對應人類版本,不必重複宣告讀者身分 | `init.sh.template:8-19`、`docs/INDEX.md:1/4`、`harness-maintenance.md:3` |
| 驗證輸出加「單句總裁決 + 燈號」置頂層 | `review-protocol.md` 的 Decision 區塊上方加一句白話總裁決 + 燈號(狀態 + 原因 + 下一步三段式,借鏡 RAG 燈號慣例),INV-id/`[SEC]`/`[QA]` 標籤保留在括號內不刪除;`acceptance-run.py` 的 Summary 行旁加白話解讀(如提醒 negative-lint 這類 expect-fail 案例「PASS 代表故意失敗成功」)。不修改任何機器判讀邏輯 | `review-protocol.md:123-166`、`acceptance-run.py:279/288-290` |

### Tier B:引導式 slash command / skill(不建 GUI,effort M)

| 提案 | 具體做法 | 風險 |
|---|---|---|
| 新增 `/guided-start`:主對話層六階段白話引導 | 新增 `.claude/commands/guided-start.md`(在主對話執行,不包進 Agent/Task 子任務):分批用 AskUserQuestion 收集需求(1-2 題一組,先覆誦已知再問剩下的)→ 呼叫 Plan Mode/ExecPlan 產出計劃 → 計劃摺疊成白話摘要置頂、技術 diff 放後面 → 高風險/不可逆節點(如即將執行的 ExecPlan 涉及刪檔或跨模組大改)才要求輸入確認短語,其餘維持輕量確認 → 執行 → 驗收階段委派 fresh-context agent 附加白話摘要於 PASS/FAIL 之上(僅檢查摘要與技術結論的忠實度,不判斷「夠不夠白話」,見 §2 原則 4)→ 用 CLAUDE.md 既有 ✓Done/→Next/⚠Note 模板呈現最終結果並連結真正證據檔路徑,使該模板首次被實際機制連結而非孤兒設計。**確認短語錯誤復原**(plan-reviewer 批判後補上):打錯字不鎖定、不計次數上限,直接重新顯示「請照打:XXX,或輸入『取消』返回上一步」;連續失敗改為改問 yes/no 式的簡化確認並記一筆 `state/` 遙測供之後檢討這個機制對非技術用戶是否過度摩擦 | `/guided-start` 是决策樹外的**第二條路徑**,若它對 ExecPlan 觸發條件的判斷邏輯與 CLAUDE.md 決策樹本文出現差異,兩條路徑會給出不同結果(例如一邊判定要開 ExecPlan、一邊判定不用)——這是與 Tier C 雙軌文件相同性質的「治理路由邏輯多一個來源」風險,不只是文件層問題。緩解:`/guided-start` 的判斷邏輯必須直接呼叫/引用 CLAUDE.md 決策樹本文而非另寫一份摘要版判準,只包裝呈現層 |
| 改寫 `.claude/uiux/WORKFLOW.md` 的「快速上手」範例 | 把 `@uiux-agent please help me design...`、`/ui-ux-pro-max` 等示範句改為白話優先(「你只要說『幫我設計登入畫面』就好」),`@agent`/斜線語法改列為「進階/可選捷徑」註記而非唯一教法,與 `model-dispatch.md` 已經做到的「主對話自動路由、使用者不必知道 agent 名稱」設計意圖對齊 | 低,單檔案改動,不涉及判準邏輯 |
| 驗收證據轉譯腳本 + 近似 agent 白話同義觸發詞 | 新增 `scripts/translate-acceptance.py`:讀取 `state/acceptance/*.jsonl` 與 `docs/reviews/*.md`,仿 CTRF 樣板轉譯模式衍生一份白話摘要檔(不修改、不取代原始證據檔)。為 market-researcher/data-analyst/competitive-analyst/spectra-amplifier 的 frontmatter description 增加白話同義觸發詞(如「幫我看看市場」「這個功能想清楚了嗎」),降低使用者需講對 TAM/SAM/SOM/acceptance criteria 才能觸發正確 agent 的靜默誤判風險 | 低,轉譯腳本是唯讀衍生產物;同義詞擴充有極小的誤觸發風險(需簡單測試新舊觸發詞不衝突) |

### Tier C:結構性重組(effort L,需先過 ExecPlan)

| 提案 | 具體做法 | 風險 |
|---|---|---|
| 雙軌文件:`docs/PLAIN/` 白話衍生索引 | 新增 `docs/PLAIN-INDEX.md` 作為人類起點,每份 `.claude/rules/*.md` 對應一份極簡白話衍生版。技術版規則檔本身完全不動、維持 AI 的唯一 canon 來源;白話版標明「衍生自 X,如有衝突以 X 為準」防止正典分裂,每次更新後須委派 fresh-context agent 做 read-back 才可上線 | 雙邊修改不同步導致正典分裂;需要明確的稽核週期與負責人 |
| 風險分級確認機制(擴充而非取代既有 hooks/人審) | 在 ExecPlan/PR 等中高風險關頭,於既有人審步驟之上加白話摘要 + 風險分級確認(低風險可選擇性確認;高風險要求輸入確認短語,且必須內建與 Tier B 相同的錯誤復原路徑——打錯字重新提示+可取消,不鎖定使用者)。此變更涉及 `.claude/hooks/` 或 `execplan-lifecycle.md` 的機制性調整,屬於 CLAUDE.md 決策樹定義的「跨模組變更」,**本身必須走 ExecPlan 流程並經人審,不可用「讓非技術用戶友善」的名義繞過治理去改治理機制本身** | 修改治理機制本身的風險;需要明確授權;確認短語模式的證據基礎是破壞性操作(見 §2 原則 5 適用範圍限縮),擴大使用前應先在 Tier B 的 `/guided-start` 小範圍驗證這個摩擦對非技術用戶是幫助還是困擾,再決定要不要擴大到 hooks 層 |

## 4. MVP 建議(分三階段)

**硬限制貫穿全程:不拆除既有治理機制。**

- **Phase 1(先做,S effort,近乎零風險)**:全部 Tier A 提案。這些改動只在既有文件上疊加白話說明,不改變任何可執行判準、不改變任何治理流程,風險最低;用 §2 原則 4 定義的機械忠實度檢查(而非「夠不夠白話」的主觀判斷)做 fresh-context 驗證——可在做 Tier B/C 之前先驗證「白話翻譯這條路本身有沒有效」。
- **Phase 2(視 Phase 1 效果決定範圍,M effort)**:先做 `uiux/WORKFLOW.md` 白話化與近似 agent 白話同義觸發詞(風險低、單檔案改動),再做 `/guided-start` 雛形——但建議先只做「需求收集」與「驗收白話摘要」兩段(呼叫既有 Plan Mode/ExecPlan,不新建判準),驗證主對話層分批提問與驗收轉譯腳本的實際體驗後,再決定是否擴充到完整六階段。
- **Phase 3(視 Phase 1-2 成效與人類明確決定,L effort,需要 ExecPlan)**:雙軌文件與風險分級確認機制屬結構性重組,前者有正典分裂風險、後者涉及修改治理機制本身——兩者都應按 CLAUDE.md 決策樹規則走 ExecPlan、經人審。是否值得投入,應等 Phase 1-2 的 read-back 驗證結果出來後再由人類拍板。

## 5. 承重牆宣稱查證結果(9 條)

**7 條 CONFIRMED**:clig.dev 風險分級確認(Severe 級要求非平凡輸入)、gh/Stripe CLI 裝置碼分離通道確認、Plan Mode 唯讀探索+核准前不變更狀態、plainlanguage.gov 術語就地定義原則、Diátaxis Reference「只描述不解釋」誡律、CTRF 樣板轉譯模式(機器 schema 不被修改)、Claude Code 內建 Explanatory output style(**查證附帶技術細節修正,供未來若採用此模式時參考**:`/output-style` 指令已於 v2.1.91 移除,現行改用 `/config` 或 settings.json 的 `outputStyle` 欄位切換;本文件 §2/§3 未實際引用該指令,此處僅記錄以免日後落地時踩坑)。

**2 條 REFUTED(已於 §2 修正反映)**:
1. ~~Anthropic《Building Effective Agents》主張「不可逆動作前設置人審檢查點,監督強度應對應風險高低」~~ → 原文只提「在檢查點暫停等待人類回饋」,無「不可逆」「風險分級」字眼,原始歸因張冠李戴(類似論述實際出自另一篇文章《Measuring AI agent autonomy in practice》,但本次未直接查證該文)。設計原則本身保留(與 clig.dev 一致),但不應引用該文章為出處。
2. ~~AskUserQuestion 不可在子 agent 內使用,且子 agent 對需許可工具呼叫一律自動拒絕~~ → 前半屬實,**後半錯誤**:子 agent 並非一律自動拒絕,前景模式的權限提示會轉發給使用者,只有 `dontAsk`/背景模式才靜默拒絕。核心結論(澄清/確認留在主對話層)不受影響,已在 §2 原則 2 修正措辭。

## 6. 開放問題(待人類裁決)

1. **雙軌文件長期一致性**:技術版 `.claude/rules/*.md` + 白話版 `docs/PLAIN/` 是否會因兩邊修改不同步造成正典分裂?由誰負責保證一致、多久稽核一次?
2. **治理詞彙的顯隱程度**:非技術使用者最終要不要「看到」ExecPlan / Plan Mode 這兩個詞本身?完全用使用者自己的白話詞彙包裝隱藏底層機制名稱,還是保留原詞但加註解——這個決定直接影響 Tier C 的具體寫法。
3. **風險分級確認機制的授權範圍**:若要落地到 `.claude/hooks/` 或 `execplan-lifecycle.md`,是否要先走一次完整 ExecPlan 治理流程再實作?由誰核准這個「改治理機制本身」的變更?
4. **`/guided-start` 的定位**:取代 CLAUDE.md 決策樹的預設入口,還是僅作為非技術使用者的替代路徑、與現有決策樹並存?兩者對後續維護成本與「兩條路徑會不會分岔出不同結果」的風險差異很大。
5. **白話層驗證頻率**:fresh-context read-back 驗證要多頻繁執行——每次新增白話內容都驗證,還是只在初次上線與重大修改後做一次?驗證成本要不要計入這次改善的預算?
6. **README 入口拆分**:是否值得投入拆出一份 `README-STARTHERE.md`(現有 README 全面降級為進階版),還是先做 Tier A 的一句分流句觀察實際效果就好?

## 附錄:主要來源

- 內部稽核讀過的檔案:見各稽核 JSON 的 `sources` 欄(CLAUDE.md、六份 `.claude/rules/*.md`、README/README_zh.md、docs/INDEX.md、`.claude/templates/init.sh.template`、`docs/harness/NEW-PROJECT-VALIDATION.md`、`.claude/protocols/{handoff,review,execplan-lifecycle,harness-maintenance}.md`、`scripts/acceptance-run.py`、`state/*.jsonl`、`agent_docs/AI-TEAM-REGISTRY.md`、`.claude/uiux/WORKFLOW.md`、多份 `.claude/agents/*.md` 與 `.claude/skills/*/SKILL.md`)
- 外部研究:diataxis.fr;digital.gov/guides/plain-language;clig.dev;cli.github.com/manual/gh_auth_login;docs.stripe.com;code.claude.com/docs(agent-sdk/user-input、output-styles);anthropic.com/engineering/building-effective-agents;rebelsguidetopm.com;securityideals.com;testparty.ai;accessible.org;github.com/ctrf-io/github-test-reporter;common-changelog.org;guidance.publishing.service.gov.uk
