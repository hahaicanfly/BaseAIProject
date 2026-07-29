# G. Letter to Future Sessions

> Written 2026-07-04, one-off architecture session by Fable 5. You (the reader) are probably Sonnet, Opus, or Haiku.
> This letter covers three things the user never asked about but that matter most, how this institution will decay, and the work left unfinished.

## I. Three things the user never asked, but that matter most

### 1. Do not trust any defense that has not been black-box tested
This project's 5 hooks had never executed since deployment (no execute permission + wrong exit code in the guard — double failure), yet CLAUDE.md kept claiming "enforce mode interception". **A document saying a defense exists ≠ the defense existing.** Every time you change a hook, and every time you fork this template into a new project, run the smoke test in `harness-maintenance.md` §4.
Extended alert: the same-named hooks in the parent project `MenuProject/Menu-Android` very likely share the same problem (extracted from the same source) — **unverified**. Next time you enter that repo, run the smoke test first.

### 2. This harness's real asset is the "lessons pipeline", and it has a bleeding wound
The institution compounds via: mistake → ERRORS.md → human review → mechanization into invariants/guard. Menu-Android grew 693 lines of invariants and 81 lessons through this pipeline, proving it works. But this project's `stop-retro-logger.py` included the timestamp in its dedup hash, so nothing ever deduplicates, and ERRORS.md has been flooded with duplicate noise — **once the lessons file fills with noise, later models stop reading it, and the whole pipeline dies**. The fix is item 1 in the handoff checklist below; do it first.

### 3. The always-on load surface is a scarce budget; every added line taxes all future sessions
CLAUDE.md + `.claude/rules/security.md` + the tier pack chosen for the running model (`strong.md`, `mid.md` or `light.md` under `.claude/tiers/`) are injected into **every** session. You will keep feeling the urge to push new rules into that surface ("this one is important!") — the vast majority of rules do not need to be standing; leave them in `.claude/rules/` as full-text reference and reach them by reference. The criterion: **only "needed for the very first decision of every session" earns standing status**.

Since F-003 this is no longer a matter of judgment: `python3 scripts/context-budget.py --tier <tier>` measures the real injected volume against `.claude/tiers/budget.json` and fails the acceptance run when it is over. Add a line to a tier pack source and the gate tells you what it cost. Two things that surprise people: the budget counts **Unicode characters, not bytes** (CJK is 3 bytes per character, so `wc -c` overstates by ~50%), and a SKILL.md body is **not** part of this surface — only its frontmatter `description` is resident, so splitting a long skill saves nothing here and everything at invocation time.

## II. How this institution is most likely to decay, and prevention

| Decay mode | Concrete symptom | Prevention / remedy |
|---------|---------|-----------|
| **Rule accretion** | total rules volume rises month over month, no deletion record | maintenance §5 trigger line; every new standing rule must justify "why it must be standing" |
| **Canon re-fragmentation** | someone "conveniently" copies the model table/roster into a new file, then the two copies evolve separately | "reference only, never re-list" (CLAUDE.md canon hierarchy); on discovery delete the copy, keep a reference |
| **Rubber-stamp acceptance** | acceptance reports containing 「看起來沒問題」 ("looks fine"), PASS without item-by-item evidence | format enforcement in delegation-templates §6; user periodically spot-checks one acceptance report |
| **Lessons-file noise** | duplicate ERRORS.md entries, missing dates, missing line numbers | dedup fix + §3 dedup rule; weekly review clears Pending Review |
| **Dead-reference buildup** | documents reference paths/skills that don't exist; models chase empty paths or fabricate | "reference = verify" discipline; run a full `/harness-eval` checkup quarterly |
| **Placeholder normalization** | new projects fork without filling {{}}; models habitually skip whole documents | CLAUDE.md "Activation Status" section defines skip semantics; the first task after forking is to fill in or delete |
| **Mirror drift** | a `*_zh.md` mirror keeps describing a mechanism the English original has already replaced; no existing gate catches it, because path checks only prove a file exists, not that a sentence is still true | change a file and its mirror in the **same commit**; F-003 left `CLAUDE_zh.md` asserting a dismantled mechanism for 8 commits (ERRORS.md 2026-07-28) |

The most insidious is the **rubber stamp**: it makes every other defense look like it still works. If you can only guard against one, guard against that.

## III. Handoff checklist (unfinished work, by priority)

> Delete an item from here once done (no tombstones). Ask the user before touching red-tier files (see harness-maintenance.md §1).

1. **skillopt-loop.md keep-or-delete decision** (needs user decision): already marked "unwired design draft" with fictitious references removed (2026-07-04 round 3). Options: (a) keep as a draft for future wiring (b) delete (red-tier deletion needs consent).
2. **First-run verification of session-handoffs** (watch item): `state/session-handoffs/` is currently empty — this session never triggered PreCompact. Next time compaction happens, verify a new snapshot file appears in that directory; if not, pre-compact-snapshot.py may have an isomorphic failure (cf. the hooks smoke-test lesson).
3. **Menu-Android guard fix done but not committed** (2026-07-04): the exit 2 fix passed its smoke test; the changes sit in that repo's `feat/ga-event-tracking` working tree — commit them along with that branch.
> All three optimization rounds of 2026-07-04 completed (details in §IV); 26 atomic commits on feat/harness-institution, not pushed.

## IV. Completed this session (for archaeology)

A diagnosis (docs/harness/DIAGNOSIS.md), B rewrote CLAUDE.md (old version in .bak), C model-dispatch.md, D judgment-rubrics.md, E delegation-templates.md, F harness-maintenance.md, G this file; physical fixes: hooks chmod +x, guard exit 1→2 (live-tested), cost-optimization/plan-first pruned and deduplicated (each with a .bak).
Follow-up batch (same day, workflow-executed, fresh-context acceptance PASS): boilerplate collapsed across 14 agent files (−9~−20 lines each), YAML frontmatter added to 15 SKILL.md files, AI-TEAM-REGISTRY.md regenerated from frontmatter (fixed 9 model contradictions, added code-reviewer, counts 14 agents/15 skills), Life-Vault and menu.jpg residue removed.
Round 3 (same day, three-way deep audit → six-way implementation → isolated acceptance PASS): four review agents' output unified to review-protocol vocabulary; tech-lead repositioned as architecture advisor (no PR gating); research trio's trigger words made mutually exclusive + output templates; ui-ux-designer merged into three-phase Phase 3; model rebalance opus 10→4 (architect/pm/security-reviewer/plan-reviewer stay opus); skillopt-loop demoted to unwired draft (fictitious references removed); guard gained INV-SEC-003 staging interception (live-tested 4/4); retro tombstone ledger state/retro-hashes.jsonl + 30/90-day rotate; five-layer knowledge map table (INDEX.md); multi-agent-guide deduplicated; TECHNICAL-REFERENCE minimal fill-in checklist.
Same-day incident and fix: an acceptance subagent overstepped scope and deleted the untracked《AI 基礎架構優化目標說明.md》; rebuilt verbatim from the main conversation context; lesson logged in ERRORS.md; delegation-templates gained a destructive-command blacklist.
Round 4 (2026-07-06, absorption of external harness research): researched 7 external repos in parallel (fable-commander / obra-superpowers / revfactory-harness / walkinglabs tutorial / everything-claude-code / aden-hive / deer-flow — star counts and contents verified on site), absorbing nine mechanisms: delegation scope declaration + termination conditions (delegation-templates), acceptance FAIL restricted to objective criteria + non-blocking suggestions column (model-dispatch §5), gate-softening ban + no-improvement circuit breaker + Red Flags rationalization table (judgment-rubrics §2/§3/§7), agent/skill quality gates and five-dimension checkup (harness-maintenance §6/§7), init.sh.template, CLAUDE.md decision-tree verifiability routing, skill-creator-plus quantified bidirectional trigger tests. 7 atomic commits, isolated acceptance 8/8 PASS, ff-merged into master.
