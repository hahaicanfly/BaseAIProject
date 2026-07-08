# UI/UX Skills Status List

> This project uses Claude Code's built-in Skills system (`.claude/skills/`).
> Below are the preset UI/UX-related skills — confirm whether the actual implementation needs to be filled in before use.

---

## Preset UI/UX-Related Skills

### 1. ui-ux-pro-max

| Item | Value |
|------|-----|
| **Name** | ui-ux-pro-max |
| **Source** | Built into project (`.claude/skills/ui-ux-pro-max/`) |
| **Install Status** | ⚠️ Stub (needs implementation) |
| **Trigger Command** | `/ui-ux-pro-max` |

**Purpose**: Generate a complete design system (color palette, font pairing, UI style).

---

### 2. frontend-design

| Item | Value |
|------|-----|
| **Name** | frontend-design |
| **Source** | Built into project (`.claude/skills/frontend-design/`) |
| **Install Status** | ⚠️ Stub (needs implementation) |
| **Trigger Command** | `/frontend-design` |

**Purpose**: Produce high-quality UI components centered on design philosophy (Typography, Color, Motion).

---

## Preset UI/UX-Related Agents

### 1. ui-ux-designer

| Item | Value |
|------|-----|
| **Name** | ui-ux-designer |
| **Source** | Built into project (`.claude/agents/ui-ux-designer.md`) |
| **Model** | opus |
| **Trigger Words** | UI, UX, design, interface, screen, flow |

### 2. uiux-agent

| Item | Value |
|------|-----|
| **Name** | uiux-agent |
| **Source** | Built into project (`.claude/agents/uiux-agent.md`) |
| **Model** | sonnet |
| **Trigger Words** | wireframe, sketch, critique, three-phase workflow |

---

## How to Use

### Method 1: Call the Skill Directly
```
/ui-ux-pro-max
/frontend-design
```

### Method 2: Use an Agent (in conversation)
Mentioning a trigger word auto-activates it:
- "help me design a UI"
- "the UX flow for this screen..."
- "interface design suggestions"

---

*Last updated: 2026-05-28*
