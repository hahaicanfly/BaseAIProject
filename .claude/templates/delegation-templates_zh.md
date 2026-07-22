# E. 派工 Prompt 模板（Delegation Templates）

> 配套規則：`.claude/rules/model-dispatch.md`（何時派工、升降級）。
> 用法：複製對應模板 → 填 `[…]` 空格 → 作為 Agent tool 的 prompt。**三件套（目標與動機／驗收條件／回報格式）缺一不派。**
> 每個模板末尾的「回報格式」直接約束 subagent，不要刪。

## 通用規範（所有模板共用，派工時附在 prompt 末尾）

```
回報規範：
- 回報 ≤ 40 行；只回結論與 檔案:行號，禁止貼超過 10 行的代碼/原文
- 超過 40 行的產物寫入檔案，回報只給路徑
- 如實回報失敗：卡在哪、試過什麼；禁止回報「大致完成」
- 最後一行必須是 [HANDOFF: main] 或 [VERIFY_FAILED: <原因>] 或 [HUMAN_ATTENTION_REQUIRED: <原因>]（`main` = 回報主對話，已列入 handoff-protocol.md 白名單）
- 破壞性指令黑名單：禁止對「非指派檔案」執行 rm、git checkout --、git restore、git clean、mv 覆蓋——即使是為了測試清理。未追蹤檔案不受 git 保護，刪了就是永久（教訓：ERRORS.md 2026-07-04 誤刪事故）
```

## 範圍宣告（每次派工必填，接在 prompt 的「目標」之後）

黑名單擋破壞性指令；本節是它的正向補集——白名單界定可動範圍，終止條件界定何時停手。

```
範圍宣告：
- 允許讀：[檔案/目錄清單，或「全 repo 唯讀」]
- 允許寫：[明確清單；未列出的檔案一律禁止修改/刪除/移動/建立]
- 禁止觸碰：[高風險路徑，如 .env*、state/、其他任務的 worktree]
- 終止條件：驗收條件全數滿足即停；同一驗收項嘗試 2 次未過即停，回報 [VERIFY_FAILED:*]；發現需要動「允許寫」以外的檔案即停，回報 [HUMAN_ATTENTION_REQUIRED:*]
```

---

## 1. 搜尋定位（找檔案／符號／用法）

- 建議：`Explore` agent；廣度小用 quick、跨多處用 very thorough。不需指定 model。

```
在 [repo/目錄] 中定位 [目標：函式/設定/字串/呼叫點]。
動機：[找到後要做什麼，讓你能判斷哪些結果相關]。
搜尋線索：[已知關鍵字/命名慣例/可能位置]。
驗收條件：
- 每個結果附 檔案:行號 與一句話說明為何相關
- 若搜不到，列出你試過的 3 種以上搜法與關鍵字
回報格式：結果清單（檔案:行號 — 說明），或「未找到 + 已試搜法」。
```

**填好範例**：「在 src/ 中定位所有直接呼叫 fetch() 而未經 apiClient 包裝的呼叫點。動機：要統一加上 retry 與 auth header。搜尋線索：`fetch(`、`axios`。驗收條件：每個呼叫點附檔案:行號；若為 0 個，列出試過的搜法。回報格式：清單。」

## 2. 功能實作

- 建議：`general-purpose`，`model: "sonnet"`；涉架構決策才用 `opus`。多人並行改檔時加 `isolation: "worktree"`。

```
實作 [功能一句話]。
動機與背景：[為什麼要做、使用者場景、相關 ExecPlan/issue 路徑]。
範圍：只改 [檔案/模組清單]；不要動 [排除清單]。
技術約束：[介面簽名/依賴方向/命名，引用 docs/architecture/domains.md 相關節]。
驗收條件（全部滿足才算完成）：
- [測試指令] 通過，貼出實際輸出的最後 10 行
- 新增/修改的每個公開函式有 [測試/使用範例]
- 改動檔案清單與計劃一致，無計劃外改動
- API evidence table：每個第一次使用的外部 API / 第三方 symbol 都要有一列
  `symbol → 定義位置（repo 檔案:行號，或官方文件 URL + 存取日期）`；沒有 evidence 列的外部
  symbol 視同用猜的（CLAUDE.md：NEVER guess API signatures）→ FAIL
回報格式：改動檔案清單（檔案:行號範圍）＋ 測試輸出尾段 ＋ API evidence table ＋ 未決項（若有）。
```

## 3. 代碼重構

- 建議：`general-purpose`，`model: "sonnet"`；重構前後行為必須可證明不變。

```
重構 [目標範圍]，目的：[消除重複/抽介面/降耦合，一句話]。
動機：[現況痛點，附 檔案:行號]。
不變式（重構後必須保持）：
- 對外行為不變：[現有測試清單/黃金輸出] 全數通過
- 公開 API 簽名 [不變 / 允許哪些變更]
禁止事項：不改測試遷就代碼；不放寬型別；不註解掉檢查（judgment-rubrics §4）。
驗收條件：重構前先跑一次測試記錄基線，重構後同指令輸出一致；diff 行數 [上限]。
回報格式：重構摘要（模式一句話）＋ 前後測試輸出對照 ＋ 改動檔案:行號清單。
```

## 4. 研究調查（網頁／文件）

- 建議：`general-purpose`，`model: "sonnet"`；重大選型加派第二個獨立 agent 比對結論。

```
研究問題：[一句話問題]。
動機：[這個答案會決定什麼]。
必查來源：[官方文件/repo/指定網址]；優先一手來源。
驗收條件：
- 每個結論附來源（URL 或 檔案:行號）與日期
- 區分「事實（有來源）」與「推論（你的判斷）」兩節
- 查不到的一律在文中內嵌標記 `[UNCONFIRMED: <claim>]`（標準語法，見 handoff-protocol.md「行內輔助標記」；會被自動收割做週檢），禁止編造
回報格式：結論（≤5 條，每條附來源）＋ 未確認清單 ＋ 建議（≤3 行）。
```

## 5. 代碼審查

- 建議：`code-reviewer` agent（frontmatter 已定 sonnet）；輸出格式以 `.claude/protocols/review-protocol.md` 為準。

```
審查 [分支/PR/檔案清單]，變更意圖：[這次改動想達成什麼]。
重點維度：[正確性/安全/效能/可讀性，至少一個]。
驗收條件：
- 每個 finding 附 檔案:行號、嚴重度（Blocker/Warning/Suggestion，同 review-protocol.md 分級）、具體失敗情境（什麼輸入會壞）
- 無 finding 也要列出「檢查過的維度與方法」
- 不確定是否為 bug 的，在該條 finding 註明「未確認，需人工驗證」，不要寫成斷言
回報格式：依 review-protocol.md 的格式輸出；finding 依嚴重度排序。
```

## 6. Fresh-Context 驗收（驗證不自驗，配 model-dispatch §5）

- 建議：新開 `general-purpose`，`model: "sonnet"`。**prompt 不得含實作過程敘述**，只給驗收條件與檔案路徑——防止驗收員被實作者的自述帶偏。

```
你是驗收員，對以下產出做獨立驗證（你沒有參與實作，不要假設它是對的）。
待驗產出：[檔案路徑清單]。
驗收條件（逐條檢查）：
1. [條件一，可機械判定]
2. [條件二]
驗證方法：
- 文件類：重新讀檔，逐條對照驗收條件，引用 檔案:行號 作證據
- 代碼類：實跑 [測試/指令]，貼實際輸出最後 10 行
- API evidence table（若待驗產出有附）：抽查 ≥3 列 —— repo symbol 必須能在引用的
  檔案:行號 Grep 到；URL 列必須 WebFetch 且該頁面須包含該 symbol
驗收報告只允許兩種結論：
- PASS：逐條列「條件 → 證據（檔案:行號 或 輸出）」
- FAIL：列未過項 → 證據 → 一句話修復建議
FAIL 只准基於上列可機械檢查的驗收條件；風格/寫法/觀點類意見寫入獨立的
「建議（非阻斷，可空）」欄，不得作為 FAIL 理由（model-dispatch §5）。
禁止「看起來沒問題」「應該可以」等無證據結論。
Verdict persistence（強制 —— 驗收結論必須撐過你的 ephemeral context）：
- 用 Write tool 把完整報告（每條 criterion → 證據、實際指令輸出）寫入
  docs/reviews/<YYYY-MM-DD>-<slug>.md。這是你唯一能建立的檔案；其餘一律唯讀。
- 最終訊息必須含 `VERDICT: PASS docs/reviews/<file>.md`（或 `VERDICT: FAIL docs/reviews/<file>.md`）
  這一行 —— stop-retro-logger 會把這行收割進 state/verifications.jsonl，FAIL 還會落入 ERRORS.md Pending Review。
- 之後照常以 handoff marker 結尾（PASS 用 [HANDOFF: main]，FAIL 用 [VERIFY_FAILED: <原因>]）。
```

**填好範例**：「你是驗收員。待驗產出：docs/harness/DIAGNOSIS.md。驗收條件：1) 三大類痛點各恰好 3 項且各附修法 2) 每項至少一個 檔案:行號 證據 3) 含能力極限一節 4) 無 {{佔位符}} 殘留。驗證方法：重新讀檔逐條對照。輸出 PASS/FAIL 報告。」

## 7. 策略研究（file-first）

- 建議：依主題選 `pm` / `market-researcher` / `competitive-analyst` / `data-analyst`
  （各 agent 的 frontmatter `description` 有範圍界線——市場規模 vs. 競品比較 vs. 量化 KPI
  是不同 agent，不要混用）。此模板是「file-first」：完整報告一律落在 `docs/research/`；
  聊天室回覆只是有上限的摘要，絕不是產出物本身。

```
研究問題／策略主題：[一句話問題]。
動機與背景：[這個答案會影響什麼決策、為何是現在]。
必查來源：[官方文件/市場報告/指定網址]；優先一手來源。
範圍宣告：（依上方標準區塊；允許寫的範圍恰好是一個新檔案：
  docs/research/<YYYY-MM-DD>-<slug>.md —— 不得修改/刪除/移動/建立其他任何檔案）
驗收條件（全部滿足才算完成）：
- 已用 Write tool 把完整報告寫入 docs/research/<YYYY-MM-DD>-<slug>.md
  （命名規則見 docs/research/README.md）
- 報告含 `### 假設-證據表`，每一列的 confidence 欄都已填妥
  （高/中/低 —— confidence 欄空白視同 FAIL，不是佔位符）
- 報告含 `### Sources` 一節，至少 3 個可驗證 URL（內部資料則用 檔案:行號）；
  任何無出處主張需行內標記 `[UNCONFIRMED: <claim>]`
- 聊天室回覆是 ≤40 行的摘要：關鍵發現 + 未決問題 + 檔案路徑 —— 完整細節留在檔案內，
  不得貼進回覆
回報格式：≤40 行聊天室摘要（結論 + 已寫入報告的路徑）；報告檔案本身依該 agent 的
Output Format 模板（須含假設-證據表 + Sources —— 確切模板見 agent frontmatter）。
```

把**通用規範**（本檔開頭）附加在每個填好的 prompt 末尾，同 §1-6 模板。
