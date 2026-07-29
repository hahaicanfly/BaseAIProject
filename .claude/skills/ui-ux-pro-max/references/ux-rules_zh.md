# ui-ux-pro-max — UX 規則目錄

> `.claude/skills/ui-ux-pro-max/SKILL_zh.md` 的參考檔。以下優先序即設計審查應由上而下遵循的順序。

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
