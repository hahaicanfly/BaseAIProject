# {{PROJECT_NAME}} — Technical Reference

> **Role**: This file is the AI agent's technical encyclopedia. Each agent should consult the relevant section before executing a task.
> **Update policy**: Sync after major architecture changes; accuracy over immediacy.
> **Usage**: ExecPlan §2 Context references specific section anchors (e.g. `TECHNICAL-REFERENCE.md §3`).

### Minimum Viable Fill-In

Fill in the following 5 items and this file unlocks "must-read" status in `CLAUDE.md`; the remaining placeholders can be filled in later:

1. Core mission in one sentence
2. Tech stack, 4 cells: frontend / backend / database / deployment
3. Top-level module list
4. API base URL (dev + production)
5. Authentication method

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Architecture Design](#3-architecture-design)
4. [Core Modules](#4-core-modules)
5. [API Spec](#5-api-spec)
6. [Data Models](#6-data-models)
7. [Authentication & Authorization](#7-authentication--authorization)
8. [Testing Strategy](#8-testing-strategy)
9. [Deployment & Environments](#9-deployment--environments)
10. [Known Limitations & TODO](#10-known-limitations--todo)

---

## 1. Project Overview

> TODO: fill in the project's core mission, target users, and main features.

**Core mission**: {{fill in a one-sentence description}}

**Main features**:
- {{feature 1}}
- {{feature 2}}
- {{feature 3}}

**Current version**: {{fill in version number}}

---

## 2. Tech Stack

> TODO: fill in the technologies actually used.

| Layer | Technology | Version | Notes |
|------|------|------|------|
| Frontend | {{React / SwiftUI / Jetpack Compose / ...}} | {{version}} | |
| Backend | {{Node.js / Python / Go / ...}} | {{version}} | |
| Database | {{PostgreSQL / MySQL / SQLite / ...}} | {{version}} | |
| AI Model | {{Claude API / Gemini / ...}} | {{version}} | |
| Deployment | {{Vercel / AWS / GCP / ...}} | — | |
| CI/CD | {{GitHub Actions / GitLab CI / ...}} | — | |

**Local dev dependencies**:
```bash
# TODO: fill in dev environment setup commands
# e.g.:
# npm install
# cp .env.template .env
# docker-compose up -d
```

---

## 3. Architecture Design

> TODO: fill in an architecture diagram and description. See `docs/architecture/domains.md` for details.

```
┌─────────────────────────────────────────────────┐
│                 {{PROJECT_NAME}}                  │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────┐    ┌──────────────────────────┐ │
│  │   Frontend   │    │        Backend           │ │
│  │              │◄───┤                          │ │
│  │  (UI Layer)  │    │  (API / Business Logic)  │ │
│  └──────────────┘    └──────────────────────────┘ │
│                                 │                  │
│                      ┌──────────┴──────────┐       │
│                      │     Data Layer      │       │
│                      │   (DB / Storage)    │       │
│                      └─────────────────────┘       │
└─────────────────────────────────────────────────┘
```

**Design principles**:
- Dependency inversion: upper layers depend on interfaces, not concrete implementations
- Single responsibility: each module has a clear responsibility
- Open/closed: open for extension, closed for modification

---

## 4. Core Modules

> TODO: fill in each module's responsibility, inputs/outputs, and key functions.

### 4.1 {{module name}}

**Responsibility**: {{fill in responsibility description}}

**Key interface**:
```
TODO: fill in interface definition
```

**Dependencies**: {{list other modules this depends on}}

---

### 4.2 {{module name}}

**Responsibility**: {{fill in responsibility description}}

**Key interface**:
```
TODO: fill in interface definition
```

---

## 5. API Spec

> TODO: fill in API endpoints, request/response formats, authentication method.

### Base URL

```
Dev: http://localhost:{{port}}
Production: https://{{your-domain}}
```

### Authentication method

```
Authorization: Bearer <token>
```

### Endpoint list

| Method | Path | Description | Auth |
|--------|------|------|------|
| GET | `/api/health` | Health check | No |
| POST | `/api/{{resource}}` | {{description}} | Yes |
| GET | `/api/{{resource}}/:id` | {{description}} | Yes |

### Error format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

---

## 6. Data Models

> TODO: fill in core data models.

### {{Model name}}

```
{
  id: string (UUID)
  created_at: ISO 8601
  updated_at: ISO 8601
  // TODO: fill in other fields
}
```

---

## 7. Authentication & Authorization

> TODO: fill in the authentication flow, token management, permission model.

**Authentication method**: {{JWT / OAuth2 / Session / ...}}

**Token lifetime**: {{fill in}}

**Permission model**:
- {{role 1}}: {{permission description}}
- {{role 2}}: {{permission description}}

---

## 8. Testing Strategy

> TODO: fill in test framework, coverage requirements, test execution commands.

**Test framework**: {{Jest / pytest / JUnit / ...}}

**Execution commands**:
```bash
# Unit tests
{{fill in command}}

# Integration tests
{{fill in command}}

# All tests
{{fill in command}}
```

**Coverage requirement**: {{fill in, e.g. "core domain logic ≥ 80%"}}

---

## 9. Deployment & Environments

> TODO: fill in environment variables, deployment process, environment differences.

### Environment variables

| Variable | Required | Description | Example |
|------|------|------|------|
| `API_KEY` | Yes | Primary API key | `sk-...` |
| `DATABASE_URL` | Yes | Database connection string | `postgres://...` |
| `NODE_ENV` | Yes | Environment | `development` / `production` |

### Deployment process

```bash
# TODO: fill in deployment steps
# 1. Build
# 2. Test
# 3. Deploy
```

### Environment differences

| Config item | Dev | Test | Production |
|--------|------|------|------|
| Database | Local | Test DB | Production DB |
| Log level | DEBUG | INFO | WARN |
| AI model | haiku (cost-saving) | sonnet | sonnet/opus |

---

## 10. Known Limitations & TODO

> Record known tech debt, temporary limitations, and pending improvements.

| Item | Priority | Description | Expected resolution |
|------|--------|------|---------|
| {{limitation 1}} | High/Medium/Low | {{description}} | {{version or date}} |

---

## Referenced By

- ExecPlan §2 Context (referencing specific section anchors)
- `.claude/agents/*.md` frontmatter `always_read`
- `agent_docs/AI-TEAM-REGISTRY.md`
