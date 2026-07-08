# UI/UX 三階段工作流程

> **強制規定：所有 UI 開發必須遵循「草圖 → 評審 → 實作」三階段流程。**
>
> **禁止一次跳到實作。每個階段必須獲得用戶「OK」才能進入下一階段。**

---

## 流程總覽

```
┌─────────────────────────────────────────────────────────────────┐
│                        UI/UX 開發流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Phase 1          Phase 2          Phase 3                     │
│   ┌──────┐        ┌──────┐        ┌──────┐                      │
│   │ 草圖  │───OK───│ 評審  │───OK───│ 實作  │                      │
│   │      │        │      │        │      │                      │
│   └──────┘        └──────┘        └──────┘                      │
│      │               │               │                           │
│      ▼               ▼               ▼                           │
│   Wireframe      Critique       Production                      │
│   Layout         3 Options      Code + States                   │
│   Structure      Selection      + a11y + Responsive             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1：草圖（Wireframe）

### 目標
確認資訊架構和佈局結構，**不涉及視覺細節**。

### 執行者
`@uiux-agent` 或 `/ui-ux-pro-max`

### 輸入
- 用戶需求描述
- 使用者目標
- 核心操作

### 輸出
1. **ASCII Wireframe**：區塊結構圖
2. **區塊說明**：每個區塊的用途
3. **資訊層級**：Primary > Secondary > Tertiary
4. **初步元件清單**

### 禁止事項
- ❌ 定義顏色、字體、圓角
- ❌ 寫任何程式碼
- ❌ 討論動畫效果
- ❌ 選擇配色方案

### 完成條件
用戶回覆「OK」或明確表示草圖通過。

### 使用的 Prompt
→ [Prompt 1：Wireframe 草圖生成](prompt-templates.md#prompt-1wireframe-草圖生成)

---

## Phase 2：評審（Critique）

### 目標
用設計師視角檢視草圖，找出問題並提出替代方案。

### 執行者
`@uiux-agent` 或 `/frontend-design`

### 輸入
- Phase 1 的草圖
- 品牌調性
- 目標用戶

### 輸出
1. **問題清單**：含嚴重度（High/Med/Low）
2. **AI 味檢測**：是否看起來像模板
3. **3 個替代方向**：每個方向包含核心改變、預期效果、風險
4. **建議採用**：推薦的方向

### 評審維度
- [ ] AI 味 / 模板感
- [ ] 資訊層級清晰度
- [ ] 觸控/互動可用性
- [ ] 元件一致性
- [ ] 遺漏狀態（Loading/Empty/Error）
- [ ] 極端情境處理

### 完成條件
1. 用戶選擇一個方向
2. 用戶回覆「OK」或要求調整
3. 調整後再次獲得「OK」

### 使用的 Prompt
→ [Prompt 2：設計評審](prompt-templates.md#prompt-2設計評審挑毛病)

---

## Phase 3：實作（Implementation）

### 目標
根據核准的草圖和 Style Spec，產生完整的 UI 程式碼。

### 執行者
開發 Agent 或開發者

### 輸入
- Phase 2 核准的草圖
- 填好的 [Style Spec](style-spec.template.md)
- 技術棧（React / SwiftUI / Compose / Vue 等）
- Design Token 來源

### 輸出
1. **完整元件程式碼**
2. **所有狀態**：Default, Hover, Focus, Pressed, Disabled, Loading
3. **a11y 支援**：aria-label / contentDescription, 對比度, 鍵盤操作
4. **響應式**：Mobile, Tablet, Desktop
5. **Edge Cases**：Empty, Error, 長文字, 極端資料

### 必須實作項目
| 類別 | 項目 | 必須 |
|-----|------|-----|
| 狀態 | Default | ✅ |
| 狀態 | Hover | ✅ |
| 狀態 | Focus | ✅ |
| 狀態 | Pressed | ✅ |
| 狀態 | Disabled | ✅ |
| 狀態 | Loading | ✅ |
| a11y | aria-label / contentDescription | ✅ |
| a11y | 對比度 4.5:1 | ✅ |
| a11y | 觸控 44-48dp/px | ✅ |
| a11y | 鍵盤操作 | ✅ |
| Edge | Empty State | ✅ |
| Edge | Error State | ✅ |
| Edge | 長文字 | ✅ |

### 完成條件
1. 程式碼通過驗收清單
2. 用戶測試確認

### 使用的 Prompt
→ [Prompt 3：UI 實作](prompt-templates.md#prompt-3ui-實作)

---

## 階段轉換規則

### 從 Phase 1 到 Phase 2

```
用戶: 請幫我設計一個新畫面...
Agent: [產生草圖]
Agent: 這是草圖，請確認資訊架構是否正確？
用戶: OK / 確認 / 可以
Agent: ✅ 草圖通過，現在進入評審階段...
```

**必要條件**：
- [ ] 草圖已完成
- [ ] 用戶明確回覆「OK」或等同意思

### 從 Phase 2 到 Phase 3

```
Agent: [提出 3 個替代方向]
Agent: 請選擇一個方向，或提出其他想法。
用戶: 選方向 B / 用第二個
Agent: ✅ 選擇方向 B，現在請填寫 Style Spec...
用戶: [填好 Style Spec] OK
Agent: ✅ 評審通過，現在進入實作階段...
```

**必要條件**：
- [ ] 問題清單已審視
- [ ] 用戶已選擇方向
- [ ] Style Spec 已填寫（或使用預設）
- [ ] 用戶明確回覆「OK」

---

## 快速指令

### 開始 UI 任務

```
@uiux-agent 請幫我設計 [畫面名稱]
```

Agent 會自動從 Phase 1 開始。

### 跳過評審（僅限緊急情況）

```
@uiux-agent 跳過評審，直接實作
```

⚠️ 這會產生警告，需要用戶再次確認。

---

## 常見問題

### Q: 可以跳過 Phase 1 直接畫高保真設計嗎？
**A**: 不可以。必須先確認資訊架構，避免後期大改。

### Q: 小改動也要走三階段嗎？
**A**: 如果只是微調（間距、顏色），可以直接用 [Prompt 6：UI Polish](prompt-templates.md#prompt-6ui-polish微調)。但如果涉及佈局改變，必須走三階段。

### Q: 評審可以自己做嗎？
**A**: 可以，但建議讓 `@uiux-agent` 用第三方視角評審，更容易發現盲點。

---

## 相關文件

- [UI/UX 規則](rules.md)
- [Style Spec 模板](style-spec.template.md)
- [Prompt 模板](prompt-templates.md)
- [已安裝 Skills](installed-skills.md)

---

*最後更新：2026-01-27*
