# Style Spec Template

> **每個畫面實作前必須填寫此規格，經 UIUX Agent 評審後才可進入實作。**
>
> 複製此模板，填入具體內容，存為 `design-system/pages/{screen-name}.md`

---

## Screen: [畫面名稱]

### 基本資訊

| 項目 | 內容 |
|-----|------|
| **Screen ID** | `screen_xxx` |
| **所屬流程** | 例：主流程 |
| **前置畫面** | 例：HomeScreen |
| **後續畫面** | 例：DetailScreen |
| **設計師** | @uiux-agent |
| **開發者** | 待指派 |
| **狀態** | 草圖 / 評審中 / 核准 / 實作中 / 完成 |

---

## 1. 使用者目標

### 主要目標
用戶來到這個畫面想要達成什麼？
- [ ] 目標 1：_______
- [ ] 目標 2：_______

### 核心操作（Primary Action）
用戶最可能/最應該執行的操作是什麼？

| 操作 | 優先級 | 觸發方式 |
|-----|-------|---------|
| ______ | Primary | 按鈕 / 滑動 / 點擊 |
| ______ | Secondary | |
| ______ | Tertiary | |

### 成功指標
- 用戶在 ___ 秒內完成 ___
- 錯誤率低於 ___%
- 放棄率低於 ___%

---

## 2. Layout（區塊結構）

### 視覺結構圖（ASCII Wireframe）

```
┌─────────────────────────────────┐
│        [Top App Bar]            │  ← 固定 / 滾動
├─────────────────────────────────┤
│                                 │
│        [Hero / Header]          │  ← 區塊 A
│                                 │
├─────────────────────────────────┤
│                                 │
│        [Main Content]           │  ← 區塊 B（可滾動）
│                                 │
│                                 │
├─────────────────────────────────┤
│        [Bottom Action]          │  ← 固定底部
└─────────────────────────────────┘
```

### 區塊定義

| 區塊 | 內容 | 高度/比例 | 是否固定 |
|-----|------|---------|---------|
| Top App Bar | 標題、返回、操作 | 56px / 64px | 固定 |
| Hero | | | |
| Main Content | | flex | 可滾動 |
| Bottom Action | | 80px | 固定 |

---

## 3. Components（元件清單）

### 元件列表

| 元件 | 類型 | 狀態 | Props / 參數 |
|-----|-----|-----|-------------|
| `TopAppBar` | 導航 | default, scrolled | title, onBack, actions |
| `ItemCard` | 卡片 | default, selected, disabled, loading | item, onSelect |
| `PrimaryButton` | 按鈕 | default, hover, pressed, disabled, loading | label, onClick, enabled |
| | | | |

### 各元件狀態詳述

#### 元件：`[元件名稱]`

| 狀態 | 視覺表現 | 觸發條件 |
|-----|---------|---------|
| Default | 基準樣式 | 初始 |
| Hover | 背景輕微變色 | 滑鼠移入 |
| Pressed | scale 0.98, 背景變深 | 點擊中 |
| Selected | 邊框高亮, 背景變色 | 選中後 |
| Disabled | opacity 0.5, 無互動 | enabled=false |
| Loading | 內容替換為 spinner | isLoading=true |

---

## 4. Design Tokens

### 顏色

| Token | 色碼 | 用途 |
|-------|------|-----|
| `background` | #FFFBF5 | 頁面背景 |
| `surface` | #FFFFFF | 卡片背景 |
| `primary` | #_______ | 主要操作、強調 |
| `secondary` | #_______ | 次要操作 |
| `onSurface` | #1C1B1F | 主要文字 |
| `error` | #B3261E | 錯誤狀態 |

### 字體

| Token | 大小 | 行高 | 字重 | 用途 |
|-------|------|------|------|-----|
| `headlineLarge` | 32px | 40px | Bold | 頁面標題 |
| `titleLarge` | 22px | 28px | SemiBold | 區段標題 |
| `titleMedium` | 16px | 24px | Medium | 卡片標題 |
| `bodyLarge` | 16px | 24px | Regular | 主要內文 |
| `bodyMedium` | 14px | 20px | Regular | 次要內文 |
| `labelSmall` | 11px | 16px | Medium | 標籤、輔助 |

### 間距

| Token | 值 | 用途 |
|-------|-----|-----|
| `xs` | 4px | 元素內微間距 |
| `sm` | 8px | 相關元素間 |
| `md` | 16px | 標準 padding |
| `lg` | 24px | 區塊間距 |
| `xl` | 32px | 主區塊分隔 |
| `xxl` | 48px | 頁面區段 |

### 圓角（Radius）

| Token | 值 | 用途 |
|-------|-----|-----|
| `sm` | 8px | 小元件（tag, chip） |
| `md` | 12px | 按鈕 |
| `lg` | 16px | 卡片 |
| `xl` | 24px | 大型容器 |
| `full` | 50% | 圓形 |

---

## 5. Edge Cases

### 空狀態（Empty State）

**觸發條件**：______

**視覺呈現**：
```
┌─────────────────────────────────┐
│                                 │
│         [插圖/圖示]              │
│                                 │
│      [標題：提示訊息]            │
│      [說明：引導文字]            │
│                                 │
│       [ CTA 按鈕 ]              │
│                                 │
└─────────────────────────────────┘
```

---

### 錯誤狀態（Error State）

**類型 1：網路錯誤**
- 標題：______
- 說明：______
- 操作：重試 / 離線模式

**類型 2：API 錯誤**
- 標題：______
- 說明：______
- 操作：重試 / 回報問題

**類型 3：驗證錯誤**
- 顯示位置：欄位下方
- 文案樣式：error 色、小字

---

### 長文字處理

| 元素 | 策略 | 最大行數 |
|-----|------|---------|
| 標題 | 截斷 + ellipsis | 2 行 |
| 描述 | 截斷 + ellipsis | 3 行 |
| 價格/數字 | 不截斷，縮小字體 | 1 行 |

---

## 6. Acceptance Criteria（驗收項）

### 功能驗收

- [ ] Primary action 可正常執行
- [ ] 所有互動元件有正確的狀態回饋
- [ ] Loading state 正確顯示
- [ ] Error state 有重試機制
- [ ] Empty state 有引導 CTA

### 視覺驗收

- [ ] 顏色來自 Design Token
- [ ] 間距符合 Spacing Scale
- [ ] 字體符合 Typography 層級

### 可用性驗收

- [ ] 對比度 >= 4.5:1
- [ ] 觸控目標 >= 44-48px
- [ ] 鍵盤可完整操作
- [ ] 所有圖示有 aria-label / contentDescription

---

## 簽核

| 角色 | 姓名/代號 | 日期 | 狀態 |
|-----|----------|------|------|
| UIUX Agent | @uiux-agent | | 草圖 / 評審中 / 核准 |
| 開發者 | | | 待實作 / 實作中 / 完成 |
| 驗收者 | | | 待驗收 / 通過 / 退回 |

---

*模板版本：v1.0*
*最後更新：2026-01-27*
