---
name: frontend-design
description: 以字體、色彩、動效、空間構成等設計哲學為核心，產出高品質 UI 元件與視覺設計指引；當使用者要設計介面、美化畫面或建立設計系統時觸發。
---

# Frontend Design Skill

高品質前端 UI 設計指南，基於 Anthropic 官方 Frontend Design Skill（Frontend Aesthetics Cookbook），技術棧無關——原則適用於任何前端框架（Web/CSS、React、Vue、SwiftUI、Compose 等），程式碼範例以 Compose 示範，換成專案實際技術棧的等價寫法即可。

## 使用方式

```
/frontend-design [元件名稱或畫面描述]
```

## 設計哲學

你是一位擁有世界級美學品味的設計工程師。設計必須：

- **獨特性**：永遠不要建立看起來「模板化」或「千篇一律」的 UI
- **藝術指導**：每個專案都需要清晰、一致的視覺語言
- **細節執著**：魔鬼藏在細節中，從動效到間距都要精心設計

## 五項核心原則

| # | 原則 | 一句話 |
|---|------|--------|
| 1 | 字體 Typography | 有個性、有辨識度的字體搭配明確層級 — 不要 Arial，也不要沒思考就套 Inter |
| 2 | 色彩 Color & Theme | 用 Theme／design token 系統，強主色配一個銳利的 accent — 絕不硬編碼色值 |
| 3 | 動效 Motion | 集中在入場與轉場的高衝擊動效，而非到處散落的微互動 |
| 4 | 空間構成 Spatial Composition | 非對稱、刻意重疊、充足留白，勝過可預測的對稱佈局 |
| 5 | 視覺細節 Visual Details | 細緻漸層、有目的的陰影、講究的圓角 — 營造氛圍而非硬邊 |

**動手寫任何 UI 代碼之前，先讀 `references/design-principles_zh.md`** — 五項原則各自的 avoid/prefer 對照表與完整程式碼範例都在裡面。要把設計綁定到具體專案時（品牌定位、色彩／間距／圓角規範、各元件設計重點），再讀 `references/project-application_zh.md`。

## 禁止事項 (Anti-Patterns)

### 絕對禁止

1. **通用字體**：不要使用 Arial、Helvetica、預設 sans-serif
2. **俗套配色**：避免千篇一律的藍灰白商務風
3. **可預測佈局**：不要只用對稱置中的樣板佈局
4. **模板感設計**：每個設計都必須有獨特的藝術指導

### 警告標誌

如果你的設計看起來像：
- Bootstrap/Material 預設樣式 → **重新設計**
- 任何人都能想到的佈局 → **更有創意**
- 沒有視覺焦點 → **建立層級**

## 設計審查清單

在完成設計前，檢查以下項目：

```
□ 字體是否有明確層級？標題與內文對比足夠？
□ 色彩是否使用 Theme 系統？有無硬編碼顏色？
□ 關鍵操作有無適當的動效引導？
□ 佈局是否有視覺焦點？留白是否充足？
□ 細節是否到位？圓角、陰影、過渡是否精緻？
□ 整體是否有獨特的藝術指導？還是看起來像模板？
```

## 參考資源

- [Anthropic Frontend Aesthetics Cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/coding/prompting_for_frontend_aesthetics.ipynb)
- [Material Design 3](https://m3.material.io/)

*此 Skill 基於 Anthropic 官方 Frontend Design Skill，程式碼範例以 Compose Multiplatform/Kotlin 示範，原則本身技術棧無關。*

## 驗證項目

- **產出形式**：design guidance MD（含程式碼示例 + a11y checklist）。
- **整合**：作為 `uiux-agent` Phase 2 評審的判準依據。
- **必查 invariants**：若專案在 `docs/architecture/invariants.md` 定義了 UI 元件相關的 INV（例如 Compose/前端框架既知陷阱），一併對照；無對應 INV 時，依本檔審查清單自行檢查。
- **與 ui-ux-pro-max 區別**：frontend-design = 原則／美學指引；ui-ux-pro-max = 完整 design system spec 產出。
- **交接 marker**：guidance 提供完畢 → `[HANDOFF: uiux-agent]` 或 `[HANDOFF: dev]`。
