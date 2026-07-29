# ui-ux-pro-max — search.py CLI 指南

> `.claude/skills/ui-ux-pro-max/SKILL_zh.md` 的參考檔。操作 BM25 搜尋工具的全部說明：前置需求、四步驟流程、domain 與 stack 對照表、輸出格式、完整範例。

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
