---
name: ui-ux-pro-max
description: 產出完整設計系統，涵蓋色彩調色盤、字體配對、UI 風格與 UX 準則，支援多種前端技術棧；當使用者要規劃、設計或檢視 UI/UX 時觸發。
---

# UI/UX Pro Max - Design Intelligence

Comprehensive design guide for web and mobile applications. 內含 50+ UI 風格、97 組色彩調色盤、57 組字體配對、99 條 UX 準則、25 種圖表類型，涵蓋 9+ 種前端技術棧。以 BM25 搜尋引擎查詢，依優先級回傳建議。

## When to Apply

在以下情境參考本 skill：
- 設計新的 UI 元件或頁面
- 選擇色彩調色盤與字體
- 審查代碼中的 UX 問題
- 建立 landing page 或 dashboard
- 落實無障礙（accessibility）需求

## Rule Categories by Priority

| Priority | Category | Impact | Domain |
|----------|----------|--------|--------|
| 1 | Accessibility | CRITICAL | `ux` |
| 2 | Touch & Interaction | CRITICAL | `ux` |
| 3 | Performance | HIGH | `ux` |
| 4 | Layout & Responsive | HIGH | `ux` |
| 5 | Typography & Color | MEDIUM | `typography`, `color` |
| 6 | Animation | MEDIUM | `ux` |
| 7 | Style Selection | MEDIUM | `style`, `product` |
| 8 | Charts & Data | LOW | `chart` |

## Quick Reference

### 1. Accessibility (CRITICAL)

- `color-contrast` - 一般文字最低 4.5:1 對比度
- `focus-states` - 互動元素要有清楚的 focus ring
- `alt-text` - 有意義的圖片要有描述性 alt text
- `aria-labels` - 純圖示按鈕要有 aria-label
- `keyboard-nav` - Tab 順序需符合視覺順序
- `form-labels` - 表單欄位使用 label 搭配 for attribute

### 2. Touch & Interaction (CRITICAL)

- `touch-target-size` - 最小 44x44px 觸控區域
- `hover-vs-tap` - 主要互動使用 click/tap，不依賴 hover
- `loading-buttons` - 非同步操作進行中要停用按鈕
- `error-feedback` - 錯誤訊息要出現在問題附近
- `cursor-pointer` - 可點擊元素加上 cursor-pointer

### 3. Performance (HIGH)

- `image-optimization` - 使用 WebP、srcset、lazy loading
- `reduced-motion` - 檢查 prefers-reduced-motion
- `content-jumping` - 非同步內容預留版面空間

### 4. Layout & Responsive (HIGH)

- `viewport-meta` - width=device-width initial-scale=1
- `readable-font-size` - 手機版內文最小 16px
- `horizontal-scroll` - 確保內容不超出 viewport 寬度
- `z-index-management` - 定義 z-index 分層（10, 20, 30, 50）

### 5. Typography & Color (MEDIUM)

- `line-height` - 內文使用 1.5-1.75 行高
- `line-length` - 每行限制在 65-75 字元
- `font-pairing` - 標題/內文字體個性要搭配

### 6. Animation (MEDIUM)

- `duration-timing` - 微互動使用 150-300ms
- `transform-performance` - 使用 transform/opacity，避免 width/height 動畫
- `loading-states` - Skeleton 畫面或 spinner

### 7. Style Selection (MEDIUM)

- `style-match` - 風格要match產品類型
- `consistency` - 全站使用一致風格
- `no-emoji-icons` - 使用 SVG icon，不要用 emoji

### 8. Charts & Data (LOW)

- `chart-type` - 圖表類型要match資料類型
- `color-guidance` - 使用無障礙色彩調色盤
- `data-table` - 提供表格版本以利無障礙存取

## How to Use

用下方 CLI 工具搜尋特定 domain。

---

## Prerequisites

檢查 Python 是否已安裝：

```bash
python3 --version || python --version
```

若尚未安裝，依作業系統安裝：

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install python3
```

**Windows:**
```powershell
winget install Python.Python.3.12
```

---

## How to Use This Skill

當使用者提出 UI/UX 需求（設計、建置、實作、審查、修復、優化），依以下流程執行：

### Step 1: Analyze User Requirements

從使用者請求提取關鍵資訊：
- **產品類型**：SaaS、電商、作品集、dashboard、landing page 等
- **風格關鍵字**：minimal、playful、professional、elegant、dark mode 等
- **產業別**：healthcare、fintech、gaming、education 等
- **技術棧**：React、Vue、Next.js，若未指定則預設 `html-tailwind`

### Step 2: Generate Design System (REQUIRED)

**永遠先跑 `--design-system`** 取得完整建議與理由：

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

此指令會：
1. 並行搜尋 5 個 domain（product, style, color, landing, typography）
2. 套用 `ui-reasoning.csv` 的推理規則選出最佳匹配
3. 回傳完整設計系統：pattern、style、colors、typography、effects
4. 附上應避免的 anti-patterns

**範例：**
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### Step 2b: Persist Design System (Master + Overrides Pattern)

要跨 session 保存設計系統供分層檢索，加上 `--persist`：

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

會產生：
- `design-system/MASTER.md` — 全域設計規則 Source of Truth
- `design-system/pages/` — 頁面級 override 資料夾

**搭配頁面級 override：**
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

同時會產生：
- `design-system/pages/dashboard.md` — 該頁面相對於 Master 的差異規則

**分層檢索運作方式：**
1. 建置特定頁面（例如「Checkout」）時，先檢查 `design-system/pages/checkout.md`
2. 若該頁面檔存在，其規則**覆蓋** Master 檔
3. 若不存在，僅使用 `design-system/MASTER.md`

**context-aware 檢索 prompt：**
```
I am building the [Page Name] page. Please read design-system/MASTER.md.
Also check if design-system/pages/[page-name].md exists.
If the page file exists, prioritize its rules.
If not, use the Master rules exclusively.
Now, generate the code...
```

### Step 3: Supplement with Detailed Searches (as needed)

取得設計系統後，用 domain 搜尋補充細節：

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**何時需要細部搜尋：**

| Need | Domain | Example |
|------|--------|---------|
| 更多風格選項 | `style` | `--domain style "glassmorphism dark"` |
| 圖表建議 | `chart` | `--domain chart "real-time dashboard"` |
| UX 最佳實踐 | `ux` | `--domain ux "animation accessibility"` |
| 替代字體 | `typography` | `--domain typography "elegant luxury"` |
| Landing 結構 | `landing` | `--domain landing "hero social-proof"` |

### Step 4: Stack Guidelines (Default: html-tailwind)

取得實作層級的最佳實踐。若使用者未指定技術棧，**預設 `html-tailwind`**。

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
```

可用技術棧：`html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`（`data/stacks/` 另含 `astro`, `nuxtjs`, `nuxt-ui`）

---

## Search Reference

### Available Domains

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | 產品類型建議 | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style` | UI 風格、配色、效果 | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | 字體配對、Google Fonts | elegant, playful, professional, modern |
| `color` | 依產品類型的色彩調色盤 | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | 頁面結構、CTA 策略 | hero, hero-centric, testimonial, pricing, social-proof |
| `chart` | 圖表類型、函式庫建議 | trend, comparison, timeline, funnel, pie |
| `ux` | 最佳實踐、anti-patterns | animation, accessibility, z-index, loading |
| `react` | React/Next.js 效能 | waterfall, bundle, suspense, memo, rerender, cache |
| `web` | Web 介面準則 | aria, focus, keyboard, semantic, virtualize |
| `prompt` | AI prompt、CSS 關鍵字 | (style name) |

### Available Stacks

| Stack | Focus |
|-------|-------|
| `html-tailwind` | Tailwind utilities、responsive、a11y（預設） |
| `react` | State、hooks、效能、pattern |
| `nextjs` | SSR、routing、images、API routes |
| `vue` | Composition API、Pinia、Vue Router |
| `svelte` | Runes、stores、SvelteKit |
| `swiftui` | Views、State、Navigation、Animation |
| `react-native` | Components、Navigation、Lists |
| `flutter` | Widgets、State、Layout、Theming |
| `shadcn` | shadcn/ui components、theming、forms、patterns |
| `jetpack-compose` | Composables、Modifiers、State Hoisting、Recomposition |

---

## Example Workflow

**使用者請求：**「做一個給皮膚護理服務的 landing page」

### Step 1: Analyze Requirements
- 產品類型：Beauty/Spa service
- 風格關鍵字：elegant, professional, soft
- 產業別：Beauty/Wellness
- 技術棧：html-tailwind（預設）

### Step 2: Generate Design System (REQUIRED)

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service elegant" --design-system -p "Serenity Spa"
```

**輸出：** 完整設計系統，含 pattern、style、colors、typography、effects、anti-patterns。

### Step 3: Supplement with Detailed Searches (as needed)

```bash
# 取得動效與無障礙的 UX 準則
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# 取得替代字體選項
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "elegant luxury serif" --domain typography
```

### Step 4: Stack Guidelines

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "layout responsive form" --stack html-tailwind
```

**接著：** 整合設計系統 + 細部搜尋結果，實作設計。

---

## Output Formats

`--design-system` flag 支援兩種輸出格式：

```bash
# ASCII box（預設）— 適合終端機顯示
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system

# Markdown — 適合寫入文件
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system -f markdown
```

---

## Tips for Better Results

1. **關鍵字要具體** - 「healthcare SaaS dashboard」優於「app」
2. **多搜幾次** - 不同關鍵字會揭露不同洞見
3. **組合多個 domain** - Style + Typography + Color = 完整設計系統
4. **一定要檢查 UX** - 搜尋「animation」「z-index」「accessibility」找出常見問題
5. **使用 stack flag** - 取得實作層級的最佳實踐
6. **反覆迭代** - 第一次搜尋沒match就換關鍵字

---

## Common Rules for Professional UI

以下是常被忽略、卻讓 UI 看起來不夠專業的細節：

### Icons & Visual Elements

| Rule | Do | Don't |
|------|----|----- |
| **No emoji icons** | 用 SVG icon（Heroicons、Lucide、Simple Icons） | 用 🎨 🚀 ⚙️ 這類 emoji 當 UI icon |
| **Stable hover states** | hover 用 color/opacity transition | 用會位移版面的 scale transform |
| **Correct brand logos** | 從 Simple Icons 找官方 SVG | 猜測或用錯誤的 logo |
| **Consistent icon sizing** | 固定 viewBox（24x24）搭配 w-6 h-6 | 隨意混用不同尺寸的 icon |

### Interaction & Cursor

| Rule | Do | Don't |
|------|----|----- |
| **Cursor pointer** | 所有可點/可 hover 卡片加 `cursor-pointer` | 互動元素留預設游標 |
| **Hover feedback** | 提供視覺回饋（color, shadow, border） | 沒有任何互動提示 |
| **Smooth transitions** | 用 `transition-colors duration-200` | 狀態瞬間切換或過慢（>500ms） |

### Light/Dark Mode Contrast

| Rule | Do | Don't |
|------|----|----- |
| **Glass card light mode** | 用 `bg-white/80` 或更高透明度 | 用 `bg-white/10`（太透明） |
| **Text contrast light** | 內文用 `#0F172A`（slate-900） | 內文用 `#94A3B8`（slate-400） |
| **Muted text light** | 至少用 `#475569`（slate-600） | 用更淺的 gray-400 |
| **Border visibility** | light mode 用 `border-gray-200` | 用 `border-white/10`（看不見） |

### Layout & Spacing

| Rule | Do | Don't |
|------|----|----- |
| **Floating navbar** | 加上 `top-4 left-4 right-4` 間距 | navbar 貼齊 `top-0 left-0 right-0` |
| **Content padding** | 預留固定 navbar 的高度空間 | 內容被固定元素遮住 |
| **Consistent max-width** | 統一用 `max-w-6xl` 或 `max-w-7xl` | 混用不同容器寬度 |

---

## Pre-Delivery Checklist

交付 UI 代碼前，確認以下項目：

### Visual Quality
- [ ] 沒有用 emoji 當 icon（改用 SVG）
- [ ] 所有 icon 來自同一套 icon set（Heroicons/Lucide）
- [ ] 品牌 logo 正確（已從 Simple Icons 驗證）
- [ ] hover 狀態不會造成版面位移
- [ ] 直接用 theme color（bg-primary），不要多包一層 var()

### Interaction
- [ ] 所有可點擊元素都有 `cursor-pointer`
- [ ] hover 狀態提供清楚的視覺回饋
- [ ] transition 平滑（150-300ms）
- [ ] focus 狀態在鍵盤操作時可見

### Light/Dark Mode
- [ ] Light mode 文字對比足夠（至少 4.5:1）
- [ ] Glass/半透明元素在 light mode 下仍可視
- [ ] 邊框在兩種模式下都可見
- [ ] 交付前兩種模式都測過

### Layout
- [ ] 浮動元素與邊緣有適當間距
- [ ] 內容不會被固定 navbar 遮住
- [ ] 375px、768px、1024px、1440px 都 responsive
- [ ] 手機版無橫向捲動

### Accessibility
- [ ] 所有圖片有 alt text
- [ ] 表單輸入有 label
- [ ] 顏色不是唯一的資訊指示
- [ ] 尊重 `prefers-reduced-motion`

## 驗證項目

- **產出形式**：完整設計系統規範（含 palette / typography / spacing / component samples）。
- **整合 uiux-agent**：作為 Phase 1 草圖的設計依據，Phase 2 評審的標準（見 `.claude/agents/uiux-agent.md`）。
- **ExecPlan 整合**：UI 類 ExecPlan 的 Context 區塊引用本 spec 對應段落（格式見 `.claude/protocols/execplan-lifecycle.md`）。
- **與既有設計系統對齊**：若專案已有設計系統文件（如 `agent_docs/TECHNICAL-REFERENCE.md` 或專案自訂 design-system 文件），輸出不得與其衝突；沒有既有文件時，本次輸出即為起點。
- **交接 marker**：spec 完成後 `[HANDOFF: uiux-agent]` 進入三階段流程（`.claude/uiux/WORKFLOW.md`）。
