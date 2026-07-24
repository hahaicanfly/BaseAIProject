# SESSION-HANDOFF:精靈工作室(Wizard Studio)實作啟動

> 產出:2026-07-24。上一 session 完成 GUI 封裝研究與全部裁決;本檔是下一 session(實作 session)的唯一入口。
> 讀完本檔後的第一件事:讀「必讀文件」兩份研究文件,然後執行「啟動步驟」。

## 一句話背景

BaseAIProject harness 的 GUI 封裝已完成研究與裁決:採**提案一「精靈工作室」**(本地 daemon + 瀏覽器 UI × 精靈步進式)+ **開放供應商模型**(session 之間的 Agents 溝通是系統脊椎);使用者將 clone 本 repo 建新專案實作。

## 必讀文件(依序)

1. `docs/research/2026-07-24-gui-packaging-proposals.md` — 為什麼是提案一;三項共同新建工程(人在環管線/失敗迴圈/用量護欄)
2. `docs/research/2026-07-24-wizard-studio-implementation.md` — **實作藍圖**:架構(§4)、能力分級 Tier 0-3(§3.1)、可行性與查證(§5/§6)、技術棧(§7)、四期計畫與機械驗收(§8)、裁決紀錄(§9)、風險(§10)

## 已裁決事項(2026-07-24,不要重問)

- **掛載語意 = 身分沿用**:daemon 重生受管 session、沿用本機 OAuth 登入態(Claude 訂閱 /login、Codex auth.json、Copilot keychain);不接管用戶既有終端視窗
- 定位**個人自用工具**(Anthropic 條款:對外產品化前須申請批准或改 API key)
- Copilot 初版接受「生命週期可見 + 降級徽章」;headless SDK 升級路徑列 P4 實測
- 用量護欄:觸頂**自動暫停 + 問人**;上限初值 P3 實作時定(可調)
- 新專案**沿用完整 harness**,fork 後填活化槽位(CLAUDE.md Quick Commands 的 build/test/lint 是第一個必填)
- 每 session 獨立 worktree;成果合併**一律開 PR + 用戶確認**
- MVP = 核心三家(Claude Code / Codex / Copilot);**第四家 = agy(Antigravity CLI,Google 系入口,非 gemini)**,與 Grok Build spike 同列 P4
- 技術棧:Node 22 LTS + TypeScript + node-pty + @xterm/xterm 6 + React/Vite + better-sqlite3 + @modelcontextprotocol/sdk;WebSocket(終端)+ SSE(看板);**不採** Bun / A2A / 直接解析各家 transcript 檔

## 啟動步驟

1. **確認所在 repo**:若使用者尚未 clone 出新專案,協助建立(clone → 新 remote → 依 CLAUDE.md Activation Status 填活化槽位);若已在新專案,先跑 `git branch --show-current` 確認不在 master
2. **建 ExecPlan**(本實作屬跨模組工程,CLAUDE.md 決策樹第 1 類):`docs/plans/active/` 新建,spec 見 `docs/plans/PLANS.md`,範圍 = 實作文件 §8 的 **P1**,**等人審核准再動工**
3. **P1 範圍**(2-3 週):daemon 骨架(bind 127.0.0.1 + Bearer token + Origin 驗證)、事件信封 + append-only JSONL 帳本 + SQLite 索引、ClaudeAdapter(`claude -p --output-format stream-json --verbose --forward-subagent-text`,OAuth 訂閱態、**顯式避開 --bare**)、worktree 管理器 v0(每 session 一 worktree)、Studio MCP server v0(report_status / send_message / read_inbox)、hooks http 收件端、最小 React 看板(單泳道 + 時間軸)
4. **P1 機械驗收**(全過才算完,詳見實作文件 §8):未設 ANTHROPIC_API_KEY 完成任務;事件落帳本且 SSE 推播 <2s;子代理巢狀歸因正確;拔 hooks 後輪詢補償補齊;session 全程獨立 worktree、主樹零改動;kill -9 daemon 重啟後帳本重建+resume;CI 鎖定 CLI 版本

## 動工即生效的風險(實作文件 §10 全文)

- Claude `--bare` 將成 `-p` 未來預設 → 啟動探針偵測,勿依賴預設行為
- Codex `auth.json` 官方禁止並發共用(P2 用到,架構先留序列化鎖介面)
- 三家 HTTP hooks 皆無重試 → 輪詢補償 + gap 偵測是必要工程,不是可選優化
- 實作前對 §6 的 12 條承重牆宣稱做**實測二次驗證**(官方文件平台轉址中,以實測為準)

## 執行紀律(本 harness 規則對實作 session 一樣有效)

plan-first / clarify-first(範圍新歧義才問,已裁決事項不重問)/ 驗收不得自我認證(fresh-context agent)/ gate-softening 禁止(FAIL 就是 FAIL)/ worktree 隔離 / 不 commit master(branch + PR)
