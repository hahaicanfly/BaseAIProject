#!/usr/bin/env python3
"""translate-acceptance.py -- plain-language translator for ExecPlan
acceptance evidence and review verdicts (F-002 guided-start MVP, /guided-start
Step 4).

Why: `scripts/acceptance-run.py` produces machine evidence in
state/acceptance/<plan-stem>.jsonl, and `docs/reviews/*.md` reports carry a
`VERDICT: PASS|FAIL` line plus an optional plain-language traffic-light line
(review-protocol.md's Output Format). Both are readable but not friendly to
a non-technical user. This script translates them into plain language --
it invents no new pass/fail judgment of its own, it only reads what already
exists and says plainly when it can't find something (never guesses).

This is a **read-only** tool: it never opens a file in write mode, never
calls .write(), and never appends to any state/*.jsonl or docs/reviews/*.md
file. Exit code is always 0 -- this is a format-translation tool, not an
acceptance gate -- except for a genuinely unexpected runtime error this
script did not anticipate (e.g. a file-permission error), which is allowed
to propagate as a non-zero exit rather than being silently swallowed.

Usage:
    python3 scripts/translate-acceptance.py [plan.md] [--review <file>] [--json]

If plan.md is omitted, the newest F-*.md file (by mtime) in
docs/plans/active/ is used (same convention as scripts/acceptance-run.py).
If none can be found, this is reported plainly in the output -- never
fabricated.

If --review is omitted, this script tries a best-effort auto-match against
state/verifications.jsonl using a filename-substring heuristic keyed off the
plan's `F-NNN` id (e.g. plan stem "F-001-..." -> normalized id "f001",
matched against the normalized basename of each evidence_path). Zero matches
or more than one match are both reported as an explicit caveat -- this
script never picks a "looks plausible" answer when the match isn't unique.

state/acceptance/<stem>.jsonl is append-only: `acceptance-run.py` appends a
fresh full run's worth of lines every time it is invoked, so the same
`label` can appear many times across many runs. This script keeps only the
LAST record seen per label (append-order = chronological order), never
mixing older and newer results together.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# scripts/translate-acceptance.py -> repo root is the parent of scripts/
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

STATUS_EMOJI = {"PASS": "\U0001F7E2", "FAIL": "\U0001F534", "SKIP": "⚪"}  # green / red / white circle
TRAFFIC_LIGHT_RE = re.compile("[\U0001F7E2\U0001F7E1\U0001F534]")  # green / yellow / red circle
VERDICT_LINE_RE = re.compile(r"^\s*\*{0,2}VERDICT:\s*(PASS|FAIL)\*{0,2}\s*(\S+)?\s*$")
VERDICT_LOOSE_RE = re.compile(r"\*{0,2}VERDICT:\s*(PASS|FAIL)\*{0,2}\s*(\S+)?")
FEATURE_ID_RE = re.compile(r"^(F-\d+)")
NON_ALNUM_RE = re.compile(r"[^a-z0-9]")


# --------------------------------------------------------------------------
# Small shared helpers (deliberately not imported from any other script --
# each scripts/*.py file in this repo is self-contained by convention)
# --------------------------------------------------------------------------

def get_state_dir() -> Path:
    override = os.environ.get("HARNESS_STATE_DIR")
    if override:
        return Path(override)
    return REPO_ROOT / "state"


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def normalize(s: str) -> str:
    return NON_ALNUM_RE.sub("", s.lower())


def find_default_plan(active_dir: Path) -> Optional[Path]:
    """Newest (by mtime) F-*.md file in active_dir, or None. Mirrors
    scripts/acceptance-run.py's find_default_plan exactly."""
    if not active_dir.is_dir():
        return None
    candidates = [p for p in active_dir.glob("F-*.md") if p.is_file()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def resolve_plan_path(arg_plan: Optional[str]) -> Tuple[Optional[Path], List[str]]:
    """Returns (resolved_absolute_path_or_None, notes). Never raises."""
    notes: List[str] = []
    if arg_plan:
        p = Path(arg_plan)
        if not p.is_absolute():
            p = (REPO_ROOT / p).resolve()
        if not p.is_file():
            notes.append("Specified ExecPlan file does not exist: {}".format(repo_relative(p)))
            return None, notes
        return p, notes

    active_dir = REPO_ROOT / "docs" / "plans" / "active"
    found = find_default_plan(active_dir)
    if found is None:
        notes.append(
            "No plan given, and docs/plans/active/ has no F-*.md file "
            "(the directory may be empty or missing)."
        )
        return None, notes
    return found, notes


# --------------------------------------------------------------------------
# Acceptance jsonl -> plain language
# --------------------------------------------------------------------------

def load_acceptance_records(stem: str) -> Tuple[List[dict], List[str]]:
    """Read state/acceptance/<stem>.jsonl, keep only the LAST record per
    label (first-seen order for display), return (records, notes). Never
    raises; malformed lines are skipped and noted, not fatal."""
    notes: List[str] = []
    jsonl_path = get_state_dir() / "acceptance" / "{}.jsonl".format(stem)
    if not jsonl_path.is_file():
        notes.append(
            "No acceptance record yet (could not find {}).".format(repo_relative(jsonl_path))
        )
        return [], notes

    order: List[str] = []
    last_by_label: Dict[str, dict] = {}
    total_lines = 0
    bad_lines = 0

    with jsonl_path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            total_lines += 1
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                bad_lines += 1
                continue
            label = rec.get("label")
            if not label:
                bad_lines += 1
                continue
            if label not in last_by_label:
                order.append(label)
            last_by_label[label] = rec  # append-only file: a later line always wins

    if total_lines == 0:
        notes.append(
            "Acceptance record file exists but is empty ({}) -- nothing to translate yet.".format(
                repo_relative(jsonl_path)
            )
        )
        return [], notes
    if bad_lines:
        notes.append(
            "{} line(s) in the acceptance record file could not be parsed and were skipped.".format(bad_lines)
        )

    return [last_by_label[label] for label in order], notes


def status_of(rec: dict) -> str:
    if rec.get("skipped"):
        return "SKIP"
    return "PASS" if rec.get("pass") else "FAIL"


def render_acceptance(records: List[dict]) -> List[str]:
    """Plain-language lines. Reuses acceptance-run.py's own Summary /
    expect-fail wording verbatim (not reinventing that phrasing)."""
    lines: List[str] = []
    n_pass = n_fail = n_skip = 0
    for rec in records:
        status = status_of(rec)
        if status == "PASS":
            n_pass += 1
        elif status == "FAIL":
            n_fail += 1
        else:
            n_skip += 1
        emoji = STATUS_EMOJI[status]
        lines.append("{} {} {}: {}".format(emoji, status, rec.get("label"), rec.get("cmd")))

    total = len(records)
    lines.append("Summary: {} total, {} pass, {} fail, {} skip".format(total, n_pass, n_fail, n_skip))
    if any(r.get("expect_fail") for r in records):
        lines.append(
            "Note: some checks above are expect-fail (negative-lint style) -- "
            "for those, PASS means the intentional failure succeeded, it does "
            "not mean something broke."
        )
    return lines


# --------------------------------------------------------------------------
# Review report -> plain language
# --------------------------------------------------------------------------

def parse_verdict(text: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """Returns (verdict, evidence_path_or_None, line_index_or_None).
    Supports both existing VERDICT line conventions seen in docs/reviews/:
      - "**VERDICT: PASS**"                                (bold, no path)
      - "VERDICT: FAIL docs/reviews/<file>.md"             (plain, with path)
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = VERDICT_LINE_RE.match(line)
        if m:
            return m.group(1), m.group(2), i
    # Fallback: loose, unanchored search in case the VERDICT text has
    # leading/trailing prose on its line.
    m = VERDICT_LOOSE_RE.search(text)
    if m:
        return m.group(1), m.group(2), None
    return None, None, None


def find_traffic_light_line(text: str) -> Optional[str]:
    for line in text.splitlines():
        if TRAFFIC_LIGHT_RE.search(line):
            return line.strip()
    return None


SUMMARY_HEADING_RE = re.compile(r"^#{1,3}\s*(總結|Summary)\b")


def find_summary_section(text: str) -> Optional[str]:
    """Grab the body of a '## 總結' / '## Summary' heading, if present."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if SUMMARY_HEADING_RE.match(line.strip()):
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if re.match(r"^#{1,3}\s", lines[j]):
            end = j
            break
    chunk = [line for line in lines[start:end] if line.strip()]
    return "\n".join(chunk) if chunk else None


def render_review(review_path: Path) -> Tuple[List[str], List[str], dict]:
    notes: List[str] = []
    if not review_path.is_file():
        notes.append("Specified review file does not exist: {}".format(repo_relative(review_path)))
        return [], notes, {}

    text = review_path.read_text(encoding="utf-8", errors="replace")
    verdict, verdict_path, verdict_idx = parse_verdict(text)
    light_line = find_traffic_light_line(text)

    lines: List[str] = []
    if light_line:
        lines.append("Plain-language summary: {}".format(light_line))
    else:
        notes.append("This report has no plain-language layer -- excerpting the technical original below.")
        excerpt = find_summary_section(text)
        if excerpt is None and verdict_idx is not None:
            all_lines = text.splitlines()
            start = max(0, verdict_idx - 6)
            excerpt_lines = [line for line in all_lines[start:verdict_idx] if line.strip()]
            excerpt = "\n".join(excerpt_lines) if excerpt_lines else None
        if excerpt:
            lines.append("Original excerpt:")
            for line in excerpt.splitlines():
                lines.append("  " + line)

    if verdict:
        tail = " {}".format(verdict_path) if verdict_path else ""
        lines.append("VERDICT: {}{}".format(verdict, tail))
    else:
        notes.append("No VERDICT line found in this report -- cannot determine PASS/FAIL.")

    return lines, notes, {"verdict": verdict, "verdict_path": verdict_path, "has_plain_layer": bool(light_line)}


# --------------------------------------------------------------------------
# Best-effort review auto-match (only used when --review is not given)
# --------------------------------------------------------------------------

def extract_feature_id(stem: str) -> Optional[str]:
    m = FEATURE_ID_RE.match(stem)
    if not m:
        return None
    return normalize(m.group(1))


def autodetect_review(stem: str) -> Tuple[Optional[Path], List[str]]:
    """Best-effort match against state/verifications.jsonl by normalized
    filename substring. Returns (path_or_None, notes). Ambiguous (>1) or
    empty (0) matches are both reported as an explicit caveat rather than
    picking a plausible-looking answer."""
    notes: List[str] = []
    feature_id = extract_feature_id(stem)
    verif_path = get_state_dir() / "verifications.jsonl"

    if not verif_path.is_file():
        notes.append(
            "Could not find state/verifications.jsonl -- skipping review auto-match "
            "(pass --review explicitly instead)."
        )
        return None, notes
    if not feature_id:
        notes.append(
            "Plan filename is not in F-NNN form -- cannot auto-match a review by filename "
            "heuristic (pass --review explicitly instead)."
        )
        return None, notes

    candidates: List[str] = []
    with verif_path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                continue
            ev = rec.get("evidence_path")
            if not ev:
                continue
            if feature_id in normalize(ev) and ev not in candidates:
                candidates.append(ev)

    if not candidates:
        notes.append(
            "No entry in state/verifications.jsonl has a filename matching {} "
            "(pass --review explicitly instead).".format(feature_id.upper())
        )
        return None, notes
    if len(candidates) > 1:
        notes.append(
            "{} entries in state/verifications.jsonl have filenames matching {} -- "
            "not guessing which one applies, listing all: {} "
            "(pass --review to pick one explicitly).".format(
                len(candidates), feature_id.upper(), ", ".join(candidates)
            )
        )
        return None, notes

    notes.append(
        "Auto-matched by filename-substring heuristic (not a guaranteed unique match): {}".format(
            candidates[0]
        )
    )
    return REPO_ROOT / candidates[0], notes


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Translate ExecPlan acceptance-run evidence (state/acceptance/*.jsonl) and a "
            "review report's VERDICT into plain language. Read-only; exit code is always 0 "
            "except for a genuinely unexpected runtime error."
        )
    )
    parser.add_argument(
        "plan",
        nargs="?",
        default=None,
        help="Path to an ExecPlan markdown file (default: newest F-*.md in docs/plans/active/)",
    )
    parser.add_argument(
        "--review",
        default=None,
        help="Path to a docs/reviews/*.md review report to translate alongside the acceptance evidence",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit a machine-readable JSON object instead of prose"
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    all_notes: List[str] = []
    plan_repo_rel: Optional[str] = None

    plan_path, plan_notes = resolve_plan_path(args.plan)
    all_notes.extend(plan_notes)

    stem: Optional[str] = None
    if plan_path is not None:
        plan_repo_rel = repo_relative(plan_path)
        stem = plan_path.stem
    elif args.plan:
        # The user named an explicit (nonexistent) plan path -- still try
        # its stem for the acceptance lookup, in case the jsonl outlived
        # the plan file (e.g. plan moved/renamed after the run).
        stem = Path(args.plan).stem

    acceptance_records: List[dict] = []
    acceptance_lines: List[str] = []
    if stem:
        acceptance_records, acc_notes = load_acceptance_records(stem)
        all_notes.extend(acc_notes)
        if acceptance_records:
            acceptance_lines = render_acceptance(acceptance_records)

    review_lines: List[str] = []
    review_meta: dict = {}
    review_path_used: Optional[Path] = None
    if args.review:
        rp = Path(args.review)
        if not rp.is_absolute():
            rp = (REPO_ROOT / rp).resolve()
        review_path_used = rp
        review_lines, review_notes, review_meta = render_review(rp)
        all_notes.extend(review_notes)
    elif stem:
        auto_path, auto_notes = autodetect_review(stem)
        all_notes.extend(auto_notes)
        if auto_path is not None:
            review_path_used = auto_path
            review_lines, review_notes, review_meta = render_review(auto_path)
            all_notes.extend(review_notes)

    if args.json:
        payload = {
            "plan": plan_repo_rel,
            "acceptance": {
                "records": [
                    {
                        "label": r.get("label"),
                        "cmd": r.get("cmd"),
                        "status": status_of(r),
                        "exit_code": r.get("exit_code"),
                        "expect_fail": r.get("expect_fail", False),
                        "ts": r.get("ts"),
                    }
                    for r in acceptance_records
                ],
                "summary": {
                    "total": len(acceptance_records),
                    "pass": sum(1 for r in acceptance_records if status_of(r) == "PASS"),
                    "fail": sum(1 for r in acceptance_records if status_of(r) == "FAIL"),
                    "skip": sum(1 for r in acceptance_records if status_of(r) == "SKIP"),
                },
            }
            if acceptance_records
            else None,
            "review": {
                "path": repo_relative(review_path_used) if review_path_used else None,
                "verdict": review_meta.get("verdict"),
                "verdict_evidence_path": review_meta.get("verdict_path"),
                "has_plain_layer": review_meta.get("has_plain_layer", False),
            }
            if review_path_used
            else None,
            "notes": all_notes,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("=== ExecPlan Acceptance Evidence, Translated ===")
    print("Plan: {}".format(plan_repo_rel if plan_repo_rel else "(not resolved)"))
    print()
    if acceptance_lines:
        print("-- Acceptance results (state/acceptance/{}.jsonl) --".format(stem))
        for line in acceptance_lines:
            print(line)
        print()
    if review_lines:
        label = repo_relative(review_path_used) if review_path_used else "?"
        print("-- Review, translated ({}) --".format(label))
        for line in review_lines:
            print(line)
        print()
    if all_notes:
        print("-- Caveats / evidence not found --")
        for note in all_notes:
            print("- {}".format(note))

    return 0


if __name__ == "__main__":
    sys.exit(main())
