#!/usr/bin/env python3
"""PostToolUse sentinel: log Edit/Write/MultiEdit + quick invariant grep.

Phase D mode: SENTINEL ONLY (per ADR-0001 D5). Never blocks; only:
- Appends record to state/tool-calls.jsonl
- Appends event to state/hook-events.jsonl
- Runs sub-millisecond grep checks against project-specific INV-* patterns.
  Findings are written to hook-events.jsonl with result=warn for human
  review (not blocking).

HOW TO CUSTOMIZE FOR YOUR PROJECT:
- Add entries to QUICK_CHECKS below: (INV-id, compiled_regex, hint_message)
- Each check runs against the edited file's full text content
- File extension filter: currently runs on all files; restrict via suffix check
- See docs/architecture/invariants.md for the full INV-* catalog

Why grep instead of full lint here?
- Full lint can take 30s+; running it on every edit tanks DX.
- Real lint/test is for `code-reviewer` agent at PR time.
- Grep checks catch the most common high-signal violations cheaply.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import (  # noqa: E402
    REPO_ROOT,
    TOOL_CALLS,
    append_jsonl,
    is_sentinel_mode,
    log_event,
    now_iso,
    read_stdin_json,
)

HOOK_NAME = "post-edit-lint"

# ──────────────────────────────────────────────────────────────────────────
# PROJECT-SPECIFIC QUICK CHECKS
# Add tuples of (INV-id, compiled_regex, hint_message) for your project.
# These run on every file edit in sentinel mode (warn but don't block).
#
# Example (uncomment and adapt):
#
# QUICK_CHECKS: list[tuple[str, re.Pattern, str]] = [
#     (
#         "INV-SEC-001",
#         re.compile(r'api[_-]?key\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']', re.IGNORECASE),
#         "Possible hardcoded API key detected",
#     ),
#     (
#         "INV-LOG-001",
#         re.compile(r'\bprint\s*\(.*token\b', re.IGNORECASE),
#         "Possible token leak in print/log statement",
#     ),
# ]
# ──────────────────────────────────────────────────────────────────────────
QUICK_CHECKS: list[tuple[str, re.Pattern, str]] = [
    # INV-SEC-001: hardcoded API key/token (generic — adapt src/ path as needed)
    (
        "INV-SEC-001",
        re.compile(r'api[_-]?key\s*=\s*["\'][A-Za-z0-9_\-]{20,}["\']', re.IGNORECASE),
        "Possible hardcoded API key — use environment variable instead",
    ),
    # INV-SEC-002: token/secret leak in log/print statements
    (
        "INV-SEC-002",
        re.compile(
            r'(print|console\.log|logger\.\w+)\s*\(.*\b(token|api_key|secret|password)\b',
            re.IGNORECASE,
        ),
        "Possible secret leak in log/print — remove sensitive value from output",
    ),
    # TODO: Add project-specific checks below, referencing INV-* in invariants.md
    # Example:
    # (
    #     "INV-ARC-001",
    #     re.compile(r'import.*from.*\.\.\/\.\.\/infra', re.IGNORECASE),
    #     "ui layer must not import infra directly — use api layer",
    # ),
]


def quick_invariant_scan(file_path: Path) -> list[tuple[str, str]]:
    """Return list of (INV-id, hint) for quick grep matches in the file."""
    if not file_path.is_file():
        return []
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    findings = []
    for inv_id, pat, hint in QUICK_CHECKS:
        if pat.search(text):
            findings.append((inv_id, hint))
    return findings


def main() -> int:
    payload = read_stdin_json()
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""

    if not file_path:
        log_event(HOOK_NAME, "pass", reason="no-file-path", tool=tool)
        return 0

    p = Path(file_path)
    if not p.is_absolute():
        p = REPO_ROOT / p

    # Always log the tool call
    record = {
        "ts": now_iso(),
        "tool": tool,
        "file": str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p),
        "matcher": "Write|Edit|MultiEdit",
    }
    append_jsonl(TOOL_CALLS, record)

    # Sentinel mode (default): scan and log warnings but never block
    sentinel = is_sentinel_mode(HOOK_NAME)
    findings = quick_invariant_scan(p)

    if findings:
        for inv_id, hint in findings:
            log_event(
                HOOK_NAME,
                "warn",
                reason=inv_id,
                file=record.get("file", ""),
                hint=hint,
                mode="sentinel" if sentinel else "enforce",
            )
        if not sentinel:
            sys.stderr.write(
                f"[harness/{HOOK_NAME}] possible invariant violations in {record.get('file','')}:\n"
            )
            for inv_id, hint in findings:
                sys.stderr.write(f"  - {inv_id}: {hint}\n")
            sys.stderr.write(
                "See docs/architecture/invariants.md for full rules.\n"
            )
            return 2  # PostToolUse: feedback to Agent
    else:
        log_event(HOOK_NAME, "pass", file=record.get("file", ""))

    return 0


if __name__ == "__main__":
    sys.exit(main())
