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

---

## 核心設計原則

### 1. Typography（字體）

**原則**：選擇獨特且有個性的字體，並建立清晰的層級。

| 禁止 | 建議 |
|------|------|
| Arial, Helvetica | 系統字體搭配明確層級 |
| Inter, Roboto（過度通用、未經挑選） | 跨平台可用且有個性的特色字體 |
| 預設字體配置 | 依專案自訂的 Typography 系統 |

**範例（Compose，其他技術棧替換為等價的 Typography/CSS 系統）：**
```kotlin
// 定義清晰的字體層級
val Typography = Typography(
    headlineLarge = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        letterSpacing = (-0.5).sp  // 緊湊標題
    ),
    bodyLarge = TextStyle(
        fontSize = 16.sp,
        lineHeight = 24.sp  // 舒適閱讀行高
    )
)
```

### 2. Color & Theme（色彩）

**原則**：使用 Theme / 設計變數維護一致的調色盤，不硬編碼顏色值。

| 禁止 | 建議 |
|------|------|
| 硬編碼顏色值 | 使用 Theme / CSS variable |
| 俗套配色（藍灰白商務風） | 強主色 + 銳利點綴色 |
| 無一致性的隨機顏色 | 明確的色彩系統 |

**範例（Compose，Web 專案可替換為 CSS custom properties / Tailwind theme）：**
```kotlin
// 定義品牌色彩系統
private val LightColors = lightColorScheme(
    primary = Color(0xFF6750A4),
    secondary = Color(0xFF625B71),
    tertiary = Color(0xFF7D5260),  // 點綴色
    surface = Color(0xFFFFFBFE),
    background = Color(0xFFFFFBFE)
)

// 自訂擴展顏色
val ColorScheme.accent: Color
    get() = Color(0xFFFF6B35)  // 銳利橘色點綴
```

### 3. Motion（動效）

**原則**：優先高影響動效（入場、頁面切換），而非散亂的微互動。

| 禁止 | 建議 |
|------|------|
| 到處都是微動效 | 聚焦在入場/頁面切換 |
| 無意義的彈跳 | 有目的的引導動畫 |
| 分散注意力 | 強化資訊層級 |

**範例（Compose，Web 專案可替換為 CSS transition / Framer Motion）：**
```kotlin
// 列表項目交錯進場
LazyColumn {
    itemsIndexed(items) { index, item ->
        AnimatedVisibility(
            visible = true,
            enter = fadeIn(
                animationSpec = tween(
                    durationMillis = 300,
                    delayMillis = index * 50  // 交錯延遲
                )
            ) + slideInVertically(
                initialOffsetY = { it / 2 }
            )
        ) {
            ItemCard(item)
        }
    }
}
```

### 4. Spatial Composition（空間構圖）

**原則**：打破可預測的對稱佈局，用留白與適度重疊創造視覺焦點。

| 禁止 | 建議 |
|------|------|
| 完美對稱 | 不對稱佈局創造視覺張力 |
| 元素孤立 | 適度重疊增加層次 |
| 擁擠佈局 | 大量負空間留白 |

**範例（Compose，其他技術棧替換為等價的容器/間距系統）：**
```kotlin
// 使用負空間創造呼吸感
Column(
    modifier = Modifier
        .fillMaxSize()
        .padding(horizontal = 24.dp)  // 充足邊距
) {
    Spacer(modifier = Modifier.height(48.dp))  // 大量頂部留白

    Text(
        text = title,
        style = MaterialTheme.typography.headlineLarge
    )

    Spacer(modifier = Modifier.height(32.dp))  // 區塊間距

    // 內容...
}
```

### 5. Visual Details（視覺細節）

**原則**：運用漸層、紋理、陰影營造氛圍，避免生硬邊緣。

| 禁止 | 建議 |
|------|------|
| 純平面色塊 | 微妙漸層增加深度 |
| 無陰影設計 | 適當陰影建立層次 |
| 生硬邊緣 | 精緻圓角和過渡 |

**範例（Compose，Web 專案可替換為 CSS box-shadow / gradient）：**
```kotlin
// 漸層背景
Box(
    modifier = Modifier
        .fillMaxSize()
        .background(
            brush = Brush.verticalGradient(
                colors = listOf(
                    MaterialTheme.colorScheme.surface,
                    MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
                )
            )
        )
)

// 精緻卡片陰影
Card(
    elevation = CardDefaults.cardElevation(
        defaultElevation = 2.dp,
        hoveredElevation = 8.dp
    ),
    shape = RoundedCornerShape(16.dp)
) { /* ... */ }
```

---

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

---

## 專案套用指南

本節為模板，實際品牌色彩 / 調性 / 目標感受請依專案 CLAUDE.md 或 `agent_docs/TECHNICAL-REFERENCE.md` 填入，不要沿用其他專案的既有品牌值。

### 品牌定位（依專案填入）

- **核心價值**：[依專案填入]
- **視覺調性**：[依專案填入，例如：現代、清晰、友善、專業]
- **目標感受**：[依專案填入，使用者拿到產品的第一印象]

### 設計規範範本

```kotlin
// 專案色彩系統（範例結構，實際色值依專案品牌填入）
object AppColors {
    val Primary = Color(0xFF6750A4)     // 主色
    val Accent = Color(0xFFFF6B35)      // 點綴色
    val Success = Color(0xFF4CAF50)     // 成功狀態
    val Surface = Color(0xFFFFFBFE)     // 表面
    val OnSurface = Color(0xFF1C1B1F)   // 文字
}

// 間距系統
object Spacing {
    val xs = 4.dp
    val sm = 8.dp
    val md = 16.dp
    val lg = 24.dp
    val xl = 32.dp
    val xxl = 48.dp
}

// 圓角系統
object Radius {
    val sm = 8.dp
    val md = 12.dp
    val lg = 16.dp
    val xl = 24.dp
}
```

### 元件設計原則（範例，依專案實際元件調整）

| 元件類型 | 設計要點 |
|------|----------|
| 列表卡片 | 清晰的主/次資訊對照、關鍵數值突出、狀態明確 |
| 首頁 | 簡潔的 CTA、友善的空狀態設計 |
| 摘要展示畫面 | 大字清晰、適合快速掃視、多語言並列（如需要） |
| Loading 狀態 | 有趣的載入動畫、清晰的進度提示 |

---

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

---

## 參考資源

- [Anthropic Frontend Aesthetics Cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/coding/prompting_for_frontend_aesthetics.ipynb)
- [Material Design 3](https://m3.material.io/)

---

*此 Skill 基於 Anthropic 官方 Frontend Design Skill，程式碼範例以 Compose Multiplatform/Kotlin 示範，原則本身技術棧無關。*

## 驗證項目

- **產出形式**：design guidance MD（含程式碼示例 + a11y checklist）。
- **整合**：作為 `uiux-agent` Phase 2 評審的判準依據。
- **必查 invariants**：若專案在 `docs/architecture/invariants.md` 定義了 UI 元件相關的 INV（例如 Compose/前端框架既知陷阱），一併對照；無對應 INV 時，依本檔審查清單自行檢查。
- **與 ui-ux-pro-max 區別**：frontend-design = 原則／美學指引；ui-ux-pro-max = 完整 design system spec 產出。
- **交接 marker**：guidance 提供完畢 → `[HANDOFF: uiux-agent]` 或 `[HANDOFF: dev]`。
