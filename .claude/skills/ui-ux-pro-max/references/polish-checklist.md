# ui-ux-pro-max — polish rules and pre-delivery checklist

> Reference for `.claude/skills/ui-ux-pro-max/SKILL.md`. Run the checklist before delivering any UI code.

## Common Rules for Professional UI

The following are commonly overlooked details that make a UI look unpolished:

### Icons & Visual Elements

| Rule | Do | Don't |
|------|----|----- |
| **No emoji icons** | Use SVG icons (Heroicons, Lucide, Simple Icons) | Use emoji like 🎨 🚀 ⚙️ as UI icons |
| **Stable hover states** | Use color/opacity transitions on hover | Use scale transforms that shift layout |
| **Correct brand logos** | Find official SVGs from Simple Icons | Guess or use an incorrect logo |
| **Consistent icon sizing** | Fixed viewBox (24x24) with w-6 h-6 | Mix arbitrary icon sizes |

### Interaction & Cursor

| Rule | Do | Don't |
|------|----|----- |
| **Cursor pointer** | Add `cursor-pointer` to all clickable/hoverable cards | Leave the default cursor on interactive elements |
| **Hover feedback** | Provide visual feedback (color, shadow, border) | Give no interaction cue at all |
| **Smooth transitions** | Use `transition-colors duration-200` | Snap state changes instantly, or make them too slow (>500ms) |

### Light/Dark Mode Contrast

| Rule | Do | Don't |
|------|----|----- |
| **Glass card light mode** | Use `bg-white/80` or higher opacity | Use `bg-white/10` (too transparent) |
| **Text contrast light** | Use `#0F172A` (slate-900) for body text | Use `#94A3B8` (slate-400) for body text |
| **Muted text light** | Use at least `#475569` (slate-600) | Use a lighter gray-400 |
| **Border visibility** | Use `border-gray-200` in light mode | Use `border-white/10` (invisible) |

### Layout & Spacing

| Rule | Do | Don't |
|------|----|----- |
| **Floating navbar** | Add `top-4 left-4 right-4` spacing | Pin navbar flush to `top-0 left-0 right-0` |
| **Content padding** | Reserve space for the height of a fixed navbar | Let content get obscured by fixed elements |
| **Consistent max-width** | Standardize on `max-w-6xl` or `max-w-7xl` | Mix different container widths |

---

## Pre-Delivery Checklist

Confirm the following before delivering UI code:

### Visual Quality
- [ ] No emoji used as icons (use SVG instead)
- [ ] All icons come from a single icon set (Heroicons/Lucide)
- [ ] Brand logos are correct (verified against Simple Icons)
- [ ] Hover states don't cause layout shift
- [ ] Theme colors used directly (bg-primary), not wrapped in an extra var()

### Interaction
- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states are visible during keyboard navigation

### Light/Dark Mode
- [ ] Light-mode text contrast is sufficient (at least 4.5:1)
- [ ] Glass/translucent elements remain visible in light mode
- [ ] Borders are visible in both modes
- [ ] Both modes tested before delivery

### Layout
- [ ] Floating elements have proper spacing from edges
- [ ] Content isn't obscured by a fixed navbar
- [ ] Responsive at 375px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile

### Accessibility
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is never the sole indicator of information
- [ ] `prefers-reduced-motion` is respected
