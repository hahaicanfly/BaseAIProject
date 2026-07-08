# A. Harness 漏水診斷書

> 產出：2026-07-04 Fable 5 一次性架構 session。讀者：Sonnet / Opus / Haiku 等長期運作模型。
> 依據：3 組並行審計（BaseAIProject 68 檔全量、全域 ~/.claude 環境、MaiNeu 母專案比較）+ 主對話實測驗證。
> 本檔是後續所有 harness 檔案的依據；修復狀態標記：[已修] [未修]。

## 診斷方法

- 全量盤點 68 檔（約 8,760 行），標記 DUP（重複）/ STALE（過時）/ HEAVY（常駐過重）
- 對 hooks 做黑箱實測（餵 JSON payload 看 exit code），不信文件自述
- 與 MaiNeu 母專案（Menu-Android，實戰調校最久）比對演化差異
- 判定「漏 token」的標準：每 session 或每 spawn 必然載入、且資訊密度低或重複

## 一、Token 最漏 Top 3

### 1. 「必讀」的空殼檔：agent_docs/TECHNICAL-REFERENCE.md（257 行，33 個 {{佔位符}} 全空）[已修]
CLAUDE.md 第一條 MUST 是「任務前必讀此檔」，但整檔是未填模板 —— 每個任務強制付 257 行 token 換到零資訊，還訓練弱模型「必讀檔可以不含資訊」的壞直覺。
**阻斷方案**：CLAUDE.md 改為「若 TECHNICAL-REFERENCE.md 仍含 {{佔位符}}，視為未啟用、跳過」；模板頂部加啟用開關說明。新專案填實後才恢復必讀地位。

### 2. 常駐 rules 全量載入 + 同一規則三重拷貝（每 session ~420 行，其中過半重複）[已修]
`.claude/rules/*.md` 全部自動注入每個 session。security 規則存在三份（rules/security.md ≈ agent_docs/security-policy.md ≈ invariants.md INV-SEC-*），cost 規則兩份，內容僅措辭差異。
**阻斷方案**：單一事實源分層 —— rules/ 只放「常駐精簡版」（判準與硬規則），詳版與教學內容留在 agent_docs/ 且由 rules 引用；重複段落刪除。新增規則檔先問「這需要常駐嗎」。

### 3. 14 個 agent 檔的逐字重複樣板（每次 spawn 重付 ~15-20 行 ×14 檔 ≈ 250 行）[未修→維護協議接手]
三 marker 交接說明、`git branch --show-current` 自檢、「讀 invariants 列 INV-id」等段落在 14 個 agent 檔逐字複製（源頭是 handoff-protocol.md:13-17）。
**阻斷方案**：agent 檔尾段收斂為一行：「交接與自檢規範見 `.claude/protocols/handoff-protocol.md`，final response 必含 marker」。批次修改屬機械套用，適合派 Haiku/Sonnet 批次執行（正好是 model-dispatch.md §4 降級批次的範例任務）。

## 二、最容易失焦 Top 3

### 1. 單一事實源分裂：同一件事有多份互相矛盾的正典 [部分已修]
- 模型分派表 9 處矛盾（agent frontmatter vs CLAUDE.md 表 vs AI-TEAM-REGISTRY.md，如 pm 一邊標 haiku 一邊標 opus）
- Review 輸出格式三套互斥（code-reviewer vs review-protocol vs tech-lead）
- Agent/skill 名單兩份且計數皆錯（REGISTRY 漏 code-reviewer、skill 清單漏 4 個後加 skill）
弱模型遇到矛盾不會停下來查證，會隨機採信其一，行為因此不可預測。
**阻斷方案**：宣告正典層級（新 CLAUDE.md 已寫入）：模型分派以 **agent frontmatter** 為準；review 格式以 **review-protocol.md** 為準；名單以 **AI-TEAM-REGISTRY.md** 為準，其他檔案只准引用不准另列。矛盾未清完前，弱模型遇不一致按此層級採信。

### 2. 死引用與幽靈路徑：追不到的東西會讓弱模型編造 [部分已修]
`ADR-0001`（7 處引用、檔案不存在）、`/harness-workflow` skill（CLAUDE.md 引用、不存在）、`scripts/*.sh`（parallel-worktree.md 引用、不存在）、`src/`（techdebt 兩處引用、不存在）、docs/INDEX.md 宣稱的 `always_read` frontmatter（0 個 agent 有）。
**阻斷方案**：新 CLAUDE.md 刪除死引用；維護協議（harness-maintenance.md）規定「引用即驗證」：寫下任何路徑前必須確認存在，發現死引用記入 ERRORS.md。剩餘死引用清單已列入 LETTER-TO-FUTURE-SESSIONS.md 交接清單。

### 3. 雙軌前置流程無先後：plan-first.md（Plan Mode）vs ExecPlan（PLANS.md）[已修]
兩套「動手前先計劃」機制並存且未定義關係，弱模型會兩個都做（重複勞動）或都不做（各自以為另一個涵蓋了）。
**阻斷方案**：新 CLAUDE.md 定義單一決策樹：跨模組/API/重構 → ExecPlan（重量級、入版控、需人類核可）；其餘非瑣碎任務 → Plan Mode（輕量級、對話內）；< 20 行單檔修改 → 直接做。

## 三、最容易出錯 Top 3（工具/hook/skill 調用）

### 1. 全部 4 個 hooks（+1 共用庫 `_lib.py`）從未執行過：雙重失效 [已修，實測通過]
(a) 檔案無執行權限（`-rw-r--r--`）且 settings.json 直呼 `.py` → 每次觸發都 Permission denied；
(b) 即使修好 (a)，guard 用 `exit 1` 想攔截 —— Claude Code hook 協議中 **exit 2 才阻斷，exit 1 只是警告、指令照跑**。
也就是說 CLAUDE.md 宣稱的「enforce mode 攔截」自部署以來完全是紙上防線。
**修復**：`chmod +x` 全部 hooks；guard 兩處 `return 1` → `return 2`（備份於 pre-tool-use-guard.py.bak）。實測：攔截情境 exit 2 且 stderr 帶原因、正常指令 exit 0。
**教訓（已成規則）**：任何 hook 部署後必須黑箱實測一次 block 與 pass 兩情境，寫入 harness-maintenance.md。

### 2. stop-retro-logger dedup 失效，持續污染 ERRORS.md [未修→交接]
dedup hash 把 timestamp 算進去 → 永不判重 → ERRORS.md 已被 7 條重複 PR_RETRO noise 灌入。教訓檔被 noise 稀釋後，弱模型會停止信任並停止閱讀它，整條「踩坑→教訓→規則」管線就死了。
**阻斷方案**：修 `_hash` 移除 timestamp 欄位（stop-retro-logger.py，具體行號見交接清單）；清除 ERRORS.md 現有重複條目。

### 3. Agent 工具權限與職責矛盾 + skill 觸發失效 [未修→交接]
- pm、security-reviewer 無 Bash，卻被 review-protocol.md 要求跑 `git branch --show-current`；tech-lead 唯讀（Read/Grep/Glob），execplan-lifecycle.md:82 卻指派它「實作、commit」→ agent 執行到一半發現無工具，回報失敗或亂繞路
- 部分 SKILL.md（如 skill-creator）缺 YAML frontmatter → 可能根本不被觸發
**阻斷方案**：以「職責決定工具」重審 14 個 agent frontmatter；SOP 中要求 agent 做的每個動作，該 agent 必須有對應工具。批次修正適合派 Sonnet 照 checklist 執行。

## 四、Harness 能力極限（誠實條款）

拆解、隔離驗證、多答案評審能把弱模型的**執行品質**逼近高階模型；以下三類**補不了**，遇到走指定出口（詳見 `.claude/rules/judgment-rubrics.md` §6）：

1. **品味與美感決策**（UI 好不好看、文案語感）：弱模型產出 2-3 個候選 + trade-off 交人選，不自行拍板。
2. **模糊商業判斷**（值不值得做、使用者要什麼）：列可驗證假設，明說需要人類決策。
3. **無 ground truth 的長鏈推理**（無法用測試/實跑/文件驗證的結論）：標信心等級，升級模型或第二意見；查不到就寫「未確認」，不編造。

此外本診斷自身的極限:「未確認」項目包括 commands/last-word.md 與 uiux/ 5 檔的逐行內容、agy（Gemini）端實際行為 —— 均未實測。

## 附：本次已完成的實體修復清單

| 項目 | 動作 | 驗證 |
|------|------|------|
| hooks 無執行權限 | `chmod +x .claude/hooks/*.py` | 實測 guard 可執行 |
| guard exit code | `return 1` → `return 2` ×2 處 + docstring | block→exit 2 / pass→exit 0 實測通過 |
| 備份 | pre-tool-use-guard.py.bak、CLAUDE.md.bak | 已存在 |
