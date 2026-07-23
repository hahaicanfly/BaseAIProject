#!/usr/bin/env python3
"""PreCompact sentinel: snapshot active task state before context compaction.

Phase D mode: SENTINEL (always pass, never block — PreCompact can't
block compaction anyway, but we log defensively).

Output:
- state/session-handoffs/<ISO>.json — structured snapshot
- state/token-usage.jsonl — one row per compaction event

Snapshot fields (state/SCHEMA.md §2):
  schema_version, snapshot_at, session_id, active_execplan,
  active_branch, active_handoff_marker, open_questions, todo_items,
  recent_invariant_violations
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import (  # noqa: E402
    HANDOFFS_DIR,
    HOOK_EVENTS,
    TOKEN_USAGE,
    append_jsonl,
    current_branch,
    ensure_state_dirs,
    find_active_execplan,
    log_event,
    now_iso,
    read_stdin_json,
)

HOOK_NAME = "pre-compact-snapshot"


def recent_violations(n: int = 5) -> list[dict]:
    """Last N hook-events.jsonl entries with result == 'enforced_block' or 'warn'."""
    out: list[dict] = []
    if not HOOK_EVENTS.is_file():
        return out
    try:
        with HOOK_EVENTS.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in reversed(lines[-200:]):  # scan last 200
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("result") in ("enforced_block", "warn"):
                out.append(rec)
                if len(out) >= n:
                    break
    except Exception:
        pass
    return out


def latest_handoff_marker_from_execplan(execplan_path: str | None) -> str:
    """Try to read §9 Handoff Manifest 'Current state marker' from active ExecPlan."""
    if not execplan_path:
        return ""
    try:
        from _lib import REPO_ROOT  # local import to avoid cycle warning
        full = REPO_ROOT / execplan_path
        if not full.is_file():
            return ""
        text = full.read_text(encoding="utf-8", errors="ignore")
        # crude: find first [HANDOFF: / [VERIFY_FAILED: / [HUMAN_ATTENTION_REQUIRED: in last 50 lines
        tail = "\n".join(text.splitlines()[-80:])
        for marker in ("[HUMAN_ATTENTION_REQUIRED:", "[VERIFY_FAILED:", "[HANDOFF:"):
            idx = tail.rfind(marker)
            if idx != -1:
                end = tail.find("]", idx)
                if end != -1:
                    return tail[idx : end + 1]
        return ""
    except Exception:
        return ""


def main() -> int:
    payload = read_stdin_json()
    session_id = payload.get("session_id") or payload.get("sessionId") or ""
    transcript_path = payload.get("transcript_path", "")
    # Some Claude Code versions provide token info; tolerate absence.
    input_tokens = payload.get("input_tokens", 0)
    output_tokens = payload.get("output_tokens", 0)
    cache_creation = payload.get("cache_creation_tokens", 0)
    cache_read = payload.get("cache_read_tokens", 0)

    ensure_state_dirs()

    branch = current_branch()
    execplan = find_active_execplan()
    marker = latest_handoff_marker_from_execplan(execplan)

    snapshot = {
        "schema_version": "1.0",
        "snapshot_at": now_iso(),
        "session_id": session_id,
        "transcript_path": transcript_path,
        "active_execplan": execplan,
        "active_branch": branch,
        "active_handoff_marker": marker,
        "open_questions": [],
        "todo_items": [],
        "recent_invariant_violations": recent_violations(),
    }

    # Filename: ISO-friendly, sortable
    fname = snapshot["snapshot_at"].replace(":", "").replace("+", "Z")
    out_path = HANDOFFS_DIR / f"{fname}.json"
    try:
        out_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log_event(HOOK_NAME, "fail", reason=f"write-failed: {e}")
        return 0  # never block

    # Token usage row
    append_jsonl(
        TOKEN_USAGE,
        {
            "ts": snapshot["snapshot_at"],
            "session_id": session_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_creation": cache_creation,
            "cache_read": cache_read,
            "trigger": "pre-compact",
        },
    )

    log_event(
        HOOK_NAME,
        "sentinel",
        reason="snapshot-written",
        path=str(out_path.relative_to(out_path.parent.parent.parent)),
        execplan=execplan or "",
        branch=branch,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
