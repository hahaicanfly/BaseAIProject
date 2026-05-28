"""Shared helpers for harness hooks.

Phase D — designed for Claude Code hook protocol:
- stdin: JSON describing tool/event
- exit 0: continue normally
- exit 1: PreToolUse only — block tool call
- exit 2: PostToolUse — feedback to Agent (stderr returned)

All helpers must be FAST (<100ms in normal case) and never throw to
stdout (only stderr for user-visible feedback).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Hooks live under <repo_root>/.claude/hooks/_lib.py
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STATE_DIR = REPO_ROOT / "state"
HANDOFFS_DIR = STATE_DIR / "session-handoffs"
HOOK_EVENTS = STATE_DIR / "hook-events.jsonl"
TOOL_CALLS = STATE_DIR / "tool-calls.jsonl"
TOKEN_USAGE = STATE_DIR / "token-usage.jsonl"
ERRORS_MD = REPO_ROOT / "docs" / "learnings" / "ERRORS.md"
ACTIVE_PLANS = REPO_ROOT / "docs" / "plans" / "active"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")


def read_stdin_json() -> dict:
    """Read and parse stdin as JSON. Returns {} on any failure."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except Exception:
        return {}


def ensure_state_dirs() -> None:
    """Create state directories on first hook run; cheap if exist."""
    STATE_DIR.mkdir(exist_ok=True)
    HANDOFFS_DIR.mkdir(exist_ok=True)


def append_jsonl(path: Path, record: dict) -> None:
    """Append one JSON line. Best-effort; failures are silent."""
    try:
        ensure_state_dirs()
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass  # never crash a hook for logging failure


def log_event(hook: str, result: str, reason: str = "", **extra) -> None:
    """Standard hook-events.jsonl writer."""
    record = {"ts": now_iso(), "hook": hook, "result": result}
    if reason:
        record["reason"] = reason
    record.update(extra)
    append_jsonl(HOOK_EVENTS, record)


def is_sentinel_mode(hook_name: str) -> bool:
    """Resolve sentinel/enforce mode for a given hook.

    Default per ADR-0001 D5:
    - pre-tool-use-guard: enforce
    - post-edit-lint: sentinel
    - pre-compact-snapshot: sentinel
    - stop-retro-logger: sentinel

    Override via env var HARNESS_HOOK_MODE=enforce|sentinel (global)
    or HARNESS_HOOK_MODE_<HOOK_UPPER>=... (per-hook).
    """
    per_hook = os.environ.get(
        f"HARNESS_HOOK_MODE_{hook_name.upper().replace('-', '_')}"
    )
    if per_hook:
        return per_hook.lower() == "sentinel"
    global_mode = os.environ.get("HARNESS_HOOK_MODE")
    if global_mode:
        return global_mode.lower() == "sentinel"
    # default by hook name
    enforce_default = {"pre-tool-use-guard"}
    return hook_name not in enforce_default


def current_branch(cwd: str | None = None) -> str:
    """Run git branch --show-current with 2s timeout. Returns '' on failure.

    `cwd` defaults to REPO_ROOT but can be overridden so cross-repo
    operations (e.g. `git -C <path> commit ...`) ask the right repo.
    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=cwd if cwd else str(REPO_ROOT),
        )
        return result.stdout.strip()
    except Exception:
        return ""


def find_active_execplan() -> str | None:
    """Return path of most-recently-touched ExecPlan in docs/plans/active/."""
    try:
        if not ACTIVE_PLANS.is_dir():
            return None
        candidates = [p for p in ACTIVE_PLANS.glob("F-*.md") if p.is_file()]
        if not candidates:
            return None
        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        return str(latest.relative_to(REPO_ROOT))
    except Exception:
        return None
