給 BaseAIProject 非技術背景使用者的引導式、自然對話入口指令。把一句白話需求轉成:(0) 偵測是否在接續進行中的工作、(1) 用一兩個針對性問題補齊還缺的意圖欄位、(3) 把路由判斷交還給 CLAUDE.md 既有的 Decision Tree Before Acting、(4) 工作完成後,把驗收證據翻成白話。這個指令**不新增任何自己的治理判斷**——每一個路由決定、每一條驗收標準,都來自一份本來就存在的檔案,而且每次用到時都是即時重讀,不是憑記憶複製。

**Non-Goals(這個縮小版刻意不做的事)**:沒有「確認再執行」/ 錯誤復原這一段(這是完整六階段引導流程的其中一段,本 MVP 只做其中一片);本指令沒有被接進 README/CLAUDE.md 成為新的正典入口——它是與 Decision Tree 並存的替代路徑,永遠不是取代它;控制權在 Step 3 交出去之後,本指令不會繼續追蹤那項工作的後續進度。

依序執行以下步驟,每步完成後簡短回報。**不要跳過 Step 3**——這是讓本指令維持「翻譯既有決策樹」而不是變成第二套、互相打架的判斷來源的唯一防線。

## Step 0: 偵測是否在接續進行中的工作

在問使用者任何問題之前,先檢查 `docs/plans/active/` 底下有沒有 `F-*.md`。

- 如果目錄是空的、或沒有看起來進行中的 ExecPlan(檢查其 `Status` 欄位,以及 `state/feature-list.json`,若存在的話)→ 沒有東西可接續,進 Step 1。
- 如果有一份進行中的 ExecPlan,**而且**使用者這句話讀起來像是在接續它(提到同一個 feature、說「繼續」「接著做」、或從 ExecPlan 的 `## 6. Progress Log` 或 `## 9. Handoff Manifest` 接上一個話頭)→ 直接跳到 Step 4(使用者要的是驗收/進度讀報,不是開一個新需求)。
- 如果分不清這句話是全新需求還是接續 → **不要**靜默地選一邊猜。用一句話講出那份進行中的 ExecPlan 名稱,直接問使用者:「這是在講已經進行中的 `F-NNN-<slug>`,還是新的事?」等回答後再繼續。

## Step 1: 收集需求

1. 用一句白話覆誦你理解到的使用者需求——這樣理解錯誤會立刻浮現,而不是等到計畫寫完才發現。
2. **現在就**去讀 `.claude/rules/clarify-first.md` §1(讀它當下的原文,不是記憶中的摘要),用它的 4 欄位檢查表核對這個需求:目標使用者、成功指標、範圍邊界/non-goals、觸發時機。本指令不維護自己的一份判準副本——它每次都即時重讀規則檔本身,這樣就不可能跟規則本身產生落差。
3. 套用 clarify-first.md §1 當下判定「要不要停下來問」的訊號(本指令不持有這個門檻的副本,每次都即時重讀)。如果判定要問,就把缺漏的欄位分批問,每輪 1-2 個簡短問題(有 `AskUserQuestion` 就用它,沒有就用一般文字),而且絕不重問使用者在這次對話裡已經講過的事。
4. 收集的同時,也**即時**去讀 `.claude/rules/plan-first.md` 的 Exceptions 清單(本指令同樣不持有這份清單的副本)。如果這個需求已經明顯落在它當下某條 Exception 裡 → 直接跳過 Step 3,進入直接執行。用一句話明講適用哪一條 Exception——引用剛讀到的原文,不是憑記憶。
5. 否則,等 4 個欄位都覆蓋得差不多了(或使用者確認沒有更多要補充的),進入 Step 3。

## Step 3: 交由 CLAUDE.md 的 Decision Tree Before Acting 路由

這是本指令唯一會做的判斷,而且嚴格來說這不是本指令自己的判斷——是 CLAUDE.md 的。

1. **現在**就去讀 `CLAUDE.md`「Decision Tree Before Acting」段落的即時原文,讀全文——不是意譯,也不是「上次讀過的印象」。
2. 把它第 0-5 項的判準,原封不動套用到剛收集好的需求上。本指令不持有自己的路由表、不持有自己的門檻清單、也不持有那棵決策樹的任何捷徑副本——它只是把決策樹自己產出的結論,翻成白話講給使用者聽。
3. 把控制權交給決策樹指名的那個分支——起草 ExecPlan(`docs/plans/active/`,規格見 `docs/plans/PLANS.md`,流程依 `.claude/protocols/execplan-lifecycle.md`)、進入 Plan Mode、或直接執行——並用一句話講清楚選了哪個分支、為什麼,引用對應到的那條判準原文。
4. 控制權一旦交出去,本指令這一輪的任務就結束了——它不會留在迴圈裡盯著後續工作進行,也不會在任務中途重跑這份檢查表(那是 `judgment-rubrics.md` §3 的工作,不是本指令的)。

## Step 4: 把驗收證據翻成白話

等交出去的工作真的跑完驗證後(ExecPlan §5 Verification Strategy、一份 review 報告,或兩者都有):

1. 執行 `python3 scripts/translate-acceptance.py [plan.md] [--review <review-file>]`(省略 `plan.md` 會讓它預設取 `docs/plans/active/` 裡最新的 ExecPlan;如果這項工作有對應的 `docs/reviews/*.md` 報告,加上 `--review`)。
2. 原樣採信它的輸出——它是一個唯讀的翻譯工具,不是第二道驗收關卡,找不到某項證據時它會明講,不會用猜的。
3. 把這份輸出套進 CLAUDE.md 既有的三行回報模板(`✓ Done / → Next / ⚠ Note`),並確保每一行只要宣稱某件事通過或失敗,都連結到腳本回報的真實證據檔路徑(它讀取的那份 `state/acceptance/<stem>.jsonl`,或它翻譯的那份 `docs/reviews/*.md`)——絕不在沒有路徑佐證的情況下覆誦一個結果。
4. 如果腳本回報它找不到對應證據(沒有 jsonl、沒有 review、或比對結果模稜兩可)→ 在 `⚠ Note` 那行明講這件事,不要捏造一個狀態。

## 參考

- `.claude/rules/clarify-first.md` — Step 1 即時重讀的 4 欄位檢查表
- `CLAUDE.md` — 「Decision Tree Before Acting」,Step 3 交由它決定路由的權威來源
- `.claude/rules/plan-first.md` — Step 1 用來判斷「連 Step 3 都不用進」的 Exceptions 清單
- `.claude/protocols/execplan-lifecycle.md` — Step 3 若交入 ExecPlan 範疇後進入的 10 階段生命週期
- `scripts/translate-acceptance.py` — Step 4 呼叫的唯讀驗收/review 翻譯工具
- `.claude/protocols/review-protocol.md` — `translate-acceptance.py` 解析的 review 報告格式(`VERDICT:` 行、白話燈號層)
