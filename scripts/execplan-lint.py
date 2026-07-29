#!/usr/bin/env python3
"""execplan-lint.py — mechanical structure checker for ExecPlan instances.

Checks a docs/plans/active/F-NNN-*.md file (or any ExecPlan-shaped markdown
file) against the required structure defined in docs/plans/PLANS.md §2:
header table fields, the 9 required section headers in ascending order,
a Non-Goals / Out of Scope line in §1, an INV- reference in §3, a valid
handoff marker in §9, and no leftover `{{...}}` template placeholders.

Usage:
    python3 scripts/execplan-lint.py <plan.md> [more.md ...]
    python3 scripts/execplan-lint.py                # lints docs/plans/active/*.md
    python3 scripts/execplan-lint.py --json ...      # machine-readable output

Exit status: 1 if any ERROR-severity finding was produced across all linted
files, 0 otherwise (WARN-only or fully clean runs both exit 0).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from typing import List, Optional

REQUIRED_HEADER_FIELDS = [
    "Status",
    "Owner Agent",
    "Branch",
    "Created",
    "Last Updated",
    "Linked PR",
]

# A "## <n>." section heading; title text after the number is not constrained.
SECTION_HEADING_RE = re.compile(r"^##\s+(\d+)\.")
# Any top-level "## " heading, used as the end-of-section boundary.
TOP_HEADING_RE = re.compile(r"^##\s")
# A syntactically valid handoff-style marker: [KEYWORD: <non-empty reason>]
MARKER_RE = re.compile(
    r"\[(?:HANDOFF|VERIFY_FAILED|HUMAN_ATTENTION_REQUIRED):\s*\S[^\]]*\]"
)


class Finding:
    __slots__ = ("severity", "check_id", "message")

    def __init__(self, severity: str, check_id: str, message: str) -> None:
        self.severity = severity  # "ERROR" or "WARN"
        self.check_id = check_id
        self.message = message

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "check_id": self.check_id,
            "message": self.message,
        }


def get_section_content(lines: List[str], section_num: int) -> Optional[List[str]]:
    """Return the lines belonging to '## <section_num>. ...' up to (not
    including) the next top-level '## ' heading, or None if the section
    heading itself is not present."""
    start = None
    for i, line in enumerate(lines):
        m = SECTION_HEADING_RE.match(line)
        if m and int(m.group(1)) == section_num:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if TOP_HEADING_RE.match(lines[j]):
            end = j
            break
    return lines[start:end]


def check_e1_header_table(text: str, findings: List[Finding]) -> None:
    missing = []
    for field_name in REQUIRED_HEADER_FIELDS:
        pattern = re.compile(r"^\|\s*" + re.escape(field_name) + r"\s*\|", re.MULTILINE)
        if not pattern.search(text):
            missing.append(field_name)
    if missing:
        findings.append(
            Finding("ERROR", "E1", "header table missing field(s): " + ", ".join(missing))
        )


def check_e2_sections(lines: List[str], findings: List[Finding]) -> None:
    nums_seen = []
    for line in lines:
        m = SECTION_HEADING_RE.match(line)
        if m:
            nums_seen.append(int(m.group(1)))

    missing = [n for n in range(1, 10) if n not in nums_seen]
    if missing:
        wanted = ", ".join("## %d." % n for n in missing)
        findings.append(Finding("ERROR", "E2", "missing section header(s): " + wanted))
        return

    first_occurrence = {}
    for idx, n in enumerate(nums_seen):
        if n not in first_occurrence:
            first_occurrence[n] = idx
    positions = [first_occurrence[n] for n in range(1, 10)]
    if positions != sorted(positions):
        findings.append(
            Finding("ERROR", "E2", "section headers 1-9 present but not in ascending order")
        )


def check_e3_non_goals(lines: List[str], findings: List[Finding]) -> None:
    section1 = get_section_content(lines, 1)
    if section1 is None:
        return  # already reported by E2

    idx_found = None
    for i, line in enumerate(section1):
        if line.strip().startswith("Non-Goals / Out of Scope"):
            idx_found = i
            break
    if idx_found is None:
        findings.append(Finding("ERROR", "E3", "§1 missing a 'Non-Goals / Out of Scope' line"))
        return

    line = section1[idx_found]
    remainder = line.split(":", 1)[1] if ":" in line else ""
    if remainder.strip():
        return

    for later_line in section1[idx_found + 1 :]:
        if later_line.strip().startswith("- "):
            return

    findings.append(
        Finding(
            "ERROR",
            "E3",
            "'Non-Goals / Out of Scope' line has no inline content and no following '- ' list items",
        )
    )


def check_e4_constraints(lines: List[str], findings: List[Finding]) -> None:
    section3 = get_section_content(lines, 3)
    if section3 is None:
        return  # already reported by E2
    if not any("INV-" in line for line in section3):
        findings.append(Finding("ERROR", "E4", "§3 Constraints does not mention any INV- reference"))


def check_e5_handoff(lines: List[str], findings: List[Finding]) -> None:
    section9 = get_section_content(lines, 9)
    if section9 is None:
        return  # already reported by E2
    if not MARKER_RE.search("\n".join(section9)):
        findings.append(
            Finding(
                "ERROR",
                "E5",
                "§9 Handoff Manifest missing a valid [HANDOFF:...]/[VERIFY_FAILED:...]/"
                "[HUMAN_ATTENTION_REQUIRED:...] marker",
            )
        )


def check_e6_placeholders(text: str, findings: List[Finding]) -> None:
    if "{{" in text:
        first_line = None
        for i, line in enumerate(text.splitlines(), 1):
            if "{{" in line:
                first_line = i
                break
        findings.append(
            Finding("ERROR", "E6", "'{{' placeholder remnant found (first at line %s)" % first_line)
        )


def _status_value(text: str) -> Optional[str]:
    m = re.search(r"^\|\s*Status\s*\|\s*([^|]+?)\s*\|", text, re.M)
    return m.group(1).strip().lower() if m else None


def _step_boxes(lines: List[str]) -> tuple[int, int]:
    """(ticked, unticked) step checkboxes in §4."""
    section4 = get_section_content(lines, 4)
    if section4 is None:
        return (0, 0)
    ticked = sum(1 for l in section4 if re.match(r"^\s*\d+[a-z]?\.\s*\[x\]", l, re.I))
    unticked = sum(1 for l in section4 if re.match(r"^\s*\d+[a-z]?\.\s*\[ \]", l))
    return (ticked, unticked)


def check_e7_completion_consistency(
    path: str, text: str, lines: List[str], findings: List[Finding]
) -> None:
    """INV-ARC-002 — a completion claim must agree with the checkboxes.

    F-003 shipped with §6 recording twelve phases as finished while every
    step in §4 sat unticked, and every gate stayed green. One step really
    had not been done, and nobody noticed across three sessions, because
    nothing compared the plan's own two accounts of itself.
    """
    status = _status_value(text)
    if status is None:
        return  # E1 already reports a missing Status field
    in_completed = "docs/plans/completed/" in path.replace(os.sep, "/")
    done = status in ("done", "completed")

    if done:
        _, unticked = _step_boxes(lines)
        if unticked:
            findings.append(Finding(
                "ERROR", "E7",
                "Status is '%s' but §4 still has %d unticked step(s) — tick them "
                "or say why they were dropped" % (status, unticked),
            ))
        if not in_completed:
            findings.append(Finding(
                "ERROR", "E7",
                "Status is '%s' but the file is not under docs/plans/completed/ "
                "(execplan-lifecycle.md Phase 8 step 2)" % status,
            ))
    elif in_completed:
        findings.append(Finding(
            "ERROR", "E7",
            "file is under docs/plans/completed/ but Status is '%s'" % status,
        ))


def check_w2_progress_without_ticks(lines: List[str], findings: List[Finding]) -> None:
    """The shape F-003 was in for three sessions: §6 narrates progress,
    §4 records none of it. Not an error — a plan can legitimately log a
    decision before finishing step 1 — but past a few entries it means the
    two halves have stopped being reconciled."""
    ticked, unticked = _step_boxes(lines)
    if ticked or not unticked:
        return
    section6 = get_section_content(lines, 6)
    if section6 is None:
        return
    entries = sum(1 for l in section6 if l.lstrip().startswith("- ["))
    if entries >= 3:
        findings.append(Finding(
            "WARN", "W2",
            "§6 has %d progress entries but §4 has no ticked steps — the plan's "
            "two accounts of itself have diverged" % entries,
        ))


def check_w1_clarify_first(lines: List[str], findings: List[Finding]) -> None:
    section1 = get_section_content(lines, 1)
    if section1 is None:
        return  # E2 already reports this; don't pile on with a warning too
    if not any("Clarify-first:" in line for line in section1):
        findings.append(Finding("WARN", "W1", "§1 Goal lacks a 'Clarify-first:' line"))


def lint_file(path: str) -> List[Finding]:
    findings: List[Finding] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        return [Finding("ERROR", "read-failure", "could not read file: %s" % e)]

    lines = text.splitlines()
    check_e1_header_table(text, findings)
    check_e2_sections(lines, findings)
    check_e3_non_goals(lines, findings)
    check_e4_constraints(lines, findings)
    check_e5_handoff(lines, findings)
    check_e6_placeholders(text, findings)
    check_e7_completion_consistency(path, text, lines, findings)
    check_w1_clarify_first(lines, findings)
    check_w2_progress_without_ticks(lines, findings)
    return findings


def discover_default_plans() -> List[str]:
    pattern = os.path.join("docs", "plans", "active", "*.md")
    return sorted(glob.glob(pattern))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint ExecPlan instances against docs/plans/PLANS.md §2 structure spec."
    )
    parser.add_argument("files", nargs="*", help="ExecPlan markdown file(s) to lint")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON output")
    args = parser.parse_args(argv)

    files = args.files
    if not files:
        files = discover_default_plans()
        if not files:
            if args.json:
                print(json.dumps({"results": [], "message": "no active plans"}))
            else:
                print("no active plans")
            return 0

    results = []
    any_error = False
    for path in files:
        findings = lint_file(path)
        if any(f.severity == "ERROR" for f in findings):
            any_error = True
        results.append({"path": path, "findings": [f.to_dict() for f in findings]})

    if args.json:
        print(json.dumps({"results": results}, indent=2))
    else:
        for r in results:
            if not r["findings"]:
                print("OK %s" % r["path"])
            else:
                for f in r["findings"]:
                    print("%s %s: %s %s" % (f["severity"], r["path"], f["check_id"], f["message"]))

    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
