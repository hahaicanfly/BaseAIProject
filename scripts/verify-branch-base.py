#!/usr/bin/env python3
"""Verify the current branch's base is master (INV-GIT-005).

Why this exists: `git checkout master && git checkout -b X` can half-fail —
the checkout of master fails (dirty tree) but the `-b` still runs, silently
cutting X from whatever branch you were on. The branch is created, nothing
errors, and no mechanism notices (observed live 2026-07-29, ERRORS.md).
Run this right after cutting a branch:

    python3 scripts/verify-branch-base.py

Verdicts (exit code):
  PASS (0) — every commit unique to this branch is genuinely its own;
             the branch is equivalent to one cut from master. A branch
             whose fork point is behind master's tip because master moved
             on afterwards still PASSes (that is normal aging, not a
             wrong base — refuting the naive `merge-base == master tip`
             check, which would flag every aged branch).
  FAIL (1) — commits between the fork point and this branch's HEAD also
             belong to another non-master branch: this branch is stacked
             on that branch, not cut from master.
  WARN (2) — could not decide (no master ref, detached HEAD, not a repo).

Honest limitation: this checks whether the branch's *current state* is
equivalent to a cut from master — it cannot recover which command created
it. A branch cut wrong and later rebased onto master PASSes, which is fine:
the tree is what INV-GIT-005 actually cares about.

--self-test builds throwaway repos covering the three canonical scenarios
(fresh cut → PASS, cut from a feature branch → FAIL, master advanced after
the cut → PASS) and exits non-zero if any scenario misbehaves.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

MAX_COMMITS_CHECKED = 50


def _git(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    try:
        p = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd,
        )
        return p.returncode, p.stdout.strip()
    except Exception:
        return 1, ""


def _resolve_base(cwd: str | None) -> str | None:
    for ref in ("origin/master", "master", "origin/main", "main"):
        code, _ = _git(["rev-parse", "--verify", "--quiet", ref], cwd)
        if code == 0:
            return ref
    return None


def verify(cwd: str | None = None, base: str | None = None,
           branch: str | None = None) -> tuple[str, list[str]]:
    """Return (verdict, detail_lines). Verdict: PASS | FAIL | WARN."""
    if branch is None:
        code, branch = _git(["branch", "--show-current"], cwd)
        if code != 0 or not branch:
            return "WARN", ["not a git repo, or detached HEAD — cannot judge"]

    if base is None:
        base = _resolve_base(cwd)
        if base is None:
            return "WARN", ["no master/main ref found — cannot judge"]

    base_short = base.split("/")[-1]
    if branch == base_short:
        return "PASS", [f"already on {branch} — nothing to verify"]

    code, fork = _git(["merge-base", branch, base], cwd)
    if code != 0 or not fork:
        return "WARN", [f"no merge-base between {branch} and {base}"]

    _, base_tip = _git(["rev-parse", base], cwd)
    _, behind = _git(["rev-list", "--count", f"{fork}..{base}"], cwd)
    _, ahead = _git(["rev-list", "--count", f"{fork}..{branch}"], cwd)
    detail = [
        f"branch={branch} base={base}",
        f"fork point {fork[:12]} — {ahead or '?'} commit(s) ahead, "
        f"{behind or '?'} behind {base}",
    ]

    # NOTE: fork == base_tip does NOT prove a fresh cut — a branch stacked
    # on another feature branch that was itself just cut from the tip has
    # the same fork point (self-test scenario 2 caught exactly this).
    # Ownership of the post-fork commits is the only reliable signal.
    code, own_raw = _git(["rev-list", f"{fork}..{branch}"], cwd)
    if code != 0:
        return "WARN", detail + ["rev-list failed — cannot judge"]
    own = own_raw.splitlines()
    if not own:
        if fork == base_tip:
            detail.append(f"HEAD IS the current {base} tip — fresh cut")
        else:
            detail.append(
                f"no commits after fork point — HEAD sits on old {base} "
                f"history"
            )
        return "PASS", detail

    ignore = {branch, base, base_short, f"origin/{branch}",
              f"origin/{base_short}", "origin/HEAD"}
    # Oldest commits sit at the bottom of the stack — if this branch was
    # cut from another feature branch, those are the foreign ones.
    for commit in list(reversed(own))[:MAX_COMMITS_CHECKED]:
        code, out = _git(
            ["branch", "--all", "--format=%(refname:short)",
             "--contains", commit], cwd)
        if code != 0:
            continue
        foreign = [b for b in out.splitlines()
                   if b and b not in ignore]
        if foreign:
            detail.append(
                f"commit {commit[:12]} also belongs to: {', '.join(foreign)}"
            )
            detail.append(
                f"→ this branch is stacked on {foreign[0]}, not cut from "
                f"{base} (INV-GIT-005). Fix: git rebase --onto {base} "
                f"{foreign[0]} {branch}  (or recut with git checkout -B "
                f"{branch} {base})"
            )
            return "FAIL", detail
    if fork == base_tip:
        detail.append(
            f"cut from the current {base} tip; every commit since is "
            f"exclusively this branch's own"
        )
    else:
        detail.append(
            f"{base} moved on after the cut, but every post-fork commit is "
            f"exclusively this branch's own — normal aged branch"
        )
    return "PASS", detail


# ---------------------------------------------------------------- self-test

def _sh(cwd: str, *cmds: list[str]) -> None:
    for c in cmds:
        subprocess.run(["git"] + c, cwd=cwd, capture_output=True,
                       text=True, check=True)


def self_test() -> int:
    failures = []
    tmp = tempfile.mkdtemp(prefix="verify-branch-base-selftest-")
    try:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        _sh(repo, ["init", "-q", "-b", "master"],
            ["config", "user.email", "t@t"], ["config", "user.name", "t"],
            ["commit", "--allow-empty", "-q", "-m", "root"])

        # Scenario 1: fresh cut from master → PASS
        _sh(repo, ["checkout", "-q", "-b", "feat/fresh", "master"])
        v, d = verify(cwd=repo, base="master")
        if v != "PASS":
            failures.append(f"scenario1 fresh-cut: want PASS got {v} ({d})")

        # Scenario 2: branch stacked on a feature branch → FAIL
        _sh(repo, ["checkout", "-q", "-b", "feat/parent", "master"],
            ["commit", "--allow-empty", "-q", "-m", "parent work"],
            ["checkout", "-q", "-b", "feat/stacked"],
            ["commit", "--allow-empty", "-q", "-m", "stacked work"])
        v, d = verify(cwd=repo, base="master")
        if v != "FAIL":
            failures.append(f"scenario2 stacked: want FAIL got {v} ({d})")

        # Scenario 3: correct cut, then master advances → PASS (no false alarm)
        _sh(repo, ["checkout", "-q", "-b", "feat/aged", "master"],
            ["commit", "--allow-empty", "-q", "-m", "aged work"],
            ["checkout", "-q", "master"],
            ["commit", "--allow-empty", "-q", "-m", "master moved on"],
            ["checkout", "-q", "feat/aged"])
        v, d = verify(cwd=repo, base="master")
        if v != "PASS":
            failures.append(f"scenario3 aged: want PASS got {v} ({d})")
    except subprocess.CalledProcessError as e:
        failures.append(f"self-test setup failed: {e}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        for f in failures:
            print(f"SELF-TEST FAIL: {f}")
        return 1
    print("SELF-TEST PASS: fresh-cut=PASS stacked=FAIL aged=PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify the current branch's base is master "
                    "(INV-GIT-005)")
    ap.add_argument("--base", help="base ref (default: origin/master → "
                                   "master → origin/main → main)")
    ap.add_argument("--branch", help="branch to check (default: current)")
    ap.add_argument("--self-test", action="store_true",
                    help="run built-in scenario tests in a throwaway repo")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    verdict, detail = verify(base=args.base, branch=args.branch)
    print(f"{verdict}: branch-base check (INV-GIT-005)")
    for line in detail:
        print(f"  {line}")
    return {"PASS": 0, "FAIL": 1, "WARN": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
