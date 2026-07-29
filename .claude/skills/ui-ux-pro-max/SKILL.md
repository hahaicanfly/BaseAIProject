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

## References — load the one the task needs, not all three

| File | Read it when |
|------|--------------|
| `references/search-cli.md` | Driving `search.py`: prerequisites, the four-step flow, domain and stack tables, output formats, worked example |
| `references/ux-rules.md` | Reviewing or auditing a UI — 8 rule categories in priority order, Accessibility first |
| `references/polish-checklist.md` | Before delivering UI code — polish rules and the pre-delivery checklist |

## The step that is not optional

Always generate the design system first; every other search supplements it.

Start by extracting from the user's request: **product type** (SaaS, e-commerce, portfolio, dashboard, landing page…), **style keywords** (minimal, playful, elegant, dark mode…), **industry**, and **tech stack** — defaulting to `html-tailwind` when none is named. Those become the query:

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

The command searches 5 domains in parallel (product, style, color, landing, typography), applies the `ui-reasoning.csv` reasoning rules, and returns a complete design system — pattern, style, colors, typography, effects — plus the anti-patterns to avoid. Add `--persist` to write `design-system/MASTER.md` and per-page override files.

Supplementary domain searches (`--domain style|chart|ux|typography|landing`), stack guidelines (`--stack`), the layered MASTER/overrides lookup, and output formats: `references/search-cli.md`.

## Non-negotiables

The rest of the rules live in the references; these three are the ones most often lost:

- Accessibility and touch-target size are CRITICAL priority — never traded away for aesthetics
- SVG icons (Heroicons, Lucide, Simple Icons), never emoji, as UI icons
- Light mode and dark mode are both tested before delivery

## Verification Items

- **Output form**: a complete design system spec (with palette / typography / spacing / component samples).
- **uiux-agent integration**: serves as the design basis for Phase 1 sketches and the review standard for Phase 2 (see `.claude/agents/uiux-agent.md`).
- **ExecPlan integration**: UI-related ExecPlans' Context section references the relevant part of this spec (format per `.claude/protocols/execplan-lifecycle.md`).
- **Alignment with existing design system**: if the project already has a design-system document (e.g. `agent_docs/TECHNICAL-REFERENCE.md` or a project-specific design-system doc), the output must not conflict with it; if no such document exists yet, this output serves as the starting point.
- **Handoff marker**: once the spec is complete → `[HANDOFF: uiux-agent]`, entering the three-phase flow (`.claude/uiux/WORKFLOW.md`).
