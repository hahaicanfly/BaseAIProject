---
name: ui-ux-pro-max
description: Produces a complete design system covering color palettes, typography pairings, UI styles, and UX guidelines, across multiple frontend tech stacks; triggers when the user wants to plan, design, or review UI/UX, or mentions "規劃UI", "設計介面", "檢視UI/UX".
---

# UI/UX Pro Max - Design Intelligence

Comprehensive design guide for web and mobile applications. Includes 50+ UI styles, 97 color palettes, 57 typography pairings, 99 UX guidelines, and 25 chart types, across 9+ frontend tech stacks. Queried via a BM25 search engine, returning priority-ranked recommendations.

## When to Apply

Reference this skill in the following situations:
- Designing a new UI component or page
- Choosing a color palette and typography
- Reviewing UX issues in existing code
- Building a landing page or dashboard
- Implementing accessibility requirements

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

## How to Use

Use the CLI tool below to search a specific domain.

---

## Prerequisites

Check whether Python is installed:

```bash
python3 --version || python --version
```

If not yet installed, install per OS:

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install python3
```

**Windows:**
```powershell
winget install Python.Python.3.12
```

---

## How to Use This Skill

When the user makes a UI/UX request (design, build, implement, review, fix, optimize), follow this flow:

### Step 1: Analyze User Requirements

Extract key information from the user's request:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page, etc.
- **Style keywords**: minimal, playful, professional, elegant, dark mode, etc.
- **Industry**: healthcare, fintech, gaming, education, etc.
- **Tech stack**: React, Vue, Next.js; if unspecified, default to `html-tailwind`

### Step 2: Generate Design System (REQUIRED)

**Always run `--design-system` first** to get complete recommendations with rationale:

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

This command:
1. Searches 5 domains in parallel (product, style, color, landing, typography)
2. Applies `ui-reasoning.csv` reasoning rules to select the best match
3. Returns a complete design system: pattern, style, colors, typography, effects
4. Attaches anti-patterns to avoid

**Example:**
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### Step 2b: Persist Design System (Master + Overrides Pattern)

To persist the design system across sessions for layered lookup, add `--persist`:

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

This generates:
- `design-system/MASTER.md` — global design rules, source of truth
- `design-system/pages/` — page-level override folder

**With a page-level override:**
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

Also generates:
- `design-system/pages/dashboard.md` — rules for that page, as a diff against Master

**How layered lookup works:**
1. When building a specific page (e.g. "Checkout"), check `design-system/pages/checkout.md` first
2. If that page file exists, its rules **override** the Master file
3. If it doesn't exist, use only `design-system/MASTER.md`

**Context-aware lookup prompt:**
```
I am building the [Page Name] page. Please read design-system/MASTER.md.
Also check if design-system/pages/[page-name].md exists.
If the page file exists, prioritize its rules.
If not, use the Master rules exclusively.
Now, generate the code...
```

### Step 3: Supplement with Detailed Searches (as needed)

After getting the design system, supplement with domain searches for detail:

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**When a detailed search is needed:**

| Need | Domain | Example |
|------|--------|---------|
| More style options | `style` | `--domain style "glassmorphism dark"` |
| Chart recommendations | `chart` | `--domain chart "real-time dashboard"` |
| UX best practices | `ux` | `--domain ux "animation accessibility"` |
| Alternative fonts | `typography` | `--domain typography "elegant luxury"` |
| Landing structure | `landing` | `--domain landing "hero social-proof"` |

### Step 4: Stack Guidelines (Default: html-tailwind)

Get implementation-level best practices. If the user didn't specify a tech stack, **default to `html-tailwind`**.

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
```

Available stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose` (`data/stacks/` also includes `astro`, `nuxtjs`, `nuxt-ui`)

---

## Search Reference

### Available Domains

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | Product-type recommendations | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style` | UI style, color scheme, effects | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | Font pairing, Google Fonts | elegant, playful, professional, modern |
| `color` | Palettes by product type | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | Page structure, CTA strategy | hero, hero-centric, testimonial, pricing, social-proof |
| `chart` | Chart types, library recommendations | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility, z-index, loading |
| `react` | React/Next.js performance | waterfall, bundle, suspense, memo, rerender, cache |
| `web` | Web interface guidelines | aria, focus, keyboard, semantic, virtualize |
| `prompt` | AI prompt, CSS keywords | (style name) |

### Available Stacks

| Stack | Focus |
|-------|-------|
| `html-tailwind` | Tailwind utilities, responsive, a11y (default) |
| `react` | State, hooks, performance, patterns |
| `nextjs` | SSR, routing, images, API routes |
| `vue` | Composition API, Pinia, Vue Router |
| `svelte` | Runes, stores, SvelteKit |
| `swiftui` | Views, State, Navigation, Animation |
| `react-native` | Components, Navigation, Lists |
| `flutter` | Widgets, State, Layout, Theming |
| `shadcn` | shadcn/ui components, theming, forms, patterns |
| `jetpack-compose` | Composables, Modifiers, State Hoisting, Recomposition |

---

## Example Workflow

**User request:** "Build a landing page for a skincare service"

### Step 1: Analyze Requirements
- Product type: Beauty/Spa service
- Style keywords: elegant, professional, soft
- Industry: Beauty/Wellness
- Tech stack: html-tailwind (default)

### Step 2: Generate Design System (REQUIRED)

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service elegant" --design-system -p "Serenity Spa"
```

**Output:** a complete design system, including pattern, style, colors, typography, effects, anti-patterns.

### Step 3: Supplement with Detailed Searches (as needed)

```bash
# Get UX guidelines for animation and accessibility
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# Get alternative typography options
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "elegant luxury serif" --domain typography
```

### Step 4: Stack Guidelines

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "layout responsive form" --stack html-tailwind
```

**Then:** integrate the design system + detailed search results, and implement the design.

---

## Output Formats

The `--design-system` flag supports two output formats:

```bash
# ASCII box (default) — best for terminal display
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system

# Markdown — best for writing to documentation
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system -f markdown
```

---

## Tips for Better Results

1. **Be specific with keywords** - "healthcare SaaS dashboard" beats "app"
2. **Search multiple times** - different keywords surface different insights
3. **Combine multiple domains** - Style + Typography + Color = a complete design system
4. **Always check UX** - search "animation", "z-index", "accessibility" to catch common issues
5. **Use the stack flag** - to get implementation-level best practices
6. **Iterate** - if the first search doesn't match, try different keywords

---

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

## Verification Items

- **Output form**: a complete design system spec (with palette / typography / spacing / component samples).
- **uiux-agent integration**: serves as the design basis for Phase 1 sketches and the review standard for Phase 2 (see `.claude/agents/uiux-agent.md`).
- **ExecPlan integration**: UI-related ExecPlans' Context section references the relevant part of this spec (format per `.claude/protocols/execplan-lifecycle.md`).
- **Alignment with existing design system**: if the project already has a design-system document (e.g. `agent_docs/TECHNICAL-REFERENCE.md` or a project-specific design-system doc), the output must not conflict with it; if no such document exists yet, this output serves as the starting point.
- **Handoff marker**: once the spec is complete → `[HANDOFF: uiux-agent]`, entering the three-phase flow (`.claude/uiux/WORKFLOW.md`).
