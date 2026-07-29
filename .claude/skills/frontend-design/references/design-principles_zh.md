# frontend-design — 五項核心原則

> `.claude/skills/frontend-design/SKILL_zh.md` 的參考檔。每項原則都附 avoid/prefer 對照表與完整程式碼範例。範例以 Compose 撰寫，實作時換成專案實際技術棧的等價寫法。

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
