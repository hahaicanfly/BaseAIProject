#!/usr/bin/env python3
"""PreToolUse (Task/Agent) sentinel: ledger of subagent delegations.

Why: Task/Agent delegations are invisible to the harness — there is no
record of who was delegated what, with what acceptance criteria attached
(ExecPlan F-001 step C2c). model-dispatch.md §2 requires every delegation
prompt to carry a "trio" (goal, acceptance criteria, report format), plus
scope boundaries and a handoff-marker requirement are best practice. This
hook appends one line per delegation attempt to state/delegations.jsonl,
flagging (via cheap regex over the prompt text) whether each of those five
signals is present — the ledger makes weak delegations measurable without
blocking anything.

CRITICAL — this is a SENTINEL (ADR-0001 D5): every code path returns 0.
A non-zero exit from PreToolUse would BLOCK the delegation, which this
hook must never do. All logic below main() is wrapped in try/except so an
unexpected payload shape degrades to "no-op", never to a blocked tool call.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import (  # noqa: E402
    STATE_DIR,
    append_jsonl,
    log_event,
    now_iso,
    read_stdin_json,
)

HOOK_NAME = "delegation-ledger"
DELEGATIONS_LEDGER = STATE_DIR / "delegations.jsonl"

_TOOL_NAMES = ("Task", "Agent")

# Five signals model-dispatch.md §2 (trio) + scope + marker require every
# delegation prompt to carry. Case-insensitive; CJK alternatives included
# since prompts in this repo are often written in Traditional Chinese.
_GOAL_RE = re.compile(r"motivation|動機|目標|goal|背景", re.I)
_AC_RE = re.compile(r"acceptance|驗收|criteria|標準", re.I)
_REPORT_FORMAT_RE = re.compile(
    r"report format|報告格式|回報格式|report ≤|報告 ≤|≤\s*\d+\s*(lines|行)", re.I
)
_SCOPE_RE = re.compile(
    r"allowed to (read|write)|scope|唯讀|read-only|只准|不得修改|do not touch", re.I
)
_MARKER_RE = re.compile(r"HANDOFF|VERIFY_FAILED|HUMAN_ATTENTION_REQUIRED", re.I)


def _as_str(value: object) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)


def _run() -> None:
    payload = read_stdin_json()
    if not isinstance(payload, dict):
        return
    tool_name = payload.get("tool_name", "")
    if tool_name not in _TOOL_NAMES:
        return

    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    session_id = _as_str(payload.get("session_id"))
    subagent_type = _as_str(
        tool_input.get("subagent_type") or tool_input.get("agent_type")
    )
    description = _as_str(tool_input.get("description"))
    prompt = _as_str(tool_input.get("prompt"))
    model = _as_str(tool_input.get("model"))

    prompt_sha1_10 = hashlib.sha1(
        prompt.encode("utf-8", errors="ignore")
    ).hexdigest()[:10]

    has_goal = bool(_GOAL_RE.search(prompt))
    has_ac = bool(_AC_RE.search(prompt))
    has_report_format = bool(_REPORT_FORMAT_RE.search(prompt))
    has_scope = bool(_SCOPE_RE.search(prompt))
    has_marker_req = bool(_MARKER_RE.search(prompt))

    append_jsonl(
        DELEGATIONS_LEDGER,
        {
            "ts": now_iso(),
            "session": session_id,
            "subagent_type": subagent_type,
            "model": model,
            "desc": description[:120],
            "prompt_sha1_10": prompt_sha1_10,
            "prompt_chars": len(prompt),
            "has_goal": has_goal,
            "has_ac": has_ac,
            "has_report_format": has_report_format,
            "has_scope": has_scope,
            "has_marker_req": has_marker_req,
        },
    )

    log_event(
        HOOK_NAME,
        "sentinel",
        reason="delegation-recorded",
        session=session_id,
        subagent=subagent_type,
        trio_ok=(has_goal and has_ac and has_report_format),
    )


def main() -> int:
    try:
        _run()
    except Exception:
        pass  # sentinel: never block a delegation over a logging failure
    return 0


if __name__ == "__main__":
    sys.exit(main())
