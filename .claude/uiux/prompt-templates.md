# UI/UX Prompt Templates

> **Six copy-paste-ready prompts, aligned to the three-phase workflow (Wireframe → Critique → Implementation).**
>
> Each prompt includes an "input block" and an "output format" section.

---

## Prompt 1: Wireframe Generation

> **Purpose**: Generate a layout wireframe from requirements, focused only on information architecture — no final styling allowed.
>
> **Phase**: Phase 1 - Wireframe

### Prompt

```markdown
# Role
You are a UI/UX designer specializing in information architecture and layout design.

# Task
Based on the following requirements, produce a "pure layout wireframe."

## Input

### Screen Name
[Fill in the screen name, e.g. ProductListScreen]

### User Goal
[Fill in what the user wants to accomplish]

### Core Actions
[Fill in 1-3 primary actions]

### Data Content
[Fill in what data this screen will display]

### Constraints
[Fill in any technical or design constraints]

## Output Format Requirements

### 1. ASCII Wireframe
Draw the block structure in plain text, labeling the purpose of each block.

### 2. Block Description Table
List for each block: content, height/ratio, whether it's fixed.

### 3. Information Hierarchy
State the priority order of information: Primary > Secondary > Tertiary.

### 4. Preliminary Component List
List the component types needed (no styling).

## Prohibited
- ❌ Do not define visual details like colors, font sizes, or corner radii
- ❌ Do not write any code
- ❌ Do not discuss animation effects
- ❌ Do not choose a color scheme

Begin generating the wireframe.
```

---

## Prompt 2: Design Critique (Nitpicking)

> **Purpose**: Have Claude review a wireframe/design from a designer's perspective, identify issues, and propose alternatives.
>
> **Phase**: Phase 2 - Critique

### Prompt

```markdown
# Role
You are a senior UI/UX design reviewer, skilled at spotting "AI smell" and "template feel" design problems.

# Task
Review the following design wireframe/implementation, point out issues, and propose alternatives.

## Input

### Design Wireframe/Screenshot
[Paste the ASCII wireframe or describe the existing design]

### Design Goal
[What this design is meant to achieve]

### Target Users
[Describe the target user characteristics]

### Brand Tone
[Fill in brand style keywords, e.g. modern, friendly, professional, playful]

## Review Requirements

### 1. AI Smell Detection
Identify any elements that make the design look "AI-generated" or "templated"

### 2. Usability Issues
- Is the information hierarchy clear?
- Are touch targets large enough?
- Is the cognitive load too high?

### 3. Missing States
- Is a Loading state missing?
- Is an Empty state missing?
- Is an Error state missing?

## Output Format Requirements

### Issue List
| Issue | Severity | Location | Description |
|-----|-------|------|------|
| | High/Med/Low | | |

### 3 Alternative Directions
Propose 3 different improvement directions, each including:
- **Direction name**
- **Core change**
- **Expected effect**
- **Risk/trade-off**

### Recommendation
State which direction you recommend and why.
```

---

## Prompt 3: UI Implementation

> **Purpose**: Turn an approved wireframe + Style Spec into executable UI code.
>
> **Phase**: Phase 3 - Implementation

### Prompt

```markdown
# Role
You are a frontend engineer specializing in [fill in tech stack: React/Tailwind / Compose Multiplatform / SwiftUI / Vue].

# Task
Implement complete UI code based on the approved wireframe and Style Spec.

## Input

### Approved Wireframe
[Paste the ASCII wireframe]

### Style Spec
[Paste or reference the contents of style-spec.template.md]

### Tech Stack
[React + Tailwind / Compose Multiplatform (Kotlin) / SwiftUI / Vue + Tailwind]

### Design Token Source
[Reference the project's Design Token file path]

## Implementation Requirements

### 1. State Completeness
Must implement all interaction states:
- [ ] Default
- [ ] Hover (desktop)
- [ ] Focus (keyboard)
- [ ] Pressed/Active
- [ ] Disabled
- [ ] Loading

### 2. Accessibility (a11y)
- [ ] All icons have aria-label / contentDescription
- [ ] Contrast ratio >= 4.5:1
- [ ] Touch target >= 44-48px
- [ ] Fully keyboard operable
- [ ] Respects prefers-reduced-motion

### 3. Responsive
- [ ] Mobile (< 640px)
- [ ] Tablet (640-1024px)
- [ ] Desktop (> 1024px)

### 4. Edge Cases
- [ ] Empty state
- [ ] Error state
- [ ] Loading state (Skeleton)
- [ ] Long text handling

## Prohibited
- ❌ Do not use hardcoded colors/spacing
- ❌ Do not omit any state
- ❌ Do not ignore a11y
- ❌ Do not add unrequested features
```

---

## Prompt 4: Design Token Extraction

> **Purpose**: Extract Design Tokens from a reference site/screenshot.
>
> **Phase**: Any phase (design research)

### Prompt

```markdown
# Role
You are a design systems expert, skilled at analyzing visual designs and extracting reusable Design Tokens.

# Task
Analyze the following reference material and extract Design Tokens.

## Input

### Reference Source
[Paste one of the following]
- Website URL
- Screenshot description
- Figma/design file link

### Extraction Focus
- [ ] Color system
- [ ] Typography system
- [ ] Spacing system
- [ ] Corner radius/shape
- [ ] Shadow/elevation
- [ ] Animation timing

### Target Tech Stack
[CSS Variables / Tailwind / Compose / SwiftUI]

## Output Format Requirements

### 1. Color Tokens
```css
:root {
  --color-primary: #______;
  --color-secondary: #______;
  --color-background: #______;
  --color-surface: #______;
  --color-error: #______;
}
```

### 2. Typography Tokens
Complete definitions of font size, line height, and font weight.

### 3. Spacing Tokens
Complete definitions of xs / sm / md / lg / xl / xxl.

### 4. Application Example
Show how these tokens apply to an actual component.
```

---

## Prompt 5: Microcopy Generation

> **Purpose**: Generate interface copy with a consistent tone (buttons, error messages, empty states).
>
> **Phase**: Any phase

### Prompt

```markdown
# Role
You are a UX writer specializing in interface copy and microcopy design.

# Task
Write copy for the following interface elements, ensuring a consistent tone.

## Input

### Brand Voice
[Describe how the brand speaks, e.g. friendly, professional, playful, concise]

### Target Users
[Describe user background]

### Elements Needing Copy
[List buttons, error messages, empty states, confirmation dialogs, etc.]

### Language
[Traditional Chinese / English / Bilingual]

## Output Format

### Button Copy
| Action | Copy | Alternative |
|-----|------|---------|

### Error Messages
| Error Type | Title | Description | Action |
|---------|------|------|------|

### Empty States
| Scenario | Title | Description | CTA |
|-----|------|------|-----|
```

---

## Prompt 6: UI Polish (Fine-tuning)

> **Purpose**: Refine animation, hover/focus, and spacing — no major changes to information architecture allowed.
>
> **Phase**: Post-Phase-3 (polish)

### Prompt

```markdown
# Role
You are a detail-oriented UI engineer specializing in animation and interaction details.

# Task
Polish the following UI to improve visual quality and interaction experience.

## Input

### Existing Code
[Paste the component code that needs polishing]

### Polish Scope
- [ ] Animation / Transition
- [ ] Hover effects
- [ ] Focus effects
- [ ] Spacing adjustments
- [ ] Loading animation

### Target Feel
[Describe the desired feeling after optimization: smoother, more refined, more lively]

## Constraints

### ❌ Prohibited
- Do not change the information architecture (block order, content structure)
- Do not add/remove features
- Do not change the component API

### ✅ Allowed
- Add/adjust animation (150-300ms)
- Adjust hover/focus/active states
- Fine-tune spacing (within ±4px)
- Add Skeleton Loading

## Output

1. Change list (before vs. after)
2. Code diff
3. Performance notes (whether GPU-accelerated properties are used)
4. Reduced Motion handling
```

---

## Usage Recommendations

### Workflow Mapping

| Phase | Prompt Used |
|-----|--------------|
| Phase 1: Wireframe | Prompt 1 (Wireframe) |
| Phase 2: Critique | Prompt 2 (Design Critique) |
| Phase 3: Implementation | Prompt 3 (UI Implementation) |
| Polish | Prompt 6 (UI Polish) |
| Research | Prompt 4 (Token Extraction) |
| Any phase | Prompt 5 (Microcopy) |

---

*Last updated: 2026-01-27*
