# 精靈工作室(Wizard Studio)實作研究:多供應商 OAuth Session 編排

> 日期:2026-07-24
> 前置決策:採用 `2026-07-24-gui-packaging-proposals.md` 提案一(本地 daemon + 瀏覽器 UI × 精靈步進式)
> 來源:Workflow 三階段研究(5 路並行官方文件調研 → 架構綜合 → 12 條承重牆宣稱對抗性查證)+ 2 路開放供應商補研(Gemini/agy、Grok/ACP 生態)+ plan-reviewer 批判
> 用途:供 clone BaseAIProject 後的新專案作為實作依據
> 狀態:研究定稿,§9 開放問題已於 2026-07-24 全數裁決 → 可進入實作(P1 起,依 §8)

## 1. 需求與範圍

在提案一基礎上新增的硬需求(2026-07-24 使用者補充:供應商**包含但不限於**起點三家,亦須可接入 Gemini(agy)、Grok 等;**系統脊椎是 session 之間的 Agents 溝通**):

- **R1**:用戶已在 terminal 各自以 **OAuth 登入(非 API key)**使用 Claude Code、OpenAI Codex CLI、GitHub Copilot CLI(起點三家),要把這些 session「掛載」進工作室
- **R2(脊椎)**:session 之間能相互溝通、同步工作狀態——供應商無關,任何接入者皆可參與
- **R3**:每個 session 可各自建立子 agent,且全部子代理在工作室可見
- **R4**:開放供應商模型——新供應商以插件式 adapter 接入,不改動核心(能力分級見 §3.1)
- 另需考慮「跨 daemon 溝通」(未來多機/多 daemon)的預留設計

## 2. 最重要的語意澄清(動工前必須確認)

「掛載已開啟的 3 個 terminal session」有兩種語意,技術路徑互斥:

| | (a) 字面附掛:接管用戶已開的互動視窗 | (b) 身分沿用:daemon 重生受管 session,沿用同一 OAuth 登入態 |
|---|---|---|
| 可行性 | 僅當 session 預先跑在 tmux 內才可附掛(control mode);PTY 函式庫**無法領養非自己 spawn 的行程**(POSIX controlling-terminal 語意,查證 CONFIRMED) | 三家皆有官方非互動路徑且 OAuth 沿用已查證(見 §3) |
| 資料品質 | screen-scraping 原始 ANSI bytes,無結構化事件 | 結構化事件流(stream-json / JSON-RPC / hooks),含子代理歸因 |
| 穩定性 | 連 Anthropic 官方 Agent Teams tmux backend 都有已知 shell 初始化 race condition(issue #23513/#25315) | 官方介面,可鎖版+整合測試管理 |
| 業界先例 | 無成熟先例 | claude-squad、Tmux-Orchestrator 兩個 OSS 多 CLI 編排器**都選擇重生而非附掛**(查證 CONFIRMED) |

**本研究的主路線 = (b)**:工作室重生的 session 沿用同一 OAuth 身分與額度(憑證在磁碟/keychain,不複製、不落庫),用戶既有的 3 個視窗保留給人手動用,工作室內以 xterm.js 提供等價終端視圖;tmux 附掛做為備援模式(僅限用戶願意把 session 改跑在 tmux 內)。**若用戶堅持字面語意 (a),工程量級與穩定性判定全面翻盤——此為 §9 開放問題第 1 條。**

## 3. 三家 CLI 整合面(全部經官方文件查證)

| 能力 | Claude Code | Codex CLI | Copilot CLI |
|---|---|---|---|
| OAuth 非互動執行 | ✅ `-p`(非 bare)沿用 /login 訂閱 OAuth,官方認證順位明列;`setup-token` 供長期 | ✅ `codex exec` 官方明載「reuses saved CLI authentication」(`~/.codex/auth.json`) | ✅ spawn `copilot -p` 自動吃 keychain OAuth;headless SDK server 需明傳 gitHubToken(可否傳 OAuth token 未定,見 §6 修正) |
| 結構化事件流 | ✅ `--output-format stream-json`(NDJSON,token 級) | ✅ app-server JSON-RPC(delta 通知)/ `exec --json` | ⚠️ `-p` 無原生 JSON;hooks http 事件 + SDK Streaming Events(headless 路徑)補償 |
| 執行中注入(steer) | ⚠️ Channels 為 research preview;`--bg`+`attach` 可互動 | ✅ app-server `turn/steer` / `interrupt` | ❌ 未證實(ACP 屬 client 協定,public preview) |
| resume / 多 session | ✅ `--resume`/`--session-id`/`--bg`/`claude agents --json` | ✅ CLI resume + app-server `thread/*` | ✅ `--resume SESSION-ID`;無多 session 管理,daemon 自管行程表 |
| 子代理可見性 | **完整**:`parent_tool_use_id` 歸因 + `--forward-subagent-text` 全文 | **接近完整**:SubagentStart/Stop hooks(2026-05-14 GA)+ `thread/list` sourceKinds 子執行緒樹(部分欄位 experimental) | **生命週期**:hooks `subagentStart/subagentStop`(14 種事件之一);過程內容需 headless+SDK Streaming Events(opt-in) |
| hooks → daemon 推播 | ✅ `type:"http"` POST(non-blocking、無重試) | ✅ hooks GA(command 型)+ `notify` 轉發 | ✅ hooks `http` 型別 POST |
| MCP client | ✅ `claude mcp add`(stdio/http/sse/ws) | ✅ `[mcp_servers]`(stdio/Streamable HTTP) | ✅ `~/.copilot/mcp-config.json`(stdio/http/sse) |

三家各自的完整能力清單、風險與官方來源:見本檔附錄與 Workflow journal(`wf-claude-code/codex/copilot/interop/runtime` 五份結構化報告)。

### 3.1 開放供應商模型:能力分級(R4)

接入門檻不是「像核心三家一樣什麼都有」,而是**分級宣告**——adapter 自報等級,UI 與排程器按等級啟用功能:

| Tier | 門檻 | 得到什麼 |
|---|---|---|
| **0 可互通(唯一硬性門檻)** | MCP client(可掛 Studio MCP hub) | 參與 Agents 溝通:報狀態/收發訊息/檔案租約/人在環升級 |
| **1 可託管** | + 非互動模式 + OAuth 登入態重用 | daemon 重生受管 session(spawn 於 worktree) |
| **2 權威時間軸** | + 結構化事件流(stream-json / JSON-RPC / ACP session updates)或 hooks 推播 | 時間軸第一級資料、失敗迴圈熔斷 |
| **3 完整編排** | + 子代理可觀測 + mid-turn steer | 巢狀時間軸、執行中注入 |

生態查證(2026-07):**MCP client 已是 agentic CLI 事實標準**——除核心三家外,Gemini CLI、Antigravity CLI(agy)、Grok Build(xAI 官方)、Qwen Code、OpenCode、Amp、Cursor CLI 皆支援;顯著例外只有 Aider(需第三方 bridge)。暫定分級:

| 供應商 | 暫定 Tier | 依據(節錄) |
|---|---|---|
| Claude Code / Codex | 3 | 已查證(§3);Codex `turn/steer` 為最穩 mid-turn 通道;Claude 的 steer 靠 `--bg`+`attach` 與下一回合注入(Channels 僅 research preview),屬 Tier 3 邊緣 |
| Copilot CLI | 2 | 子代理僅生命週期;steer 未證實 |
| Gemini CLI | 2(3 候選) | headless `-p --output-format stream-json`;OAuth 憑證檔 `~/.gemini/oauth_creds.json` 同 HOME 子行程可重用(daemon 情境官方未明文保證);MCP 三傳輸;11 種 hooks 事件;子代理 2026-04 上線(過程可觀測性未明) |
| Antigravity CLI(agy) | 2 候選(待實測) | 2026-05 起有獨立 CLI(`agy`,Go 二進位):`-p` / `--headless --approve`、MCP、hooks/subagents,與 Gemini CLI 共用 agent harness → **可被 daemon 編排**;本 repo 已有 agy 橋接慣例(CLAUDE.md「Antigravity Bridge」) |
| Grok Build(xAI 官方,2026-05) | 1–2 候選 | 訂閱制 device-auth(`~/.grok/auth.json`,非 API key)、MCP、原生 ACP、相容 `.claude/` skills/agents/hooks 格式;headless flag 語法 `[UNCONFIRMED: 僅第三方文件,無 xAI 一手佐證]` |
| Qwen Code / OpenCode / Amp | 1–2 候選 | MCP + 非互動模式皆確認;OpenCode 另可作 ACP server |
| Aider | 未達 Tier 0 | 無原生 MCP;納入需 bridge,不建議 MVP 處理 |

**ACP(Agent Client Protocol)的角色**:Zed + JetBrains 共推(2026-01 起有 Agent Registry),已支援者含 Copilot(原生,public preview)、Gemini CLI、Grok Build、Qwen Code、OpenCode;Claude Code/Codex 走維護中的社群 bridge。ACP 的定位——宿主(client)↔ agent(server):建 session、灌 prompt、收結構化事件流——正是工作室 daemon 的控制面需求,**一個通用 ACPAdapter 即可覆蓋所有 ACP 供應商的 Tier 1–2 能力**,把新供應商接入成本壓到設定檔等級。分工結論:**MCP = 工具面(Tier 0 硬門檻,agent 掛工作室 hub)**;**ACP = 控制面(Tier 1–2 的通用實作路徑,daemon 驅動 agent)**;核心三家仍用專屬 adapter(事件最豐、已逐項查證)。

## 4. 架構設計

### 4.1 元件總覽

```
┌─────────────────────────── 瀏覽器 UI(React)───────────────────────────┐
│ 精靈六階段步進面板 │ 多 Session 泳道看板 │ 時間軸(含子代理)│ xterm.js 終端視圖 │
└──────────┬───────────────────────┬─────────────────────────────────────┘
     WebSocket(終端雙向)      SSE(狀態/時間軸單向推播)
           │                       │
┌──────────┴───────────────────────┴─────────────────────────────────────┐
│              Studio Daemon(Node.js/TypeScript,單機常駐)                │
│  精靈流程引擎(六階段狀態機)← 事件匯流排(統一信封+扇出)→ JSONL 帳本+SQLite │
│  ┌──────────────── Session Adapter 層(插件式註冊)────────────────┐    │
│  │ ClaudeAdapter    CodexAdapter    CopilotAdapter    ACPAdapter(通用)│    │
│  │ -p stream-json   app-server      spawn -p(主)     Gemini/agy/Grok │    │
│  │ --bg/agents      JSON-RPC        hooks http        /Qwen/OpenCode… │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│  Studio MCP Server(跨 CLI 匯流排)│ Webhook Receiver │ node-pty 池 │ worktree 管理器 │
└─────────────────────────────────────────────────────────────────────────┘
      ▲ MCP(stdio/http)      ▲ HTTP POST(hooks)      ▲ PTY/stdio
 Claude Code(OAuth 訂閱) │ Codex CLI(ChatGPT OAuth) │ Copilot CLI(GitHub OAuth)
                     ——各自沿用本機既有 OAuth 登入態——
```

安全基線(套用 MCP 官方 transports 規範):daemon 只 bind 127.0.0.1、驗證 Origin header 防 DNS rebinding、應用層 Bearer token;憑證檔絕不複製、不入庫、不跨機。

### 4.2 統一 Adapter 介面

```typescript
interface SessionAdapter {
  vendor: string;  // 'claude' | 'codex' | 'copilot' | 'gemini' | 'agy' | 'grok' | ...(插件註冊,R4)
  tier: 0 | 1 | 2 | 3;  // 能力分級(§3.1)——由 subagentVisibility/steer/events 等能力欄推導,不可獨立設定,避免兩處漂移
  spawn(task: TaskSpec): Promise<ManagedSession>;      // 重生受管 session(重用本機登入態;cwd = 該任務的 worktree,見 §4.6)
  resume(sessionRef: string): Promise<ManagedSession>;
  events(): AsyncIterable<StudioEvent>;                 // 正規化事件流(權威時間軸來源)
  steer?(sessionId: string, input: string): Promise<void>; // 能力不對等,可選
  subagentVisibility: 'full' | 'lifecycle' | 'none';    // 誠實宣告能力等級
  health(): AdapterHealth;                              // 版本探針(偵測介面破壞)
}
```

CopilotAdapter 落差處置:主通道 = spawn `copilot -p`(OAuth 保留)+ hooks http 事件 + `-s` 文字解析(best-effort);UI 對 Copilot 泳道顯示「事件粒度受限」降級徽章。headless SDK 路徑(完整 Streaming Events)列為 opt-in 升級——經查證,官方並未字面禁止 OAuth token 用於該路徑(見 §6),但憑證行為不同須實測,實測前不列入 OAuth 硬需求的達成路徑。

### 4.3 事件匯流排與狀態同步(R2)

- **統一事件信封**:`{event_id, ts, daemon_id, vendor, session_id, subagent_id?, kind, payload, source_channel, confidence}`;`source_channel` 標記來源(official-stream / hook / mcp-tool / file-watch),`confidence` 區分權威與補償來源。持久化:append-only JSONL(單一 writer = daemon)+ SQLite 索引,沿用 `state/SCHEMA.md` 精神。
- **三管道並用**:
  1. **Studio MCP Server(共用匯流排)**:三家 CLI 都以 MCP client 掛載(三家 client 能力皆官方確認;跨異質 CLI hub 有 mcp_agent_mail 先例,Copilot 一腳屬技術外推)。工具集:`studio_report_status` / `studio_send_message`(跨 session inbox)/ `studio_read_inbox` / `studio_claim_file`(勸告性檔案租約,僅跨 worktree 共享檔案用,§4.6)/ `studio_request_human`(人在環升級)。**跨 session 溝通是拉取式**——A 寫入 hub、B 於下一回合讀取;真正 mid-turn 推入只有 Codex `turn/steer` 穩定可用,UI 須明示「訊息將於對方下一回合送達」。
  2. **Hooks/notify HTTP 推播(遙測)**:三家 hooks 事件 POST 到 daemon webhook;皆 non-blocking、無重試,**必須配輪詢補償 + gap 偵測**,不得當必達管道。
  3. **官方事件流(權威)**:stream-json / app-server 通知為第一級資料;**transcript/rollout JSONL 檔案監看降為最後備援**(三家官方皆註明內部格式、版本間會變),啟用時標低 confidence。
  4. **ACP 控制面(通用路徑)**:對支援 ACP 的供應商,daemon 以 ACP client 建 session、灌 prompt、收 session update 事件流——即 §3.1 通用 ACPAdapter 的 Tier 1–2 實作;核心三家仍走專屬通道(事件更豐)。
- **跨 daemon 預留**:信封自帶 `daemon_id`;bus 抽象為 `LocalBus | RemoteBusBridge`,遠端橋接走帶 token 的 WebSocket + NDJSON,零改造升級。**明確不採 A2A**:協議雖 v1.0(Linux Foundation 治理),但三家 CLI 皆無原生支援、僅社群 wrapper;信封欄位命名參照 A2A 概念保留映射空間即可。

### 4.4 子代理可見性(R3)

時間軸統一以 `session → subagent` 樹狀渲染,由 `subagentVisibility` 宣告驅動呈現等級,**絕不偽造未取得的過程資料**:

| 供應商 | 粒度 | 降級方案 |
|---|---|---|
| Claude Code | 完整(巢狀節點、逐訊息展開) | — |
| Codex | 接近完整(子執行緒樹+狀態通知) | sourceKinds 欄位變動時退回 hooks 起訖事件 |
| Copilot | 生命週期(哪個子代理、何時起訖) | 摺疊節點「內部活動中(N 個子代理)」;opt-in headless 路徑可升級至 Streaming Events 完整粒度 |

### 4.5 與精靈六階段 UI 的整合

- **泳道看板**:執行階段每 session 一列(供應商圖示、當前任務、狀態燈 ⚪idle/🔵working/🟡waiting-human/🔴failed-loop/⚫disconnected、子代理徽章);計劃階段每條目可指派 session(「這步由 Codex 做」)。
- **人在環管線**(承接提案一共同新建工程 1):任一 session 經 `studio_request_human` 或 hooks 事件升級 → bus 發 `human_attention_required` → UI 置頂通知卡 + 泳道轉 🟡;應答經「下一回合注入」送回。
- **失敗迴圈**(共同新建工程 2):FAIL 事件標記輪次;「兩輪無改善」由 **daemon 機械比對兩輪 FAIL 集合**後強制升級「需要你決定」——熔斷邏輯在 daemon,不信任 agent 自律(對應 judgment-rubrics §2.5/§3)。
- **成本護欄 → 用量護欄**(共同新建工程 3 的 OAuth 訂閱改寫):訂閱模式無 per-token 金額,改呈現各帳號速率/額度狀態、任務級「回合數/子代理數/工具呼叫數」上限、觸頂自動暫停+問人。**工作室 session 與用戶手動使用共吃同一訂閱額度,護欄是必要保護而非加分項。**
- **計劃所有權與仲裁**:計劃的唯一權威副本由 daemon 的精靈流程引擎持有(存帳本+SQLite),UI 與各 session 看到的都是投影。計劃條目帶相依邊(DAG),排程器只把「無未完成前置」的條目派給被指派的 session(每 session 一條佇列);有相依關係或檔案交集的條目由 daemon 串行化——**仲裁在 daemon,不靠 session 自律**。指派由用戶在計劃階段決定(daemon 可建議預設),執行中改派走「調整計劃 → 重新確認」既有迴圈。時間軸是單一事件信封流(§4.3)按泳道分組渲染;跨 session 因果(A 完成觸發 B)以 step_id 關聯標註。

### 4.6 工作區隔離(worktree)

沿用 parallel-worktree.md 硬規:**每個受管 session(連同其子代理)在自己的 git worktree + `agent/<task-id>` 分支中作業,絕不直接寫主工作樹**;daemon 內建 worktree 管理器負責建立/回收(提案一本就把 daemon 定位為「session/worktree 編排薄層」,此為並發隔離的主機制)。`studio_claim_file` 勸告性租約只服務少數必須跨 worktree 共享的檔案(如共用規格文件),不承擔並發隔離責任。成果合併回主幹發生在六階段的「檢核」階段:daemon 產生變更摘要給用戶檢視,確認後以分支合併(或 PR)落地;合併衝突翻譯成非技術用戶可理解的介面(「兩個 session 改了同一處:選 A / 選 B / 我來說明」),不暴露 git 術語。

### 4.7 Daemon 崩潰恢復

daemon 同時是單一 writer 與所有受管 session 的 spawn 母行程,屬單點故障,恢復設計:

1. **session 登記表**(vendor / session_id / worktree / pid / 最後事件序號)隨事件即時落帳本
2. **重啟 reconcile**:逐筆檢查 pid 存活——存活者重新接管(Claude `claude agents` + `attach`;Codex app-server 重連 `thread/resume`;Copilot 走 `--resume SESSION-ID`),死亡者標記 interrupted 並提供「從上次狀態續跑」(三家官方 resume 機制,§3)
3. **帳本 append-only**:崩潰最多截斷最後一行,重放即可重建看板狀態;hooks 漏收由輪詢補償的 gap 偵測補齊
4. **受管子行程預設隨 daemon 一起終止**(process group)——刻意取捨:避免孤兒 session 在無人監看下持續消耗訂閱額度,恢復靠 resume 而非接管孤兒

## 5. 可行性判定

| 需求 | 判定 | 關鍵依據與條件 |
|---|---|---|
| R1 掛載 3 個 OAuth session | **feasible-with-caveats** | 字面附掛官方手段不可行(PTY 無法領養行程);身分沿用語意下三家皆可行。條件:(1) 用戶接受語意轉換(§2);(2) Codex auth.json 官方要求序列化存取,daemon 須加鎖;(3) Copilot 走 spawn 路徑;(4) Anthropic 條款風險(§9);(5) Claude `--bare` 未來預設化須以探針防範 |
| R2 session 互通同步(脊椎) | **feasible-with-caveats** | Studio MCP server 匯流排 + hooks 推播——供應商無關:MCP client 為 Tier 0 硬門檻且已是生態事實標準(§3.1),任何達標者即可參與;三家皆官方確認,有 mcp_agent_mail 先例。邊界:溝通是拉取式非即時推入;hooks 不保證送達需輪詢補償;不可押注 A2A |
| R3 子代理全可見 | **feasible-with-caveats** | 三家「可建子代理」皆確認;可見粒度不對等(Claude 完整/Codex 接近完整/Copilot 生命週期+opt-in 升級)。若接受不對等呈現(UI 誠實標註),R3 成立 |
| R4 開放供應商 | **feasible(Tier 0)/ feasible-with-caveats(Tier 1–2)** | Tier 0:MCP client 為生態事實標準,近乎普及(例外 Aider 明確標示)。Tier 1–2:通用 ACPAdapter 尚未建置、各家 ACP 支援等級混雜(風險 15),須逐家實測(P4 以第四家供應商實證);能力分級讓不對等供應商誠實共存 |

## 6. 承重牆宣稱查證結果(12 條對抗性驗證)

**10 條 CONFIRMED**,涵蓋:Claude `-p` 非 bare 沿用訂閱 OAuth、`--bare` 只認 API key 且將成 `-p` 未來預設、stream-json 子代理歸因、hooks http 推播(無重試)、`codex exec` 重用 OAuth、app-server JSON-RPC 方法族、auth.json 禁止並發共用、Codex hooks GA(2026-05-14)、三家 MCP client、OSS 先例皆重生不附掛。查證附帶的精確化:

- Claude `setup-token` 產生的 token 在 `--bare` 下**同樣不被讀取**——bare 化風險的因應是「顯式避開 bare」,setup-token 不是 bare 模式的替代方案。
- Codex app-server 核心方法存在無疑,但官方**從未使用「stable」字樣**——「穩定」是從其他功能被標 experimental 的反面推論,鎖版仍必要。
- Codex experimental 標記在 `parentThreadId/ancestorThreadId` 欄位,非 sourceKinds 本身。

**2 條 REFUTED(皆 Copilot 側,修正後對可行性更有利)**:

1. ~~「headless SDK 路徑官方拒絕 OAuth user token 用於自動化」~~ → 官方文件無此字面條款,僅「建議」CI/CD 用機器範圍 token;SDK 的 gitHubToken 參數可否傳 OAuth token 未被官方否定,**待實測**。CopilotAdapter 主路線仍為 spawn(最穩),但 headless 升級路徑從「官方封死」改判「未定、可實測」。
2. ~~「Copilot hooks 13 種事件是子代理可見的唯一官方依據」~~ → 實為 **14 種**事件;且 **SDK Streaming Events(subagent.started/completed/failed)是第二條官方結構化管道**——Copilot 子代理可見性天花板高於原判定(需走 headless 路徑)。

**未經對抗性查證的第 13 條**(超出 12 條驗證上限被裁掉,來源為官方文件逐字引用):Anthropic Agent SDK 文件明文「Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products」——個人自用屬灰色地帶,**產品化/分發前必須向 Anthropic 申請批准或改用 API key**,列 §9 開放問題。

## 7. 技術棧推薦(單選)

| 層 | 選型 | 理由/注意 |
|---|---|---|
| Daemon | **Node.js 22 LTS + TypeScript** | 與 node-pty/xterm.js/VS Code 範本重疊度最高;三家 CLI 的 NDJSON/JSON-RPC 天然對應;可直接嵌 @openai/codex-sdk 與 MCP 官方 TS SDK。Bun 排除(無原生 PTY,oven-sh/bun#22468);Rust/Go 活動零件多、驗證期開發慢 |
| 終端層 | **node-pty + @xterm/xterm 6.x** | 必開 `handleFlowControl=true`(>4KB 快速輸出丟資料,#726);舊 xterm 套件已棄用;macOS 優先避開 ConPTY 問題(#827) |
| 前端 | **React + Vite;WebSocket(終端雙向)+ SSE(狀態看板單向)** | SSE 自動重連、複雜度低,只有終端需要雙向 |
| 匯流排持久化 | **append-only JSONL(單一 writer)+ better-sqlite3 索引** | 沿用 state/ 帳本精神,規避勸告性檔案鎖並發風險 |
| MCP hub | **@modelcontextprotocol/sdk(stdio + Streamable HTTP)** | |
| 安全 | **bind 127.0.0.1 + Origin 驗證 + Bearer token** | MCP 官方 transports 規範基線;機密存取用 macOS `security` CLI(keytar 已封存棄用) |
| 備援 | tmux 3.6(僅 attach 備援載入,core 不依賴) | |

明確不採:Bun、A2A、直接解析三家 transcript/rollout JSONL(官方皆註明內部格式)、Copilot headless SDK 作為預設路徑(實測通過前)。

## 8. 分期實作計畫(clone 後新專案)

| 期 | 內容 | 機械驗收(節錄) |
|---|---|---|
| **P1 Claude 垂直切片 + 匯流排骨架**(2-3 週) | daemon 骨架(loopback+token+Origin)、事件信封與帳本、ClaudeAdapter(`-p --output-format stream-json --verbose --forward-subagent-text`)、worktree 管理器 v0(每 session 一 worktree)、Studio MCP server v0、hooks 收件端、最小看板 | 未設 ANTHROPIC_API_KEY 下完成任務(證明 OAuth 沿用);事件落帳本並 SSE 推播 <2s;子代理巢狀歸因正確;拔 hooks 後輪詢補償補齊事件;session 全程在獨立 worktree 作業、主工作樹零改動;kill -9 daemon 後重啟,帳本重建看板並 resume(或正確標記 interrupted);CI 鎖定 CLI 版本 |
| **P2 Codex + 跨 session 溝通實證**(2-3 週) | CodexAdapter(app-server 為主)、auth.json 序列化鎖、turn/steer、子執行緒樹、雙 session 經 MCP hub 互傳、DAG 排程器 v0 | Claude→Codex 訊息來回一輪全程入帳本;並發 3 session 跑 10 分鐘 auth.json 無 refresh race;sourceKinds 缺失自動降級有測試;steer 注入成功;有檔案交集的兩條計劃條目被 daemon 串行化(仲裁測試) |
| **P3 Copilot(降級模式)+ 精靈六階段整合**(3-4 週) | CopilotAdapter(spawn+hooks+文字解析)、六階段 UI 接泳道、人在環管線、失敗迴圈熔斷、用量護欄、合併回主幹流程 | 三 session 同掛且 OAuth 身分無誤;Copilot 掛載 studio MCP hub 完成一次 `studio_report_status` 往返(補實技術外推缺口);端到端走完六階段含一次人工升級與一次合併(含人為製造衝突以非技術介面解決);連續兩輪相同 FAIL 自動出「需要你決定」;Copilot 泳道降級徽章正確、無偽造資料 |
| **P4 開放供應商 + 加固**(2-3 週) | 通用 ACPAdapter v0、第四家供應商實證(Gemini CLI 或 agy,依 §9-8 核對結果)、Grok Build spike(headless 語法實測)、tmux 附掛備援、RemoteBusBridge、版本升級探針套件、Channels/Copilot-headless 實驗評估 | 第四家供應商以 Tier 0(掛 hub 互通)+ Tier 1(OAuth 重生)接入且**核心零改動**(R4 實證);升級任一 CLI 後探針偵測介面破壞並降級告警;tmux 備援可附掛;兩 daemon 橋接互見事件 |

## 9. 開放問題與裁決紀錄

> **裁決(2026-07-24,使用者)**:Q1 = **接受身分沿用語意**;Q2–Q7 採建議預設:Q2 定位個人自用工具(產品化前向 Anthropic 申請批准或改 API key)、Q3 接受 Copilot 生命週期+降級徽章初版(headless 升級列 P4 實測)、Q4 觸頂自動暫停+問人(上限初值 P3 實作時定)、Q5 新專案沿用完整 harness(fork 後填活化槽位)、Q6 每 session 獨立 worktree且合併一律開 PR + 用戶確認、Q7 MVP 核心三家(第四家與 Grok spike 列 P4);Q8 = **Google 系接 `agy`**(P4 的第四家供應商即 agy)。以下原始問題保留供上下文。

1. **掛載語意確認(最關鍵)**:接受 §2 的「身分沿用」語意轉換?(重生受管 session、沿用同一 OAuth 身分額度;既有 3 個視窗保留手動用)——堅持字面附掛則走 tmux screen-scraping,量級與穩定性判定全面重估
2. **Anthropic 條款**:本產品未來若對外分發,Claude 側 OAuth 路線需先向 Anthropic 申請批准或改 API key;現階段是否定位「個人自用工具」?
3. **Copilot 不對等呈現**:接受 Copilot 泳道「生命週期可見+降級徽章」的初版?headless SDK 升級路徑(完整事件流)是否列入 P4 實測?
4. **用量護欄參數**:任務級回合數/子代理數上限預設值?觸頂行為(自動暫停 vs 即時問人)?
5. **新專案啟動方式**:clone 後沿用本 repo 的 harness(hooks/rules/protocols)還是精簡子集?
6. **整合策略**:預設每 session 獨立 worktree(遵循 parallel-worktree.md,§4.6);成果合併路徑選 daemon 直接合併還是一律開 PR?合併是否一律經用戶確認?
7. **供應商範圍**:MVP 僅核心三家、第四家(Gemini/agy)與 Grok 列 P4?或其中之一提前?
8. **Google 系入口核對**:官方訊息互相矛盾——一文稱 2026-06-18 起消費版 Gemini CLI 停止服務、OAuth 遷移 agy,另一文稱兩者並存——動工前人工核對最新公告,決定 Google 系接 `gemini` 還是 `agy`

## 10. 風險清單(節錄,完整見 Workflow 報告)

1. **語意落差**(§9-1):未確認前不得動工——返工成本最高的單一風險
2. **Anthropic 條款**(§9-2):產品化的翻盤點
3. **Claude `--bare` 預設化**:升版後 OAuth headless 可能無預警失效;鎖版 + 啟動探針 + 顯式避開 bare
4. **Codex auth.json 併發 race**:官方禁止並發共用;無鎖會**弄壞用戶的 ChatGPT 登入**(影響日常使用,非僅工作室故障)
5. **Copilot 介面最不穩**:2026-02 曾無預警移除 `--headless --stdio` 令官方 SDK 全版本失效(#1606 關為 not planned);Copilot 泳道維護預算應為三家最高
6. **事件送達不保證**:三家 HTTP hooks 皆 non-blocking 無重試;輪詢補償 + gap 偵測是必要工程
7. **內部格式漂移**:三家 transcript/rollout 檔案格式官方皆不承諾穩定;只能當低 confidence 備援
8. **preview/experimental 依賴**:Claude Channels(research preview)、Codex 部分欄位(experimental)、Copilot ACP(public preview)——皆已排除出關鍵路徑
9. **訂閱額度共享**:工作室高並發子代理可能耗盡用戶日常額度;用量護欄必要
10. **node-pty 流控**:AI CLI 大段輸出下必開 handleFlowControl 並於 P1 壓測
11. **文件平台遷移**:developers.openai.com/codex 正 308 轉址 learn.chatgpt.com;關鍵宣稱實作前應以實測二次驗證
12. **並發寫入隔離**:主機制為 per-session worktree(§4.6);殘餘風險是跨 worktree 共享檔案的租約僅勸告性,以及合併衝突對非技術用戶的呈現成本
13. **daemon 單點故障**:恢復設計見 §4.7;P1 起驗收含 kill-restart 測項,防孤兒 session 靜默燒訂閱額度
14. **Google 系入口不確定**:消費版 Gemini CLI 可能已/將 EOL 轉移 Antigravity CLI(官方訊息矛盾,§9-8);Google 系 adapter 應以「兩者共用 agent harness」的抽象吸收此變動
15. **ACP 支援等級混雜**:Copilot 為原生 preview、Claude Code/Codex 是社群 bridge、Grok headless 語法未經一手證實——通用 ACPAdapter 對每家的穩定性需逐家實測,「支援 ACP」四字不可視為同級

## 附錄:主要官方來源

- Claude Code:code.claude.com/docs — headless / authentication / hooks / mcp / channels / sessions / cli-reference / agent-sdk/overview
- Codex:developers.openai.com/codex — noninteractive / auth / ci-cd-auth / app-server / hooks / mcp / sdk / config-reference;github.com/openai/codex(app-server README、mcp interface)
- Copilot:docs.github.com/copilot — run-cli-programmatically / authenticate-copilot-cli / hooks-reference / add-mcp-servers / copilot-sdk(backend-services、streaming-events);github.blog GA 公告(2026-02-25)
- 互通:github.com/Dicklesworthstone/mcp_agent_mail;a2a-protocol.org;github.com/smtg-ai/claude-squad;github.com/Jedward23/Tmux-Orchestrator;anthropics/claude-code issues #23513/#25315
- 技術棧:github.com/microsoft/node-pty(#726/#827);npmjs.com/@xterm/xterm;modelcontextprotocol.io transports 規範;oven-sh/bun#22468
- Gemini/agy:github.com/google-gemini/gemini-cli(docs/cli/headless.md);geminicli.com/docs(mcp-server / hooks / session-management / remote-agents);developers.googleblog.com(subagents 上線、gemini-cli→antigravity-cli 轉移公告);cloud.google.com(Antigravity 五面向);antigravity.google/docs
- Grok / ACP 生態:superagent-ai/grok-cli;hermes-agent.nousresearch.com(Grok device-auth);blog.jetbrains.com(ACP 共建、Agent Registry);github.blog(Copilot ACP public preview);qwenlm.github.io/qwen-code-docs(headless);opencode.ai/docs
