#!/usr/bin/env python3
"""SessionStart: inject the tier pack the main conversation should run under.

The tier is DECLARED, not detected — no hook event before the first
response knows the model (F-003 DEC-4). tier-drift-check.py verifies the
declaration against the transcript once a real model id exists.

CRITICAL — sentinel (ADR-0001 D5): every path returns 0. SessionStart is a
context-only event, and a harness that fails to load must never be a
harness that stops the session.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import log_event, read_stdin_json  # noqa: E402
from tier_resolve import (  # noqa: E402
    emit_context,
    load_pack,
    record_session_tier,
    resolve_main_tier,
)

HOOK_NAME = "session-tier-inject"


def main() -> int:
    payload = read_stdin_json() or {}
    session_id = payload.get("session_id") or ""

    tier, source = resolve_main_tier()
    pack = load_pack(tier)
    record_session_tier(session_id, tier=tier, source=source, verified=False)

    if not pack:
        # Packs not built yet, or an unreadable file. Say so rather than
        # letting the session silently run with no tier guidance at all.
        log_event(HOOK_NAME, "warn", reason="pack-missing", tier=tier)
        print(f"[harness] tier={tier} (source: {source}) — 對應的 tier pack "
              f".claude/tiers/{tier}.md 不存在，本 session 未載入分層規則。")
        return 0

    header = (
        f"# Harness tier: {tier}\n"
        f"<!-- source: {source} — declared, not detected; "
        f"see .claude/tiers/README.md -->\n\n"
    )
    print(emit_context("SessionStart", header + pack))
    log_event(HOOK_NAME, "pass", reason="injected", tier=tier, source=source)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
