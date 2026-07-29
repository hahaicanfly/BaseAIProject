#!/usr/bin/env python3
"""check-hook-doc-coupling.py — make a hook's literal dependency on a
document's wording visible, and keep its target path honest.

Why this exists: session-activation-check.py decides whether the product
build/test slot is still unfilled by testing for the literal "{{fill in"
inside CLAUDE.md. That is a contract between a Python file and a sentence
in a markdown file, and nothing announced it. When CI wanted that exact
string gone (PR #14, placeholder-gate), the obvious fix — reword the line
— would have made CI green by silently switching off a warning printed at
every session start. It was caught by luck, not by design.

What this does NOT check, deliberately: whether the needle is still
present in the target. These needles detect an *unfilled* slot, so in a
properly activated fork they are supposed to be gone. A gate demanding
their presence would fire on every real project using this template —
the same mistake in reverse as the one that produced this script
(ERRORS.md 2026-07-29: "ask whether the rule holds for the template
itself, not only for projects using it").

What it does instead is turn an undeclared dependency into a declared
one. Every literal-needle-against-a-document pair must carry a
`# COUPLING: <path> -- <what the needle means>` comment in its enclosing
block, so that anyone editing that document can grep for it.

Checks:
    C1 (ERROR) a hook couples to a document path that does not exist.
    C2 (ERROR) a literal needle is tested against a document with no
       COUPLING declaration in its enclosing block.
    C3 (ERROR) a COUPLING declaration names a path that does not exist.

Usage:
    python3 scripts/check-hook-doc-coupling.py             # gate
    python3 scripts/check-hook-doc-coupling.py --inventory # list couplings, exit 0
    python3 scripts/check-hook-doc-coupling.py --json

Exit status: 1 if any ERROR, else 0. --inventory always exits 0.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"

COUPLING_RE = re.compile(r"#\s*COUPLING:\s*(?P<path>\S+)\s*--\s*(?P<note>.+?)\s*$")
# A string constant that looks like a repo document rather than a fragment.
DOC_PATH_RE = re.compile(r"^[\w./-]+\.(md|json|ya?ml)$")


def _string_constants(node: ast.AST) -> list[str]:
    return [n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _needles(node: ast.AST) -> list[str]:
    """String literals used as the left side of an `x in text` test.

    That is the shape of "does this document still say this?" — the exact
    pattern that couples a hook to someone else's wording.
    """
    found = []
    for n in ast.walk(node):
        if not isinstance(n, ast.Compare):
            continue
        if not any(isinstance(op, ast.In) for op in n.ops):
            continue
        if isinstance(n.left, ast.Constant) and isinstance(n.left.value, str):
            found.append(n.left.value)
    return found


def scan_hook(path: Path) -> tuple[list[dict], list[dict]]:
    """Return (couplings, findings) for one hook file."""
    source = path.read_text(encoding="utf-8")
    rel = path.relative_to(REPO_ROOT).as_posix()
    lines = source.split("\n")
    couplings: list[dict] = []
    findings: list[dict] = []

    declared: dict[int, tuple[str, str]] = {}
    for i, line in enumerate(lines, start=1):
        m = COUPLING_RE.search(line)
        if m:
            declared[i] = (m.group("path"), m.group("note"))

    for decl_line, (decl_path, note) in declared.items():
        if not (REPO_ROOT / decl_path).exists():
            findings.append({
                "rule": "C3", "severity": "ERROR", "file": rel, "line": decl_line,
                "message": f"COUPLING declares {decl_path}, which does not exist",
            })

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        findings.append({
            "rule": "C1", "severity": "ERROR", "file": rel, "line": exc.lineno or 0,
            "message": f"cannot parse: {exc.msg}",
        })
        return couplings, findings

    # A "block" is any container that groups a path with the needles tested
    # against it — the tuple/list/assignment the pattern actually appears in.
    # Only the INNERMOST such container is reported: an assignment holding a
    # list of tuples matches at all three levels, and the outer two would
    # cross-multiply every path against every needle in the whole structure.
    candidates = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Tuple, ast.List, ast.Assign)):
            continue
        needles = _needles(node)
        if not needles:
            continue
        paths = [s for s in _string_constants(node)
                 if DOC_PATH_RE.match(s) and s not in needles]
        if paths:
            candidates.append((node, paths, needles))

    def _encloses(outer: ast.AST, inner: ast.AST) -> bool:
        if outer is inner:
            return False
        return any(n is inner for n in ast.walk(outer))

    innermost = [c for c in candidates
                 if not any(_encloses(c[0], other[0]) for other in candidates)]

    for node, paths, needles in innermost:
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start) or start
        # Declarations count when they sit inside the block or on the few
        # lines just above it, where a comment for the block would live.
        in_scope = [d for ln, d in declared.items() if start - 3 <= ln <= end]

        for doc in paths:
            if not (REPO_ROOT / doc).exists():
                findings.append({
                    "rule": "C1", "severity": "ERROR", "file": rel, "line": start,
                    "message": f"couples to {doc}, which does not exist",
                })
            for needle in needles:
                couplings.append({
                    "hook": rel, "line": start, "document": doc, "needle": needle,
                    "declared": bool(in_scope),
                    "note": in_scope[0][1] if in_scope else None,
                })
            if not in_scope:
                findings.append({
                    "rule": "C2", "severity": "ERROR", "file": rel, "line": start,
                    "message": (
                        f"undeclared coupling to {doc} via {needles!r} — add a "
                        f"'# COUPLING: {doc} -- <what this needle means>' comment "
                        f"so an editor of that file can find it"
                    ),
                })

    return couplings, findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--inventory", action="store_true",
                    help="print every coupling found and exit 0")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    couplings: list[dict] = []
    findings: list[dict] = []
    for hook in sorted(HOOKS_DIR.glob("*.py")):
        c, f = scan_hook(hook)
        couplings.extend(c)
        findings.extend(f)

    errors = [f for f in findings if f["severity"] == "ERROR"]

    if args.json:
        print(json.dumps({"couplings": couplings, "findings": findings},
                         ensure_ascii=False, indent=1))
    else:
        if args.inventory:
            if not couplings:
                print("no hook couples to a document by literal string")
            for c in couplings:
                mark = "declared" if c["declared"] else "UNDECLARED"
                print(f"{mark}  {c['hook']}:{c['line']}  {c['document']}  needle={c['needle']!r}")
                if c["note"]:
                    print(f"           -> {c['note']}")
        for f in findings:
            print(f"{f['severity']} {f['file']}:{f['line']} [{f['rule']}] {f['message']}")
        print(f"SUMMARY: {len(errors)} ERROR across {len(couplings)} coupling(s)")

    if args.inventory:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
