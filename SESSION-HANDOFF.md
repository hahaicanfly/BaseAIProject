# SESSION-HANDOFF — 2026-07-29

> F-003 已結案。這份不是「未完成工作的交接」，是「**現在這套 harness 長什麼樣**」的落地說明，寫給下一個 session。
> 下次 `/last-word` 會覆寫本檔。

## 一句話

分層 harness 上線了。規則不再是一份全量常駐，而是**依當下執行的模型注入對應重量的 tier pack**；strong tier 常駐量從 635 行 / 33,164 字元降到 **245 行 / 13,669 字元（減 59%）**，且這個上限現在是 `INV-ARC-001`，由 `scripts/context-budget.py` 在每次 acceptance 強制執行。

## 下一個 session 開場會看到什麼

`SessionStart` hook 注入一份 tier pack，開頭寫著 `# Harness tier: <tier>` 與來源。**那份 pack 就是正典**，`.claude/rules/*.md` 是它背後的全文參考（只有 `security.md` 仍然常駐）。

- tier 由 `.claude/settings.json` 的 `HARNESS_TIER` 決定，出廠值 `auto` = 不宣告 → 從 `~/.claude/settings.json` 猜
- 猜錯的話，第二輪起 `tier-drift-check.py` 會比對 transcript 裡的真實 model id 並要求改讀正確的 pack
- **本機殘留 `HARNESS_TIER=mid` 環境變數**（Phase 1 探測所致）。上一個 session 實際跑 Opus 卻載入 mid，靠 drift-check 更正。開新 session 就會消失——若仍看到 tier=mid，先查這個變數

## 這輪新增、之後會一直生效的閘門

| 閘門 | 它擋什麼 |
|---|---|
| `context-budget.py` | 常駐層超過 `budget.json` 當前模式上限（`INV-ARC-001`） |
| `build-tier-packs.py --check` | tier pack 與 `src/` 片段漂移 |
| `check-mirror-parity.py` | `_zh` 鏡像與原文的章節／子章節／表格列結構不符 |
| `check-hook-doc-coupling.py` | hook 靠某份文件的字面字串做判斷卻未加 `# COUPLING:` 宣告 |

acceptance **14/14**，CI **6 job**。改 harness 檔之前先讀 `.claude/protocols/harness-maintenance.md` §1（紅黃綠分級）與 §4（安全改動程序，本輪新增三條 hook 撰寫規則）。

## 三個容易踩的坑（都已寫進 §4，這裡只提醒存在）

1. **hook payload 欄位一律以實測為準** —— 官方文件已經錯了三次。先寫一個 dump hook 跑一次 `claude -p`，再寫邏輯。
2. **內容掃描類防線的豁免面要跟規則同時設計** —— 掃描器誤打自己引用的內容，本 repo 已發生四次，第四次真的擋下合法操作。
3. **改一份有 `_zh` 鏡像的檔案，鏡像要在同一個 commit 內一起改** —— 分兩次做等於承諾一個不會兌現的 TODO。

## 待人類裁決（沒有時效壓力，但沒人做就一直在）

- `docs/harness/LETTER-TO-FUTURE-SESSIONS.md` §III 剩 3 項：skillopt-loop 去留、session-handoffs 首次運轉驗證、Menu-Android guard 修復未 commit
- `docs/learnings/ERRORS.md` Pending Review 13 條：其中 3 條是 PR #14 retro 的新產出（含 `INV-ARC-002` 候選：ExecPlan 完成宣稱與勾選狀態必須一致），其餘是 `/pr-retro` 提醒與外部工具待查證事實
- `agent_docs/TECHNICAL-REFERENCE.md` 仍全檔未填 → 依 CLAUDE.md「Activation Status」跳過

## 非技術使用者入口

`docs/PLAIN/START-HERE_zh.md` —— 第一句話該打什麼、接下來會發生什麼、它絕對不會擅自做的事。`/guided-start` 是引導式入口（本輪修好：它原本指向 CLAUDE.md 一個已被搬走的章節，壞了 15 個 commit）。

## 相關

- 設計紀錄：`docs/plans/completed/F-003-tiered-harness.md`（§7 DEC-1~12 是「為什麼這樣做」的完整理由）
- 分層機制與已知限制：`.claude/tiers/README.md`
- PR：[#14](https://github.com/hahaicanfly/BaseAIProject/pull/14)，2026-07-29 合併為 `b777d98`
