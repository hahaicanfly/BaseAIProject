#!/usr/bin/env python3
"""Measure the always-on context footprint of a model tier against a budget.

Why: `.claude/rules/*.md` with `always: true` plus CLAUDE.md are injected into
EVERY session, so every line added there taxes all future work. Before F-003
that surface was 627 lines / 34,786 chars with no mechanical ceiling — the
budget existed only as prose in LETTER-TO-FUTURE-SESSIONS.md §I.3, which
nothing enforced. This script turns that prose into an executable gate.

Thresholds are NOT hardcoded here. They come from `.claude/tiers/budget.json`
so a human can retune them from real usage without editing code or the
ExecPlan acceptance block (F-003 DEC-5).

Exit codes: 0 = within budget, 1 = over budget, 2 = usage/config error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TIERS_DIR = REPO_ROOT / ".claude" / "tiers"
BUDGET_FILE = TIERS_DIR / "budget.json"
MODEL_MAP_FILE = TIERS_DIR / "model-map.json"
RULES_DIR = REPO_ROOT / ".claude" / "rules"

TIERS = ("strong", "mid", "light")

# `always: true` in a rule file's YAML frontmatter is what makes it standing.
_ALWAYS_RE = re.compile(r"^always:\s*true\s*$", re.M)


class ConfigError(Exception):
    """Raised for a malformed or missing budget config."""


def load_budget() -> dict:
    if not BUDGET_FILE.exists():
        raise ConfigError(f"missing config: {BUDGET_FILE.relative_to(REPO_ROOT)}")
    try:
        cfg = json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{BUDGET_FILE.name} is not valid JSON: {exc}") from exc

    modes = cfg.get("modes")
    if not isinstance(modes, dict) or not modes:
        raise ConfigError("config has no non-empty 'modes' object")

    active = cfg.get("active_mode")
    if active not in modes:
        raise ConfigError(
            f"active_mode {active!r} is not one of: {', '.join(sorted(modes))}"
        )

    for mode_name, tiers in modes.items():
        for tier in TIERS:
            limits = tiers.get(tier)
            if not isinstance(limits, dict):
                raise ConfigError(f"mode {mode_name!r} is missing tier {tier!r}")
            for key in ("max_lines", "max_chars"):
                if key not in limits:
                    raise ConfigError(f"mode {mode_name!r} tier {tier!r} lacks {key}")
                val = limits[key]
                if val is not None and (not isinstance(val, int) or val <= 0):
                    raise ConfigError(
                        f"mode {mode_name!r} tier {tier!r} {key} must be a "
                        f"positive int or null, got {val!r}"
                    )
    return cfg


def standing_rule_files() -> list[Path]:
    """Rule files that are auto-injected every session (frontmatter always: true)."""
    if not RULES_DIR.is_dir():
        return []
    out = []
    for path in sorted(RULES_DIR.glob("*.md")):
        if _ALWAYS_RE.search(path.read_text(encoding="utf-8")):
            out.append(path)
    return out


def tier_surface(tier: str) -> list[Path]:
    """Files injected into context for `tier`.

    Core (all tiers) = CLAUDE.md + standing rules. Tier pack = the per-tier
    file added by the SessionStart / SubagentStart hooks. Before F-003 Phase 2
    no tier packs exist yet, so every tier resolves to the full current
    surface — which is exactly why strong/mid FAIL at that point.
    """
    surface = [REPO_ROOT / "CLAUDE.md", *standing_rule_files()]
    pack = TIERS_DIR / f"{tier}.md"
    if pack.exists():
        surface.append(pack)
    return [p for p in surface if p.exists()]


def measure(paths: list[Path]) -> tuple[int, int, list[tuple[str, int, int]]]:
    per_file = []
    total_lines = total_chars = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        lines = len(text.splitlines())
        chars = len(text)
        per_file.append((str(path.relative_to(REPO_ROOT)), lines, chars))
        total_lines += lines
        total_chars += chars
    per_file.sort(key=lambda row: row[2], reverse=True)
    return total_lines, total_chars, per_file


def cmd_measure(args: argparse.Namespace, cfg: dict) -> int:
    mode = args.mode or cfg["active_mode"]
    if mode not in cfg["modes"]:
        print(f"ERROR: unknown mode {mode!r}", file=sys.stderr)
        return 2
    limits = dict(cfg["modes"][mode][args.tier])
    if args.max_chars is not None:
        limits["max_chars"] = args.max_chars
    if args.max_lines is not None:
        limits["max_lines"] = args.max_lines

    paths = tier_surface(args.tier)
    if not paths:
        print(f"ERROR: tier {args.tier!r} resolves to no existing files", file=sys.stderr)
        return 2
    total_lines, total_chars, per_file = measure(paths)

    breaches = []
    for key, actual, unit in (
        ("max_lines", total_lines, "lines"),
        ("max_chars", total_chars, "chars"),
    ):
        cap = limits[key]
        if cap is not None and actual > cap:
            breaches.append(f"{unit} {actual} > {cap} (over by {actual - cap})")

    cap_l, cap_c = limits["max_lines"], limits["max_chars"]
    verdict = "OVER BUDGET" if breaches else "within budget"
    print(
        f"tier={args.tier} mode={mode} -> {total_lines} lines / {total_chars} chars "
        f"(cap: {cap_l if cap_l else 'none'} lines / {cap_c if cap_c else 'none'} chars) "
        f"[{verdict}]"
    )
    for name, lines, chars in per_file:
        share = (chars / total_chars * 100) if total_chars else 0
        print(f"  {chars:>7} chars  {lines:>4} lines  {share:5.1f}%  {name}")
    for breach in breaches:
        print(f"BREACH: {breach}", file=sys.stderr)
    return 1 if breaches else 0


def cmd_list_modes(cfg: dict) -> int:
    active = cfg["active_mode"]
    print(f"active_mode: {active}   (edit {BUDGET_FILE.relative_to(REPO_ROOT)} to switch)")
    for mode, tiers in cfg["modes"].items():
        marker = "*" if mode == active else " "
        note = tiers.get("_note", "")
        print(f"{marker} {mode}: {note}")
        for tier in TIERS:
            lim = tiers[tier]
            cap_l = lim["max_lines"] if lim["max_lines"] else "none"
            cap_c = lim["max_chars"] if lim["max_chars"] else "none"
            print(f"      {tier:<6} max_lines={cap_l:<6} max_chars={cap_c}")
    return 0


def cmd_self_test(cfg: dict) -> int:
    """Config integrity + surface resolution (+ tier mapping once Phase 1 lands)."""
    failures = []
    checks = 0

    checks += 1
    print(f"ok   config parses, active_mode={cfg['active_mode']!r}, "
          f"{len(cfg['modes'])} modes, all tiers present")

    for tier in TIERS:
        checks += 1
        paths = tier_surface(tier)
        if not paths:
            failures.append(f"tier {tier!r} resolves to no existing files")
            continue
        total_lines, total_chars, _ = measure(paths)
        print(f"ok   tier {tier:<6} surface = {len(paths)} files / "
              f"{total_lines} lines / {total_chars} chars")

    # model-map.json arrives in Phase 1; absence is reported, not failed.
    checks += 1
    if not MODEL_MAP_FILE.exists():
        print(f"skip model-map.json absent (F-003 Phase 1 not landed yet)")
    else:
        try:
            mapping = json.loads(MODEL_MAP_FILE.read_text(encoding="utf-8"))
            rules = mapping["rules"]
            fallback = mapping["fallback_tier"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            failures.append(f"model-map.json malformed: {exc}")
        else:
            if fallback != "light":
                failures.append(
                    f"fallback_tier must be 'light' (fail-safe, F-003 DEC-3), "
                    f"got {fallback!r}"
                )
            for tier in {r.get("tier") for r in rules}:
                if tier not in TIERS:
                    failures.append(f"model-map references unknown tier {tier!r}")
            print(f"ok   model-map.json valid, {len(rules)} rules, "
                  f"fallback={fallback}")

    for msg in failures:
        print(f"FAIL {msg}", file=sys.stderr)
    print(f"self-test: {checks} checks, {len(failures)} failed")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure always-on context footprint against the tier budget."
    )
    parser.add_argument("--tier", choices=TIERS, help="tier to measure")
    parser.add_argument("--mode", help="override active_mode for this run")
    parser.add_argument(
        "--max-chars", type=int, help="temporary override of the mode's max_chars"
    )
    parser.add_argument(
        "--max-lines", type=int, help="temporary override of the mode's max_lines"
    )
    parser.add_argument("--list-modes", action="store_true", help="show all modes")
    parser.add_argument(
        "--self-test", action="store_true", help="validate config and tier resolution"
    )
    args = parser.parse_args(argv)

    try:
        cfg = load_budget()
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.list_modes:
        return cmd_list_modes(cfg)
    if args.self_test:
        return cmd_self_test(cfg)
    if args.tier:
        return cmd_measure(args, cfg)

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
