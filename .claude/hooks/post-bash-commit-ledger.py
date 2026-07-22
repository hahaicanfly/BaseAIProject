#!/usr/bin/env python3
"""PostToolUse (Bash) sentinel: ledger of real git commits per session.

Why: git history is the only durable, cross-machine trail this harness
has, but it carried no link back to harness state — "which session made
this commit" was unanswerable. This hook appends one line per successful
`git commit` to state/commits.jsonl, making the commit hash the join key
across commits ↔ sessions ↔ (later) delegations/verifications.

Success detection: instead of parsing tool output, compare HEAD before
recording — a blocked/failed commit leaves HEAD unchanged and is skipped
via the last-recorded-hash dedup. Always exit 0 (sentinel, ADR-0001 D5).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import (  # noqa: E402
    REPO_ROOT,
    STATE_DIR,
    append_jsonl,
    current_branch,
    log_event,
    now_iso,
    read_stdin_json,
)

HOOK_NAME = "post-bash-commit-ledger"
COMMITS_LEDGER = STATE_DIR / "commits.jsonl"

_GIT_COMMIT_RE = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?commit\b")


def _last_recorded_hash() -> str:
    try:
        if not COMMITS_LEDGER.is_file():
            return ""
        lines = COMMITS_LEDGER.read_text(encoding="utf-8").strip().splitlines()
        if not lines:
            return ""
        return json.loads(lines[-1]).get("head_hash") or ""
    except Exception:
        return ""


def main() -> int:
    payload = read_stdin_json()
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command", "")
    if not isinstance(cmd, str) or not _GIT_COMMIT_RE.search(cmd):
        return 0
    session_id = payload.get("session_id") or ""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=2, cwd=str(REPO_ROOT),
        ).stdout.strip()
        msg = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True, text=True, timeout=2, cwd=str(REPO_ROOT),
        ).stdout.strip()
    except Exception:
        return 0
    if not head or head == _last_recorded_hash():
        # Commit didn't happen (denied/failed) or already recorded.
        return 0
    append_jsonl(
        COMMITS_LEDGER,
        {
            "ts": now_iso(),
            "session": session_id,
            "branch": current_branch(),
            "head_hash": head,
            "msg_first_line": msg[:120],
        },
    )
    log_event(
        HOOK_NAME, "sentinel", reason="commit-recorded",
        session=session_id, head=head[:12],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
