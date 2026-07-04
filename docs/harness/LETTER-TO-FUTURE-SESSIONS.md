# G. 給未來 Session 的信

> 寫於 2026-07-04，Fable 5 一次性架構 session。你（讀者）大概是 Sonnet、Opus 或 Haiku。
> 這封信講三件使用者沒問但最重要的事、這套制度會怎麼腐化、以及還沒做完的工作。

## 一、三件使用者沒問、但最重要的事

### 1. 不要相信任何沒有被黑箱實測過的防線
本專案的 5 個 hooks 從部署起就從未執行過（無執行權限 + guard 用錯 exit code，雙重失效），但 CLAUDE.md 一直宣稱「enforce mode 攔截」。**文件說有防線 ≠ 有防線。** 每次改 hook、每次 fork 這個模板到新專案，都要跑 `harness-maintenance.md` §4 的煙霧測試。
延伸警報：母專案 `MenuProject/Menu-Android` 的同名 hooks 大概率有同樣問題（同一來源抽取），**未驗證** —— 下次進那個 repo 先做煙霧測試。

### 2. 這套 harness 的真正資產是「教訓管線」，而它有一個正在流血的傷口
制度的複利來自：踩坑 → ERRORS.md → 人審 → invariants/guard 機械化。Menu-Android 用這條管線長出了 693 行 invariants 與 81 條教訓，證明管線可行。但本專案 `stop-retro-logger.py` 的 dedup hash 把 timestamp 算進去導致永不判重，ERRORS.md 已被重複 noise 灌入 —— **教訓檔一旦充滿 noise，後續模型就會停止讀它，管線整條壞死**。修復方法在下方交接清單第 1 項，優先做。

### 3. 常駐載入面是稀缺預算，每加一行都是對所有未來 session 徵稅
`.claude/rules/*.md`（frontmatter `always: true`）+ CLAUDE.md 會注入**每一個** session。你會不斷有衝動把新規則塞進常駐面（「這條很重要！」）——絕大多數規則不需要常駐，放 agent_docs/ 或 templates/ 用引用觸達即可。判準：**「每個 session 的第一個決定就需要它」才配常駐**。超過 harness-maintenance.md §5 的觸發線就必須精簡。

## 二、這套制度最可能的腐化方式與預防

| 腐化模式 | 具體徵兆 | 預防／解法 |
|---------|---------|-----------|
| **規則堆積** | rules 總量逐月上升、沒有刪除紀錄 | maintenance §5 觸發線；每加一條常駐規則需說明「為何非常駐不可」 |
| **正典再分裂** | 有人把模型表/名單「順手」複製到新檔案，之後兩份各自演化 | 「只准引用、不准另列」（CLAUDE.md 正典層級）；發現複製即刪，留引用 |
| **驗收橡皮章** | 驗收報告出現「看起來沒問題」、PASS 無逐條證據 | delegation-templates §6 的格式強制；使用者定期抽查一份驗收報告 |
| **教訓檔 noise 化** | ERRORS.md 重複條目、無日期、無行號 | dedup 修復 + §3 去重規則；週審清 Pending Review |
| **死引用累積** | 文件引用的路徑/skill 不存在，模型追空路徑或編造 | 「引用即驗證」紀律；每季跑一次 `/harness-eval` 全面體檢 |
| **模板佔位符正常化** | 新專案 fork 後不填 {{}}，模型習慣性跳過整份文件 | CLAUDE.md「啟用狀態」節已定義跳過語義；fork 後第一個任務就是填實或刪除 |

最陰險的是**橡皮章**：它讓所有其他防線看起來還在運作。如果只能防一個，防它。

## 三、交接清單（未完成工作，按優先級）

> 完成一項就從這裡刪掉（不留墓碑）。動紅級檔案前先問使用者（見 harness-maintenance.md §1）。

1. **skillopt-loop.md 去留決策**（需使用者決定）：已標為「未接線設計草案」並清除虛構引用（2026-07-04 第三輪）。選項：(a) 保留為草案備將來接線 (b) 刪除（紅級刪檔需同意）。
2. **session-handoffs 首次運轉驗證**（觀察項）：`state/session-handoffs/` 目前為空——本 session 從未觸發 PreCompact。下次發生 compaction 時，核實該目錄出現新快照檔；若沒有，pre-compact-snapshot.py 可能有同構失效（參照 hooks 煙霧測試教訓）。
3. **Menu-Android guard 修復已完成但未 commit**（2026-07-04）：exit 2 修復與煙霧測試通過，改動留在該 repo `feat/ga-event-tracking` working tree，隨該分支一起 commit 即可。

> 2026-07-04 三輪優化全部完成（詳見 §四），26 個原子 commit 在 feat/harness-institution，未 push。

## 四、本次 session 已完成（供考古）

A 診斷書（docs/harness/DIAGNOSIS.md）、B 重寫 CLAUDE.md（舊版 .bak）、C model-dispatch.md、D judgment-rubrics.md、E delegation-templates.md、F harness-maintenance.md、G 本檔；實體修復：hooks chmod +x、guard exit 1→2（實測通過）、cost-optimization/plan-first 修剪去重（各留 .bak）。
後續批次（同日，workflow 執行、fresh-context 驗收 PASS）：14 agent 檔樣板收斂（每檔 -9~-20 行）、15 個 SKILL.md 補 YAML frontmatter、AI-TEAM-REGISTRY.md 由 frontmatter 重生成（修 9 處模型矛盾、補 code-reviewer、計數 14 agents/15 skills）、Life-Vault 與 menu.jpg 殘留清除。
第三輪（同日，三路深度審計→六路實作→隔離驗收 PASS）：四個 review agent 輸出統一至 review-protocol 詞彙；tech-lead 重定位為架構顧問（不做 PR gating）；研究三人組觸發詞互斥化＋輸出模板；ui-ux-designer 併入三階段 Phase 3；模型再平衡 opus 10→4（architect/pm/security-reviewer/plan-reviewer 留 opus）；skillopt-loop 降級為未接線草案（虛構引用清除）；guard 新增 INV-SEC-003 staging 攔截（實測 4/4）；retro 墓碑帳本 state/retro-hashes.jsonl + 30/90 天 rotate；知識地圖五層表（INDEX.md）；multi-agent-guide 去重；TECHNICAL-REFERENCE 最小填寫清單。
同日事故與修復：驗收 subagent 超範圍誤刪未追蹤的《AI 基礎架構優化目標說明.md》，已從主對話 context 逐字重建；教訓進 ERRORS.md，delegation-templates 補破壞性指令黑名單。
