#!/usr/bin/env python3
"""check-doc-refs.py — verify that paths and section refs cited inside this
harness's canon markdown actually exist, so dead references don't quietly
become hallucination bait (see ExecPlan F-001 step C3a; the PR #2 review
caught a zh-mirror desync and stale line-count claims of exactly this
class — this script mechanizes that class of catch).

Checks (see docstrings on the check_* functions for exact rules):
    R1 (ERROR) backtick-quoted repo-relative path that does not exist.
    R2 (ERROR/WARN) `file:line` / `file:start-end` refs: missing target
       file is ERROR; a line number beyond the target's EOF is WARN
       (line-count drift).
    R3 (WARN) `<path> §N` section refs: missing target file, or fewer
       than N '## '-prefixed heading lines in it.
    R4 (WARN) canon doc missing its zh-mirror sibling.

Path resolution (R1/R2/R3): a referenced path is checked first as
repo-root-relative, then — if that misses — relative to the directory of
the file that cites it (mirrors how a markdown renderer resolves a
relative link). Neither hitting is what makes it a finding.

Usage:
    python3 scripts/check-doc-refs.py                  # same as --all
    python3 scripts/check-doc-refs.py --all
    python3 scripts/check-doc-refs.py --file <path.md>
    python3 scripts/check-doc-refs.py --all --json
    python3 scripts/check-doc-refs.py --all --strict    # exit 1 on any ERROR

Exit status: without --strict, always 0 (this script is meant to be usable
as a passive sentinel/report generator). With --strict, 1 if any
ERROR-severity finding exists across the run, else 0.
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
IGNORE_FILE = os.path.join(REPO_ROOT, ".claude", "doc-ref-ignore.txt")

DEFAULT_TOP_FILES = ["CLAUDE.md", "CLAUDE_zh.md"]
DEFAULT_GLOB_PATTERNS = [".claude/**/*.md", "docs/**/*.md", "agent_docs/**/*.md"]

FENCE_RE = re.compile(r"^\s*```")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
HEADING2_RE = re.compile(r"^##\s")
URL_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*://")
SECTION_REF_OUTSIDE_RE = re.compile(r"`([^`\n]+)`\s*§\s*(\d+)")
SECTION_REF_INSIDE_RE = re.compile(r"^(.+?)\s+§\s*(\d+)$")

# R4 mirror-pairing rules (spec-literal: exact directories, not recursive).
MIRROR_SIBLING_DIRS = {
    os.path.join(".claude", "protocols"),
    os.path.join(".claude", "templates"),
    "docs",
    os.path.join("docs", "plans"),
}
MIRROR_AGENTDOCS_DIRS = {
    os.path.join(".claude", "rules"): "rules",
    os.path.join(".claude", "agents"): "agents",
    os.path.join(".claude", "commands"): "commands",
}


class Finding:
    __slots__ = ("severity", "file", "line", "check_id", "referenced", "hint")

    def __init__(self, severity: str, file: str, line: int, check_id: str, referenced: str, hint: str) -> None:
        self.severity = severity  # "ERROR" or "WARN"
        self.file = file
        self.line = line
        self.check_id = check_id
        self.referenced = referenced
        self.hint = hint

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "check": self.check_id,
            "referenced": self.referenced,
            "hint": self.hint,
        }

    def to_line(self) -> str:
        return "%s %s:%d %s %s — %s" % (
            self.severity,
            self.file,
            self.line,
            self.check_id,
            self.referenced,
            self.hint,
        )


# --------------------------------------------------------------------------
# Allowlist
# --------------------------------------------------------------------------

def load_allowlist(path: str = IGNORE_FILE) -> List[str]:
    patterns: List[str] = []
    if not os.path.isfile(path):
        return patterns
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line)
    return patterns


def is_allowlisted(referenced: str, patterns: List[str]) -> bool:
    return any(fnmatch.fnmatch(referenced, p) for p in patterns)


# --------------------------------------------------------------------------
# File discovery
# --------------------------------------------------------------------------

def discover_all_files() -> List[str]:
    files: List[str] = []
    for name in DEFAULT_TOP_FILES:
        p = os.path.join(REPO_ROOT, name)
        if os.path.isfile(p):
            files.append(p)
    for pattern in DEFAULT_GLOB_PATTERNS:
        files.extend(glob.glob(os.path.join(REPO_ROOT, pattern), recursive=True))
    # de-dup, keep stable order
    seen = set()
    out = []
    for f in files:
        rf = os.path.normpath(f)
        if rf not in seen:
            seen.add(rf)
            out.append(rf)
    return sorted(out)


# --------------------------------------------------------------------------
# Text preprocessing
# --------------------------------------------------------------------------

def strip_fenced_blocks(text: str) -> str:
    """Blank out the content of ``` fenced code blocks (keeping line count
    and line numbers intact) so example command/regex/JSON snippets inside
    them are never mistaken for doc-ref citations. Doc-ref citations are an
    inline-prose convention (single backtick), not something we expect to
    find inside a fenced example."""
    lines = text.split("\n")
    out = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


# --------------------------------------------------------------------------
# Candidate classification
# --------------------------------------------------------------------------

def is_placeholder_or_external(tok: str) -> bool:
    """True if tok is a URL/URI, an absolute or home-relative path (out of
    repo-relative scope by definition), or contains a known
    template/placeholder marker per the R1 skip list: {{ , < / >, *, $,
    [ / ] (bracket-style placeholders like `[date]`), F-NNN, YYYY-MM-DD,
    or a literal '...' elision marker."""
    if URL_SCHEME_RE.match(tok):
        return True
    if tok.startswith("/") or tok.startswith("~"):
        return True
    for marker in ("{{", "<", ">", "*", "$", "...", "[", "]"):
        if marker in tok:
            return True
    if "F-NNN" in tok or "YYYY-MM-DD" in tok:
        return True
    return False


def looks_like_repo_path(tok: str) -> bool:
    """Structural precision filter beyond 'contains / and no space': the
    token must either end with / (directory reference) or have a dot in
    its final path segment (file extension). Filters stray slash-joined
    prose fragments like `N/A` that are not path references at all."""
    if tok.endswith("/"):
        return True
    last_seg = tok.rsplit("/", 1)[-1]
    return "." in last_seg


def parse_path_line_token(tok: str) -> Optional[Tuple[str, int, Optional[int]]]:
    """Recognize `path:123` or `path:12-34` shaped tokens for R2. Requires
    a dot in the path's final segment (an extension) to avoid false
    positives on unrelated colon-separated text."""
    if ":" not in tok:
        return None
    path_part, _, rest = tok.rpartition(":")
    if not path_part:
        return None
    last_seg = path_part.rsplit("/", 1)[-1]
    if "." not in last_seg:
        return None
    m = re.match(r"^(\d+)(?:-(\d+))?$", rest)
    if not m:
        return None
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else None
    return path_part, start, end


# --------------------------------------------------------------------------
# Path resolution
# --------------------------------------------------------------------------

def resolve_ref(raw_path: str, containing_file_abs: str) -> Optional[str]:
    """Try repo-root-relative, then containing-file-directory-relative.
    Returns the resolved absolute path if it exists, else None."""
    candidates = [os.path.normpath(os.path.join(REPO_ROOT, raw_path))]
    containing_dir = os.path.dirname(containing_file_abs)
    dir_rel = os.path.normpath(os.path.join(containing_dir, raw_path))
    if dir_rel not in candidates:
        candidates.append(dir_rel)
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


_SUFFIX_INDEX: Optional[List[str]] = None


def _build_suffix_index() -> List[str]:
    """Lazy repo tree index (files and dirs; dirs carry a trailing /) for
    unique-suffix resolution of shorthand references."""
    global _SUFFIX_INDEX
    if _SUFFIX_INDEX is not None:
        return _SUFFIX_INDEX
    idx: List[str] = []
    skip = {".git", "node_modules", "__pycache__", ".DS_Store"}
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in skip]
        for d in dirs:
            idx.append(os.path.join(root, d) + "/")
        for fn in files:
            if fn in skip:
                continue
            idx.append(os.path.join(root, fn))
    _SUFFIX_INDEX = idx
    return idx


def resolve_unique_suffix(raw_path: str) -> List[str]:
    """Docs routinely cite shorthand — `handoff-protocol.md:19`,
    `completed/` — omitting the directory prefix. Rather than force
    prose (and archived reports) to spell full paths, resolve the
    shorthand by suffix match against the repo tree: exactly one match
    means the reference is unambiguous and real. Returns all matches
    (caller decides: 1 = resolved, 0 = dead, >1 = ambiguous WARN)."""
    target = raw_path.rstrip("/")
    want_dir = raw_path.endswith("/")
    matches: List[str] = []
    for p in _build_suffix_index():
        is_dir = p.endswith("/")
        if want_dir != is_dir:
            continue
        if p.rstrip("/").endswith(os.sep + target):
            matches.append(p)
    return matches


def count_lines(path: str) -> int:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def count_h2_headings(path: str) -> int:
    count = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if HEADING2_RE.match(line):
                count += 1
    return count


# --------------------------------------------------------------------------
# Per-file checks: R1, R2, R3
# --------------------------------------------------------------------------

def check_file_refs(filepath_abs: str, allow_patterns: List[str]) -> List[Finding]:
    findings: List[Finding] = []
    rel_file = os.path.relpath(filepath_abs, REPO_ROOT)
    try:
        with open(filepath_abs, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        return [Finding("ERROR", rel_file, 1, "read-failure", rel_file, "could not read file: %s" % e)]

    stripped = strip_fenced_blocks(text)
    lines = stripped.split("\n")

    for lineno, line in enumerate(lines, start=1):
        # --- R3 form (a): `path` §N  (path in backticks, §N outside) ---
        for m in SECTION_REF_OUTSIDE_RE.finditer(line):
            path_raw, num_s = m.group(1), m.group(2)
            _check_section_ref(path_raw, int(num_s), filepath_abs, rel_file, lineno, findings)

        # --- backtick tokens on this line: R2, R3-form-b, then R1 ---
        for bt in BACKTICK_RE.finditer(line):
            tok = bt.group(1)

            # R3 form (b): `path §N` — both inside one backtick pair.
            m2 = SECTION_REF_INSIDE_RE.match(tok)
            if m2 and ("." in m2.group(1) or "/" in m2.group(1)):
                _check_section_ref(m2.group(1), int(m2.group(2)), filepath_abs, rel_file, lineno, findings)
                continue

            # R2: `path:line` or `path:start-end`
            parsed = parse_path_line_token(tok)
            if parsed is not None:
                path_part, start, end = parsed
                if is_placeholder_or_external(path_part):
                    continue
                if is_allowlisted(path_part, allow_patterns):
                    continue
                resolved = resolve_ref(path_part, filepath_abs)
                if resolved is None:
                    suffix_matches = resolve_unique_suffix(path_part)
                    if len(suffix_matches) == 1:
                        resolved = suffix_matches[0]
                    elif len(suffix_matches) > 1:
                        findings.append(
                            Finding(
                                "WARN", rel_file, lineno, "R2", tok,
                                "shorthand ambiguous (%d candidates)" % len(suffix_matches),
                            )
                        )
                        continue
                if resolved is None:
                    findings.append(Finding("ERROR", rel_file, lineno, "R2", tok, "referenced file does not exist"))
                else:
                    max_line = end if end is not None else start
                    target_lines = count_lines(resolved)
                    if max_line > target_lines:
                        findings.append(
                            Finding(
                                "WARN",
                                rel_file,
                                lineno,
                                "R2",
                                tok,
                                "line %d exceeds target's %d lines (drift)" % (max_line, target_lines),
                            )
                        )
                continue

            # R1: bare backtick-quoted repo-relative path.
            if "/" not in tok or re.search(r"\s", tok):
                continue
            if is_placeholder_or_external(tok):
                continue
            if not looks_like_repo_path(tok):
                continue
            if is_allowlisted(tok, allow_patterns):
                continue
            resolved = resolve_ref(tok, filepath_abs)
            if resolved is None:
                suffix_matches = resolve_unique_suffix(tok)
                if len(suffix_matches) == 1:
                    continue  # unambiguous shorthand, reference is real
                if len(suffix_matches) > 1:
                    findings.append(
                        Finding(
                            "WARN", rel_file, lineno, "R1", tok,
                            "shorthand ambiguous (%d candidates)" % len(suffix_matches),
                        )
                    )
                    continue
                findings.append(Finding("ERROR", rel_file, lineno, "R1", tok, "referenced path does not exist"))

    return findings


def _check_section_ref(
    path_raw: str,
    num: int,
    filepath_abs: str,
    rel_file: str,
    lineno: int,
    findings: List[Finding],
) -> None:
    if is_placeholder_or_external(path_raw):
        return
    resolved = resolve_ref(path_raw, filepath_abs)
    ref_text = "%s §%d" % (path_raw, num)
    if resolved is None or not os.path.isfile(resolved):
        suffix_matches = [m for m in resolve_unique_suffix(path_raw) if os.path.isfile(m)]
        if len(suffix_matches) == 1:
            resolved = suffix_matches[0]
        else:
            findings.append(Finding("WARN", rel_file, lineno, "R3", ref_text, "section-ref target file not found"))
            return
    h2_count = count_h2_headings(resolved)
    if h2_count < num:
        findings.append(
            Finding(
                "WARN",
                rel_file,
                lineno,
                "R3",
                ref_text,
                "target has %d '## ' heading(s), need >= %d" % (h2_count, num),
            )
        )


# --------------------------------------------------------------------------
# R4: zh-mirror pairing
# --------------------------------------------------------------------------

def check_mirrors(all_files_abs: List[str]) -> List[Finding]:
    findings: List[Finding] = []
    for fp in all_files_abs:
        rel = os.path.relpath(fp, REPO_ROOT)
        dirname = os.path.dirname(rel)
        base = os.path.basename(rel)
        if base.endswith("_zh.md"):
            continue
        if dirname in MIRROR_SIBLING_DIRS:
            zh_name = base[:-3] + "_zh.md"
            zh_rel = os.path.join(dirname, zh_name) if dirname else zh_name
            if not os.path.isfile(os.path.join(REPO_ROOT, zh_rel)):
                findings.append(Finding("WARN", rel, 1, "R4", rel, "missing zh mirror %s" % zh_rel))
        elif dirname in MIRROR_AGENTDOCS_DIRS:
            subdir = MIRROR_AGENTDOCS_DIRS[dirname]
            zh_rel = os.path.join("agent_docs", "zh", subdir, base)
            if not os.path.isfile(os.path.join(REPO_ROOT, zh_rel)):
                findings.append(Finding("WARN", rel, 1, "R4", rel, "missing zh mirror %s" % zh_rel))
    return findings


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def run(files_abs: List[str], allow_patterns: List[str], apply_r4: bool) -> List[Finding]:
    findings: List[Finding] = []
    for fp in files_abs:
        findings.extend(check_file_refs(fp, allow_patterns))
    if apply_r4:
        findings.extend(check_mirrors(files_abs))
    return findings


def summarize(findings: List[Finding]) -> Dict[str, int]:
    counts: Dict[str, int] = {"ERROR": 0, "WARN": 0}
    per_check: Dict[str, int] = {}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
        per_check[f.check_id] = per_check.get(f.check_id, 0) + 1
    counts.update(per_check)
    return counts


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check doc/path references cited in this repo's markdown canon.")
    parser.add_argument("--file", help="check a single markdown file")
    parser.add_argument("--all", action="store_true", help="scan CLAUDE.md, CLAUDE_zh.md, .claude/**/*.md, docs/**/*.md, agent_docs/**/*.md (default)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON output")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any ERROR-level finding exists")
    args = parser.parse_args(argv)

    allow_patterns = load_allowlist()

    if args.file:
        files_abs = [os.path.abspath(args.file)]
        apply_r4 = False
    else:
        files_abs = discover_all_files()
        apply_r4 = True

    findings = run(files_abs, allow_patterns, apply_r4)
    counts = summarize(findings)

    if args.json:
        print(json.dumps({"findings": [f.to_dict() for f in findings], "summary": counts}, indent=2))
    else:
        for f in findings:
            print(f.to_line())
        print(
            "SUMMARY: %d ERROR, %d WARN (R1=%d R2=%d R3=%d R4=%d) across %d file(s)"
            % (
                counts.get("ERROR", 0),
                counts.get("WARN", 0),
                counts.get("R1", 0),
                counts.get("R2", 0),
                counts.get("R3", 0),
                counts.get("R4", 0),
                len(files_abs),
            )
        )

    if args.strict and counts.get("ERROR", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
