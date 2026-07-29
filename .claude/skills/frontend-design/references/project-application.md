# frontend-design — project application guide

> Reference for `.claude/skills/frontend-design/SKILL.md`. A template to fill in per project: brand positioning, the design-spec skeleton (colors / spacing / radius), component design focus.

## Project Application Guide

This section is a template — fill in the actual brand colors / tone / target feeling per project's CLAUDE.md or `agent_docs/TECHNICAL-REFERENCE.md`; do not carry over another project's existing brand values.

### Brand Positioning (fill in per project)

- **Core values**: [fill in per project]
- **Visual tone**: [fill in per project, e.g. modern, clean, friendly, professional]
- **Target feeling**: [fill in per project — the user's first impression on encountering the product]

### Design Spec Template

```kotlin
// Project color system (example structure — actual values per project brand)
object AppColors {
    val Primary = Color(0xFF6750A4)     // Primary
    val Accent = Color(0xFFFF6B35)      // Accent
    val Success = Color(0xFF4CAF50)     // Success state
    val Surface = Color(0xFFFFFBFE)     // Surface
    val OnSurface = Color(0xFF1C1B1F)   // Text
}

// Spacing system
object Spacing {
    val xs = 4.dp
    val sm = 8.dp
    val md = 16.dp
    val lg = 24.dp
    val xl = 32.dp
    val xxl = 48.dp
}

// Corner-radius system
object Radius {
    val sm = 8.dp
    val md = 12.dp
    val lg = 16.dp
    val xl = 24.dp
}
```

### Component Design Principles (examples — adjust per project's actual components)

| Component Type | Design Focus |
|------|----------|
| List card | Clear primary/secondary info contrast, key values emphasized, clear status |
| Home screen | Concise CTA, friendly empty states |
| Summary display screen | Large clear type, quick-scan friendly, multi-language side-by-side (if needed) |
| Loading state | Engaging loading animation, clear progress indication |

