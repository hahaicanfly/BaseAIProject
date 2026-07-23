# docs/research/ — Strategy & Market Research Reports

> **Role**: version-controlled filing point for strategy/market/competitive/data research
> produced by `pm` / `market-researcher` / `competitive-analyst` / `data-analyst` (and any
> agent doing product-strategy research). Without a fixed landing point, research findings
> evaporate with the producing agent's context and product-strategy hallucinations have
> nowhere to be caught — this directory plus the Document Reviewer Checklist
> (`.claude/protocols/review-protocol.md`) closes that gap (ExecPlan F-001 Phase C4c, O14).

## Naming Convention

```
docs/research/<YYYY-MM-DD>-<slug>.md
```

- Date = the day the report was produced (not the event/data date it discusses).
- Slug = short kebab-case topic, e.g. `2026-07-23-delivery-market-tam.md`.
- One file per report. Do not append to a prior day's file — write a new dated file and,
  if it supersedes an earlier one, note that in the new file's opening paragraph.

## Required Sections (every report in this directory must include both)

- **`### 假設-證據表` (Hypothesis-Evidence Table)** — every non-trivial claim the report
  relies on, in the fixed format defined in each research agent's Output Format
  (`.claude/agents/pm.md`, `market-researcher.md`, `competitive-analyst.md`,
  `data-analyst.md`): 假設 / 證據 (URL or file:line, else `[UNCONFIRMED: ...]`) / 證據型別
  (實測數據/外部引述/模型推論) / 信心 (高/中/低) / 可證偽檢驗.
- **`### Sources`** — every cited source with a verifiable URL or `file:line`; a claim
  citing neither must be tagged `[UNCONFIRMED: <claim>]` inline
  (`.claude/protocols/handoff-protocol.md` "Inline Auxiliary Markers").

A report missing either section fails review on sight — see Review below.

## Review

Every report in this directory is reviewed against the **Document Reviewer Checklist**
in `.claude/protocols/review-protocol.md` §"Document Reviewer Checklist" (dead-ref scan,
per-claim sourcing, spot-fetch of cited URLs, facts/inference separation, hypothesis-evidence
table completeness, second-opinion attachment for decisions feeding architecture/security/
irreversible calls). The full review report is written to `docs/reviews/<YYYY-MM-DD>-<slug>.md`
(see `docs/reviews/README.md` for that directory's conventions); the chat-facing summary
carries only the `VERDICT: PASS|FAIL <path>` line.

## Relationship to PDR (Product Decision Record)

A research report in this directory is *evidence*, not a decision. When a research finding
here is used to justify a P0 product/feature decision, that decision must additionally be
recorded as a PDR using `docs/decisions/PDR-template.md`, which cites back into the relevant
research report(s) by path. See `.claude/agents/pm.md` Output Format for when a PDR is
mandatory.
