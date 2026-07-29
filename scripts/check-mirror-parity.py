#!/usr/bin/env python3
"""check-mirror-parity.py — catch a Chinese mirror that has stopped
describing what its English original says.

Why this exists: F-003 rewrote CLAUDE.md's standing-rules section into the
tier-pack mechanism and did not touch CLAUDE_zh.md, which went on telling
human readers that seven rule files were auto-loaded — for eight commits,
past every existing gate. docs/INDEX.md labelled two of those files
"(standing)" for just as long. Nothing caught either, because
check-doc-refs.py proves a *path* exists; it has no way to know whether a
*sentence* is still true.

Structure is the part of "still true" a script can actually check. A
section that gets rewritten, split, merged or dropped on one side almost
always changes the shape of that side: how many sections there are, how
many subsections sit under each, how many table rows. Text cannot be
compared across languages; shape can.

Checks:
    P1 (ERROR) different number of '## ' sections between a file and its
       mirror. This is the CLAUDE_zh case: en merged two sections into
       one, zh kept both.
    P2 (ERROR) same section count, but a differing number of '### '
       subsections inside the n-th section. This is a section rewritten
       on one side only.
    P3 (WARN)  differing table-row count inside the n-th section — a row
       added to one side and not the other (a document-map entry, a
       roster line). WARN, not ERROR: a mirror may legitimately carry an
       extra note row.

Headings and tables inside fenced code blocks are ignored — directory
trees and shell snippets are full of '#' lines that are not headings.

Pairs are discovered two ways, matching this repo's two mirror
conventions (CLAUDE.md "Document Map"):
    same-directory   <name>.md        <-> <name>_zh.md
    auto-discovered  .claude/<kind>/<name>.md
                     <-> agent_docs/zh/<kind>/<name>.md

Usage:
    python3 scripts/check-mirror-parity.py            # gate: exit 1 on ERROR
    python3 scripts/check-mirror-parity.py --report   # always exit 0
    python3 scripts/check-mirror-parity.py --json
    python3 scripts/check-mirror-parity.py --pair CLAUDE.md

Exit status: 1 if any ERROR-severity finding exists, else 0. With
--report, always 0.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories that never hold mirrored prose: runtime state, git internals,
# per-task ExecPlans (single-language by design), and backups.
SKIP_PARTS = {".git", "state", "node_modules", "__pycache__"}
SKIP_PREFIXES = ("docs/plans/",)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
H2_RE = re.compile(r"^##\s+(.*?)\s*$")
H3_RE = re.compile(r"^###\s+(.*?)\s*$")
TABLE_ROW_RE = re.compile(r"^\s*\|")

# Mirror kinds that live under agent_docs/zh/ instead of beside the original.
AUTO_DISCOVERED_KINDS = ("agents", "rules", "commands")


def _skip(rel: str) -> bool:
    parts = Path(rel).parts
    if any(p in SKIP_PARTS for p in parts):
        return True
    return rel.startswith(SKIP_PREFIXES)


def outline(text: str) -> list[dict]:
    """Section outline of a markdown file, code fences excluded.

    Returns one entry per '## ' section: its title, and the counts of the
    things inside it that a rewrite would disturb.
    """
    sections: list[dict] = []
    current: dict | None = None
    in_fence = False
    fence_marker = ""

    for raw in text.splitlines():
        fence = FENCE_RE.match(raw)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue

        h2 = H2_RE.match(raw)
        if h2:
            current = {"title": h2.group(1), "subsections": 0, "table_rows": 0}
            sections.append(current)
            continue
        if current is None:
            continue
        if H3_RE.match(raw):
            current["subsections"] += 1
        elif TABLE_ROW_RE.match(raw):
            current["table_rows"] += 1

    return sections


def discover_pairs() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    seen: set[tuple[Path, Path]] = set()

    for path in sorted(REPO_ROOT.rglob("*.md")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if _skip(rel) or rel.endswith("_zh.md"):
            continue

        sibling = path.with_name(path.stem + "_zh.md")
        if sibling.is_file():
            key = (path, sibling)
            if key not in seen:
                seen.add(key)
                pairs.append(key)
            continue

        parts = Path(rel).parts
        if len(parts) >= 3 and parts[0] == ".claude" and parts[1] in AUTO_DISCOVERED_KINDS:
            mirror = REPO_ROOT / "agent_docs" / "zh" / parts[1] / Path(*parts[2:])
            if mirror.is_file():
                key = (path, mirror)
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)

    return pairs


def compare(src: Path, mirror: Path) -> list[dict]:
    a = outline(src.read_text(encoding="utf-8"))
    b = outline(mirror.read_text(encoding="utf-8"))
    rel_src = src.relative_to(REPO_ROOT).as_posix()
    rel_mir = mirror.relative_to(REPO_ROOT).as_posix()
    findings: list[dict] = []

    if len(a) != len(b):
        only_src = [s["title"] for s in a[len(b):]] if len(a) > len(b) else []
        only_mir = [s["title"] for s in b[len(a):]] if len(b) > len(a) else []
        findings.append({
            "rule": "P1", "severity": "ERROR", "file": rel_src, "mirror": rel_mir,
            "message": (
                f"section count differs: {len(a)} vs {len(b)}"
                + (f"; trailing only in source: {only_src}" if only_src else "")
                + (f"; trailing only in mirror: {only_mir}" if only_mir else "")
            ),
        })

    for i, (sa, sb) in enumerate(zip(a, b), start=1):
        if sa["subsections"] != sb["subsections"]:
            findings.append({
                "rule": "P2", "severity": "ERROR", "file": rel_src, "mirror": rel_mir,
                "message": (
                    f"section {i} subsection count differs: "
                    f"{sa['subsections']} in \"{sa['title']}\" vs "
                    f"{sb['subsections']} in \"{sb['title']}\""
                ),
            })
        if sa["table_rows"] != sb["table_rows"]:
            findings.append({
                "rule": "P3", "severity": "WARN", "file": rel_src, "mirror": rel_mir,
                "message": (
                    f"section {i} table-row count differs: "
                    f"{sa['table_rows']} in \"{sa['title']}\" vs "
                    f"{sb['table_rows']} in \"{sb['title']}\""
                ),
            })

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="store_true",
                    help="print findings but always exit 0")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--pair", metavar="PATH",
                    help="check only this file against its mirror")
    args = ap.parse_args()

    pairs = discover_pairs()
    if args.pair:
        target = (REPO_ROOT / args.pair).resolve()
        pairs = [p for p in pairs if p[0].resolve() == target or p[1].resolve() == target]
        if not pairs:
            print(f"no mirror pair found for {args.pair}", file=sys.stderr)
            return 2

    findings: list[dict] = []
    for src, mirror in pairs:
        findings.extend(compare(src, mirror))

    errors = [f for f in findings if f["severity"] == "ERROR"]
    warns = [f for f in findings if f["severity"] == "WARN"]

    if args.json:
        print(json.dumps({"pairs": len(pairs), "findings": findings},
                         ensure_ascii=False, indent=1))
    else:
        for f in findings:
            print(f"{f['severity']} {f['file']} <-> {f['mirror']} [{f['rule']}] {f['message']}")
        print(f"SUMMARY: {len(errors)} ERROR, {len(warns)} WARN across {len(pairs)} mirror pair(s)")

    if args.report:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
