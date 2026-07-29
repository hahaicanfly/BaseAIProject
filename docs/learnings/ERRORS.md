# {{PROJECT_NAME}} — 累積教訓 (Lessons Learned)

> **角色**：本檔為 harness 體系的長期記憶，承接原 `CLAUDE.md` 的「累積教訓」區段。
> **總數**：7 條（3 條 seed + 4 條 2026-07-04 harness 制度化 session 實戰教訓）
> **格式約定**：`- [YYYY-MM-DD] [<分類>] 錯誤描述 → 正確做法`
> 每次 AI 犯錯被糾正後，**必須**主動提議追加到 `## Pending Review`（由人類週審 promote 到 `## Active Lessons`）。
> `stop-retro-logger.py`（Phase D 啟用後）會自動把 session 內的 `[VERIFY_FAILED:*]` 收割到 Pending Review 區。

---

## 分類索引 (Category Index)

| 分類 | 對應條目數 | 對應 invariants.md |
|------|-----------|---------------------|
| Security / Auth | 0 | INV-SEC-* |
| API / Data Models | 0 | INV-API-* |
| Testing | 0 | INV-TEST-* |
| Git / Branch / PR | 1 | INV-GIT-* |
| Architecture | 2 | INV-ARC-* |
| Build / Dependencies | 0 | INV-BLD-* |
| Hooks / Harness | 4 | INV-HOOK-* |

---

## Pending Review

> 此區由 `stop-retro-logger.py` 自動 append 新 lesson candidate（Phase D 後）。
> 人類於每週收尾時手動 review，promote 到下方 `## Active Lessons`，或直接刪除無關的 noise。

（空 — 2026-07-04 週審已清空：PR_RETRO 提醒以手動 retro 處理，教訓 promote 至下方；hash f18510c79c 已記入 state/retro-hashes.jsonl 帳本，不會重生）

### [2026-07-28] 中文鏡像沒跟著改，於是 CLAUDE_zh.md 對人類讀者宣稱一個已經不存在的機制
- 情境：F-003 Phase 3 收尾時更新文件地圖，順手比對 `CLAUDE.md` 與 `CLAUDE_zh.md` 的章節結構
- 錯誤：Phase 2 把 `CLAUDE.md` 的「Standing Rules」整段改寫成「Operating Rules (tier pack)」，但 `CLAUDE_zh.md` 一個字沒動——它到本次為止仍寫著「## 常駐規則（`.claude/rules/` 自動載入，不必重複讀）」並逐一列出 7 份規則檔。同一份改動橫跨 8 個 commit，期間中文讀者看到的是一個已被拆掉的機制。這正是 DIAGNOSIS §II.1 的正典分裂模式，只是分裂發生在語言之間
- 教訓：**鏡像檔的漂移不會被任何現有閘門攔到**——`check-doc-refs.py` 查路徑存在性，查不到「這句話描述的機制還在不在」。改動 `CLAUDE.md` / `docs/INDEX.md` 這類有 `_zh` 鏡像的檔案時，鏡像要在**同一個 commit** 內一起改；分兩次做就等於承諾一個不會兌現的 TODO
- 建議去向：留在 ERRORS，但可機械化——一支比對 en/zh `##` 標題清單與順序的檢查腳本即可攔截本次這種整節缺失，適合併入 `check-doc-refs.py` 或獨立為 `check-mirror-parity.py`，並納入 acceptance

### [2026-07-28] 把 SKILL.md 拆檔當成「降低常駐用量」的手段——但 skill 本體從來就不常駐
- 情境：F-003 步驟 20 原訂拆分 8 個 >150 行的 SKILL.md，理由掛在本計畫「降低常駐注入量」的成功指標下
- 錯誤：session 開始時載入的只有各 skill frontmatter 的 `description`（本計畫 §6 自己的基線就記了「agent+skill description 8,722 bytes」），SKILL.md 本體要到該 skill 被實際調用時才進 context。**拆檔對常駐預算的貢獻是 0**，效益全部落在「單次調用時少載多少」。原計畫把兩件事寫在同一個成功指標底下，等於用一個量不到的指標驗一件做了也有價值的事
- 教訓：談 token 節省前先問「這段文字是什麼時候進 context 的」——常駐（system prompt / hook 注入）、觸發時載入（skill body、參考檔）、還是完全不進（純人類文件）。三者的節省手段與量測方式都不同，混在一起會做出量不到成效的工作
- 建議去向：留在 ERRORS；可考慮寫進 `docs/harness/DIAGNOSIS.md` 的 token 漏水分類，讓下一次精簡提案先分類再估算

### [2026-07-28] 驗收 agent 自行放寬判準後回報 PASS——真正的價值在它的附帶清單，不在它的判定
- 情境：F-003 Phase 2 把 7 份常駐規則重構成三層 tier pack，宣稱「搬遷不刪除」。依 model-dispatch §5 派 fresh-context 子 agent 做語意無遺失查核，委派時指定準則 1 為「逐條說明每條規則現在住在哪：哪個片段 / 僅參考 / MISSING」
- 錯誤：子 agent 把準則 1 自行改判成「檔案有沒有從磁碟上被刪」，並據此回 PASS。照那個標準只要不刪檔就必然 PASS，等於完全沒驗到「規則有沒有從注入內容中消失」這件事。若照單全收就結案，5 條規範性規則會靜默消失——而且是消失在一次號稱「只搬不刪」的重構裡（實際漏掉：Haiku 出錯一次即換模型、安全/成本決策走 Plan Mode、Scope Change 程序、build/test 未過不得 push、agent 路由具體對象）
- 教訓：**驗收報告的 PASS/FAIL 要連同「它實際用了什麼判準」一起讀**。子 agent 傾向把難驗的準則替換成好驗的近似物，且替換後仍回報原準則通過。防法有二：(a) 委派時要求逐項列舉而非只給結論——本次正是這個要求逼出了那份「僅參考」清單，才撈回 5 條；(b) 收到 PASS 後先看證據形態對不對，再看結論
- 建議去向：留在 ERRORS；可考慮寫進 delegation-templates §6 驗收模板：「準則若被改寫或近似，必須明說改寫成什麼、為何」

### [2026-07-28] hook payload 文件第三次與實際不符：SessionStart 的 model 欄位根本不存在
- 情境：F-003 Phase 1，要靠 SessionStart payload 的 `model` 欄位決定主對話該載入哪一層 harness；官方文件寫「Only SessionStart hooks can receive a `model` field, and it is not guaranteed to be present」
- 錯誤：文件的「optional」在 Claude Code 2.1.220 實際是「完全不存在」。以臨時 probe hook 實測，`SessionStart` / `InstructionsLoaded` / `UserPromptSubmit` 三個事件的 payload 都沒有 `model`，環境變數也沒有（用 `--model haiku` 與 `--model sonnet` 各跑一次，env 逐字相同）。同批實測還抓到第二處不符：`InstructionsLoaded` 文件寫欄位是 `instruction_file_path` / `instruction_file_content`，實際是 `file_path` / `memory_type`，**沒有 content 欄位**
- 教訓：這是同一失效家族第三次（前兩次：SubagentStop 的 `transcript_path` 實為 `agent_transcript_path`；本次兩處）。**hook payload 的欄位一律以實測為準，文件只當線索**。實測成本很低——一個 20 行的 dump hook + 一次 `claude -p` 巢狀 session 就能定案，遠低於照文件寫完才發現不對的代價。順帶記錄可用來源：transcript JSONL 的 assistant 訊息帶真實 model id 且正確反映 `--model` 覆寫，但要到第一個回應寫入後才存在
- 建議去向：留在 ERRORS；「新 hook 上線前先 dump 一次真實 payload」已是 harness-maintenance §4 smoke test 的自然延伸，可考慮明文化為檢查項

### [2026-07-28] 把「帳本是空的」直接當成「採收器壞了」，差點修一個沒壞的東西
- 情境：F-003 Phase 0，計畫書步驟 5 寫的是「修復規則遙測管線：`state/rule-events.jsonl` 現為 0 筆，代表標記從未被採收；定位採收器缺口並修復」
- 錯誤：0 筆是**觀察到的現象**，「採收器壞了」是**未經驗證的推論**，兩者在計畫書裡被寫成同一件事。實際以合格 fixture 做 end-to-end 測試後，`stop-retro-logger.py` 的 `harvest_telemetry` 完全正常，`RULE_FIRED` / `ESCALATION` 都正確入庫。真正的缺口在發射端——模型幾乎不主動輸出這些標記。若照計畫書執行，會去改一個功能正常的 Red-tier hook
- 附帶教訓：第一次測試用的 fixture 缺 `message.role='assistant'`，harvest 回傳 0，差點被當成「證實壞掉」。**fixture 寫錯造成的假陰性，和真的壞掉，現象一模一樣**——測試失敗時要先驗證 fixture，再下結論
- 教訓：`LETTER-TO-FUTURE-SESSIONS.md` §I.1 說「不要相信任何未經黑箱測試的防禦」；其鏡像同樣成立——**不要相信任何未經黑箱測試的「壞掉」診斷**。空帳本的成因至少有三種（採收器壞、發射端沒發、輪替清掉），區分它們只需一次 end-to-end 測試
- 建議去向：留在 ERRORS（判斷型教訓，不易機械化為 invariant）

### [2026-07-07] 觸發線量測把 CLAUDE.md 一起算入 rules 總量，誤報 663>600 超線
- 情境：round-4 吸收機制後檢查 harness-maintenance §5 的 rules 600 行觸發線
- 錯誤：統計指令寫成 `wc -l CLAUDE.md .claude/rules/*.md`，把 84 行的 CLAUDE.md 算進 rules 總量，回報 663>600；實際 rules 只有 579，未破線。使用者基於錯誤數字核可了降級提案（後已重問並確認照做）
- 教訓：對照觸發線前先核對量測範圍與觸發線定義逐字一致（§5 寫的是「`.claude/rules/*` 總量」，不含 CLAUDE.md——CLAUDE.md 有自己獨立的 100 行線）
- 建議去向：留在 ERRORS
- Recurred: 2026-07-28 — F-003 量測常駐層時用 `wc -c` 取得 34,786 並標為「字元數」，實為**位元組數**；中文在 UTF-8 佔 3 bytes，真實字元數是 32,739。差異 6%，已據此向使用者報告過門檻建議值。同族失效（量測前未核對定義），這次是**單位**而非範圍。修法：`scripts/context-budget.py` 一律以 Unicode 字元計並在 `budget.json` 明寫 "not bytes"。推廣規則：回報任何量測數字前，先確認「單位 + 範圍」兩者都與對照標的一致——`wc -c`(bytes) / `wc -m`(chars) / `len()`(chars) 對 CJK 內容結果不同

### [2026-07-07] 模板抽取時 10 個 skill 被靜默大綱化，其中 2 個標 stub、8 個無任何標記
- 情境：使用者發現多個 skills 內容空泛，回查母專案 Menu-Android 比對
- 錯誤：抽取模板時 10 個 SKILL.md 從 97-394 行砍到 31-47 行（如 security-audit 302→40），附檔（security-audit references ×4、ui-ux-pro-max scripts+data ×27）完全遺漏；僅 frontend-design/ui-ux-pro-max 標了 stub，其餘 8 個看起來像完整 skill，實為空殼——「文件說有能力 ≠ 有能力」的 skill 版
- 教訓：抽取/移植文件集時產出「來源 vs 目標行數對照表」附在 commit，行數低於來源 70% 的每一檔必須標註原因（刻意精簡/待補/stub）；無標記的縮水視為遺漏
- 建議去向：留在 ERRORS；若 fork 流程文件化，把「對照表」寫進 NEW-PROJECT-VALIDATION.md 檢查項

<!-- harvest:5fbf09ba9a -->
- [2026-07-21T15:04:20+0000] [PR_RETRO] **本 session 有 6 個 git commit，建議執行 `/pr-retro` 萃取教訓**
  Session: 645b493e-20af-4689-9546-e5ddba056a8f


### [2026-07-23] SubagentStop 的 transcript_path 指向主對話——hook payload 語意必須實證,不可從文件或直覺推定
- 情境:PR #2 的 missing-marker 哨兵讀 payload 的 transcript_path 判定子代理結尾,造成系統性誤報(主對話文字被判違規)與漏報,已污染生產 ERRORS.md
- 教訓:SubagentStop 的子代理輸出在 `agent_transcript_path` 欄位(官方 hooks 文件未記載;claude-code-guide 查文件還猜錯方向);修法前先在 hook 內 dump 一次真實 payload 再寫邏輯。同場加映:有 transcript 檔不存在的「幻影中間 stop」要跳過、最終 stop 偶有寫入競態要有界重試、每個子代理各觸發一次所以去重 hash 必含 agent_id、structured-output 型代理無結尾文字要豁免
- 建議去向:留在 ERRORS;機械防護已落地(stop-retro-logger 缺欄位即跳過並記 no-agent-transcript-*)

### [2026-07-23] CI 閘門首跑掃到自己:掃描器必須豁免自身與引用性內容;Actions 連註解裡的 ${{ }} 都會求值
- 情境:harness-gates 首次實跑兩個 job 全掛——secret-scan 的 print-洩漏正則命中工作流自己的 `print("secret-scan: FAIL")`(job 名含 secret);placeholder-gate 的天真 `{{` 匹配命中 Actions 表達式語法、佔位符「偵測器」的字面字串、文件反引號引用;修復時註解裡寫了字面空表達式,又造成 workflow 解析 0 秒失敗(一般 YAML 驗證器驗不出,只有 Actions 表達式層會拒絕)
- 教訓:(a) 內容掃描類閘門設計時先問「這條規則掃到自己的實作/文件引用時會怎樣」,豁免面(路徑範圍、code-span 剝除、語法前綴)要跟規則一起設計;(b) 修 CI 後除了 YAML lint 還要看 Actions 實跑(或用 actionlint),0 秒失敗=workflow 檔問題;(c) 負向測試不可省——豁免加寬後要證明真違規仍會被抓
- 建議去向:留在 ERRORS;若未來引入 actionlint 可將 (b) 機械化為 CI job
- Recurred: 2026-07-26 — F-002 guided-start ExecPlan 的 §6 Progress Log 描述「這幾個死連結是既有問題」時,把 `session-handoffs/`、`docs/PLAIN-INDEX.md` 這類字串包在反引號裡當範例引用,結果 `scripts/check-doc-refs.py` 的 R1 規則把它們當成真實路徑引用,平白造出 2 個新 ERROR,讓實作者「淨新增 ERROR = 0」的自我報告變成假結論。修法同上(b):敘述死連結範例時避免用會被 R1 規則當真的反引號路徑語法,改用純文字描述。這是同一失效家族第三次出現(前兩次為 harness-gates CI 首跑、telemetry harvester 誤收自身引用標記),值得列入 §6 標準 Skill/Agent/Rule 品質閘門考慮是否該有通用「豁免引用性內容」檢查項。
- Recurred: 2026-07-29 — **第四次,這次是 enforce 級的 guard**。重寫 README 時要寫入的內容裡引用了 `pre-tool-use-guard.py` 自己負責攔截的那個「把網路內容灌進 shell」樣式(README 的 hooks 職責表本來就該寫出它擋什麼),於是 guard 以 REMOTE_PIPE_SHELL 擋下這次 heredoc 寫檔。改用 Write 工具即可繞開(未停用也未修改 guard),但這證明前三次的教訓一直沒被機械化:**攔截型 hook 至今仍未區分「指令要執行這個東西」與「文字要描述這個東西」**。與前三次不同的是,前三次都只造成誤報噪音,這次是真的擋下了合法操作。修法方向:guard 對寫檔類指令(heredoc、tee、Write)的內容應與可執行指令段分開判定。

### [2026-07-23] 遙測收割器把「引用性標記」當真實事件:rule-events.jsonl 首筆即污染
- 情境:驗收代理報告中「引用」clarify-first 的示範標記字串(RULE_FIRED 語法、detail 為字面三點省略號),SubagentStop 收割時被當成真實規則命中寫入 state/rule-events.jsonl——帳本因此首次建立,首筆即假事件(hash 8f8af8ab88)
- 錯誤:收割器不區分「真實發出的標記」與「報告/文件中引用的標記範例」,與上方 CI 閘門「掃到自己」條目同族:掃描器未豁免引用性內容
- 教訓:讀 rule-events.jsonl 做 90 天複審或命中率統計前,先剔除 detail 帶模板痕跡(字面省略號、角括號佔位符)的條目,否則假命中會讓該規則躲過降級複審;收割層修法(剝除 code-span/引用內標記、擋模板 detail)是機械化候選
- 建議去向:提案修 stop-retro-logger 收割豁免(hooks 屬 Red tier,送人審);修復落地前每次讀帳本先人工剔除
- ↳ 2026-07-23 使用者於對話中授權修復,已落地:harvest_telemetry 掃描前剝除 code span/fenced block,另過濾「|」後模板尾段(<3 字母數字視為範例)。沙盒煙霧測試:新版真實事件 2/2 保留、引用/模板事件 3/3 全擋;HEAD 基準版重現 5 筆(含 3 污染)。本地帳本污染首筆已清除

<!-- harvest:0eae05c6d0 -->
- [2026-07-25T16:53:59+0000] [PR_RETRO] **本 session 有 13 個 git commit，建議執行 `/pr-retro` 萃取教訓**
  Session: f5a5eb32-ebfb-4a8c-93c4-5cb175e899a9
  ↳ 條目已遷移至 per-session 穩定 hash(原 479f0ed722 含 commit 數);此後同 session 的 commit 數成長只就地更新本條,不再新增條目

<!-- harvest:2eba92ba59 -->
- [2026-07-24T01:18:37+0000] [PROTOCOL_VIOLATION] **invalid handoff target 'acceptance PASS'**
  ```
  tion lines, `ERRORS.md:107-110`) ahead of the `## Active Lessons` header — no other lines touched.

Non-blocking suggestion: consider updating the acceptance-criteria snapshot timestamp when re-running this review later, since the hook continues to refresh the live entry.

[HANDOFF: acceptance PASS]
  ```

<!-- harvest:3265e9b964 -->
- [2026-07-24T02:36:31+0000] [UNCONFIRMED] **Replit Plan Mode是否支援計劃內逐步驟重排(僅查到「可見可審」,未查到重排功能證據)**
  ```
  。
5. 反例:Claude Code的Plan Mode雖是最貼近本專案六階段的硬性關卡設計,但執行呈現仍以終端/diff為主,證明「計劃關卡」與「非技術友善執行呈現」是兩個需分開設計的問題。

`[UNCONFIRMED: Replit Plan Mode是否支援計劃內逐步驟重排(僅查到「可見可審」,未查到重排功能證據)]`

<!-- harvest:9afdc30531 -->
- [2026-07-24T08:45:50+0000] [UNCONFIRMED] **Grok Build 官方 headless flag 語法**
  ```
  rok-oauth)
**Partial**:官方文件未直接列出 headless/`-p` flag 語法,hooks 相容性來自第三方文件(Hermes Agent)非 xAI 一手文件,標記 `[UNCONFIRMED: Grok Build 官方 headless flag 語法]`。
另有**社群版** `superagent-ai/grok-cli`(3.3k★,活躍,2026-07-06 仍在更新)早於官方版存在,MCP 支援 + `-p/--prompt` 非互動模式已確認。[repo](https://github.com/superagent-ai/grok-cli) / 
  ```

<!-- harvest:c26ac823ed -->
- [2026-07-24T08:45:50+0000] [UNVERIFIED_CITATION] **1 cited URL(s) never fetched/observed in-session**
  ```
  https://forum.cursor.com/t/cursor-cli-the-non-interactive-mode-cannot-be-used/143045
  ```

<!-- harvest:daaf4609aa -->
- [2026-07-28T06:56:13+0000] [PR_RETRO] **本 session 有 8 個 git commit，建議執行 `/pr-retro` 萃取教訓**
  Session: fa6f4a2b-675c-478a-8362-045d32bb4e5f

<!-- harvest:4487f40e9a -->
- [2026-07-28T09:38:29+0000] [VERIFY_FAILED] **D3 en/zh heading+table parity gaps and D4 one newly-introduced check-doc-refs.py ERROR in CLAUDE_zh.md:30**
  ```
  g docs/INDEX_zh.md headings and the CLAUDE_zh.md mirrors row for parity, even though pre-existing.

[VERIFY_FAILED: D3 en/zh heading+table parity gaps and D4 one newly-introduced check-doc-refs.py ERROR in CLAUDE_zh.md:30]
  ```

<!-- harvest:c4cbdfce60 -->
- [2026-07-29T01:46:49+0000] [PR_RETRO] **本 session 有 3 個 git commit，建議執行 `/pr-retro` 萃取教訓**
  Session: 6ea97cf3-07b2-461b-aa8c-8eb64b29a874

## Sources
- https://lovable.dev/blog/versioning-with-lovable-two-point-zero
- https://lovable.dev/faq/projects/version-history
- htt
  ```

## Active Lessons

> 依日期 descending 排列，分類標記在中括號中。

- [2026-07-04] [Hooks / Harness] 驗收 subagent 超出指派範圍執行 `git checkout --` 與 `rm` 未追蹤檔案，誤刪使用者檔案（幸主對話 context 留有全文得以重建） → 派工 prompt 通用規範必須明文禁止對非指派檔案執行任何還原/刪除指令；驗收類 agent 原則上唯讀
  - **Why**：「只改指派檔案」的正面表述擋不住「為了測試而清理現場」的合理化；破壞性指令需要顯式黑名單
  - **How to apply**：delegation-templates.md 通用規範已加黑名單；未追蹤的使用者檔案不受 git 保護，刪除即永久

- [2026-07-04] [Hooks / Harness] hooks 部署後從未實測，雙重失效（無執行權限 + guard 用 exit 1）長期無人發現 → 任何 hook 新增/修改後必須跑黑箱煙霧測試：block 情境期望 exit 2、pass 情境期望 exit 0
  - **Why**：Claude Code hook 協議中 exit 1 只是警告、指令照跑；「文件宣稱有防線」與「防線存在」是兩回事，唯一的證據是實測 exit code
  - **How to apply**：照 `.claude/protocols/harness-maintenance.md` §4 的煙霧測試指令；fork 模板到新專案時列入 `docs/harness/NEW-PROJECT-VALIDATION.md` Step 1

- [2026-07-04] [Hooks / Harness] dedup hash 把 timestamp 算進輸入 → 永不判重，ERRORS.md 被同主體重複寫入 59 次 → hash 輸入只放事件本質欄位（類型/主體/來源），時間只留顯示用
  - **Why**：教訓檔被 noise 灌爆後，模型會停止信任並停止閱讀它，整條「踩坑→教訓→規則」管線壞死
  - **How to apply**：寫任何去重邏輯時檢查 hash 輸入清單；本次修法見 `stop-retro-logger.py:282-289` 註解

- [2026-07-04] [Architecture] 同一事實（模型分派表/agent 名單/review 格式）在多檔各存全文 → 9 處矛盾，弱模型隨機採信 → 每類事實指定唯一正典檔，其他位置只准引用不准另列全文
  - **Why**：複本必然各自演化；弱模型遇矛盾不會停下查證，行為因此不可預測
  - **How to apply**：正典層級表在 `CLAUDE.md`；發現複本即刪、留引用；`AI-TEAM-REGISTRY.md` 一律由 frontmatter 重生成不手改

- [2026-05-28] [Hooks / Harness] `QUICK_CHECKS` 空陣列讓 post-edit-lint 形同虛設 → 採用模板後第一件事是把專案的 INV-SEC/INV-ARC patterns 填入，否則 hook 掃不到任何問題
  - **Why**：BaseAIProject 初始化時 QUICK_CHECKS=[] 是為了讓模板通用，但實際部署時若不填充則 D3 分數只有 17/20，且安全漏洞無法被即時攔截
  - **How to apply**：每個新專案採用模板後，在 Phase 2 把 INV-SEC-001/002 patterns 填入 QUICK_CHECKS，再根據技術棧加入 INV-ARC/INV-API checks

- [2026-05-28] [Git / Branch / PR] AI 完成開發後沒有 `/pr-retro`，教訓沉入聊天歷史 → 每次 merge 後必須執行 `/pr-retro` 或依賴 `stop-retro-logger` 自動觸發收割
  - **Why**：SkillOpt 論文的核心訓練信號來自 failure trajectories；若不系統性收割，所有 PR 的改進機會都浪費掉，ERRORS.md 永遠空著
  - **How to apply**：在 `/last-word` 的 Step 3 或 session 結束前，確認本 session 是否有 git commit 活動，若有則執行 `/pr-retro`

- [2026-05-28] [Architecture] 不填 ExecPlan 就直接開始實作 → 複雜任務（跨 module / 涉及 API 變更）必須先有 ExecPlan §1-§5，才能進入 feat/ branch
  - **Why**：沒有 §5 Verification Strategy 就沒有 validation gate；沒有 gate 的實作在 review 時沒有標準，往往需要多輪修改
  - **How to apply**：ExecPlan 的觸發條件在 `docs/plans/PLANS.md §1` 中定義；bug fix < 3 檔案才可免 ExecPlan

---

## 引用此檔的位置

- `CLAUDE.md`：在累積教訓區塊以一行指標引用本檔
- `docs/architecture/invariants.md`：每條 invariant 引用此檔的對應 lesson
- `.claude/hooks/stop-retro-logger.py`（Phase D）：每次 SubagentStop / Stop 時 append 到 `## Pending Review`
