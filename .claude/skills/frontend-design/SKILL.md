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

## The Five Principles

| # | Principle | In one line |
|---|-----------|-------------|
| 1 | Typography | Distinctive, characterful typefaces with an explicit hierarchy — not Arial, not an unconsidered Inter default |
| 2 | Color & Theme | A theme / design-token system, a strong primary plus a sharp accent — never a hardcoded color value |
| 3 | Motion | High-impact entrances and screen transitions, not micro-animations scattered everywhere |
| 4 | Spatial Composition | Asymmetry, deliberate overlap and generous negative space over predictable symmetry |
| 5 | Visual Details | Subtle gradients, purposeful shadows and refined radii — atmosphere instead of hard edges |

**Read `references/design-principles.md` before writing any UI code** — it carries the avoid/prefer table and a worked code example for each of the five. When the design has to be pinned to a specific project (brand positioning, color / spacing / radius spec, per-component focus), read `references/project-application.md` as well.

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

## Reference Resources

- [Anthropic Frontend Aesthetics Cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/coding/prompting_for_frontend_aesthetics.ipynb)
- [Material Design 3](https://m3.material.io/)

*This skill is based on Anthropic's official Frontend Design Skill. Code examples are demonstrated in Compose Multiplatform/Kotlin; the principles themselves are tech-stack agnostic.*

## Verification Items

- **Output form**: design guidance MD (with code examples + a11y checklist).
- **Integration**: serves as the review criteria for `uiux-agent` Phase 2.
- **Required invariants check**: if the project defines UI-component-related INVs in `docs/architecture/invariants.md` (e.g. known Compose/frontend-framework pitfalls), cross-check against them; if there's no corresponding INV, use this document's review checklist to self-check.
- **Distinction from ui-ux-pro-max**: frontend-design = principles/aesthetic guidance; ui-ux-pro-max = full design-system spec output.
- **Handoff marker**: once guidance is delivered → `[HANDOFF: uiux-agent]` or `[HANDOFF: dev]`.
