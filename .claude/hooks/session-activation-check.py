#!/usr/bin/env python3
"""SessionStart sentinel: warn when template activation slots are unfilled.

Why: the harness's own docs call executable build/test commands "the
biggest lever on success rate" (CLAUDE.md Quick Commands), yet a freshly
forked template runs with those slots as {{placeholders}} — i.e. ZERO
executable verification — and nothing signals that state. CLAUDE.md's
Activation Status even tells the model to silently skip unfilled files.
This hook makes the unactivated state visible at every session start
(stdout from a SessionStart hook is injected into context) and leaves a
telemetry trace. Always exit 0 (sentinel, ADR-0001 D5).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import REPO_ROOT, log_event, read_stdin_json  # noqa: E402

HOOK_NAME = "session-activation-check"

# (label, repo-relative path, predicate on file text -> unfilled?)
CHECKS = [
    (
        "CLAUDE.md Quick Commands build/test/lint 指令未填",
        "CLAUDE.md",
        lambda t: "{{fill in" in t,
    ),
    (
        "docs/architecture/invariants.md 仍含未填佔位符",
        "docs/architecture/invariants.md",
        lambda t: "{{" in t or "> Fill in" in t,
    ),
    (
        "agent_docs/TECHNICAL-REFERENCE.md 未活化",
        "agent_docs/TECHNICAL-REFERENCE.md",
        lambda t: "{{" in t,
    ),
]


def main() -> int:
    read_stdin_json()  # consume stdin per hook protocol
    unfilled: list[str] = []
    for label, rel, pred in CHECKS:
        p = REPO_ROOT / rel
        try:
            if p.is_file() and pred(p.read_text(encoding="utf-8", errors="ignore")):
                unfilled.append(label)
        except Exception:
            continue
    if unfilled:
        print(
            f"[harness] 未活化槽位 {len(unfilled)} 項: "
            + "；".join(unfilled)
            + " — 未填 Quick Commands 前，本 repo 沒有任何可執行驗證閘門"
            "（CLAUDE.md Activation Status）。"
        )
        log_event(HOOK_NAME, "warn", reason="unactivated-slots", count=len(unfilled))
    else:
        log_event(HOOK_NAME, "pass", reason="activated")

    # Retro overdue reminder (sentinel, silent unless over budget):
    # SessionStart stdout is the only reliable channel to put the weekly-
    # review debt in front of the model instead of hoping someone runs
    # scripts/retro-status.py by hand.
    try:
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "retro-status.py"), "--json"],
            capture_output=True, text=True, timeout=10, cwd=str(REPO_ROOT),
        )
        st = json.loads(r.stdout.strip() or "{}")
        over = st.get("over_budget") or []
        if over:
            print(
                "[harness] retro 超線: " + "; ".join(over)
                + " — 依 harness-maintenance.md §5 建議提請人類週審。"
            )
            log_event(HOOK_NAME, "warn", reason="retro-over-budget", items=len(over))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
