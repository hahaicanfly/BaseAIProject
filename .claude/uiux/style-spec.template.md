# Style Spec Template

> **This spec must be filled in before implementing any screen, and reviewed by the UIUX Agent before implementation may begin.**
>
> Copy this template, fill in the specifics, and save as `design-system/pages/{screen-name}.md`

---

## Screen: [screen name]

### Basic Info

| Item | Content |
|-----|------|
| **Screen ID** | `screen_xxx` |
| **Flow** | e.g. Main flow |
| **Previous Screen** | e.g. HomeScreen |
| **Next Screen** | e.g. DetailScreen |
| **Designer** | @uiux-agent |
| **Developer** | Unassigned |
| **Status** | Wireframe / In Review / Approved / In Progress / Done |

---

## 1. User Goals

### Primary Goal
What does the user come to this screen to accomplish?
- [ ] Goal 1: _______
- [ ] Goal 2: _______

### Primary Action
What is the action the user is most likely / most expected to take?

| Action | Priority | Trigger |
|-----|-------|---------|
| ______ | Primary | Button / swipe / tap |
| ______ | Secondary | |
| ______ | Tertiary | |

### Success Metrics
- User completes ___ within ___ seconds
- Error rate below ___%
- Abandonment rate below ___%

---

## 2. Layout (Block Structure)

### Visual Structure Diagram (ASCII Wireframe)

```
┌─────────────────────────────────┐
│        [Top App Bar]            │  ← fixed / scrolling
├─────────────────────────────────┤
│                                 │
│        [Hero / Header]          │  ← block A
│                                 │
├─────────────────────────────────┤
│                                 │
│        [Main Content]           │  ← block B (scrollable)
│                                 │
│                                 │
├─────────────────────────────────┤
│        [Bottom Action]          │  ← fixed footer
└─────────────────────────────────┘
```

### Block Definitions

| Block | Content | Height/Ratio | Fixed? |
|-----|------|---------|---------|
| Top App Bar | Title, back, actions | 56px / 64px | Fixed |
| Hero | | | |
| Main Content | | flex | Scrollable |
| Bottom Action | | 80px | Fixed |

---

## 3. Components (Component List)

### Component List

| Component | Type | States | Props / Params |
|-----|-----|-----|-------------|
| `TopAppBar` | Navigation | default, scrolled | title, onBack, actions |
| `ItemCard` | Card | default, selected, disabled, loading | item, onSelect |
| `PrimaryButton` | Button | default, hover, pressed, disabled, loading | label, onClick, enabled |
| | | | |

### Per-Component State Details

#### Component: `[component name]`

| State | Visual Behavior | Trigger Condition |
|-----|---------|---------|
| Default | Baseline style | Initial |
| Hover | Slight background color change | Mouse enter |
| Pressed | scale 0.98, darker background | While clicking |
| Selected | Highlighted border, background change | After selection |
| Disabled | opacity 0.5, no interaction | enabled=false |
| Loading | Content replaced with spinner | isLoading=true |

---

## 4. Design Tokens

### Color

| Token | Hex | Purpose |
|-------|------|-----|
| `background` | #FFFBF5 | Page background |
| `surface` | #FFFFFF | Card background |
| `primary` | #_______ | Primary action, emphasis |
| `secondary` | #_______ | Secondary action |
| `onSurface` | #1C1B1F | Primary text |
| `error` | #B3261E | Error state |

### Typography

| Token | Size | Line Height | Weight | Purpose |
|-------|------|------|------|-----|
| `headlineLarge` | 32px | 40px | Bold | Page title |
| `titleLarge` | 22px | 28px | SemiBold | Section title |
| `titleMedium` | 16px | 24px | Medium | Card title |
| `bodyLarge` | 16px | 24px | Regular | Primary body text |
| `bodyMedium` | 14px | 20px | Regular | Secondary body text |
| `labelSmall` | 11px | 16px | Medium | Label, supporting text |

### Spacing

| Token | Value | Purpose |
|-------|-----|-----|
| `xs` | 4px | Fine spacing within an element |
| `sm` | 8px | Between related elements |
| `md` | 16px | Standard padding |
| `lg` | 24px | Between blocks |
| `xl` | 32px | Major block separation |
| `xxl` | 48px | Page section separation |

### Corner Radius

| Token | Value | Purpose |
|-------|-----|-----|
| `sm` | 8px | Small components (tag, chip) |
| `md` | 12px | Buttons |
| `lg` | 16px | Cards |
| `xl` | 24px | Large containers |
| `full` | 50% | Circular |

---

## 5. Edge Cases

### Empty State

**Trigger condition**: ______

**Visual presentation**:
```
┌─────────────────────────────────┐
│                                 │
│         [illustration/icon]     │
│                                 │
│      [title: prompt message]    │
│      [description: guidance]    │
│                                 │
│       [ CTA button ]            │
│                                 │
└─────────────────────────────────┘
```

---

### Error State

**Type 1: Network Error**
- Title: ______
- Description: ______
- Action: Retry / Offline mode

**Type 2: API Error**
- Title: ______
- Description: ______
- Action: Retry / Report issue

**Type 3: Validation Error**
- Display location: below the field
- Copy style: error color, small text

---

### Long Text Handling

| Element | Strategy | Max Lines |
|-----|------|---------|
| Title | Truncate + ellipsis | 2 lines |
| Description | Truncate + ellipsis | 3 lines |
| Price/number | No truncation, shrink font | 1 line |

---

## 6. Acceptance Criteria

### Functional Acceptance

- [ ] Primary action executes correctly
- [ ] All interactive components have correct state feedback
- [ ] Loading state displays correctly
- [ ] Error state has a retry mechanism
- [ ] Empty state has a guiding CTA

### Visual Acceptance

- [ ] Colors come from Design Tokens
- [ ] Spacing matches the Spacing Scale
- [ ] Typography matches the type hierarchy

### Usability Acceptance

- [ ] Contrast >= 4.5:1
- [ ] Touch targets >= 44-48px
- [ ] Fully keyboard operable
- [ ] All icons have aria-label / contentDescription

---

## Sign-off

| Role | Name/Handle | Date | Status |
|-----|----------|------|------|
| UIUX Agent | @uiux-agent | | Wireframe / In Review / Approved |
| Developer | | | Not started / In progress / Done |
| Reviewer | | | Pending / Passed / Rejected |

---

*Template version: v1.0*
*Last updated: 2026-01-27*
