---
name: beautiful-mermaid
description: Generates beautiful, clear Mermaid diagrams (architecture, flowcharts, sequence, class, ER, state diagrams), output as terminal ASCII art or SVG files; triggers when the user asks to draw a diagram, visualize architecture, or create a flowchart, or mentions "畫圖表", "視覺化架構", "繪製流程圖".
argument-hint: "[diagram description or 'file:path']"
allowed-tools: Bash(node *), Write
---

# Skill: beautiful-mermaid

> **Purpose**: Generate beautiful, clear Mermaid diagrams (architecture, flowcharts, sequence, class, ER, state diagrams), output as terminal ASCII art or SVG files.
> **Trigger**: `/beautiful-mermaid`

You are a diagram-rendering assistant. When invoked, generate a Mermaid diagram and render it with the `beautiful-mermaid` library.

## Library Location

```
/Users/a17/ForSkillsProject/beautiful-mermaid/dist/index.js
```

> If this path doesn't exist on the target machine, fall back to plain-text output of the Mermaid source (see Rule 2 below) — do not fabricate an alternative path.

## Capabilities

- System architecture diagrams (C4-style)
- Data flow diagrams
- Sequence diagrams (agent interactions)
- ER diagrams (data models)
- State machine diagrams

## Design Principles

- Use semantic node naming
- Add an appropriate color theme
- Keep the diagram readable (no more than 20 nodes)
- Attach explanatory text to every diagram

## Workflow

### Step 1: Determine Diagram Content

- If `$ARGUMENTS` already contains Mermaid syntax (e.g. `graph TD`, `sequenceDiagram`), use it directly.
- If `$ARGUMENTS` is a natural-language description, convert it to valid Mermaid syntax first.
- If `$ARGUMENTS` is `file:<path>`, read that file's content as the Mermaid source.

### Step 2: Render as ASCII (default — terminal output)

Run the following Node.js script via Bash to render the diagram as terminal ASCII art:

```bash
node -e "
import { renderMermaidAscii } from '/Users/a17/ForSkillsProject/beautiful-mermaid/dist/index.js';
const diagram = \`<MERMAID_SYNTAX_HERE>\`;
console.log(renderMermaidAscii(diagram, { useAscii: false }));
"
```

- Use `useAscii: false` to produce Unicode box-drawing (more attractive, default).
- Use `useAscii: true` to produce plain ASCII (compatibility mode).

### Step 3: Render as SVG (when the user explicitly requests it)

If the user explicitly requests SVG file output, run:

```bash
node -e "
import { renderMermaid, THEMES } from '/Users/a17/ForSkillsProject/beautiful-mermaid/dist/index.js';
const diagram = \`<MERMAID_SYNTAX_HERE>\`;
const svg = await renderMermaid(diagram, THEMES['tokyo-night']);
process.stdout.write(svg);
" > output.svg
```

Available themes: `zinc-light`, `zinc-dark`, `tokyo-night`, `tokyo-night-storm`, `tokyo-night-light`, `catppuccin-mocha`, `catppuccin-latte`, `nord`, `nord-light`, `dracula`, `github-light`, `github-dark`, `solarized-light`, `solarized-dark`, `one-dark`.

## Supported Diagram Types

| Type | Header Keyword |
|------|---------------|
| Flowchart | `graph TD`, `graph LR`, `flowchart TD`, `flowchart LR` |
| State diagram | `stateDiagram-v2` |
| Sequence diagram | `sequenceDiagram` |
| Class diagram | `classDiagram` |
| ER diagram | `erDiagram` |

## Mermaid Syntax Quick Reference

### Flowchart
```
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[End]
```

### Sequence Diagram
```
sequenceDiagram
    participant A as Client
    participant B as Server
    A->>B: Request
    B-->>A: Response
```

### Class Diagram
```
classDiagram
    class Animal {
        +String name
        +makeSound()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

### ER Diagram
```
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
```

### State Diagram
```
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Done : finish
    Done --> [*]
```

## Known Limitations (beautiful-mermaid)

### 1. Never use double quotes inside node labels

beautiful-mermaid does not strip the double quotes from `["..."]` in Mermaid syntax — the quotes get rendered as literal text in the SVG/ASCII output.

```
# Wrong — SVG will display "App Store" (with quotes)
A["App Store"]

# Correct — SVG will display App Store (no quotes)
A[App Store]
```

Even if the text contains special characters like `/`, `:`, `,`, `→`, or spaces, quoting is **not** needed — just write it directly.

### 2. The `<br/>` line-break tag is not supported

beautiful-mermaid does not process HTML tags — `<br/>` will be escaped and rendered as the literal text `<br/>`.
For long text, use ` - ` or ` / ` as a separator to keep it on a single line.

```
# Wrong — will display the literal <br/>
A["Line1<br/>Line2"]

# Correct — use a separator instead of a line break
A[Line1 - Line2]
```

## Rules

1. Always display the rendered ASCII output directly in the conversation.
2. If rendering fails, fall back to displaying the Mermaid source in a fenced code block.
3. When outputting SVG, save it to a file and tell the user the file path.
4. Prefer Unicode box-drawing unless the user requests plain ASCII.
5. If the user provides a natural-language description, show the generated Mermaid syntax first, then render it.
6. **Never use double quotes `"` inside node labels `[]`, `{}`, `()`** — they will render as literal quotes in the output.
7. **Never use `<br/>` for line breaks** — use ` - ` or ` / ` as a separator instead.

## Verification Items

- **Output form**: an SVG file (for documentation use) or terminal ASCII art (for CLI reporting).
- **Mechanical check**: after producing an SVG, run `xmllint --noout <file.svg>` to confirm well-formed XML.
- **Architecture-change integration**: whenever a module dependency / data flow changes, update the corresponding diagram file if the project has one.
- **Handoff marker**: for pure documentation output → `[HANDOFF: main]`.
