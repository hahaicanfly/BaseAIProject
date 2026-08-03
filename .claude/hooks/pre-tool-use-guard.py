#!/usr/bin/env python3
"""PreToolUse guard — enforces hard invariants by blocking tool calls.

Per ADR-0001 D5 this is the ONLY hook that runs in enforce mode in
Phase D. It blocks (exit 2) the small set of operations that are
unambiguously dangerous on this repo, with no expected false positives:

  INV-GIT-002  git commit on master/main
  INV-GIT-003  git push --force on master/main
  INV-GIT-004  git reset --hard origin/(master|main)
  -            cat/less/head/tail of .env or secrets files
  -            curl|sh, wget|sh
  -            rm -rf /, rm -rf ~, sudo rm

One ADVISORY (allow + additionalContext injection, never blocks):
  INV-GIT-005  git checkout -b/-B, git switch -c/-C → remind the model to
               run scripts/verify-branch-base.py after the cut. Spike-
               verified (F-004): additionalContext is the ONLY exit-0
               channel that reaches the model context.

Designed to be FAST: pure regex + at most one `git branch --show-current`
subprocess (cached via current_branch helper, 2s timeout).

Exit codes:
  0  — pass through, no issue
  2  — BLOCK the tool call; stderr message returned to Agent
       (Claude Code hook protocol: exit 2 = blocking error;
        exit 1 = non-blocking, the tool call would STILL RUN)
"""
from __future__ import annotations

import json
import re
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _lib import (  # noqa: E402
    current_branch,
    is_sentinel_mode,
    log_event,
    read_stdin_json,
)

HOOK_NAME = "pre-tool-use-guard"

# Verbs that read file content. Word boundary is applied at the verb level.
# `source` and `.` (dot) are env-loading variants — note the dot variant
# must be matched as a standalone token (we do this by requiring its leading
# context separately in _DOT_SOURCE_LEAD).
_READ_VERBS_RE = (
    r"(?:cat|less|more|head|tail|grep|egrep|fgrep|zgrep|"
    r"awk|gawk|sed|gsed|xxd|od|hexdump|strings|tee|cp|mv|rsync|"
    r"python\d*|ruby|perl|node|deno|"
    r"source)"
)
# Standalone "." as a shell builtin (POSIX dot-source). Must be a token,
# i.e. preceded by start/space/`;` and followed by space.
_DOT_SOURCE = r"(?:^|[\s;&|`])\.\s+"

# Filename patterns for sensitive files. The leading "/" is optional so both
# "cat ./.env" and "cat /etc/.env" hit. .env.local / .env.production are
# caught by the optional dotted suffix.
_SECRET_FILES = [
    (r"\.env(?:\.[A-Za-z0-9_-]+)?", "READ_DOTENV", ".env (含密鑰)"),
    (r"local\.properties", "READ_LOCAL_PROPERTIES", "local.properties"),
    (r"local-prod\.properties", "READ_LOCAL_PROD", "local-prod.properties (prod secrets)"),
    (r"[\w.-]*\.keystore", "READ_KEYSTORE", "*.keystore (signing key)"),
    (r"[\w.-]*\.jks", "READ_JKS", "*.jks (Java KeyStore)"),
    (r"[\w.-]*\.pem", "READ_PEM", "*.pem (private key/cert)"),
    (r"[\w.-]*\.p12", "READ_P12", "*.p12 (PKCS#12 bundle)"),
    (r"google-services\.json", "READ_GSERVICES", "google-services.json (含 API key)"),
    (r"serviceAccountKey\.json", "READ_GCP_SA", "GCP service-account key"),
    (r"[\w.-]*[Ss]ecret[\w.-]*", "READ_SECRET_FILE", "*secret* file"),
    (r"[\w.-]*[Cc]redential[\w.-]*", "READ_CREDENTIAL_FILE", "*credential* file"),
]

# Filename appears after a path-safe leading char (start-of-string, whitespace,
# `<`, `=`, `(`, `;`, quotes, etc.). Quotes are included so `python -c
# 'open(".env")'` is detected.
_FILE_LEAD = r"(?:^|[\s<>|;&=`(\"'])"
_PATH_PREFIX = r"(?:[\w./-]*?/)?"
# Trailing position: end of string or any shell metachar / whitespace.
_FILE_TRAIL = r"(?=[\s<>|;&)\"'`,]|$)"


def _build_secret_deny_patterns() -> list[tuple[re.Pattern, str, str]]:
    """Synthesize secret-read deny patterns covering many shell verbs.

    Four families per file:
    1. `<verb> ... <file>` — explicit read commands.
    2. `<file>` after `<` redirect — stdin redirect (any consumer).
    3. `. <file>` / `source <file>` env-loading.
    4. `git add ... <file>` — staging a secret file (INV-SEC-003).

    Word-boundary issues: `.env` starts with non-word `.` so we cannot use
    `\\b` before the dot; we anchor on shell metachars via _FILE_LEAD.

    Family 4 design note: we cannot practically shell out to `git diff
    --cached --name-only` here — the hook must stay a pure, fast regex pass
    (no subprocess budget beyond the one cached `git branch --show-current`
    call), and PreToolUse only ever sees the literal command string, not the
    resulting index state. So we match on the command text itself
    (`git add ... <secret-file>`); this only catches secrets named on the
    command line, not e.g. `git add -A` sweeping one in incidentally. That
    residual gap is accepted and covered by code-reviewer + human review
    before merge, per INV-SEC-003's HOOK note in invariants.md.
    """
    patterns: list[tuple[re.Pattern, str, str]] = []
    for fpat, code, desc in _SECRET_FILES:
        rx_verb = re.compile(
            rf"\b{_READ_VERBS_RE}\b[^|;&\n]*?{_FILE_LEAD}{_PATH_PREFIX}{fpat}{_FILE_TRAIL}"
        )
        rx_dot = re.compile(
            rf"{_DOT_SOURCE}{_PATH_PREFIX}{fpat}{_FILE_TRAIL}"
        )
        rx_redir = re.compile(
            rf"<\s*{_PATH_PREFIX}{fpat}{_FILE_TRAIL}"
        )
        rx_gitadd = re.compile(
            rf"\bgit\s+(?:[^|;&\n]+\s+)?add\b[^|;&\n]*?{_FILE_LEAD}{_PATH_PREFIX}{fpat}{_FILE_TRAIL}"
        )
        patterns.append((rx_verb, code, f"禁止讀取 {desc}"))
        patterns.append((rx_dot, f"{code}_DOT", f"禁止以 . (dot-source) 載入 {desc}"))
        patterns.append((rx_redir, f"{code}_REDIR", f"禁止以 stdin 重導向讀取 {desc}"))
        patterns.append((rx_gitadd, f"{code}_GITADD", f"禁止 git add {desc}（INV-SEC-003）"))
    return patterns


# Static deny patterns: (regex, code, human reason)
STATIC_DENIES: list[tuple[re.Pattern, str, str]] = _build_secret_deny_patterns() + [
    # --- Git push / reset / refspec ---
    (
        re.compile(r"\bgit\s+push\b[^|;&]*--force(?:-with-lease)?\b[^|;&]*\b(master|main)\b"),
        "INV-GIT-003",
        "禁止對 master/main force-push（含 --force-with-lease）",
    ),
    (
        re.compile(r"\bgit\s+push\b[^|;&]*\s-f\b[^|;&]*\b(master|main)\b"),
        "INV-GIT-003",
        "禁止對 master/main force-push (-f)",
    ),
    (
        re.compile(r"\bgit\s+push\b[^|;&]*\s\+[A-Za-z0-9_./:-]*?\b(master|main)\b"),
        "INV-GIT-003",
        "禁止對 master/main 用 +refspec 強制更新（等同 --force）",
    ),
    (
        re.compile(r"\bgit\s+reset\s+--hard\s+origin/(master|main)\b"),
        "INV-GIT-004",
        "禁止 git reset --hard origin/master|main；改用 git rebase origin/master",
    ),
    # --- Remote shell execution ---
    (
        re.compile(r"\b(?:curl|wget|fetch)\b[^|]*\|\s*(?:/bin/)?(?:sh|bash|zsh|ksh|fish)\b"),
        "REMOTE_PIPE_SHELL",
        "禁止 curl|wget … | sh（unverified remote execution）",
    ),
    (
        re.compile(r"\b(?:curl|wget|fetch)\b[^|]*\|\s*\$SHELL\b"),
        "REMOTE_PIPE_SHELL",
        "禁止 curl|wget … | $SHELL",
    ),
    (
        re.compile(r"\b(?:eval|sh|bash|zsh|ksh|python\d?|node|ruby|perl)\s+-c\s+[\"']?\$\(\s*(?:curl|wget|fetch)\b"),
        "REMOTE_CMD_SUBST",
        "禁止 eval/sh -c \"$(curl …)\"（command substitution + remote fetch）",
    ),
    (
        re.compile(r"\beval\s+[\"']?\$\(\s*(?:curl|wget|fetch)\b"),
        "REMOTE_EVAL",
        "禁止 eval $(curl …)",
    ),
    (
        re.compile(r"\b(?:sh|bash|zsh|ksh|source|\.\s)\s+<\(\s*(?:curl|wget|fetch)\b"),
        "REMOTE_PROC_SUBST",
        "禁止 bash <(curl …)（process substitution + remote fetch）",
    ),
    # --- Destructive ---
    (
        re.compile(r"\brm\s+-rf\s+/(\s|$)"),
        "RM_RF_ROOT",
        "禁止 rm -rf /",
    ),
    (
        re.compile(r"\brm\s+-rf\s+~(/|\s|$)"),
        "RM_RF_HOME",
        "禁止 rm -rf ~",
    ),
    (
        re.compile(r"\bsudo\s+rm\b"),
        "SUDO_RM",
        "禁止 sudo rm",
    ),
]


# --- Heredoc bodies: data, not commands -------------------------------------
#
# A heredoc that writes a file carries DATA. Scanning it for command patterns
# means this guard blocks documentation that merely *describes* what it blocks
# — which is exactly what happened when the README's hook table, whose job is
# to name the things this guard stops, was itself stopped (ERRORS.md
# 2026-07-29, fourth occurrence of "the scanner does not exempt quoted
# content"). Prose about `curl | sh` is not `curl | sh`.
#
# This is a false-positive fix, not a hole. Writing text to a file was never
# blocked by this guard — the same bytes go through the Write tool, which this
# hook never even sees (it only inspects tool_name == "Bash"). What must never
# be exempted is a heredoc feeding an INTERPRETER, where the body really is
# code about to run.
#
# Per security.md ("use allowlists rather than denylists") the exemption is an
# allowlist of data sinks, not a blocklist of interpreters: an unknown command
# gets its body scanned. Extending it is a deliberate act, and the negative
# tests in the §4 smoke test must be extended with it.
_HEREDOC_RE = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")

_DATA_SINKS = (
    # cat/tee writing to a file — the body lands on disk, nothing executes it
    re.compile(r"^\s*cat\s*>>?\s*[^|<>\s]+\s*$"),
    re.compile(r"^\s*tee\s+(?:-a\s+)?[^|<>\s]+\s*$"),
    # message bodies read from stdin by a non-interpreter
    re.compile(r"^\s*git\s+(?:commit|tag)\b.*?(?:-F|--file)\s+-\s*$"),
    re.compile(r"^\s*gh\s+\S+.*?--body-file\s+-\s*$"),
)

_SEGMENT_SPLIT_RE = re.compile(r"\|\||&&|[;&]")


def _is_data_sink(header_line: str, marker: re.Match) -> bool:
    """Does this heredoc's body land somewhere inert?

    Conservative on every unclear case: a pipe anywhere on the header line
    means the body could still reach an interpreter, more than one heredoc
    marker on a line means we cannot tell which owns what, and any command
    outside the allowlist is treated as capable of executing its input.
    """
    without_marker = header_line[:marker.start()] + header_line[marker.end():]
    if "|" in without_marker:
        return False
    if len(_HEREDOC_RE.findall(header_line)) != 1:
        return False
    owning = _SEGMENT_SPLIT_RE.split(header_line[:marker.start()])[-1]
    return any(sink.match(owning) for sink in _DATA_SINKS)


def scannable_text(command: str) -> str:
    """The part of a Bash command that is actually a command.

    Bodies of heredocs feeding an allowlisted data sink are blanked out.
    Header lines and terminators stay, so `cat > .env <<EOF` is still caught
    by the secret-file rules, and anything after the heredoc is still scanned.
    """
    if "<<" not in command:
        return command

    lines = command.split("\n")
    out = list(lines)
    i = 0
    while i < len(lines):
        marker = _HEREDOC_RE.search(lines[i])
        if not marker:
            i += 1
            continue
        dash, _, delim = marker.groups()
        exempt = _is_data_sink(lines[i], marker)

        end = None
        for j in range(i + 1, len(lines)):
            candidate = lines[j].lstrip("\t") if dash else lines[j]
            if candidate.strip() == delim:
                end = j
                break
        if end is None:
            # Unterminated: we cannot tell where the body stops, so scan it all.
            return command
        if exempt:
            for j in range(i + 1, end):
                out[j] = ""
        i = end + 1

    return "\n".join(out)


def is_protected_branch(branch: str) -> bool:
    return branch in ("master", "main")


_GIT_COMMIT_RE = re.compile(
    r"\bgit\s+(?:[^\s|;&]+\s+)*?commit(\s|$)"
)
_GIT_C_PATH_RE = re.compile(r"\bgit\s+(?:.*?\s+)?-C\s+(\S+)")
# New-branch cuts: checkout -b/-B and switch -c/-C (INV-GIT-005 advisory).
_GIT_BRANCH_CUT_RE = re.compile(
    r"\bgit\s+(?:checkout\s+(?:\S+\s+)*-[bB]|switch\s+(?:\S+\s+)*-[cC])\s"
)


def check_git_commit_on_master(command: str) -> tuple[str, str] | None:
    """Block `git commit` when the target repo's current branch is master/main."""
    if not _GIT_COMMIT_RE.search(command):
        return None
    target_path = None
    m = _GIT_C_PATH_RE.search(command)
    if m:
        target_path = m.group(1)
    branch = current_branch(cwd=target_path) if target_path else current_branch()
    if branch and is_protected_branch(branch):
        location = f" (target: {target_path})" if target_path else ""
        return (
            "INV-GIT-002",
            f"禁止在 {branch} branch 直接 commit{location}。請先 `git checkout -b feat/<slug>`",
        )
    return None


def main() -> int:
    payload = read_stdin_json()
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    command = tool_input.get("command", "") if tool == "Bash" else ""

    # Sentinel mode: log only, never block
    if is_sentinel_mode(HOOK_NAME):
        if tool == "Bash" and command:
            log_event(HOOK_NAME, "sentinel", tool=tool, command_preview=command[:120])
        else:
            log_event(HOOK_NAME, "sentinel", tool=tool)
        return 0

    if tool != "Bash" or not command:
        log_event(HOOK_NAME, "pass", tool=tool)
        return 0

    # Heredoc bodies bound for a data sink are content, not commands.
    scannable = scannable_text(command)

    # 1) static patterns
    for pat, code, reason in STATIC_DENIES:
        if pat.search(scannable):
            log_event(
                HOOK_NAME,
                "enforced_block",
                reason=code,
                command_preview=command[:120],
            )
            sys.stderr.write(
                f"[harness/{HOOK_NAME}] BLOCKED ({code}): {reason}\n"
                f"Command preview: {command[:200]}\n"
                f"See docs/architecture/invariants.md for details.\n"
            )
            return 2

    # 2) dynamic: git commit on master/main
    hit = check_git_commit_on_master(scannable)
    if hit:
        code, reason = hit
        log_event(
            HOOK_NAME,
            "enforced_block",
            reason=code,
            command_preview=command[:120],
        )
        sys.stderr.write(
            f"[harness/{HOOK_NAME}] BLOCKED ({code}): {reason}\n"
            f"Command preview: {command[:200]}\n"
        )
        return 2

    # 3) advisory (allow + context injection, never blocks): cutting a new
    # branch → remind the model to verify the base (INV-GIT-005). The
    # half-failed `git checkout master && git checkout -b X` compound cut a
    # branch from the wrong base with zero error output (2026-07-29).
    # F-004 spike result: of the exit-0 channels, ONLY hookSpecificOutput
    # .additionalContext reaches the model context (plain stdout/stderr and
    # permissionDecisionReason do not) — so this must stay JSON-shaped.
    if _GIT_BRANCH_CUT_RE.search(scannable):
        log_event(
            HOOK_NAME,
            "sentinel",
            reason="branch-cut-verify-advice",
            command_preview=command[:120],
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "additionalContext": (
                    "New branch being cut — after it completes, verify the "
                    "base is master (INV-GIT-005): run `python3 "
                    "scripts/verify-branch-base.py` and check it prints "
                    "PASS. A failed `git checkout master` earlier in a "
                    "compound command does NOT stop the `-b` from running "
                    "off the wrong base."
                ),
            }
        }))
        return 0

    log_event(HOOK_NAME, "pass", tool=tool, command_preview=command[:80])
    return 0


if __name__ == "__main__":
    sys.exit(main())
