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

Designed to be FAST: pure regex + at most one `git branch --show-current`
subprocess (cached via current_branch helper, 2s timeout).

Exit codes:
  0  — pass through, no issue
  2  — BLOCK the tool call; stderr message returned to Agent
       (Claude Code hook protocol: exit 2 = blocking error;
        exit 1 = non-blocking, the tool call would STILL RUN)
"""
from __future__ import annotations

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
_READ_VERBS_RE = (
    r"(?:cat|less|more|head|tail|grep|egrep|fgrep|zgrep|"
    r"awk|gawk|sed|gsed|xxd|od|hexdump|strings|tee|cp|mv|rsync|"
    r"python\d*|ruby|perl|node|deno|"
    r"source)"
)
# Standalone "." as a shell builtin (POSIX dot-source).
_DOT_SOURCE = r"(?:^|[\s;&|`])\.\s+"

# Filename patterns for sensitive files.
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

_FILE_LEAD = r"(?:^|[\s<>|;&=`(\"'])"
_PATH_PREFIX = r"(?:[\w./-]*?/)?"
_FILE_TRAIL = r"(?=[\s<>|;&)\"'`,]|$)"


def _build_secret_deny_patterns() -> list[tuple[re.Pattern, str, str]]:
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
        patterns.append((rx_verb, code, f"禁止讀取 {desc}"))
        patterns.append((rx_dot, f"{code}_DOT", f"禁止以 . (dot-source) 載入 {desc}"))
        patterns.append((rx_redir, f"{code}_REDIR", f"禁止以 stdin 重導向讀取 {desc}"))
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


def is_protected_branch(branch: str) -> bool:
    return branch in ("master", "main")


_GIT_COMMIT_RE = re.compile(
    r"\bgit\s+(?:[^\s|;&]+\s+)*?commit(\s|$)"
)
_GIT_C_PATH_RE = re.compile(r"\bgit\s+(?:.*?\s+)?-C\s+(\S+)")


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

    # 1) static patterns
    for pat, code, reason in STATIC_DENIES:
        if pat.search(command):
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
    hit = check_git_commit_on_master(command)
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

    log_event(HOOK_NAME, "pass", tool=tool, command_preview=command[:80])
    return 0


if __name__ == "__main__":
    sys.exit(main())
