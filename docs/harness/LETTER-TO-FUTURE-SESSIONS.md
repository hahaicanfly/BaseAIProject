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

1. **修 stop-retro-logger dedup**（紅級，需同意）：`.claude/hooks/stop-retro-logger.py` 的 dedup hash 含 timestamp → 永不判重。修法：hash 計算排除時間欄位。修完清 ERRORS.md 既有 7 條重複 PR_RETRO 條目，並煙霧測試。
2. **Agent 工具與職責矛盾**（黃級）：pm、security-reviewer 無 Bash 卻被 review-protocol.md 要求跑 git 指令；tech-lead 唯讀卻被 execplan-lifecycle.md:82 指派 commit。修 frontmatter tools 或改 SOP，二選一要一致。（agent 檔內的自檢樣板已於 2026-07-04 移除，剩 SOP 端待改）
3. **死引用清理**：ADR-0001 不存在但被 7 處引用（PLANS.md:4、invariants.md:57、execplan-lifecycle.md:5、handoff-protocol.md:5、3 個 hook docstring）→ 建議補寫一份簡短 ADR-0001 記錄 harness 採納決議（紅級）；`scripts/*.sh`（parallel-worktree.md）、`src/`（techdebt 兩處）、INV-AUTH-*/INV-COR-*（handoff/review-protocol 引用但 invariants 未定義）。
4. **security/cost 詳版收斂**（黃級）：agent_docs/security-policy.md 與 rules/security.md、agent_docs/cost-optimization.md 與 rules 版仍重複，收斂為「rules=常駐精簡、agent_docs=詳版教學」且互相引用。
5. **GEMINI.md 重述收斂**（黃級）：:87-98、:101-114、:119-128 重述 handoff/invariants/CLAUDE.md，改為引用。
6. **README.md 計數與章節引用修正**（黃級）：「11 Skill Stubs」實 15、引用 CLAUDE.md 已不存在的章節。注意：「4 Hooks」是**對的**（4 個 hook + `_lib.py` 共用庫，settings.json 只註冊 4 個），不要改成 5。
7. **uiux/ 1,147 行評估**：對無前端專案是 dormant weight，考慮 fork 時可選安裝（移到 optional/ 或文件說明）。
8. **值得從 Menu-Android 移植**：gen-app-map skill 模板化、F-CANARY 驗收 SOP 改寫為「新專案 harness 驗收流程」、ERRORS.md 分類索引對映 INV-* 的表頭格式、guard hook 的 regex 防回歸註解（泛化時被刪，見 pre-tool-use-guard.py.bak 對照）。
9. **Menu-Android guard 修復**（跨專案，需使用者同意）：煙霧測試已做（2026-07-04）——執行權限正常，但 `pre-tool-use-guard.py:257、:273` 用 `return 1`，黑箱實測 block 情境 exit=1 → **enforce 從未真正攔截**。修法與 Base 相同：兩處改 `return 2` + 煙霧測試（參照 harness-maintenance.md §4）。
10. **`.bak` 清理**（需使用者確認改動後）：本次共產生約 46 個 `.bak` 備份（agents ×14、skills ×16、rules/protocols/docs 等）；使用者驗收後可批次刪除。

## 四、本次 session 已完成（供考古）

A 診斷書（docs/harness/DIAGNOSIS.md）、B 重寫 CLAUDE.md（舊版 .bak）、C model-dispatch.md、D judgment-rubrics.md、E delegation-templates.md、F harness-maintenance.md、G 本檔；實體修復：hooks chmod +x、guard exit 1→2（實測通過）、cost-optimization/plan-first 修剪去重（各留 .bak）。
後續批次（同日，workflow 執行、fresh-context 驗收 PASS）：14 agent 檔樣板收斂（每檔 -9~-20 行）、15 個 SKILL.md 補 YAML frontmatter、AI-TEAM-REGISTRY.md 由 frontmatter 重生成（修 9 處模型矛盾、補 code-reviewer、計數 14 agents/15 skills）、Life-Vault 與 menu.jpg 殘留清除。
