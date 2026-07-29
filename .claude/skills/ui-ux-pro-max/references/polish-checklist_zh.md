# ui-ux-pro-max — 精修規則與交付前檢查表

> `.claude/skills/ui-ux-pro-max/SKILL_zh.md` 的參考檔。交付任何 UI 代碼前先跑一次檢查表。

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
