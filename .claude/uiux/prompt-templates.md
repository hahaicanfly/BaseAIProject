# UI/UX Prompt Templates

> **六份可直接複製使用的 Prompts，配合三階段流程（草圖 → 評審 → 實作）。**
>
> 每份 prompt 都包含「輸入區塊」和「輸出格式」說明。

---

## Prompt 1：Wireframe 草圖生成

> **用途**：從需求產生 Layout 草圖，只關注資訊架構，禁止寫最終樣式。
>
> **階段**：Phase 1 - 草圖

### Prompt

```markdown
# 角色
你是一位 UI/UX 設計師，專長是資訊架構與 Layout 設計。

# 任務
根據以下需求，產生「純 Layout 草圖」。

## 輸入

### 畫面名稱
[填入畫面名稱，例如：ProductListScreen]

### 使用者目標
[填入使用者想達成什麼]

### 核心操作
[填入 1-3 個主要操作]

### 資料內容
[填入這個畫面會顯示什麼資料]

### 限制條件
[填入任何技術或設計限制]

## 輸出格式要求

### 1. ASCII Wireframe
用純文字畫出區塊結構，標註每個區塊的用途。

### 2. 區塊說明表
列出每個區塊的：內容、高度/比例、是否固定。

### 3. 資訊層級
說明資訊的優先順序：Primary > Secondary > Tertiary。

### 4. 初步元件清單
列出需要的元件類型（不含樣式）。

## 禁止事項
- ❌ 禁止定義顏色、字體大小、圓角等視覺細節
- ❌ 禁止寫任何程式碼
- ❌ 禁止討論動畫效果
- ❌ 禁止選擇配色方案

開始生成草圖。
```

---

## Prompt 2：設計評審（挑毛病）

> **用途**：讓 Claude 用設計師視角評審草圖/設計，找出問題並提出替代方案。
>
> **階段**：Phase 2 - 評審

### Prompt

```markdown
# 角色
你是一位資深 UI/UX 設計評審，擅長識別「AI 味」和「模板感」的設計問題。

# 任務
審查以下設計草圖/實作，指出問題並提出替代方案。

## 輸入

### 設計草圖/截圖
[貼入 ASCII Wireframe 或描述現有設計]

### 設計目標
[這個設計要達成什麼目標]

### 目標用戶
[描述目標用戶特徵]

### 品牌調性
[填入品牌風格關鍵詞，例如：現代、友善、專業、活潑]

## 評審要求

### 1. AI 味檢測
找出任何讓設計看起來像「AI 生成」或「模板」的元素

### 2. 可用性問題
- 資訊層級是否清晰？
- 觸控目標是否足夠？
- 認知負擔是否過重？

### 3. 遺漏狀態
- 是否缺少 Loading state？
- 是否缺少 Empty state？
- 是否缺少 Error state？

## 輸出格式要求

### 問題清單
| 問題 | 嚴重度 | 位置 | 說明 |
|-----|-------|------|------|
| | High/Med/Low | | |

### 3 個替代方向
提出 3 個不同的改進方向，每個包含：
- **方向名稱**
- **核心改變**
- **預期效果**
- **風險/取捨**

### 建議採用
說明你推薦哪個方向，以及原因。
```

---

## Prompt 3：UI 實作

> **用途**：把已核准草圖 + Style Spec 轉成可執行的 UI 程式碼。
>
> **階段**：Phase 3 - 實作

### Prompt

```markdown
# 角色
你是一位前端工程師，專精 [填入技術棧: React/Tailwind / Compose Multiplatform / SwiftUI / Vue]。

# 任務
根據已核准的草圖和 Style Spec，實作完整的 UI 程式碼。

## 輸入

### 核准的草圖
[貼入 ASCII Wireframe]

### Style Spec
[貼入或引用 style-spec.template.md 的內容]

### 技術棧
[React + Tailwind / Compose Multiplatform (Kotlin) / SwiftUI / Vue + Tailwind]

### Design Token 來源
[引用專案的 Design Token 檔案路徑]

## 實作要求

### 1. 狀態完整性
必須實作所有互動狀態：
- [ ] Default
- [ ] Hover (desktop)
- [ ] Focus (keyboard)
- [ ] Pressed/Active
- [ ] Disabled
- [ ] Loading

### 2. 無障礙（a11y）
- [ ] 所有圖示有 aria-label / contentDescription
- [ ] 對比度 >= 4.5:1
- [ ] 觸控目標 >= 44-48px
- [ ] 鍵盤可完整操作
- [ ] 尊重 prefers-reduced-motion

### 3. 響應式
- [ ] Mobile (< 640px)
- [ ] Tablet (640-1024px)
- [ ] Desktop (> 1024px)

### 4. Edge Cases
- [ ] Empty state
- [ ] Error state
- [ ] Loading state（Skeleton）
- [ ] 長文字處理

## 禁止事項
- ❌ 禁止使用硬編碼顏色/間距
- ❌ 禁止省略任何狀態
- ❌ 禁止忽略 a11y
- ❌ 禁止添加未被要求的功能
```

---

## Prompt 4：Design Token 萃取

> **用途**：從參考網站/截圖萃取 Design Tokens。
>
> **階段**：任何階段（設計研究）

### Prompt

```markdown
# 角色
你是一位設計系統專家，擅長分析視覺設計並萃取可複用的 Design Tokens。

# 任務
分析以下參考資料，萃取 Design Tokens。

## 輸入

### 參考來源
[貼入以下任一種]
- 網站 URL
- 截圖描述
- Figma/設計稿連結

### 萃取重點
- [ ] 顏色系統
- [ ] 字體系統
- [ ] 間距系統
- [ ] 圓角/形狀
- [ ] 陰影/深度
- [ ] 動畫時間

### 目標技術棧
[CSS Variables / Tailwind / Compose / SwiftUI]

## 輸出格式要求

### 1. 顏色 Token
```css
:root {
  --color-primary: #______;
  --color-secondary: #______;
  --color-background: #______;
  --color-surface: #______;
  --color-error: #______;
}
```

### 2. 字體 Token
字體大小、行高、字重的完整定義。

### 3. 間距 Token
xs / sm / md / lg / xl / xxl 的完整定義。

### 4. 應用範例
展示這些 Token 如何應用在實際元件上。
```

---

## Prompt 5：Microcopy 生成

> **用途**：生成一致語氣的介面文案（按鈕、錯誤訊息、空狀態）。
>
> **階段**：任何階段

### Prompt

```markdown
# 角色
你是一位 UX Writer，專精介面文案與微文案設計。

# 任務
為以下介面元素撰寫文案，確保語氣一致。

## 輸入

### 品牌語氣
[描述品牌說話的方式，例如：友善、專業、活潑、簡潔]

### 目標用戶
[描述用戶背景]

### 需要文案的元素
[列出按鈕、錯誤訊息、空狀態、確認對話框等]

### 語言
[繁體中文 / 英文 / 雙語]

## 輸出格式

### 按鈕文案
| 動作 | 文案 | 替代方案 |
|-----|------|---------|

### 錯誤訊息
| 錯誤類型 | 標題 | 說明 | 操作 |
|---------|------|------|------|

### 空狀態
| 場景 | 標題 | 說明 | CTA |
|-----|------|------|-----|
```

---

## Prompt 6：UI Polish（微調）

> **用途**：優化動畫、hover/focus、間距，禁止大改資訊架構。
>
> **階段**：Phase 3 後（精修）

### Prompt

```markdown
# 角色
你是一位注重細節的 UI 工程師，專精動畫與互動細節。

# 任務
對以下 UI 進行 Polish（精修），提升視覺質感和互動體驗。

## 輸入

### 現有程式碼
[貼入需要 Polish 的元件程式碼]

### Polish 範圍
- [ ] 動畫 / Transition
- [ ] Hover 效果
- [ ] Focus 效果
- [ ] 間距微調
- [ ] Loading 動畫

### 目標感受
[描述優化後想達成的感覺：更流暢、更精緻、更有活力]

## 限制條件

### ❌ 禁止事項
- 禁止改變資訊架構（區塊順序、內容結構）
- 禁止新增/刪除功能
- 禁止改變元件 API

### ✅ 允許事項
- 添加/調整動畫（150-300ms）
- 調整 hover/focus/active 狀態
- 微調間距（±4px 以內）
- 添加 Skeleton Loading

## 輸出

1. 變更清單（原本 vs 修改後）
2. 程式碼 Diff
3. 效能說明（是否使用 GPU 加速屬性）
4. Reduced Motion 處理
```

---

## 使用建議

### 流程對應

| 階段 | 使用的 Prompt |
|-----|--------------|
| Phase 1: 草圖 | Prompt 1（Wireframe） |
| Phase 2: 評審 | Prompt 2（設計評審） |
| Phase 3: 實作 | Prompt 3（UI 實作） |
| 精修 | Prompt 6（UI Polish） |
| 研究 | Prompt 4（Token 萃取） |
| 任何階段 | Prompt 5（Microcopy） |

---

*最後更新：2026-01-27*
