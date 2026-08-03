---
name: model-dispatch
description: Model dispatch, the delegation trio, escalation/de-escalation path, verification-not-self-certified (full-text reference behind the tier packs)
always: false
---

> **Not auto-loaded.** Since F-003 this file is the full-text reference behind the
> tier packs (`.claude/tiers/`), which are what actually gets injected each session.
> Read this when a borderline case needs the reasoning or worked examples behind a criterion.

# Model Dispatch Rules

*白話:簡單瑣事用便宜快速的模型做,困難或有風險的判斷才升級用更貴、更強的模型,不要每件事都用最貴的那個。*

> Contains only criteria and hard rules.
> Full delegation prompt templates: `.claude/templates/delegation-templates.md`; judgment rubrics: `.claude/rules/judgment-rubrics.md`.

## 0. Actually Available Local Tiers (2026-07 inventory, facts not assumptions)

| Tier | Agent tool `model` value | Purpose |
|------|----------------------|------|
| Haiku 4.5 | `haiku` | Formatting, fixed-template application, single-point lookups |
| Sonnet | `sonnet` | Default workhorse: implementation, search, review, research |
| Opus 4.8 | `opus` | Architecture decisions, cross-module refactors, hard debugging |
| Fable 5 | `fable` | Special-authorization sessions only; do not assume availability day-to-day |

*白話:由上到下越後面越貴、越慢,但處理複雜/高風險問題的品質也越好——瑣事用 Haiku、一般工作用 Sonnet、真的難的才升級 Opus,不要為了小事動用最貴的那一級。*

- The main conversation's model is set by `model` in `~/.claude/settings.json`; don't assume which model you are mid-conversation — go by behavioral rules, not self-identification.
- `effort` parameter(白話:調整同一個模型「想得多深」的旋鈕,愈高愈仔細但也愈慢愈貴,跟換模型是兩件事): only the Workflow tool's `agent(prompt, {effort})` supports it (`low|medium|high|xhigh|max`); ignore this line if the environment has no Workflow tool. The Agent tool has no `effort` parameter — it inherits the session setting.
- When the Agent tool omits `model`, it inherits the main conversation's model — **lightweight delegated tasks must explicitly set `model: "haiku"` or `"sonnet"`, otherwise chores run on the main conversation's expensive model**.

## 1. The Commander Doesn't Do Fieldwork

The main conversation (commander) only does: deciding, decomposing, delegating, concluding acceptance review, and communicating with the user.

**Must delegate to a subagent** (any one condition triggers delegation — don't do it yourself):
- Estimated to require reading 3+ files, or a full read-through of a single file over 400 lines
- Full-repo scanning / keyword tracing (→ `Explore` agent(白話:專門負責「先大範圍搜尋、再回報結論」的子 agent,不用你自己一個個檔案翻))
- Web search or documentation research (→ `general-purpose`, `model: sonnet`)
- Batch-modifying 5+ files (→ delegate + worktree isolation(白話:讓每個任務在自己獨立的資料夾分身裡改檔案,互不干擾,細節見 parallel-worktree.md), see parallel-worktree.md)
- Any analysis requiring "reading a lot before you can conclude anything"

**The main conversation may do directly**: editing a single known file (< 20-line diff), reading a specific section of a known file, running a single command and reading the result, writing the final deliverable text.

## 2. The Delegation Trio (every delegation prompt must contain these three sections — missing one, don't delegate)

1. **Goal and motivation**: what to achieve and why (lets the subagent make small decisions autonomously)
2. **Acceptance criteria**: a mechanically checkable definition of done (file exists, tests pass, report contains specific fields)
3. **Report format**: explicitly specify the report's structure and length cap

Copy the template directly from `.claude/templates/delegation-templates.md`; don't improvise.

## 3. The Reporting Contract (subagent side)

- Report ≤ 40 lines; return only conclusions, lists, and `file:line` references(白話:寫成「檔名:行號」的格式,例如 `model-dispatch.md:48`,方便你或下一個 agent 直接跳到那一行看,不用整份翻找)
- No pasting more than 10 lines of code or raw text into a report — long artifacts go to a file, report the path
- The last line of the report must be a handoff marker (see `.claude/protocols/handoff-protocol.md`)
- Report failures honestly: state where you're stuck and what you tried; "mostly done" is not an acceptable report

## 4. Escalation/De-escalation Path

| Situation | Action |
|------|------|
| Haiku hits a tool-call error or syntax error **once** | Re-delegate straight to Sonnet; don't retry Haiku |
| Sonnet fails the **same subtask twice in a row** | Escalate to Opus, with the prompt including the full failure trace: original instruction, both error outputs, expected result |
| Opus solves it with a repeatable, fixed pattern | Write the pattern down as a rule/example (persist it), then de-escalate to Sonnet/Haiku for batch application |
| After escalation (Opus) **fails once more** | Stop retrying → circuit-break, ask the user with the failure trace (see judgment-rubrics.md §3) |

Full sequence (the only valid reading): same model fails twice in a row → escalate once → fails once more after escalation → circuit-break and ask. The escalation attempt does not reset the failure counter or open a new budget.
When escalating, emit `[ESCALATION: <from>-><to>|<task>]` inline (handoff-protocol.md "Inline Auxiliary Markers") so escalation frequency is measurable from state/rule-events.jsonl.
"Same subtask" is determined by matching goal and acceptance criteria — rephrasing and re-delegating still counts toward the failure count.

## 5. Verification Is Never Self-Certified

- The implementer may not declare their own output as having passed acceptance.
- Acceptance review always goes to a **fresh-context subagent** (newly spawned, without the implementation-process context):
  - Document/config output → read-back: re-read the file, check it against acceptance criteria item by item
  - Code output → actually run tests or run the program, paste the actual output
  - High-risk judgment (architecture selection, security, irreversible operations) → second opinion: dispatch a second agent with a different model or a different angle to answer independently, then compare conclusions; escalate or ask the user on disagreement
- An acceptance agent's report can only be: `PASS` (list each acceptance criterion with evidence) or `FAIL` (list unmet items with evidence). "Looks fine" is not accepted.
- Acceptance review boundary: FAIL may only be based on acceptance criteria stated at delegation time that are mechanically checkable; style/writing/opinion-type feedback goes into a "Suggestions (non-blocking)" section and must not block delivery — this prevents reviewer overreach causing wasted rework cycles.

## 6. Handling Subagent Idle State

*白話：子 agent 進入 idle 時的明確催收協議，避免「尚未回報」被誤判為「回報失敗」。*

An idle notification (tool completed, no agent output detected) means **not yet reported** — it does not mean **failed**. Those are different facts; never narrate the former to the user as the latter.

**Protocol** (in order; only the last step may conclude failure):
1. **Idle signal arrives** → do NOT report failure; note the time. Wait 5–10s — mechanical output may still be arriving.
2. **Still nothing** → active collection: `SendMessage` to the agent, one-line request ("Still waiting for your final report: [goal]. Please output now — 10 more seconds."). Wait 10–15s; most agents respond in this window.
3. **Silent through both windows** → now treat as timeout. Do NOT say "the subagent failed" — mark `[HUMAN_ATTENTION_REQUIRED: subagent-timeout]` stating: which agent/task, how long you waited, what output was expected, and a fallback (mechanical verification, re-dispatch, or escalation).

**Anti-pattern**: ❌ "Agent went idle → declare failure to the user." ✅ "Wait → collect → only if truly silent, report a timeout (not a failure)."

**Complementarity**: mechanical checks and agent judgment are complementary, not interchangeable. Agent silent but mechanical verification passes → report the mechanical evidence, not "agent failed". Mechanical verification fails but agent says "looks fine" → the mechanical evidence wins; agent judgment alone is not proof.
