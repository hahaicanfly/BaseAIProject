---
name: modularity
description: Modularity and reuse rules (non-standing, referenced on demand)
---

# Modularity Rules

> 2026-07-07 demoted from `.claude/rules/` to non-standing (code-design guidance doesn't meet the "needed for first decision" standing-rule bar).
> Reference entry points: code-review skill architecture dimension, tech-lead agent checklist.

## Core Principle

**All code design must consider cross-project reusability.**

## Module Partitioning Principle

### Shared Modules
Put the following in shared modules:
- Domain Models
- Business Logic
- Interfaces
- Utilities
- Platform-independent abstractions

### Platform/App-Specific Modules
Put the following in platform/app-specific modules:
- Platform API calls
- UI implementation
- Configuration
- Entry Points

## Design Guidelines

### 1. Dependency Inversion
```
// ✅ Depend on abstraction
class Parser(provider: Provider)  // interface

// ❌ Depend on concrete implementation
class Parser(google: GoogleProvider)  // concrete class
```

### 2. Interface First
```
// Define the interface first
interface Provider {
    process(input): Result
}

// Then implement concrete classes
class ProviderA implements Provider { ... }
class ProviderB implements Provider { ... }
```

### 3. Single Responsibility
```
// ✅ Single responsibility
class ImageProcessor { ... }  // only handles images
class TextParser { ... }      // only parses text

// ❌ Mixed responsibilities
class ImageTextProcessor { ... }  // does too much
```

### 4. Open/Closed
- Open for extension: easy to add a new Provider
- Closed for modification: no need to touch core code

## Avoid Reinventing the Wheel

Before implementing a new feature:
1. Check whether similar functionality already exists in the project
2. Search shared modules
3. Consider whether existing code can be extended
4. Search for an existing open-source solution

## Reusability Checklist

Ask yourself when adding code:
- [ ] Is this logic platform-independent? → put it in a shared module
- [ ] Does this class depend on a concrete implementation? → extract an interface
- [ ] Could this feature be used by other modules? → design it to be reusable
- [ ] Are there hardcoded values? → extract them into configuration
- [ ] Is it easy to test? → use dependency injection

## Naming Conventions

### Common Shared-Module Names
```
shared/
core/
common/
lib/
```

### Interface Naming
```
Provider, Repository, Service, Handler
Parser, Processor, Validator, Formatter
```

### Implementation Naming
```
[concrete name] + [interface name]
e.g.: GeminiProvider, LocalRepository
```
