# frontend-design — the five core principles

> Reference for `.claude/skills/frontend-design/SKILL.md`. Each principle carries an avoid/prefer table and a worked code example. Examples are Compose; swap them for the project's actual stack.

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
