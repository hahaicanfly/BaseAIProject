# {{PROJECT_NAME}} — Domain Architecture

> **Role**: This file defines the system's domain boundaries and change-impact assessment table.
> **Audience**: architect agent, code-reviewer agent, referenced by ExecPlan §3 Constraints.

---

## System Architecture Overview

> TODO: fill in your project's architecture description

```
┌─────────────────────────────────────────────────┐
│                  {{PROJECT_NAME}}                 │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────┐    ┌──────────────────────────┐ │
│  │   Frontend   │    │        Backend           │ │
│  │              │◄───┤                          │ │
│  │  (Web / App) │    │  (API / Business Logic)  │ │
│  └──────────────┘    └──────────────────────────┘ │
│                                 │                  │
│                      ┌──────────┴──────────┐       │
│                      │     Data Layer      │       │
│                      │   (DB / Storage)    │       │
│                      └─────────────────────┘       │
└─────────────────────────────────────────────────┘
```

---

## Domain Module List

> TODO: fill in your project's actual modules

| Module | Responsibility | Depends on | Blast radius |
|------|------|------|---------|
| `core/` | Core business logic | — | High (all other modules depend on it) |
| `api/` | API layer | core | Medium |
| `ui/` | UI components | api | Low (affects only the frontend) |
| `infra/` | Infrastructure (DB/Cache) | — | High (change with care) |

---

## Change-Impact Assessment Table

ExecPlan §3 Constraints must reference the corresponding row of this table.

| Change type | Affected modules | Extra verification required | Needs multi-agent review? |
|---------|---------|--------------|--------------------------|
| API schema change | api, ui, tests | All clients synchronized | Yes |
| Database schema change | infra, core | Migration + rollback plan | Yes |
| New auth mechanism | api, core | security-reviewer | Yes |
| New UI component | ui | a11y + responsive check | No |
| Dependency upgrade | all | Full build + test suite | Case-by-case |
| Config change | infra | Environment consistency check | No |

---

## Cross-Module Dependency Rules

1. **ui** may only depend on **api** (must not depend directly on **core** or **infra**)
2. **api** may only depend on **core** (must not depend on **ui**)
3. **core** depends on no upper-layer module
4. **infra** is depended on only by **core**

> Fill in your actual dependency rules; violations count as INV-ARC-* violations.

---

## Where This File Is Referenced

- ExecPlan §3 Constraints (every ExecPlan must reference the relevant row)
- `.claude/agents/architect.md`
- `docs/plans/PLANS.md` §5
