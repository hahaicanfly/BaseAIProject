# Skill Eval 迭代流程（詳版）

> 濃縮自 Anthropic 官方 skill-creator 的 eval 方法論（github.com/anthropics/skills/tree/main/skills/skill-creator，2026-07 版），適配本專案環境：用 Agent tool 派工替代官方 python 基建。需要完整自動化基建（run_eval.py、run_loop.py、viewer）時直接取用官方 repo。

## 核心迴圈

定意圖 → 草稿 → 2-3 個測試 prompt → 質化＋量化評估 → 依回饋改寫 → 重複，直到：使用者滿意、或回饋全空、或連兩輪無實質進展。

## 一、質化評估（每個 skill 都做）

1. 寫 2-3 個「真實使用者會打的」prompt——具體檔名、口語、甚至 typo；不要教科書式問句。
2. **同一 turn 平行派兩個 subagent**（照 delegation-templates.md 三件套派工）：
   - with-skill：prompt 前附上 skill 全文
   - baseline：只給 prompt（改既有 skill 時，baseline 給舊版全文）
3. 對照輸出。讀**完整過程**而非只看結果——skill 的哪些段落實際影響了行為？沒影響的段落刪掉（keep it lean）。
4. 觀察跨測試的重複工作：多個 subagent 都自己重寫同一段腳本/查同一份資料 → 把它固化進 skill 的 `scripts/` 或 `references/`。

## 二、觸發評測（description 的專屬測試）

1. 寫 16-20 條 query：should-trigger 8-10 條、should-not-trigger 8-10 條。
2. 負例的價值在 **near-miss**——與 skill 共享關鍵詞但不該觸發的情境（例：對 code-review skill，「幫我看看這段代碼怎麼寫」是 near-miss；「今天天氣如何」測不到任何東西）。
3. 每條 query 派一個 fresh-context subagent：給它本專案完整 skill 清單（名稱+description）與 query，問「你會選用哪個 skill？」。同條 query 建議測 2-3 次取多數（觸發有隨機性；官方閾值：觸發率 ≥0.5 算通過）。
4. should-trigger 沒中 → description 加原話觸發詞、加情境列舉（往 pushy 方向改）；should-not 誤中 → 加互斥限定詞。
5. 改完 description 重跑同一組 query。防 overfit：留 40% query 不參與改寫決策、只用於最終驗證（官方 train/test split 精神）。

## 三、量化 assertions（僅客觀可驗證輸出）

- 每條 assertion 要**客觀可程式化驗證**且名稱可讀（「輸出含 frontmatter 且 name 等於目錄名」而非「品質良好」）。
- Grader 派工時給雙職責（官方 grader.md 精神）：(a) 評 assertion——PASS 必須是真完成、非表面合規 (b) **批判 assertion 本身**——不具鑑別力的 assertion（兩組都全過/全掛）比沒有更糟，回報建議刪除。
- 主觀輸出（文案風格、視覺品味）不硬套 assertions——這是弱模型判斷力極限（judgment-rubrics.md §6），改用：產出 2-3 候選 → 盲測比較（去識別後交獨立 agent 判優並說理由）→ 交使用者定奪。

## 四、工作區紀律

- eval 產物放 skill 同層的 `<name>-workspace/`，按 `iteration-N/` 組織；此目錄不入版控（gitignore）。
- 只能刪除自己本輪建立的暫存檔；禁止對非自建檔案執行 rm / git checkout / git restore（破壞性黑名單，delegation-templates.md 通用規範）。
- 每輪迭代記一行：改了什麼、觸發率變化、下一步假設——中斷時這就是交接紀錄。
