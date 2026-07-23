# docs/reviews/ — Fresh-Context Verification Reports

> **Role**: version-controlled home for full acceptance/verification reports written by fresh-context reviewer agents (delegation-templates.md §6). The chat report carries only a summary + a path into this directory; the evidence lives here.
> **Why**: acceptance verdicts used to evaporate with the verifier subagent's context — "was this verified, by whom, against what evidence" was unanswerable afterwards. Now the verdict line (`VERDICT: PASS|FAIL <path>`) is machine-harvested into `state/verifications.jsonl` by `stop-retro-logger.py`, and the full evidence is committed here.

## Conventions

- Filename: `<YYYY-MM-DD>-<short-slug>.md` (e.g. `2026-07-22-f001-phase-b.md`).
- Content: deliverable under review, each acceptance criterion → PASS/FAIL → evidence (file:line or actual command output tail), suggestions (non-blocking) separated.
- The verifier agent may create exactly one new file here and must otherwise stay read-only.
- A `VERDICT: FAIL <path>` also lands in `docs/learnings/ERRORS.md` Pending Review automatically (`ACCEPTANCE_FAIL` finding) — do not add it there manually.
