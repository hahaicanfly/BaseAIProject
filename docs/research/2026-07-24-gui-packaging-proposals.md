# Harness 工作流 GUI 封裝提案

> 日期:2026-07-24
> 來源:四個並行 subagent 報告(pm / competitive-analyst / uiux-agent / architect)+ 主對話彙整,經 plan-reviewer 獨立批判(5 條阻斷性缺陷已修訂補入,見 §6「共同新建工程」與各節標註)
> 狀態:候選提案,待人類選定方向;選定後依 CLAUDE.md 決策樹走 ExecPlan(跨模組)
> 相關:docs/harness/(harness 制度背景)

## 1. 背景與目標

BaseAIProject 的 harness 系統(rules / agents / protocols / hooks / 機械閘門 / state 帳本)已梳理優化完成。下一步:封裝成 GUI(桌面應用或 Web 服務),讓**非技術背景用戶**能直覺走完六階段流程:

```
表達意圖 → AI 梳理需求 → 產出計劃 → 用戶檢視/調整 → 確認後執行 → 結果檢核 + 歷程回顧
```

核心設計約束:GUI 是薄殼,六階段全部映射到既有 harness 機制,不重造流程。但「薄殼」不等於零新工程——執行中人在環管線、失敗迴圈呈現、成本護欄是所有提案共同要新建的(見 §6「共同新建工程」)。

## 2. 產品需求錨定(pm)

**Persona**
- P1 主要「非技術創作者」:懂需求不懂 git/CLI;要能用自然語言表達意圖 → 拿到可信結果,全程看得懂、能喊停。
- P2 次要「半技術進階用戶」:會讀 diff、會下判斷但嫌 CLI 繁瑣;要快速審計劃、看驗收證據、必要時介入。

**六階段 ↔ harness 機制對應**

| 階段 | 用戶看到/做什麼 | 既有機制 |
|---|---|---|
| 1 表達意圖 | 輸入框寫一句想做的事 | 主對話入口(CLAUDE.md 決策樹) |
| 2 需求梳理 | AI 回問缺漏、用戶補答 | clarify-first 4 欄檢查(`.claude/rules/clarify-first.md` §1) |
| 3 產出計劃 | 步驟/範圍/風險卡片 | Plan Mode / ExecPlan(plan-first.md;execplan-lifecycle.md) |
| 4 檢視調整 | 編輯步驟、批准或退回 | ExecPlan human-approval 關卡(execplan-lifecycle.md Phase 3) |
| 5 確認執行 | 進度、即時狀態、可中止、**回答 AI 的執行中追問** | 子代理委派 + `pre-tool-use-guard.py`;追問/circuit-break 升級為新建 UI 管線(§6 共同新建工程 1) |
| 6 檢核+回顧 | 驗收逐項證據;FAIL 時顯示修復輪次與「需要你決定」節點;歷程時間軸 | fresh-context 驗收(model-dispatch §5)、修復迴圈上限(judgment-rubrics §2.5/§3)、transcript JSONL + `state/*.jsonl` |

**成功指標**:首次完成任務時間(TTFT)/ 計劃修改率 / 驗收一次通過率 / 執行中止率 / 需求梳理平均輪次。(各指標的驗收門檻值待人類定,如 TTFT < 30 分鐘)

**MVP MoSCoW**
- Must:意圖輸入、clarify 問答、計劃可視化+批准/退回、執行進度與中止、**執行中追問應答與失敗迴圈呈現**、**成本護欄(預算上限+即時花費+超限暫停)**、驗收證據逐項呈現
- Should:歷程時間軸、計劃內聯編輯、單用戶多任務並行
- Won't(暫不):多用戶協作、自訂 agent 編排、行動端、離線推論
- MVP 範圍界定(草案):**單活躍任務 + 佇列**;架構 D 的多 session 能力留給日後開並行(見 §7 Q7)

## 3. 競品洞察(competitive-analyst)

調研 Lovable / Replit Agent / Devin / Claude Code / Manus(六階段覆蓋矩陣與 URL 見附錄 A)。五條可借鏡結論:

1. **實體「開始執行」按鈕當硬關卡**(Replit「Start Building」、Devin、Manus approve):比 Lovable 式「送出即隱式執行」更讓非技術者感知「現在要動手/要花費」。
2. **執行過程翻譯成人類可讀時間軸**(Manus Task Replay 截圖+決策點、Devin Session Insights):預設隱藏終端輸出,保留「展開技術細節」給進階用戶。
3. **「書籤 + 還原=新版本」的可逆設計**(Lovable Versioning 2.0):用戶敢嘗試不怕破壞,免懂 git 語意。
4. **計劃逐步編輯/重排後才整體核准**(Devin):優於一次性整包核准,貼合本專案階段 4(注:Replit 的逐步重排未獲證實,引用時降權,見附錄 A 未確認項)。
5. **反例教訓**:Claude Code 的 Plan Mode 是最貼近本專案的硬關卡,但執行呈現仍以終端/diff 為主——「計劃關卡」與「非技術友善的執行呈現」是兩個必須分開設計的問題。

## 4. UIUX 互動範式(uiux-agent,Phase 1 概念)

**範式一:對話流 + 階段卡片** — 計劃拆成步驟卡,每卡「調整這步」→一句話輸入框,AI 白話覆述修改;學習成本低(像聊天),控制感中(依賴自然語言理解),實作複雜度中高。

**範式二:精靈步進式** — 計劃總覽逐條「我會做的事」,每條可編輯/刪除/插入;任何修改觸發「重新確認」才能執行。學習成本低(線性表單最熟悉),控制感高(所見即所得),實作複雜度低。

```
┌────────────────────────────────┐
│ ← 計劃總覽(第3/5步)             │
│ 我會做的事:                     │
│ 1. 讀取你的相片    [編輯][刪除]│
│ 2. 依日期分類      [編輯][刪除]│
│ 3. 建立相簿        [編輯][刪除]│
│    [+ 插入新步驟]               │
├────────────────────────────────┤
│  [返回修改]        [確認,開始]│
└────────────────────────────────┘
```

**範式三:文件畫布中心式** — 計劃即文件,直接刪字/插入/反白改寫,AI 偵測修改自動調整受影響段落;歷程用版本時光機滑桿。控制感最高,但需理解「文件即計劃」隱喻,且自由編輯轉回結構化計劃的實作複雜度最高。

**UIUX 建議**:初版走範式二(控制感高、實作風險最低);範式三留作進階;範式一作輔助輸入管道,不作唯一主線。(範式一/三線框見附錄 B)

## 5. 技術架構評估(architect)

| 路徑 | 概要 | 金鑰 | 量級 | 最大風險 |
|---|---|---|---|---|
| A 桌面 app(Tauri/Electron)| 內嵌 Agent SDK 子程序,GUI 讀 `state/*.jsonl` + transcript | OS keychain,IPC 不經手 | M | SDK 版本綁定 + 跨平台打包/簽章維護成本 |
| B 自架 Web 服務 | 伺服器託管 session,WebSocket 推進度 | 後端 Secrets Manager | L | `pre-tool-use-guard.py` 僅本機防護,伺服器端須重建沙箱與多租戶邊界 |
| C 最小改造 | 現有 Claude Code + 自訂 skills/output-style | 沿用現有 | S | 非技術用戶仍面對 CLI/Markdown,體驗天花板低 |
| D 本地 daemon + 瀏覽器 UI | daemon 常駐管理 SDK sessions,瀏覽器連 localhost | 本機 keychain,daemon 注入,不下發前端 | M | localhost 服務須綁 token/CORS 防竊連 |

四條路徑的六階段映射相同(見 §2 表),隔離用 worktree(parallel-worktree.md)、安全閘用 `pre-tool-use-guard.py` 原生生效(C/A/D)。

**架構師推薦:D** — 兼得 A 的「金鑰不落前端 + 本機安全邊界原生生效」,免去 B 最大風險(重建伺服器沙箱),又以瀏覽器 UI 免除 A 的跨平台打包負擔;daemon 僅為 session/worktree 編排薄層。日後需多人雲端協作再升級 B。

## 6. 三個封裝提案

### 提案一「精靈工作室」——本地 daemon + 瀏覽器 UI × 精靈步進式(推薦)

- **組成**:架構 D + 範式二為主線、範式一對話流為輔助輸入;借鏡競品結論 1(實體執行按鈕)、2(人類可讀時間軸)、3(書籤還原)、4(逐步編輯後整體核准)。
- **六階段呈現**:意圖輸入框 → clarify 問答卡 → 計劃逐條列表(編輯/刪除/插入,改動即觸發重新確認)→「確認,開始」硬關卡 → 時間軸進度(預設無術語,可展開技術細節)→ 驗收證據逐項 + 歷程時光機。
- **優勢**:非技術用戶控制感最高;guard、worktree、ExecPlan 核准、state 帳本原生沿用(但 §6「共同新建工程」三項為新建管線,並非零改寫);量級 M 可控;免跨平台打包。
- **風險**:(1) **P1 首裝摩擦**——裝常駐 daemon + 取得 API key + 寫入 keychain,對不懂 CLI 的用戶比學 git 更難,是本提案對 P1 的最大流失點;緩解:一鍵安裝精靈(打包 Claude Code/SDK 依賴)、OAuth 式取 key 流程、或先導期由 P2 半技術用戶協助佈署。(2) **localhost 外洩**——transcript 與 `state/*.jsonl` 含專案內容,token/CORS 錯置即遭本機其他程序或惡意網頁竊讀,須與資料隱私一併設計。(3) daemon 與 Claude Code/SDK 版本耦合。
- **適用**:單機單用戶為主的正式產品化路線。

### 提案二「最小可行封裝」——現有 Claude Code + skills 引導層

- **組成**:架構 C。不寫新前端;以自訂 skill(如 `/guided-task`)引導六階段對話、output-style 美化計劃與驗收呈現,Claude Code desktop/web 當現成外殼。
- **優勢**:量級 S,1–2 週可上線驗證「六階段流程對目標用戶是否真的有價值」;零新增安全面。
- **風險**:天花板低——用戶仍看得到 Markdown/工具呼叫,對 P1(純非技術)只能算「可忍受」,不算「直覺」。
- **適用**:作為提案一動工前的先導驗證(把 clarify 問答話術、計劃卡片資訊架構先在真實用戶上試錯),或給 P2 半技術用戶的過渡方案。

### 提案三「雲端協作服務」——自架 Web 服務 × 文件畫布

- **組成**:架構 B + 範式三(計劃即文件、直接改寫、版本時光機),支援分享連結與多人檢視。
- **優勢**:體驗與協作天花板最高;範式三的「文件畫布」與多人評註天然互補;可水平擴展。
- **風險**:量級 L;必須在伺服器端重建整套安全邊界(沙箱、多租戶、guard 等價物)——這是 harness 現有資產覆蓋不到的新工程;自由編輯↔結構化計劃的雙向同步實作複雜。
- **適用**:提案一驗證成功、出現多用戶/團隊需求後的演進方向,不建議首發。

### 所有提案的共同新建工程(plan-reviewer 批判後補入)

三項是 harness 已明訂、但 GUI 形態下必須新建管線才能承接的機制——任何提案都逃不掉:

1. **執行中人在環管線**:context_firewall 子代理不能中途問用戶(clarify-first §2),追問與 reactive circuit-break(judgment-rubrics §3)原由主對話承接;GUI 形態下必須新建「升級到人類」的通知+應答 UI,否則執行中遇歧義或連續失敗時用戶會卡死。
2. **失敗迴圈呈現**:驗收 FAIL 不是終點——harness 明訂修復輪次與「兩輪無改善即問人」(judgment-rubrics §2.5/§3);UI 需呈現「AI 修復中(第 N 輪)」與明確的「需要你決定」節點,而非裸 FAIL。
3. **成本護欄**:非技術用戶自備 API key,失控迴圈=真金白銀;需任務級預算上限、即時花費顯示、超限自動暫停+問人(high-volume paid API 本就是 harness 的 circuit-break 觸發條件);fresh-context 驗收 agent 的額外成本也應呈現在歷程時間軸。

### 建議路線(分期)

```
提案二(S,2 週先導)→ 提案一(M,主建設)→ 提案三(L,有協作需求才啟動)
```

理由:提案一是風險/回報最平衡的正式形態;提案三的伺服器安全重建成本只在多用戶需求成立時才值得付。**先導的驗證邊界**:提案二的 Markdown 外露對 P1 僅「可忍受」,故它能乾淨驗證的是 clarify 話術與計劃卡資訊架構,不能驗證 P1 的完整流程價值——先導目標應限縮於此,結論餵給提案一。

## 7. 開放問題(待人類決策)

1. **交付形態**:接受「本地 daemon + 瀏覽器」嗎?還是必須雙擊即用的桌面 app(A)/雲端服務(B)?
2. **執行後端**:綁用戶本機的 Claude Code/SDK,或後端代管(走向提案三)?注意張力:本機路線對 P1 的首裝摩擦(daemon + API key)可能比學 git 更難,若無一鍵安裝方案,「非技術用戶」定位與架構 D 互相矛盾。
3. **git 抽象程度**:非技術用戶完全隱藏 git(只見「版本快照」),或保留可展開的技術視圖給 P2?
4. **危險操作呈現**:推分支/刪檔等 guard 攔截事件,GUI 上如何二次確認(彈窗?升級為人審關卡?)
5. **是否先走提案二先導**:接受兩週先導期,或直接動工提案一?
6. **計費與預算**:任務預算上限預設多少?超限行為(自動暫停 vs 即時問人)?花費以什麼單位呈現給非技術用戶(金額/點數/次數)?
7. **並行範圍**:MVP 是否需要單用戶多任務並行?(草案:單活躍任務+佇列,見 §2 MoSCoW)

## 附錄 A:競品六階段覆蓋矩陣

| 產品 | 互動範式 | AI澄清 | 產出計劃 | 人審調整 | 確認執行關卡 | 歷程回顧 |
|---|---|---|---|---|---|---|
| Lovable | chat-first(左聊天/右預覽) | 部分 | 部分(討論式) | 部分 | 隱式(送出即動工) | 全:Versioning 2.0 書籤+還原 |
| Replit Agent | chat-first | 部分 | 全:Plan Mode | 部分(可見可評;逐步重排未證實) | 全:「Start Building」按鈕 | 部分:Checkpoint 偏計費單位 |
| Devin | chat/task 導向 | 部分~全 | 全(steps/tools/時程) | 全:可 edit/reorder/逐步 approve | 部分:checkpoint 非硬 gate | 全:Session Replay/Insights |
| Claude Code | chat/prompt(CLI 為主) | 部分 | 全:step-by-step plan | 全:web 版可逐段留言 | 全:Accept edits/Manual 切換 | 部分:靠 git/session,無消費級時間軸 |
| Manus | chat | 全:主動提問 | 全(含步驟相依) | 全 | 全:明確 approve | 全:Task Replay 截圖+決策點 |

未確認項:Replit Plan Mode 是否支援計劃內逐步驟重排(僅查到「可見可審」)。

Sources:
- https://lovable.dev/blog/versioning-with-lovable-two-point-zero
- https://lovable.dev/faq/projects/version-history
- https://alternativeto.net/news/2025/9/replit-launches-plan-mode-for-ai-assisted-planning-without-code-changes
- https://docs.replit.com/billing/ai-billing
- https://docs.devin.ai/product-guides/session-insights
- https://docs.devin.ai/get-started/devin-intro
- https://code.claude.com/docs/en/desktop
- https://www.technologyreview.com/2025/03/11/1113133/manus-ai-review/
- https://github.com/agenaiguy/awesome-manus-replay

## 附錄 B:範式一/三線框

範式一(對話流+階段卡片):

```
┌────────────────────────────────┐
│ 任務:整理相片並分類            │
├────────────────────────────────┤
│ ✓ 1.了解需求          完成      │
│ ▶ 2.整理相片   [調整這步▾]      │
│   3.建立相簿          等待中    │
│   4.完成確認          等待中    │
├────────────────────────────────┤
│   [開始執行]      [聊聊調整]    │
└────────────────────────────────┘
```

範式三(文件畫布中心式):

```
┌────────────────────────────────┐
│ 你的計劃文件           [歷史▾] │
├────────────────────────────────┤
│ ▍1. 讀取你的相片 ✓完成          │
│ ▍2. 依日期分類    ▮進行中       │
│    (你剛把這段改成"依地點") 🖊  │
│ ▍3. 建立相簿      待處理        │
├────────────────────────────────┤
│ 💬 直接在文件裡改字,或這裡留言 │
└────────────────────────────────┘
```
