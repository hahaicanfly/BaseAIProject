# UI/UX Three-Phase Workflow

> **Mandatory: all UI development must follow the "Wireframe → Critique → Implementation" three-phase workflow.**
>
> **Jumping straight to implementation is prohibited. Each phase requires the user's explicit "OK" before moving to the next.**

---

> **Plain language first**: every step below can be triggered just by describing what you need in your own words — you don't need to memorize any command syntax. Wherever this doc shows `@agent`/slash syntax (e.g. `@uiux-agent`, `/ui-ux-pro-max`), treat it as an **optional shortcut**, not a requirement.

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        UI/UX Development Flow                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Phase 1          Phase 2          Phase 3                     │
│   ┌──────┐        ┌──────┐        ┌──────┐                      │
│   │Wireframe│──OK──│Critique│──OK──│ Impl  │                      │
│   │      │        │      │        │      │                      │
│   └──────┘        └──────┘        └──────┘                      │
│      │               │               │                           │
│      ▼               ▼               ▼                           │
│   Wireframe      Critique       Production                      │
│   Layout         3 Options      Code + States                   │
│   Structure      Selection      + a11y + Responsive             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Wireframe

### Goal
Confirm information architecture and layout structure — **no visual details involved**.

### Owner
Just say something like "help me sketch a wireframe for [screen]" and the agent picks it up from there. (Advanced/optional shortcut: `@uiux-agent` or `/ui-ux-pro-max`)

### Input
- User requirements description
- User goals
- Core actions

### Output
1. **ASCII Wireframe**: block structure diagram
2. **Block descriptions**: purpose of each block
3. **Information hierarchy**: Primary > Secondary > Tertiary
4. **Preliminary component list**

### Prohibited
- ❌ Defining colors, fonts, or corner radii
- ❌ Writing any code
- ❌ Discussing animation effects
- ❌ Choosing a color scheme

### Completion Criteria
User replies "OK" or explicitly approves the wireframe.

### Prompt Used
→ [Prompt 1: Wireframe Generation](prompt-templates.md#prompt-1-wireframe-generation)

---

## Phase 2: Critique

### Goal
Review the wireframe from a designer's perspective, identify issues, and propose alternatives.

### Owner
Just say something like "critique this wireframe" or "what's wrong with this design" and the agent takes it from there. (Advanced/optional shortcut: `@uiux-agent` or `/frontend-design`)

### Input
- Phase 1 wireframe
- Brand tone
- Target users

### Output
1. **Issue list**: with severity (High/Med/Low)
2. **"AI smell" detection**: does it look like a template?
3. **3 alternative directions**: each with core change, expected effect, risk
4. **Recommendation**: the suggested direction

### Review Dimensions
- [ ] AI smell / template feel
- [ ] Clarity of information hierarchy
- [ ] Touch/interaction usability
- [ ] Component consistency
- [ ] Missing states (Loading/Empty/Error)
- [ ] Edge-case handling

### Completion Criteria
1. User selects a direction
2. User replies "OK" or requests adjustments
3. Adjustments get another "OK"

### Prompt Used
→ [Prompt 2: Design Critique (Nitpicking)](prompt-templates.md#prompt-2-design-critique-nitpicking)

---

## Phase 3: Implementation

### Goal
Produce complete UI code from the approved wireframe and Style Spec.

### Owner
Development agent or developer

### Input
- Phase 2 approved wireframe
- Filled-in [Style Spec](style-spec.template.md)
- Tech stack (React / SwiftUI / Compose / Vue, etc.)
- Design Token source

### Output
1. **Complete component code**
2. **All states**: Default, Hover, Focus, Pressed, Disabled, Loading
3. **a11y support**: aria-label / contentDescription, contrast ratio, keyboard operation
4. **Responsive**: Mobile, Tablet, Desktop
5. **Edge Cases**: Empty, Error, long text, extreme data

### Mandatory Implementation Items
| Category | Item | Required |
|-----|------|-----|
| State | Default | ✅ |
| State | Hover | ✅ |
| State | Focus | ✅ |
| State | Pressed | ✅ |
| State | Disabled | ✅ |
| State | Loading | ✅ |
| a11y | aria-label / contentDescription | ✅ |
| a11y | Contrast ratio 4.5:1 | ✅ |
| a11y | Touch target 44-48dp/px | ✅ |
| a11y | Keyboard operation | ✅ |
| Edge | Empty State | ✅ |
| Edge | Error State | ✅ |
| Edge | Long text | ✅ |

### Completion Criteria
1. Code passes the acceptance checklist
2. User testing confirms

### Prompt Used
→ [Prompt 3: UI Implementation](prompt-templates.md#prompt-3-ui-implementation)

---

## Phase Transition Rules

### Phase 1 → Phase 2

```
User: Please help me design a new screen...
Agent: [generates wireframe]
Agent: Here's the wireframe — please confirm the information architecture is correct?
User: OK / confirmed / good
Agent: ✅ Wireframe approved, moving to the critique phase...
```

**Required conditions**:
- [ ] Wireframe complete
- [ ] User has explicitly replied "OK" or equivalent

### Phase 2 → Phase 3

```
Agent: [proposes 3 alternative directions]
Agent: Please choose a direction, or suggest another idea.
User: Direction B / use the second one
Agent: ✅ Direction B selected — please fill in the Style Spec now...
User: [fills in Style Spec] OK
Agent: ✅ Critique approved, moving to the implementation phase...
```

**Required conditions**:
- [ ] Issue list reviewed
- [ ] User has selected a direction
- [ ] Style Spec filled in (or defaults used)
- [ ] User has explicitly replied "OK"

---

## Quick Commands

### Start a UI Task

Just say something like "help me design a login screen" — the agent will automatically start from Phase 1.

(Advanced/optional shortcut — the same effect via slash-style invocation:)

```
@uiux-agent please help me design [screen name]
```

### Skip Critique (emergencies only)

In a genuine emergency, just say something like "skip the critique this time, go straight to implementation."

(Advanced/optional shortcut:)

```
@uiux-agent skip critique, implement directly
```

⚠️ This produces a warning and requires the user to confirm again.

---

## FAQ

### Q: Can I skip Phase 1 and go straight to high-fidelity design?
**A**: No. Information architecture must be confirmed first, to avoid major rework later.

### Q: Do small changes also need the full three-phase flow?
**A**: For minor tweaks (spacing, color), use [Prompt 6: UI Polish](prompt-templates.md#prompt-6-ui-polish-fine-tuning) directly. If it involves layout changes, the three-phase flow is required.

### Q: Can I do the critique myself?
**A**: Yes, but it's recommended to bring in a third-party perspective — it catches blind spots more easily. Just say something like "review this design from a third-party perspective" (advanced/optional shortcut: `@uiux-agent`).

---

## Related Documents

- [UI/UX Rules](rules.md)
- [Style Spec Template](style-spec.template.md)
- [Prompt Templates](prompt-templates.md)
- [Installed Skills](installed-skills.md)

---

*Last updated: 2026-01-27*
