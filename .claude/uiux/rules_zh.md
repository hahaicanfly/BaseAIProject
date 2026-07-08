# UI/UX 設計規則

> **本規則為強制性指引，所有 UI 實作必須遵守。**
>
> 適用技術棧：React/Tailwind、Compose Multiplatform、SwiftUI、Vue 等

---

## 1. 風格與一致性

### 1.1 Design Tokens 強制使用

```
// ✅ 正確：使用 Design Token
color: var(--color-primary)
padding: spacing.md  // 16px

// ❌ 錯誤：硬編碼數值
color: #6750A4
padding: 16px  // 直接寫數字
```

**規則**：
- 顏色：只使用 Design Token 或 Theme 定義的色彩
- 字體：只使用 Typography 系統定義的樣式
- 間距：只使用 Spacing Scale（4px / 8px 倍數）
- 圓角：只使用 Shape Token

### 1.2 元件一致性

| 元件類型 | 要求 |
|---------|-----|
| 按鈕 | 統一使用設計系統 Button 元件 |
| 卡片 | 統一圓角、陰影規範 |
| 輸入框 | 統一樣式，包含 label 和 error state |
| 圖示 | 只用一套圖示庫 |

### 1.3 禁止 Random Styling

```
// ❌ 禁止：隨機顏色、隨機圓角
border-radius: 13px  // 為什麼是 13？
color: #ABCDEF  // 沒有意義的顏色

// ✅ 正確：使用語義化 Token
border-radius: var(--radius-card)
color: var(--color-primary)
```

---

## 2. 排版與留白

### 2.1 Grid 系統

遵循 8px Grid（4px 微調）：
- 邊距：`16px`（Spacing.md）
- 卡片間距：`12px`
- 區塊間距：`24px`（Spacing.lg）

### 2.2 Spacing Scale（強制）

| Token | 值 | 用途 |
|-------|-----|-----|
| `spacing.xs` | 4px | 元素內部微間距 |
| `spacing.sm` | 8px | 相關元素間距 |
| `spacing.md` | 16px | 區塊內間距、標準 padding |
| `spacing.lg` | 24px | 區塊間距 |
| `spacing.xl` | 32px | 主要區塊分隔 |
| `spacing.xxl` | 48px | 頁面區段分隔 |

### 2.3 文字階層

標題層級（不可跳級）：
- Display / Hero 標題
- 頁面標題 (H1)
- 區段標題 (H2)
- 子區段 (H3)
- 卡片標題
- 主要內文
- 次要內文
- 輔助說明

**規則**：
- 每個層級大小差距至少 2-4px
- 行高：body 1.5-1.75，heading 1.2-1.3
- 每行最多 65-75 字元（中文 35-40 字）

---

## 3. 互動細節

### 3.1 狀態完整性（必須實作所有狀態）

| 狀態 | 視覺變化 | 實作要求 |
|-----|---------|---------|
| **Default** | 基準樣式 | 必須定義 |
| **Hover** | 背景淺色、微微放大 | 桌面端 |
| **Focus** | 可見的 focus ring (2px) | 鍵盤 accessible |
| **Active/Pressed** | 深色背景、scale 0.98 | 點擊中 |
| **Disabled** | 50% opacity、無互動 | enabled = false |
| **Loading** | 內容替換為 spinner | 禁用互動 |

### 3.2 Loading 狀態

```
// ✅ 正確：Skeleton + 禁用操作
switch (state) {
  case 'loading': return <SkeletonList />  // 骨架屏
  case 'success': return <List items={data} />
  case 'error': return <ErrorState onRetry={retry} />
}

// ❌ 錯誤：只有 spinner，沒有佈局預告
<Spinner />  // 不知道會載入什麼
```

### 3.3 Empty State（必須設計）

每個列表/資料區都必須有 Empty State：
- 圖示（必須）
- 標題（必須）
- 說明（必須）
- CTA（可選）

---

## 4. 可用性與 a11y（無障礙）

### 4.1 鍵盤可操作（強制）

- 所有互動元素必須可 focus
- Tab 順序符合視覺順序
- Enter/Space 可觸發主要操作

### 4.2 對比度（WCAG AA）

| 元素 | 最低對比度 |
|-----|-----------|
| 普通文字 (< 18px) | 4.5:1 |
| 大文字 (>= 18px bold 或 24px) | 3:1 |
| 圖示、UI 元素 | 3:1 |

### 4.3 Aria / Label（強制）

```html
<!-- 所有圖示按鈕必須有 aria-label -->
<button aria-label="關閉">
  <CloseIcon />
</button>

<!-- 圖片必須有 alt -->
<img src="photo.jpg" alt="範例照片" />

<!-- 表單欄位必須關聯 label -->
<label for="email">電子郵件</label>
<input id="email" type="email" />
```

### 4.4 觸控目標

最小觸控區域 44-48px × 44-48px

---

## 5. 效能與視覺穩定

### 5.1 避免 CLS（Cumulative Layout Shift）

```
// ✅ 正確：預留空間
<div style="aspect-ratio: 16/9">
  <img src={imageUrl} />
</div>

// ❌ 錯誤：高度不確定
<img src={imageUrl} style="width: 100%" />
// 載入後高度變化 → CLS
```

### 5.2 動畫效能

```
// ✅ 使用 transform/opacity（GPU 加速）
transition: transform 300ms, opacity 300ms

// ❌ 避免動畫 width/height/padding（觸發 layout）
transition: width 300ms  // 效能差
```

### 5.3 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 6. 檢查清單

### 實作前檢查
- [ ] 是否已定義 Design Tokens？
- [ ] 是否使用專案統一的 Spacing Scale？
- [ ] 是否規劃了所有狀態（loading/empty/error）？

### 實作中檢查
- [ ] 顏色是否來自 Token？
- [ ] 間距是否使用 Token？
- [ ] 互動元素是否有 hover/focus/active/disabled？
- [ ] 圖示按鈕是否有 aria-label / contentDescription？

### 實作後檢查
- [ ] 對比度是否符合 4.5:1？
- [ ] 鍵盤是否可完整操作？
- [ ] 圖片是否有預留空間？
- [ ] 動畫是否尊重 reduced motion？

---

## 7. 違規處理

| 違規類型 | 嚴重程度 | 處理方式 |
|---------|---------|---------|
| 硬編碼顏色/間距 | 中 | Code Review 退回 |
| 缺少 aria-label / contentDescription | 高 | 強制修復 |
| 對比度不足 | 高 | 強制修復 |
| 缺少 Loading/Empty State | 中 | 補充實作 |
| CLS 問題 | 中 | 效能修復 |

---

*最後更新：2026-01-27*
*適用技術棧：React/Tailwind, Compose Multiplatform, SwiftUI, Vue*
