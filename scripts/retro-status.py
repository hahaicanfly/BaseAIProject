#!/usr/bin/env python3
"""Retro / trim-trigger status — the single measuring stick.

Computes, per the LITERAL definitions in harness-maintenance.md §5
(mis-measurement of these lines already caused one wrong human decision,
see ERRORS.md 2026-07-07):
- ERRORS.md total lines (trigger > 300) and Pending Review entry count
  (trigger > 20)
- pending /pr-retro reminder count from state/retro-reminders.jsonl
  (PR_RETRO entries moved out of ERRORS.md in F-004)
- CLAUDE.md lines (trigger > 100) — measured alone, NOT part of rules
- .claude/rules/*.md combined lines (trigger > 600, excludes CLAUDE.md)
- last 30 days of notable hook events (missing-marker, ACCEPTANCE FAIL,
  enforced_block, unverified-citation) from state/hook-events.jsonl
- last weekly review: newest `retro-log.jsonl` entry if present, else
  "unknown" (never guessed)

Usage: python3 scripts/retro-status.py [--json]
Exit 0 always (status report, not a gate); consumers decide.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.environ.get(
    "HARNESS_STATE_DIR", os.path.join(REPO_ROOT, "state")
)


def _count_lines(path: str) -> int:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def _pending_entries(errors_path: str) -> int:
    """Count entries in ## Pending Review: harvest-comment blocks plus
    `### [date]` candidate headers, between the section header and the
    next `## `."""
    try:
        text = open(errors_path, "r", encoding="utf-8").read()
    except OSError:
        return 0
    m = re.search(r"^## Pending Review\s*$", text, re.MULTILINE)
    if not m:
        return 0
    nxt = re.search(r"^## ", text[m.end():], re.MULTILINE)
    section = text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]
    return len(re.findall(r"<!--\s*harvest:", section)) + len(
        re.findall(r"^### \[", section, re.MULTILINE)
    )


def _retro_reminders() -> int:
    """Count pending /pr-retro reminders in state/retro-reminders.jsonl
    (PR_RETRO entries live there since F-004, not in ERRORS.md —
    COUPLING: written by .claude/hooks/stop-retro-logger.py)."""
    path = os.path.join(STATE_DIR, "retro-reminders.jsonl")
    if not os.path.isfile(path):
        return 0
    count = 0
    try:
        for line in open(path, "r", encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
                count += 1
            except ValueError:
                continue
    except OSError:
        return 0
    return count


def main() -> int:
    errors_md = os.path.join(REPO_ROOT, "docs", "learnings", "ERRORS.md")
    claude_md = os.path.join(REPO_ROOT, "CLAUDE.md")
    rules = sorted(glob.glob(os.path.join(REPO_ROOT, ".claude", "rules", "*.md")))

    status = {
        "errors_md_lines": _count_lines(errors_md),
        "errors_md_budget": 300,
        "pending_review_entries": _pending_entries(errors_md),
        "pending_review_budget": 20,
        "retro_reminders": _retro_reminders(),
        "claude_md_lines": _count_lines(claude_md),
        "claude_md_budget": 100,
        "rules_total_lines": sum(_count_lines(p) for p in rules),
        "rules_budget": 600,
        "rules_file_count": len(rules),
    }

    # notable hook events, last 30 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    notable = {"missing-marker-detected": 0, "verdict-fail": 0,
               "enforced_block": 0, "unverified-citation": 0}
    ev_path = os.path.join(STATE_DIR, "hook-events.jsonl")
    if os.path.isfile(ev_path):
        for line in open(ev_path, "r", encoding="utf-8", errors="replace"):
            try:
                obj = json.loads(line)
                dt = datetime.strptime(obj.get("ts", ""), "%Y-%m-%dT%H:%M:%S%z")
            except Exception:
                continue
            if dt < cutoff:
                continue
            reason = obj.get("reason", "")
            result = obj.get("result", "")
            if reason in ("missing-marker-detected", "unverified-citation"):
                notable[reason] += 1
            if reason == "verdict-recorded" and obj.get("verdict") == "FAIL":
                notable["verdict-fail"] += 1
            if result == "enforced_block":
                notable["enforced_block"] += 1
    status["events_30d"] = notable

    retro_log = os.path.join(STATE_DIR, "retro-log.jsonl")
    last_review = "unknown"
    if os.path.isfile(retro_log):
        try:
            lines = [ln for ln in open(retro_log, encoding="utf-8").read().splitlines() if ln.strip()]
            if lines:
                last_review = json.loads(lines[-1]).get("ts", "unknown")
        except Exception:
            pass
    status["last_weekly_review"] = last_review

    over = []
    if status["errors_md_lines"] > status["errors_md_budget"]:
        over.append("ERRORS.md %d/300 行" % status["errors_md_lines"])
    if status["pending_review_entries"] > status["pending_review_budget"]:
        over.append("Pending Review %d/20 條" % status["pending_review_entries"])
    if status["claude_md_lines"] > status["claude_md_budget"]:
        over.append("CLAUDE.md %d/100 行" % status["claude_md_lines"])
    if status["rules_total_lines"] > status["rules_budget"]:
        over.append("rules 總量 %d/600 行" % status["rules_total_lines"])
    status["over_budget"] = over

    if "--json" in sys.argv:
        print(json.dumps(status, ensure_ascii=False))
    else:
        print(
            "retro-status: ERRORS.md {e}/300 行 | Pending {p}/20 條 | "
            "retro 提醒 {rm} 條 (state/) | "
            "CLAUDE.md {c}/100 行 | rules {r}/600 行 | 上次週審 {w} | "
            "30 天事件 {n}".format(
                e=status["errors_md_lines"], p=status["pending_review_entries"],
                rm=status["retro_reminders"],
                c=status["claude_md_lines"], r=status["rules_total_lines"],
                w=last_review, n=json.dumps(notable, ensure_ascii=False),
            )
        )
        if over:
            print("OVER BUDGET: " + "; ".join(over))
    return 0


if __name__ == "__main__":
    sys.exit(main())
