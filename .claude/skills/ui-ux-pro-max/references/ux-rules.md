# ui-ux-pro-max — UX rule catalogue

> Reference for `.claude/skills/ui-ux-pro-max/SKILL.md`. The priority order below is what a design review should follow top-down.

## Rule Categories by Priority

| Priority | Category | Impact | Domain |
|----------|----------|--------|--------|
| 1 | Accessibility | CRITICAL | `ux` |
| 2 | Touch & Interaction | CRITICAL | `ux` |
| 3 | Performance | HIGH | `ux` |
| 4 | Layout & Responsive | HIGH | `ux` |
| 5 | Typography & Color | MEDIUM | `typography`, `color` |
| 6 | Animation | MEDIUM | `ux` |
| 7 | Style Selection | MEDIUM | `style`, `product` |
| 8 | Charts & Data | LOW | `chart` |

## Quick Reference

### 1. Accessibility (CRITICAL)

- `color-contrast` - minimum 4.5:1 contrast for body text
- `focus-states` - interactive elements need a clear focus ring
- `alt-text` - meaningful images need descriptive alt text
- `aria-labels` - icon-only buttons need an aria-label
- `keyboard-nav` - tab order must match visual order
- `form-labels` - form fields use a label with a `for` attribute

### 2. Touch & Interaction (CRITICAL)

- `touch-target-size` - minimum 44x44px touch target
- `hover-vs-tap` - primary interactions use click/tap, not hover-dependent
- `loading-buttons` - disable buttons while an async operation is in progress
- `error-feedback` - error messages appear near the point of the problem
- `cursor-pointer` - clickable elements get `cursor-pointer`

### 3. Performance (HIGH)

- `image-optimization` - use WebP, srcset, lazy loading
- `reduced-motion` - respect `prefers-reduced-motion`
- `content-jumping` - reserve layout space for async content

### 4. Layout & Responsive (HIGH)

- `viewport-meta` - `width=device-width initial-scale=1`
- `readable-font-size` - minimum 16px body text on mobile
- `horizontal-scroll` - ensure content never exceeds viewport width
- `z-index-management` - define z-index layers (10, 20, 30, 50)

### 5. Typography & Color (MEDIUM)

- `line-height` - 1.5-1.75 line-height for body text
- `line-length` - cap line length at 65-75 characters
- `font-pairing` - heading/body font personalities should complement each other

### 6. Animation (MEDIUM)

- `duration-timing` - use 150-300ms for micro-interactions
- `transform-performance` - use transform/opacity, avoid animating width/height
- `loading-states` - skeleton screens or spinners

### 7. Style Selection (MEDIUM)

- `style-match` - style should match the product type
- `consistency` - use a consistent style site-wide
- `no-emoji-icons` - use SVG icons, not emoji

### 8. Charts & Data (LOW)

- `chart-type` - chart type should match the data type
- `color-guidance` - use accessible color palettes
- `data-table` - provide a table version for accessibility
