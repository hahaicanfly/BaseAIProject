---
name: spectra-amplifier
description: Strengthens a thin requirements description or PRD draft into a complete spec where every requirement carries verifiable acceptance criteria; triggers when the user wants to strengthen a spec or mentions "spectra-amplifier" "acceptance criteria". Plain-language: 這份規格寫得不夠仔細、每一條都要補上驗收標準(已有草稿要加強,不是從零開始想新東西) / "this draft is too thin, every item needs acceptance criteria filled in" (strengthening an existing draft, not dreaming up something from a blank page).
---

# Skill: spectra-amplifier

> **Purpose**: Takes a thin spec (requirements description, PRD draft, feature idea) and outputs a strengthened spec — every requirement has acceptance criteria, and every AC maps to a verifiable item.
> **Trigger**: `/spectra-amplifier [spec description / file path]`
> **Theoretical basis**: Spectra (Long-ge's SDD format) × Speckit (testability) × Teddy's five-layer spec method

---

## Why Spectra-Amplifier Is Needed

Problem: specs written by AI are usually "thin" — they describe the feature but not how to verify the feature is correct.
This leads to:
- ExecPlan §5 Verification Strategy can't produce concrete negative test cases
- PR review can't determine "does this change actually satisfy the requirement"
- Lessons in ERRORS.md can't be traced back to "which spec design flaw caused this bug"

Three properties of a strong spec:
1. **Traceable**: every requirement traces to a design, every design traces to an implementation, every implementation traces to a test
2. **Testable**: every requirement has concrete pass/fail criteria
3. **Bounded**: explicitly states what is out of scope, avoiding scope creep

---

## Five-Layer Amplification Framework (Teddy × Speckit × Spectra)

```
Layer 5: Verification      ← How do we know it's done right? (tests / hooks / INV-*)
    ↑
Layer 4: Implementation    ← How to build it? (tech choices, API, data model)
    ↑
Layer 3: Design            ← What architecture? (module boundaries, interfaces, flow diagrams)
    ↑
Layer 2: Requirements      ← What's needed? (functional + non-functional requirements)
    ↑
Layer 1: Context           ← Why do it? (problem statement, stakeholders, success metrics)
```

Every layer must be able to answer "how?" downward and "why?" upward — if it can't, that layer of the spec has a gap.

---

## Execution Steps

### Step 1: Parse the Input Spec

Read the spec provided by the user (text description or document).
Identify which layers (L1–L5) are currently covered, and which are missing or thin.

### Step 2: Layer-by-Layer Amplification

#### L1 — Context Amplification

Fill in:
```
Problem statement: [what problem does the user face?]
Target users: [who?]
Success metrics: [how do we measure success after completion? quantify it]
Out of Scope: [explicitly state what won't be done]
```

#### L2 — Requirements Amplification

For each functional requirement, fill in:
```
REQ-NNN: [requirement description]
  Priority: P0 / P1 / P2
  Functional Requirements (FR): ...
  Non-Functional Requirements (NFR): [performance/reliability/security requirements]
  Acceptance Criteria:
    - AC-1: [Given ... When ... Then ...]
    - AC-2: [Given ... When ... Then ...]
  Edge Cases:
    - EC-1: [edge case description]
```

#### L3 — Design Amplification

Fill in:
```
Architecture decision: [which option was chosen, why not the others]
Module boundaries: [which modules in domains.md are involved]
API interface draft: [endpoint / function signature]
Data model changes: [if there's a schema change, list the fields]
Flow diagram (Mermaid):
  sequenceDiagram or flowchart LR
  [describe the main flow]
```

#### L4 — Implementation Amplification

Fill in:
```
Tech choices: [framework/library/tool]
Key implementation notes:
  - [note 1]
  - [note 2]
ExecPlan references:
  docs/plans/active/F-NNN-slug.md §3 Constraints must reference:
    - INV-[NS]-[NNN] (security-related)
    - domains.md [change-type row]
```

#### L5 — Verification Amplification (most important)

For each AC, produce a corresponding verification:
```
AC-1 → Test type: [unit / integration / e2e / manual]
       Test command: [concrete command]
       Golden Path: [normal-flow verification steps]
       Negative Test: [steps that deliberately trigger failure]
       Corresponding INV-*: [if any]
       Corresponding ExecPlan §5 verification item: [copy into ExecPlan]
```

### Step 3: Output the Amplified Spec

Output format:

```markdown
# Spec: [feature name]

## L1 Context
[amplified problem statement, success metrics, Out of Scope]

## L2 Requirements
[REQ-NNN list, with AC + EC]

## L3 Design
[architecture decisions, interface draft, Mermaid flow diagram]

## L4 Implementation Notes
[tech choices, implementation notes, INV-* references]

## L5 Verification Matrix
| AC | Test Type | Command | Golden Path | Negative |
|----|---------|------|------------|---------|
| AC-1 | ... | ... | ... | ... |

## ExecPlan §5 Draft (paste directly)
[auto-generated §5 Verification Strategy]
```

### Step 4: Gap Flagging

If the input spec is seriously lacking in some layer, output:
```
[SPEC_GAP: L3-Design] Missing module boundary definitions.
Before implementation, recommend running /feature-pipeline to complete the architecture design first.
```

---

## Interface with ExecPlan

The amplified spec can be used directly for:
- ExecPlan §1 Goal (extract one sentence from L1 Context)
- ExecPlan §3 Constraints (from L4's INV-* references)
- ExecPlan §5 Verification Strategy (from the L5 verification matrix)

Recommended workflow:
```
/spectra-amplifier [feature description]
    ↓
Confirm the L5 verification matrix
    ↓
Open an ExecPlan, copy in §5 content
    ↓
Proceed to feature-pipeline or start development directly
```

---

## Speckit Quality Score (included in output)

After each amplification, output a Speckit quality score:

| Dimension | Max Score | Description |
|------|------|------|
| Traceability (L1-L5 traceable) | 20 | Every layer can answer up/down |
| Testability (AC testable) | 30 | AC has concrete Given/When/Then |
| Boundedness (Out of Scope explicit) | 20 | Has an explicit not-doing list |
| Completeness (no missing edge cases) | 30 | EC covers the main boundaries |

Score < 70 → recommend strengthening before starting implementation.
