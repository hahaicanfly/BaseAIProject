# frontend-design — 專案套用指南

> `.claude/skills/frontend-design/SKILL_zh.md` 的參考檔。依專案填寫的範本：品牌定位、設計規範骨架（色彩／間距／圓角）、元件設計重點。

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

