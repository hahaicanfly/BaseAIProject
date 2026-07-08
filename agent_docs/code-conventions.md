# Code Conventions

> **Role**: This file defines the project's code style and naming conventions.
> **Fill-in instructions**: Replace `{{fill in language/framework}}` sections with the tech stack actually used by the project.
> **Audience**: tech-lead agent, code-reviewer agent, developers.

---

## Naming Conventions

> TODO: fill in actual naming conventions based on your language.

| Concept | Convention | Example |
|------|------|------|
| Class / Interface | PascalCase | `UserService`, `OrderRepository` |
| Function / Method | camelCase or snake_case (per language) | `parseOrder()`, `parse_order()` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private property | `_` prefix (per language convention) | `_internalState` |
| File | per language convention | `UserService.ts` / `user_service.py` |

---

## Directory Structure

> TODO: fill in the project's actual directory structure.

```
src/
├── domain/          # Domain layer (core business logic)
│   ├── models/      # Data models
│   └── repositories/# Repository interfaces
├── data/            # Data layer
│   ├── remote/      # Remote data sources (API client)
│   └── local/       # Local data sources (DB / cache)
├── ui/              # Presentation layer (Web / App UI)
│   ├── pages/       # Page components
│   └── components/  # Reusable UI components
└── utils/           # Utility functions
```

---

## Code Style

### Function design principles

- **Single responsibility**: a function does one thing, ≤ 20 lines is ideal
- **Prefer pure functions**: minimize side effects, easy to test
- **Explicit return types**: don't rely on implicit inference

```
// ✅ Short, single responsibility
function parseOrder(raw: string): Order { ... }

// ❌ Too long, unclear responsibility
function doEverything(...): any { ... 200 lines ... }
```

### Error handling

- Use explicit error types (Result / Either / sealed class)
- Don't use bare `try/catch` to swallow errors
- Error messages should be diagnostic (include context, not just "error")

### Dependency injection

- Constructor injection (don't `new` concrete implementations inside functions)
- Depend on interfaces, not concrete classes
- Easy to swap out for testing

---

## Testing Conventions

### Test naming

```
describe("OrderParser") {
  it("should return parsed result when input is valid")
  it("should throw when input is malformed")
}
```

### Test structure (Given / When / Then)

```
// Given (Arrange)
const input = createTestInput()

// When (Act)
const result = parser.parse(input)

// Then (Assert)
expect(result).toEqual(expected)
```

### Test scope

- Unit tests: pure functions, business logic
- Integration tests: API layer, database operations (don't mock the DB)
- E2E (as needed): critical user flows

---

## Git Commit Convention

### Format

```
<type>(<scope>): <subject>

<body> (optional)

<footer> (optional: Closes #NNN)
```

### Type

| type | purpose |
|------|------|
| `feat` | new feature |
| `fix` | bug fix |
| `docs` | documentation update |
| `style` | formatting change (no logic impact) |
| `refactor` | refactor (no new feature, no bug fix) |
| `test` | tests |
| `chore` | build / tooling / dependency upgrade |

### Example

```
feat(auth): add OAuth2 login flow

- Implement token exchange endpoint
- Add refresh token rotation
- Add unit tests for token validation

Closes #42
```

---

## {{fill in language/framework}}-Specific Conventions

> TODO: fill in your tech-stack-specific conventions.
>
> Examples:
> - **React**: hooks naming `use*`, no direct DOM manipulation
> - **Python**: PEP 8, type hints required, docstring format
> - **Kotlin**: coroutines instead of threads, Flow for streaming data
> - **Swift**: `@MainActor` for UI updates, Combine / async-await

---

## Anti-patterns

- Magic numbers (use named constants instead of `42`, `3600`)
- Deep nesting (more than 3 levels of if/for → consider early return or extracting a function)
- Abbreviated names (`usr`, `btn`, `tmp`)
- Unnecessary comments (don't comment what the code already expresses)
- Empty catch blocks (log the error at minimum)
