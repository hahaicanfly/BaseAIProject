---
name: gen-app-map
description: 掃描專案的進入點、路由、資料層與狀態管理，產出 app-map.json（AI 可讀 context primer）與 app-map.html（人類可讀視覺化），作為新 debug/重構 session 的輕量專案地圖。技術棧無關模板，fork 後需依專案填實掃描目標表。觸發於「gen-app-map」「生成地圖」「app map」「project map」「專案地圖」。
---

# gen-app-map Skill

掃描專案當前狀態，輸出一份使用者流程與系統結構地圖，作為新 session 的輕量 AI context primer。

> **模板說明**：本 skill 為**技術棧無關（tech-stack-agnostic）模板**。Fork 到具體專案後：
> 1. 依下方「掃描目標表」把 glob/regex 換成專案實際路徑（表中 Android／React-Next／後端 API 三欄僅為**範例**，不代表本專案技術棧）。
> 2. 更新 CLAUDE.md 的 `Tech Stack` 一節後，回填本檔 Step 0 的「本專案掃描目標」表格。

## 使用方式

```
/gen-app-map [可選：focus=<flow名稱>]
```

例如：
- `/gen-app-map` — 完整地圖
- `/gen-app-map focus=auth` — 聚焦認證流程

## 輸出

- `agent_docs/app-map.json` — AI 可讀結構（context primer）
- `agent_docs/app-map.html` — 人類可讀視覺化

兩份檔案不進常規 commit，僅作當下 session 使用（或手動 tag）。

---

## 執行流程

### Step 0：掃描目標表（fork 後必填）

本 skill 掃描四大類目標。下表為常見技術棧的 glob/regex **範例**，實際使用時請依 CLAUDE.md 的 Tech Stack 替換成專案真實路徑：

| 類別 | 定義 | Android 範例 | React / Next 範例 | 後端 API 範例 |
|------|------|--------------|--------------------|----------------|
| **entry-points**<br>進入點 | 應用程式啟動/掛載入口 | glob `**/AndroidManifest.xml` + regex `android.intent.action.MAIN`；glob `**/MainActivity.kt`、`**/*Application.kt` | glob `app/layout.tsx`（App Router）／`pages/_app.tsx`（Pages Router）／`src/main.tsx`（Vite/CRA entry） | glob `**/main.py`、`server.{js,ts}`、`cmd/*/main.go`；regex `app\s*=\s*(FastAPI|Express)\(` |
| **routes**<br>導覽/路由 | 頁面/畫面之間的導覽定義 | glob `**/ui/route/*.kt`；regex `NavHost\(.*startDestination` | glob `app/**/page.tsx`（file-based routing）；regex `<Route\s+path=` | glob `**/routes/*.{js,ts,py}`；regex `@app\.(get\|post\|put\|delete)\(|router\.(get\|post\|put\|delete)\(` |
| **data-layer**<br>資料層 | 資料存取/外部服務呼叫 | glob `**/*Dao.kt` + regex `@Dao`；glob `**/*ApiClient*.kt`、`**/*Service.kt` | glob `**/lib/api/*.ts`、`**/api/**/*.ts`；regex `useQuery\(|useMutation\(` | glob `**/models/*.py`、`prisma/schema.prisma`；regex `class \w+\(models\.Model\)|CREATE TABLE` |
| **state**<br>狀態管理 | UI/應用狀態的持有與流轉 | glob `**/viewmodel/*.kt`；regex `StateFlow<|MutableStateFlow` | glob `**/store/*.ts`、`**/slices/*.ts`；regex `createSlice\(|create\(\(set` (zustand)｜`useContext\(` | glob `**/session.*`；regex `redis\.(set\|get)\(|SESSION_` |

**本專案掃描目標**（fork 後填寫，取代上表對應欄位）：

| 類別 | 實際路徑/glob/regex |
|------|----------------------|
| entry-points | `{{填入}}` |
| routes | `{{填入}}` |
| data-layer | `{{填入}}` |
| state | `{{填入}}` |

### Step 1：掃描範圍

依 Step 0 表格逐類讀取，建立 mental model：

- **entry-points** → 找出應用啟動點，列為 `app.entryPoints`
- **routes** → 找出所有導覽路由定義，對應到 `screens[].route`
- **data-layer** → 找出 HTTP client / DAO / repository / ORM model，對應到 `services[]`
- **state** → 找出狀態持有單元（ViewModel / store / session），對應到 `screens[].stateInputs`

**Actions / Intents（跨技術棧共通概念）**
- 找出「使用者操作 → 觸發副作用」的統一入口（sealed class / action creator / event handler），列出所有子類別/變體作為 `actions[]`

**已知問題**
- 參考 `docs/learnings/ERRORS.md`（前 20 條 Active Lessons）
- 參考專案的 progress/backlog 文件的 open items

### Step 2：建構 app-map.json

使用以下技術棧無關的 schema：

```jsonc
{
  "app": {
    "name": string,
    "version": string,        // 從版本檔讀取：package.json / build.gradle.kts versionName / pyproject.toml 等
    "generatedAt": string,    // ISO 8601
    "entryPoints": string[]   // 例如 ["MainActivity"] 或 ["app/layout.tsx"] 或 ["server.ts"]
  },
  "screens": [{
    "id": string,             // "screen.<模組>.<名稱>"，例如 "screen.scan.main" 或 "page.dashboard.overview"
    "name": string,           // 給人看的名稱
    "route": string | null,   // 導覽路由字串，例如 "scan"、"/dashboard/[id]"
    "component": string | null, // UI 元件/渲染函式名（Composable / React Component / Template）
    "stateInputs": string[],  // 狀態 key，例如 ["uiState.isLoading", "cartState.items"]
    "actions": string[],      // 可觸發的 action id
    "expectedNext": string[]  // 預期跳轉的 screen id
  }],
  "actions": [{
    "id": string,             // action/intent/event 名稱，例如 "ScanImage"
    "type": "ui-event" | "domain-event" | "background-task",
    "sourceScreen": string | null,
    "calls": string[],        // service id，例如 "api.menu.parse"
    "guard": string | null,
    "onSuccess": string | null,
    "onFailure": string | null,
    "notes": string | null
  }],
  "services": [{
    "id": string,             // "api.<模組>.<方法>" 或 "db.<模組>.<方法>"
    "kind": "http" | "db" | "other",
    "path": string | null,    // HTTP: "POST /api/v1/orders"；DB: "OrderDao.insert()" / "UserRepository.findById()"
    "ownedBy": string | null, // 實作該 service 的類別/模組名
    "usedByActions": string[]
  }],
  "transitions": [{
    "from": string,
    "to": string,
    "via": string | null,     // action id
    "condition": string | null
  }],
  "knownIssues": [{
    "symptom": string,
    "suspects": string[],
    "evidence": string | null,
    "confidence": "low" | "medium" | "high"
  }]
}
```

**覆蓋範圍原則**：
- 優先涵蓋專案的 3 條主流程（fork 後填入，例如：登入認證、核心業務流程、付款/訂閱）
- 次要：歷史紀錄、設定、分享等周邊流程
- 省略：純 UI 動畫、theme 切換等不影響資料流的動作

### Step 3：建構 app-map.html

單頁 HTML，不依賴外部 CDN。包含：

1. **Overview** — app 名稱、entry points、生成時間、3 條主流程摘要
2. **Flow Diagram** — 用 Mermaid（`<script>` 內嵌）或 inline SVG 畫出核心流程；若專案已有現成流程圖（如 `agent_docs/diagrams/*.svg`），直接 `<img>` 引用
3. **Screens 表格** — route / component / stateInputs / actions / expectedNext
4. **Actions & Services 表格** — action → calls → service path
5. **Debug Hotspots** — 最多 10 條，每條附「Copy as prompt」按鈕
6. **使用說明** — 如何搭配 app-map.json 在新 session 中使用

樣式規範：
- `font-family: system-ui`，documentation 風格
- `.pill-critical/.pill-high/.pill-medium/.pill-low` 色標
- `navigator.clipboard.writeText` 實作 Copy 按鈕
- RWD，`max-width: 960px`

### Step 4：寫入檔案

```
agent_docs/app-map.json   ← 完整 JSON
agent_docs/app-map.html   ← 完整 HTML
```

完成後輸出：
```
✓ 完成：生成 agent_docs/app-map.json（N screens, N actions, N services）
✓ 完成：生成 agent_docs/app-map.html
→ 下一步：用 open agent_docs/app-map.html 在瀏覽器預覽，或在新 session 中載入 app-map.json 作為 context primer
⚠ 注意：此地圖為當下快照，不自動維護；重大架構異動後請重新執行 /gen-app-map
```

---

## 驗證

- `app-map.json` 必須是有效 JSON（可用 `python3 -m json.tool` 驗證）
- `screens[]` 數量應與 Step 1 實際掃描到的 UI 單元數量一致（不可憑空增減）
- `knownIssues[]` 至少 3 條（從 `docs/learnings/ERRORS.md` active lessons 取，若不足 3 條可留空並註記原因）
- HTML 必須可獨立開啟，不依賴網路資源
