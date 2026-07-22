#!/usr/bin/env python3
"""Execute an ExecPlan's §5 ```acceptance fenced block and log evidence.

Why: ExecPlan §5 (Verification Strategy) verification commands are prose
today -- nothing executes them or stores evidence that they were run. This
script turns a ```acceptance fenced code block into an executable,
evidence-logging gate (ExecPlan F-001 step C2a). The block format itself is
specified in docs/plans/PLANS.md §5 (defined separately from this script).

Block format (first ```acceptance fenced block in the file):
    ```acceptance
    <label>: <command>
    <label>: <command> expect-fail
    ```
- `label` matches [A-Za-z0-9_-]+
- Blank lines and lines starting with `#` are ignored
- A trailing ` expect-fail` marker means the command must exit non-zero to
  PASS (instead of the default: must exit 0 to PASS)
- A command line still containing a `{{` or `[your ` placeholder (i.e. an
  un-activated template) is SKIPped instead of run

Usage:
    python3 scripts/acceptance-run.py [execplan.md] [--json] [--timeout N]

If execplan.md is omitted, the newest F-*.md file (by mtime) in
docs/plans/active/ is used.

Exit codes:
    0 - ran, no FAIL results (SKIPs do not count as failures)
    1 - ran, at least one FAIL result
    2 - the target file has no ```acceptance fenced block

Evidence: one JSON line per command is appended to
state/acceptance/<plan-stem>.jsonl (directory created if missing). Set the
HARNESS_STATE_DIR env var to redirect the state/ root elsewhere (used by
this script's own sandbox tests so real repo state is never touched).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

# scripts/acceptance-run.py -> repo root is the parent of scripts/
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

FENCE_OPEN_RE = re.compile(r"^\s*```acceptance\b")
FENCE_CLOSE_RE = re.compile(r"^\s*```\s*$")
LABEL_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
EXPECT_FAIL_SUFFIX = " expect-fail"
PLACEHOLDER_MARKERS = ("{{", "[your ")


def now_iso() -> str:
    """Current UTC time as ISO 8601 with a Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_default_plan(active_dir: Path) -> Optional[Path]:
    """Newest (by mtime) F-*.md file in docs/plans/active/, or None."""
    if not active_dir.is_dir():
        return None
    candidates = [p for p in active_dir.glob("F-*.md") if p.is_file()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def resolve_plan_path(arg_plan: Optional[str]) -> Optional[Path]:
    if arg_plan:
        p = Path(arg_plan)
        if not p.is_absolute():
            p = (REPO_ROOT / p).resolve()
        return p
    return find_default_plan(REPO_ROOT / "docs" / "plans" / "active")


def extract_acceptance_block(text: str) -> Optional[str]:
    """Return the body text of the FIRST ```acceptance fenced block, or None."""
    lines = text.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if FENCE_OPEN_RE.match(line):
            start_idx = i + 1
            break
    if start_idx is None:
        return None
    end_idx = len(lines)
    for j in range(start_idx, len(lines)):
        if FENCE_CLOSE_RE.match(lines[j]):
            end_idx = j
            break
    return "\n".join(lines[start_idx:end_idx])


def parse_commands(block: str) -> List[Tuple[str, str, bool]]:
    """Parse block text into a list of (label, cmd, expect_fail) tuples."""
    results: List[Tuple[str, str, bool]] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = LABEL_RE.match(line)
        if not m:
            # Malformed line (no `label: command` shape) -- ignore rather
            # than crash the whole run.
            continue
        label, rest = m.group(1), m.group(2).strip()
        expect_fail = False
        if rest.endswith(EXPECT_FAIL_SUFFIX):
            expect_fail = True
            rest = rest[: -len(EXPECT_FAIL_SUFFIX)].rstrip()
        results.append((label, rest, expect_fail))
    return results


def is_placeholder(cmd: str) -> bool:
    return any(marker in cmd for marker in PLACEHOLDER_MARKERS)


def tail_lines(text: str, n: int) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-n:])


def run_command(cmd: str, timeout: int) -> Tuple[Optional[int], str]:
    """Run `cmd` in a shell at REPO_ROOT. Never raises.

    Returns (exit_code, output_tail). exit_code is None if the command
    could not be run to completion (timeout or exception) -- the error is
    folded into output_tail instead.
    """
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True,
        )
        return proc.returncode, tail_lines(proc.stdout or "", 10)
    except subprocess.TimeoutExpired as exc:
        partial = exc.output
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", "replace")
        partial = partial or ""
        note = "TIMEOUT after {}s".format(timeout)
        combined = tail_lines(partial, 10)
        combined = (combined + "\n" + note).strip() if combined else note
        return None, combined
    except Exception as exc:  # noqa: BLE001 - a single command must never kill the run
        return None, "EXCEPTION: {}".format(exc)


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


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute an ExecPlan's ```acceptance fenced block and log evidence."
    )
    parser.add_argument(
        "plan",
        nargs="?",
        default=None,
        help="Path to an ExecPlan markdown file (default: newest F-*.md in docs/plans/active/)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable results as a JSON array"
    )
    parser.add_argument(
        "--timeout", type=int, default=600, help="Per-command timeout in seconds (default: 600)"
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    plan_path = resolve_plan_path(args.plan)
    if plan_path is None or not plan_path.is_file():
        msg = "No ExecPlan file found (looked for newest F-*.md in docs/plans/active/, or none given)."
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(msg, file=sys.stderr)
        return 2

    text = plan_path.read_text(encoding="utf-8", errors="replace")
    block = extract_acceptance_block(text)
    if block is None:
        hint = (
            "No ```acceptance fenced block found in {}. "
            "See docs/plans/PLANS.md §5 (Verification Strategy) for the block format."
        ).format(repo_relative(plan_path))
        if args.json:
            print(json.dumps({"error": hint}))
        else:
            print(hint, file=sys.stderr)
        return 2

    commands = parse_commands(block)

    state_dir = get_state_dir()
    acceptance_dir = state_dir / "acceptance"
    acceptance_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = acceptance_dir / "{}.jsonl".format(plan_path.stem)

    plan_repo_rel = repo_relative(plan_path)
    results = []
    any_fail = False

    with jsonl_path.open("a", encoding="utf-8") as jf:
        for label, cmd, expect_fail in commands:
            record = {
                "ts": now_iso(),
                "plan": plan_repo_rel,
                "label": label,
                "cmd": cmd,
                "expect_fail": expect_fail,
            }
            try:
                if is_placeholder(cmd):
                    record["exit_code"] = None
                    record["pass"] = True
                    record["skipped"] = True
                    record["output_tail"] = ""
                    status = "SKIP"
                else:
                    exit_code, output_tail = run_command(cmd, args.timeout)
                    if exit_code is None:
                        passed = False
                    elif expect_fail:
                        passed = exit_code != 0
                    else:
                        passed = exit_code == 0
                    record["exit_code"] = exit_code
                    record["pass"] = passed
                    record["skipped"] = False
                    record["output_tail"] = output_tail
                    status = "PASS" if passed else "FAIL"
                    if not passed:
                        any_fail = True
            except Exception as exc:  # noqa: BLE001 - one command must never kill the run
                record["exit_code"] = None
                record["pass"] = False
                record["skipped"] = False
                record["output_tail"] = "EXCEPTION: {}".format(exc)
                status = "FAIL"
                any_fail = True

            jf.write(json.dumps(record) + "\n")
            jf.flush()
            record["status"] = status
            results.append(record)

            if not args.json:
                print("{} {}: {}".format(status, label, cmd))

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        total = len(results)
        n_pass = sum(1 for r in results if r["status"] == "PASS")
        n_fail = sum(1 for r in results if r["status"] == "FAIL")
        n_skip = sum(1 for r in results if r["status"] == "SKIP")
        print(
            "Summary: {} total, {} pass, {} fail, {} skip".format(total, n_pass, n_fail, n_skip)
        )

    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
