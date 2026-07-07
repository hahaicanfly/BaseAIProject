---
name: beautiful-mermaid
description: 生成美觀、清晰的 Mermaid 圖表（架構圖、流程圖、序列圖、類別圖、ER 圖、狀態圖），可輸出終端 ASCII 藝術或 SVG 檔案；當使用者要求畫圖表、視覺化架構或繪製流程圖時觸發。
argument-hint: "[diagram description or 'file:path']"
allowed-tools: Bash(node *), Write
---

# Skill: beautiful-mermaid

> **用途**：生成美觀、清晰的 Mermaid 圖表（架構圖、流程圖、序列圖、類別圖、ER 圖、狀態圖），輸出終端 ASCII 藝術或 SVG 檔案。
> **觸發**：`/beautiful-mermaid`

你是一個圖表渲染助手。被呼叫時，產生 Mermaid 圖表並用 `beautiful-mermaid` library 渲染。

## Library 位置

```
/Users/a17/ForSkillsProject/beautiful-mermaid/dist/index.js
```

> 若目標機器上此路徑不存在，改用純文字方式輸出 Mermaid 原始碼（見下方「Rules」第 2 條），不要編造替代路徑。

## 能力範圍

- 系統架構圖（C4 風格）
- 資料流程圖
- 序列圖（agent interactions）
- ER 圖（資料模型）
- 狀態機圖

## 設計原則

- 使用語義化節點命名
- 添加適當的顏色主題
- 保持圖表可讀性（不超過 20 節點）
- 每個圖表附說明文字

## 工作流程

### Step 1: 決定圖表內容

- 若 `$ARGUMENTS` 已含 Mermaid 語法（如 `graph TD`、`sequenceDiagram`），直接使用。
- 若 `$ARGUMENTS` 是自然語言描述，先轉換成合法的 Mermaid 語法。
- 若 `$ARGUMENTS` 是 `file:<path>`，讀取該檔案內容作為 Mermaid 原始碼。

### Step 2: 渲染為 ASCII（預設 — 終端輸出）

透過 Bash 執行以下 Node.js 腳本，將圖表渲染成終端 ASCII 藝術：

```bash
node -e "
import { renderMermaidAscii } from '/Users/a17/ForSkillsProject/beautiful-mermaid/dist/index.js';
const diagram = \`<MERMAID_SYNTAX_HERE>\`;
console.log(renderMermaidAscii(diagram, { useAscii: false }));
"
```

- 使用 `useAscii: false` 產生 Unicode box-drawing（較美觀，預設）。
- 使用 `useAscii: true` 產生純 ASCII（相容模式）。

### Step 3: 渲染為 SVG（使用者明確要求時）

若使用者明確要求輸出 SVG 檔案，執行：

```bash
node -e "
import { renderMermaid, THEMES } from '/Users/a17/ForSkillsProject/beautiful-mermaid/dist/index.js';
const diagram = \`<MERMAID_SYNTAX_HERE>\`;
const svg = await renderMermaid(diagram, THEMES['tokyo-night']);
process.stdout.write(svg);
" > output.svg
```

可用主題：`zinc-light`、`zinc-dark`、`tokyo-night`、`tokyo-night-storm`、`tokyo-night-light`、`catppuccin-mocha`、`catppuccin-latte`、`nord`、`nord-light`、`dracula`、`github-light`、`github-dark`、`solarized-light`、`solarized-dark`、`one-dark`。

## 支援的圖表類型

| 類型 | Header 關鍵字 |
|------|---------------|
| 流程圖 | `graph TD`、`graph LR`、`flowchart TD`、`flowchart LR` |
| 狀態圖 | `stateDiagram-v2` |
| 序列圖 | `sequenceDiagram` |
| 類別圖 | `classDiagram` |
| ER 圖 | `erDiagram` |

## Mermaid 語法速查

### 流程圖
```
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[End]
```

### 序列圖
```
sequenceDiagram
    participant A as Client
    participant B as Server
    A->>B: Request
    B-->>A: Response
```

### 類別圖
```
classDiagram
    class Animal {
        +String name
        +makeSound()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

### ER 圖
```
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
```

### 狀態圖
```
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Done : finish
    Done --> [*]
```

## 已知限制（beautiful-mermaid）

### 1. 節點標籤內絕對不要用雙引號

beautiful-mermaid 不會剝離 Mermaid 語法中 `["..."]` 的雙引號，會把引號作為文字內容渲染到 SVG/ASCII 輸出中。

```
# 錯誤 — SVG 會顯示 "App Store"（含引號）
A["App Store"]

# 正確 — SVG 會顯示 App Store（無引號）
A[App Store]
```

即使文字包含 `/`、`:`、`,`、`→`、空格等特殊字元，也**不需要**引號包裹，直接寫即可。

### 2. `<br/>` 換行標籤不被支援

beautiful-mermaid 不處理 HTML 標籤，`<br/>` 會被轉義為字面文字 `<br/>`。
長文字請用 ` - ` 或 ` / ` 分隔，保持單行。

```
# 錯誤 — 會顯示字面 <br/>
A["Line1<br/>Line2"]

# 正確 — 用分隔符號替代換行
A[Line1 - Line2]
```

## Rules

1. 一律直接在對話中顯示渲染後的 ASCII 輸出。
2. 若渲染失敗，改用 fenced code block 顯示 Mermaid 原始碼。
3. 輸出 SVG 時，存成檔案並告知用戶檔案路徑。
4. 除非用戶要求 ASCII，否則優先使用 Unicode box-drawing。
5. 若用戶提供自然語言描述，先展示產生的 Mermaid 語法，再渲染。
6. **節點標籤 `[]`、`{}`、`()` 內絕對不要用雙引號 `"`**——會在輸出中顯示為字面引號。
7. **絕對不要用 `<br/>` 換行**——改用 ` - ` 或 ` / ` 分隔符。

## 驗證項目

- **產出形式**：SVG 檔（文件用）或 terminal ASCII art（CLI 回報用）。
- **機械檢查**：SVG 產出後跑 `xmllint --noout <file.svg>` 確認 well-formed XML。
- **架構變更整合**：每次更動 module 依賴 / data flow 時，若專案有對應圖表檔案，需同步更新。
- **交接 marker**：純文件產出 → `[HANDOFF: main]`。
