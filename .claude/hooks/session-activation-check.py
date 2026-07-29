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
#
# Each entry below depends on the literal wording of someone else's file.
# The COUPLING comments are what make that dependency findable from the
# other end: an editor about to reword one of these documents can
# `grep -rn "COUPLING:" .claude/hooks/` and see who is watching it.
# scripts/check-hook-doc-coupling.py fails when a coupling has no such
# declaration — added after CI proposed rewording exactly the CLAUDE.md
# line the first entry keys off (ERRORS.md 2026-07-29).
CHECKS = [
    (
        "CLAUDE.md 產品層 build/test/lint 未填（harness 自檢指令已就緒）",
        # COUPLING: CLAUDE.md -- the Quick Commands product build/test/lint slot must keep the literal "{{fill in"; rewording it silently disables this warning
        "CLAUDE.md",
        lambda t: "{{fill in" in t,
    ),
    (
        "docs/architecture/invariants.md 仍含未填佔位符",
        # COUPLING: docs/architecture/invariants.md -- any remaining "{{" or a "> Fill in" blockquote means the INV sections are still template stubs
        "docs/architecture/invariants.md",
        lambda t: "{{" in t or "> Fill in" in t,
    ),
    (
        "agent_docs/TECHNICAL-REFERENCE.md 未活化",
        # COUPLING: agent_docs/TECHNICAL-REFERENCE.md -- any remaining "{{" means the technical reference is unfilled and CLAUDE.md's Activation Status says to skip it
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
            + " — 未填的槽位一律視為未活化、直接略過，不要照字面執行也不要自行編造內容"
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
