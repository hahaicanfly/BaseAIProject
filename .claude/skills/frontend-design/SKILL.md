---
name: frontend-design
description: Produces high-quality UI components and visual design guidance centered on typography, color, motion, and spatial-composition design philosophy; triggers when the user wants to design an interface, polish a screen, or build a design system, or mentions "設計介面", "美化畫面", "建立設計系統".
---

# Frontend Design Skill

A high-quality frontend UI design guide, based on Anthropic's official Frontend Design Skill (Frontend Aesthetics Cookbook). Tech-stack agnostic — the principles apply to any frontend framework (Web/CSS, React, Vue, SwiftUI, Compose, etc.); code examples are demonstrated in Compose, and should be swapped for the equivalent syntax of the project's actual tech stack.

## Usage

```
/frontend-design [component name or screen description]
```

## Design Philosophy

You are a design engineer with world-class aesthetic taste. Designs must be:

- **Distinctive**: never build UI that looks "templated" or "cookie-cutter"
- **Art-directed**: every project needs a clear, consistent visual language
- **Detail-obsessed**: the devil is in the details — from motion to spacing, everything is deliberately crafted

---

## Core Design Principles

### 1. Typography

**Principle**: Choose distinctive, characterful typefaces and establish a clear hierarchy.

| Avoid | Prefer |
|------|------|
| Arial, Helvetica | System fonts with a clear hierarchy |
| Inter, Roboto (overused, unconsidered defaults) | Cross-platform, characterful display fonts |
| Default typography config | A custom Typography system per project |

**Example (Compose; swap for the equivalent Typography/CSS system in other stacks):**
```kotlin
// Define a clear type hierarchy
val Typography = Typography(
    headlineLarge = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        letterSpacing = (-0.5).sp  // Tight heading tracking
    ),
    bodyLarge = TextStyle(
        fontSize = 16.sp,
        lineHeight = 24.sp  // Comfortable reading line-height
    )
)
```

### 2. Color & Theme

**Principle**: Use a theme / design-token system to maintain a consistent palette — never hardcode color values.

| Avoid | Prefer |
|------|------|
| Hardcoded color values | Theme / CSS custom properties |
| Cliché palettes (blue-gray-white corporate) | A strong primary color + a sharp accent |
| Inconsistent, arbitrary colors | An explicit color system |

**Example (Compose; web projects can swap for CSS custom properties / Tailwind theme):**
```kotlin
// Define the brand color system
private val LightColors = lightColorScheme(
    primary = Color(0xFF6750A4),
    secondary = Color(0xFF625B71),
    tertiary = Color(0xFF7D5260),  // Accent color
    surface = Color(0xFFFFFBFE),
    background = Color(0xFFFFFBFE)
)

// Custom extended color
val ColorScheme.accent: Color
    get() = Color(0xFFFF6B35)  // Sharp orange accent
```

### 3. Motion

**Principle**: Prioritize high-impact motion (entrances, screen transitions) over scattered micro-interactions.

| Avoid | Prefer |
|------|------|
| Micro-animations everywhere | Focus on entrance / screen-transition motion |
| Meaningless bounces | Purposeful, guiding animation |
| Distracting effects | Reinforcing information hierarchy |

**Example (Compose; web projects can swap for CSS transitions / Framer Motion):**
```kotlin
// Staggered list-item entrance
LazyColumn {
    itemsIndexed(items) { index, item ->
        AnimatedVisibility(
            visible = true,
            enter = fadeIn(
                animationSpec = tween(
                    durationMillis = 300,
                    delayMillis = index * 50  // Stagger delay
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

### 4. Spatial Composition

**Principle**: Break predictable symmetric layouts; use whitespace and deliberate overlap to create visual focal points.

| Avoid | Prefer |
|------|------|
| Perfect symmetry | Asymmetric layouts that create visual tension |
| Isolated elements | Deliberate overlap to add depth |
| Cramped layouts | Generous negative space |

**Example (Compose; swap for the equivalent container/spacing system in other stacks):**
```kotlin
// Use negative space to create breathing room
Column(
    modifier = Modifier
        .fillMaxSize()
        .padding(horizontal = 24.dp)  // Generous margins
) {
    Spacer(modifier = Modifier.height(48.dp))  // Large top whitespace

    Text(
        text = title,
        style = MaterialTheme.typography.headlineLarge
    )

    Spacer(modifier = Modifier.height(32.dp))  // Section spacing

    // Content...
}
```

### 5. Visual Details

**Principle**: Use gradients, texture, and shadow to build atmosphere; avoid harsh edges.

| Avoid | Prefer |
|------|------|
| Flat, solid color blocks | Subtle gradients that add depth |
| No shadows at all | Purposeful shadows that build hierarchy |
| Hard edges | Refined corner radii and transitions |

**Example (Compose; web projects can swap for CSS box-shadow / gradient):**
```kotlin
// Gradient background
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

// Refined card shadow
Card(
    elevation = CardDefaults.cardElevation(
        defaultElevation = 2.dp,
        hoveredElevation = 8.dp
    ),
    shape = RoundedCornerShape(16.dp)
) { /* ... */ }
```

---

## Anti-Patterns

### Absolutely Forbidden

1. **Generic fonts**: don't use Arial, Helvetica, or default sans-serif
2. **Cliché palettes**: avoid the cookie-cutter blue-gray-white corporate look
3. **Predictable layouts**: don't rely solely on centered, symmetric boilerplate layouts
4. **Templated design**: every design must have its own distinctive art direction

### Warning Signs

If your design looks like:
- Default Bootstrap/Material styling → **redesign it**
- A layout anyone could have guessed → **be more creative**
- No visual focal point → **build a hierarchy**

---

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

---

## Design Review Checklist

Check the following before finalizing a design:

```
□ Does typography have a clear hierarchy? Enough contrast between headings and body text?
□ Does color use the theme system? Any hardcoded colors?
□ Do key actions have appropriate motion guidance?
□ Does the layout have a visual focal point? Enough whitespace?
□ Are details polished? Are corner radii, shadows, and transitions refined?
□ Does the overall design have distinctive art direction, or does it look templated?
```

---

## Reference Resources

- [Anthropic Frontend Aesthetics Cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/coding/prompting_for_frontend_aesthetics.ipynb)
- [Material Design 3](https://m3.material.io/)

---

*This skill is based on Anthropic's official Frontend Design Skill. Code examples are demonstrated in Compose Multiplatform/Kotlin; the principles themselves are tech-stack agnostic.*

## Verification Items

- **Output form**: design guidance MD (with code examples + a11y checklist).
- **Integration**: serves as the review criteria for `uiux-agent` Phase 2.
- **Required invariants check**: if the project defines UI-component-related INVs in `docs/architecture/invariants.md` (e.g. known Compose/frontend-framework pitfalls), cross-check against them; if there's no corresponding INV, use this document's review checklist to self-check.
- **Distinction from ui-ux-pro-max**: frontend-design = principles/aesthetic guidance; ui-ux-pro-max = full design-system spec output.
- **Handoff marker**: once guidance is delivered → `[HANDOFF: uiux-agent]` or `[HANDOFF: dev]`.
