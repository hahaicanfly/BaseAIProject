---
name: tdd-workflow
description: Runs the Red → Green → Refactor test-driven development cycle, for core business logic and high-reliability requirements; triggers when the user wants TDD development or mentions "測試驅動", "先寫測試".
---

# TDD Workflow Skill

Runs the Test-Driven Development cycle: Red → Green → Refactor.

## Usage

```
/tdd-workflow [feature description]
```

## TDD Cycle

```
┌─────────────────────────────────────┐
│                                     │
│  1. RED: write a failing test       │
│     ↓                               │
│  2. GREEN: write the minimum code   │
│     to pass                         │
│     ↓                               │
│  3. REFACTOR: improve code quality  │
│     ↓                               │
│  back to 1 (next test case)         │
│                                     │
└─────────────────────────────────────┘
```

## Execution Steps

### Phase 1: Define the Interface

```
// Define the public API first, no implementation yet
// Example (pseudocode)
interface Parser {
    parse(input): Result
}
```

### Phase 2: RED - Write the Test

```
// Write a test that will fail
test("parse should return result when valid input") {
    // Arrange
    parser = createParser()
    input = createTestInput()

    // Act
    result = parser.parse(input)

    // Assert
    assertSuccess(result)
}
```

Run the test, confirm it **fails** (compile error or assertion failure)

### Phase 3: GREEN - Minimal Implementation

```
// Write the minimum code to pass the test
class ParserImpl implements Parser {
    parse(input): Result {
        return Result.success(minimalData)
    }
}
```

Run the test, confirm it **passes**

### Phase 4: REFACTOR - Improve

```
// Improve the implementation while keeping tests passing
class ParserImpl implements Parser {
    constructor(dependency) { ... }

    parse(input): Result {
        // Improved implementation logic
        processed = dependency.process(input)
        return Result.success(processed)
    }
}
```

Run the test, confirm it **still passes**

### Phase 5: Next Test Case

Repeat Phase 2-4 until the feature is complete.

## TDD Conventions

- Test naming: `should_[behavior]_when_[condition]`
- Each test verifies exactly one behavior
- Include both positive and negative cases
- Use test doubles (fake/mock/stub) to isolate external dependencies

## Test Case Planning

```markdown
## [Feature] Test Cases

### Happy Path
- [ ] TC001: Valid input returns correct result
- [ ] TC002: Multiple formats handled correctly

### Edge Cases
- [ ] TC101: Empty input returns empty result
- [ ] TC102: Boundary values handled correctly

### Error Cases
- [ ] TC201: Invalid input throws the appropriate exception
- [ ] TC202: External errors are handled appropriately
```

## Coverage Targets

- Line coverage: >80%
- Branch coverage: >70%
- Core logic: 100%

## Test Commands

The specific command depends on the project's `CLAUDE.md` Quick Commands. Common conventions for reference:

```bash
# JavaScript/TypeScript
npm test
npm run test:coverage

# Python
pytest
pytest --cov

# Go
go test ./...
go test -cover ./...
```

Other languages/build systems follow the pattern set by the project's Quick Commands.

## Output Template

```markdown
## TDD Progress: [Feature Name]

### Current Status
- Phase: [RED/GREEN/REFACTOR]
- Test cases: [X/Y] complete

### Test Results
- Passed: X
- Failed: X
- Coverage: X%

### Next Step
[Next test case or refactoring target]
```

## Reference Documents

Check before starting whether the project has:
- CLAUDE.md (project conventions, including test commands)
- Test directory structure
- Test configuration files

## Verification Items

- **Output form**: a RED → GREEN → REFACTOR commit sequence (commit message matches the phase type).
- **Mechanical check**: for each RED commit, running the project's test command (CLAUDE.md Quick Commands) must **fail**; GREEN commit must pass; REFACTOR commit must **remain passing**.
- **ExecPlan integration**: append one line per commit to §6 Progress Log (including hash + phase marker).
- **Invariants reference**: `docs/architecture/invariants.md` INV-TEST-* section (defer to whatever entries the project has actually filled in; the template currently has only one example entry).

## References

- `.claude/agents/qa-engineer.md`
- `docs/architecture/invariants.md` INV-TEST-*
