# UI/UX Design Rules

> **These rules are mandatory guidance — all UI implementation must comply.**
>
> Applicable tech stacks: React/Tailwind, Compose Multiplatform, SwiftUI, Vue, etc.

---

## 1. Style and Consistency

### 1.1 Design Tokens Are Mandatory

```
// ✅ Correct: use a Design Token
color: var(--color-primary)
padding: spacing.md  // 16px

// ❌ Wrong: hardcoded value
color: #6750A4
padding: 16px  // writing the number directly
```

**Rules**:
- Color: only use colors defined by a Design Token or Theme
- Typography: only use styles defined by the Typography system
- Spacing: only use the Spacing Scale (multiples of 4px / 8px)
- Corner radius: only use Shape Tokens

### 1.2 Component Consistency

| Component Type | Requirement |
|---------|-----|
| Button | Uniformly use the design system's Button component |
| Card | Uniform corner radius and shadow rules |
| Input | Uniform style, including label and error state |
| Icon | Use only one icon library |

### 1.3 No Random Styling

```
// ❌ Prohibited: random colors, random corner radii
border-radius: 13px  // why 13?
color: #ABCDEF  // meaningless color

// ✅ Correct: use semantic tokens
border-radius: var(--radius-card)
color: var(--color-primary)
```

---

## 2. Layout and Whitespace

### 2.1 Grid System

Follow an 8px grid (4px fine adjustment):
- Margin: `16px` (Spacing.md)
- Card spacing: `12px`
- Section spacing: `24px` (Spacing.lg)

### 2.2 Spacing Scale (Mandatory)

| Token | Value | Purpose |
|-------|-----|-----|
| `spacing.xs` | 4px | Fine spacing within an element |
| `spacing.sm` | 8px | Spacing between related elements |
| `spacing.md` | 16px | Spacing within a block, standard padding |
| `spacing.lg` | 24px | Spacing between blocks |
| `spacing.xl` | 32px | Separation between major sections |
| `spacing.xxl` | 48px | Separation between page sections |

### 2.3 Text Hierarchy

Heading levels (must not skip):
- Display / Hero title
- Page title (H1)
- Section title (H2)
- Subsection (H3)
- Card title
- Primary body text
- Secondary body text
- Supporting text

**Rules**:
- At least a 2-4px size difference between adjacent levels
- Line height: body 1.5-1.75, heading 1.2-1.3
- Max 65-75 characters per line (35-40 for Chinese)

---

## 3. Interaction Details

### 3.1 State Completeness (all states must be implemented)

| State | Visual Change | Implementation Requirement |
|-----|---------|---------|
| **Default** | Baseline style | Must be defined |
| **Hover** | Lighter background, slight scale-up | Desktop only |
| **Focus** | Visible focus ring (2px) | Keyboard accessible |
| **Active/Pressed** | Darker background, scale 0.98 | While clicking |
| **Disabled** | 50% opacity, no interaction | enabled = false |
| **Loading** | Content replaced with spinner | Interaction disabled |

### 3.2 Loading State

```
// ✅ Correct: Skeleton + disabled interaction
switch (state) {
  case 'loading': return <SkeletonList />  // skeleton screen
  case 'success': return <List items={data} />
  case 'error': return <ErrorState onRetry={retry} />
}

// ❌ Wrong: only a spinner, no layout preview
<Spinner />  // no indication of what will load
```

### 3.3 Empty State (must be designed)

Every list/data area must have an Empty State:
- Icon (required)
- Title (required)
- Description (required)
- CTA (optional)

---

## 4. Usability and a11y (Accessibility)

### 4.1 Keyboard Operability (Mandatory)

- All interactive elements must be focusable
- Tab order matches visual order
- Enter/Space triggers the primary action

### 4.2 Contrast Ratio (WCAG AA)

| Element | Minimum Contrast |
|-----|-----------|
| Normal text (< 18px) | 4.5:1 |
| Large text (>= 18px bold or 24px) | 3:1 |
| Icons, UI elements | 3:1 |

### 4.3 Aria / Label (Mandatory)

```html
<!-- All icon buttons must have aria-label -->
<button aria-label="Close">
  <CloseIcon />
</button>

<!-- Images must have alt text -->
<img src="photo.jpg" alt="Example photo" />

<!-- Form fields must be associated with a label -->
<label for="email">Email</label>
<input id="email" type="email" />
```

### 4.4 Touch Targets

Minimum touch area 44-48px × 44-48px

---

## 5. Performance and Visual Stability

### 5.1 Avoid CLS (Cumulative Layout Shift)

```
// ✅ Correct: reserve space
<div style="aspect-ratio: 16/9">
  <img src={imageUrl} />
</div>

// ❌ Wrong: height is indeterminate
<img src={imageUrl} style="width: 100%" />
// height changes after load → CLS
```

### 5.2 Animation Performance

```
// ✅ Use transform/opacity (GPU-accelerated)
transition: transform 300ms, opacity 300ms

// ❌ Avoid animating width/height/padding (triggers layout)
transition: width 300ms  // poor performance
```

### 5.3 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 6. Checklist

### Before Implementation
- [ ] Have Design Tokens been defined?
- [ ] Is the project's unified Spacing Scale being used?
- [ ] Have all states (loading/empty/error) been planned?

### During Implementation
- [ ] Do colors come from Tokens?
- [ ] Does spacing use Tokens?
- [ ] Do interactive elements have hover/focus/active/disabled?
- [ ] Do icon buttons have aria-label / contentDescription?

### After Implementation
- [ ] Does contrast meet 4.5:1?
- [ ] Is the UI fully keyboard operable?
- [ ] Do images have reserved space?
- [ ] Does animation respect reduced motion?

---

## 7. Violation Handling

| Violation Type | Severity | Handling |
|---------|---------|---------|
| Hardcoded color/spacing | Medium | Rejected in code review |
| Missing aria-label / contentDescription | High | Mandatory fix |
| Insufficient contrast | High | Mandatory fix |
| Missing Loading/Empty State | Medium | Must be added |
| CLS issue | Medium | Performance fix |

---

*Last updated: 2026-01-27*
*Applicable tech stacks: React/Tailwind, Compose Multiplatform, SwiftUI, Vue*
