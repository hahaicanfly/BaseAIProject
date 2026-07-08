---
name: gen-app-map
description: Scans a project's entry points, routes, data layer, and state management to produce app-map.json (an AI-readable context primer) and app-map.html (a human-readable visualization), serving as a lightweight project map for new debug/refactor sessions. Tech-stack-agnostic template — fill in the scan-target table after forking to a specific project. Triggers on "gen-app-map" "生成地圖" "app map" "project map" "專案地圖".
---

# gen-app-map Skill

Scans the current state of a project and outputs a map of user flows and system structure, serving as a lightweight AI context primer for a new session.

> **Template note**: this skill is a **tech-stack-agnostic template**. After forking to a concrete project:
> 1. Replace the globs/regexes in the "Scan Target Table" below with the project's actual paths (the Android / React-Next / backend-API columns in the table are **examples only** and do not imply this project's tech stack).
> 2. Update the `Tech Stack` section in CLAUDE.md, then fill in this file's Step 0 "This Project's Scan Targets" table.

## Usage

```
/gen-app-map [optional: focus=<flow name>]
```

Examples:
- `/gen-app-map` — full map
- `/gen-app-map focus=auth` — focus on the auth flow

## Output

- `agent_docs/app-map.json` — AI-readable structure (context primer)
- `agent_docs/app-map.html` — human-readable visualization

Neither file is committed as part of routine commits — they're for the current session's use (or manual tagging).

---

## Execution Flow

### Step 0: Scan Target Table (must fill in after forking)

This skill scans four target categories. The table below gives common tech-stack glob/regex **examples**; in actual use, replace them with the project's real paths per CLAUDE.md's Tech Stack section:

| Category | Definition | Android example | React / Next example | Backend API example |
|------|------|--------------|--------------------|----------------|
| **entry-points** | App startup/mount entry | glob `**/AndroidManifest.xml` + regex `android.intent.action.MAIN`; glob `**/MainActivity.kt`, `**/*Application.kt` | glob `app/layout.tsx` (App Router) / `pages/_app.tsx` (Pages Router) / `src/main.tsx` (Vite/CRA entry) | glob `**/main.py`, `server.{js,ts}`, `cmd/*/main.go`; regex `app\s*=\s*(FastAPI|Express)\(` |
| **routes**<br>navigation/routing | Navigation definitions between screens/pages | glob `**/ui/route/*.kt`; regex `NavHost\(.*startDestination` | glob `app/**/page.tsx` (file-based routing); regex `<Route\s+path=` | glob `**/routes/*.{js,ts,py}`; regex `@app\.(get\|post\|put\|delete)\(|router\.(get\|post\|put\|delete)\(` |
| **data-layer** | Data access / external service calls | glob `**/*Dao.kt` + regex `@Dao`; glob `**/*ApiClient*.kt`, `**/*Service.kt` | glob `**/lib/api/*.ts`, `**/api/**/*.ts`; regex `useQuery\(|useMutation\(` | glob `**/models/*.py`, `prisma/schema.prisma`; regex `class \w+\(models\.Model\)|CREATE TABLE` |
| **state**<br>state management | Where UI/app state is held and flows | glob `**/viewmodel/*.kt`; regex `StateFlow<|MutableStateFlow` | glob `**/store/*.ts`, `**/slices/*.ts`; regex `createSlice\(|create\(\(set` (zustand) / `useContext\(` | glob `**/session.*`; regex `redis\.(set\|get)\(|SESSION_` |

**This project's scan targets** (fill in after forking, replacing the corresponding columns above):

| Category | Actual path/glob/regex |
|------|----------------------|
| entry-points | `{{fill in}}` |
| routes | `{{fill in}}` |
| data-layer | `{{fill in}}` |
| state | `{{fill in}}` |

### Step 1: Scan Scope

Read through each category per the Step 0 table and build a mental model:

- **entry-points** → find application startup points, list as `app.entryPoints`
- **routes** → find all navigation route definitions, map to `screens[].route`
- **data-layer** → find HTTP clients / DAOs / repositories / ORM models, map to `services[]`
- **state** → find state-holding units (ViewModel / store / session), map to `screens[].stateInputs`

**Actions / Intents (cross-stack common concept)**
- Find the unified entry point where "user action → triggers side effect" happens (sealed class / action creator / event handler), and list all subclasses/variants as `actions[]`

**Known issues**
- Reference `docs/learnings/ERRORS.md` (top 20 Active Lessons)
- Reference open items in the project's progress/backlog docs

### Step 2: Build app-map.json

Use the following tech-stack-agnostic schema:

```jsonc
{
  "app": {
    "name": string,
    "version": string,        // read from a version file: package.json / build.gradle.kts versionName / pyproject.toml etc.
    "generatedAt": string,    // ISO 8601
    "entryPoints": string[]   // e.g. ["MainActivity"] or ["app/layout.tsx"] or ["server.ts"]
  },
  "screens": [{
    "id": string,             // "screen.<module>.<name>", e.g. "screen.scan.main" or "page.dashboard.overview"
    "name": string,           // human-readable name
    "route": string | null,   // navigation route string, e.g. "scan", "/dashboard/[id]"
    "component": string | null, // UI component/render function name (Composable / React Component / Template)
    "stateInputs": string[],  // state keys, e.g. ["uiState.isLoading", "cartState.items"]
    "actions": string[],      // triggerable action ids
    "expectedNext": string[]  // expected next screen ids
  }],
  "actions": [{
    "id": string,             // action/intent/event name, e.g. "ScanImage"
    "type": "ui-event" | "domain-event" | "background-task",
    "sourceScreen": string | null,
    "calls": string[],        // service id, e.g. "api.menu.parse"
    "guard": string | null,
    "onSuccess": string | null,
    "onFailure": string | null,
    "notes": string | null
  }],
  "services": [{
    "id": string,             // "api.<module>.<method>" or "db.<module>.<method>"
    "kind": "http" | "db" | "other",
    "path": string | null,    // HTTP: "POST /api/v1/orders"; DB: "OrderDao.insert()" / "UserRepository.findById()"
    "ownedBy": string | null, // the class/module that implements this service
    "usedByActions": string[]
  }],
  "transitions": [{
    "from": string,
    "to": string,
    "via": string | null,     // action id
    "condition": string | null
  }],
  "knownIssues": [{
    "symptom": string,
    "suspects": string[],
    "evidence": string | null,
    "confidence": "low" | "medium" | "high"
  }]
}
```

**Coverage principle**:
- Prioritize the project's 3 main flows (fill in after forking, e.g. login/auth, core business flow, payment/subscription)
- Secondary: history, settings, sharing, and other peripheral flows
- Omit: pure UI animations, theme switching, and other actions that don't affect data flow

### Step 3: Build app-map.html

A single-page HTML with no external CDN dependency. Includes:

1. **Overview** — app name, entry points, generation time, summary of the 3 main flows
2. **Flow Diagram** — draw the core flows with Mermaid (inline `<script>`) or inline SVG; if the project already has an existing flow diagram (e.g. `agent_docs/diagrams/*.svg`), reference it directly via `<img>`
3. **Screens table** — route / component / stateInputs / actions / expectedNext
4. **Actions & Services table** — action → calls → service path
5. **Debug Hotspots** — up to 10 items, each with a "Copy as prompt" button
6. **Usage notes** — how to use this together with app-map.json in a new session

Style rules:
- `font-family: system-ui`, documentation style
- `.pill-critical/.pill-high/.pill-medium/.pill-low` color coding
- Implement the Copy button with `navigator.clipboard.writeText`
- Responsive, `max-width: 960px`

### Step 4: Write Files

```
agent_docs/app-map.json   ← full JSON
agent_docs/app-map.html   ← full HTML
```

On completion, output:
```
✓ Done: generated agent_docs/app-map.json (N screens, N actions, N services)
✓ Done: generated agent_docs/app-map.html
→ Next: preview with open agent_docs/app-map.html in a browser, or load app-map.json as a context primer in a new session
⚠ Note: this map is a point-in-time snapshot and is not auto-maintained; re-run /gen-app-map after major architecture changes
```

---

## Verification

- `app-map.json` must be valid JSON (verify with `python3 -m json.tool`)
- The number of `screens[]` should match the number of UI units actually found in Step 1 (no fabricating counts)
- `knownIssues[]` should have at least 3 entries (pulled from `docs/learnings/ERRORS.md` active lessons; if fewer than 3, leave it and note why)
- HTML must be openable standalone, with no network dependency
