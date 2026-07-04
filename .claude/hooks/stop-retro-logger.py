#!/usr/bin/env python3
"""Stop / SubagentStop sentinel: harvest [VERIFY_FAILED:*] markers.

Phase D mode: SENTINEL — always pass, never block.

When the session (or a subagent) ends:
1. If transcript_path is in payload, read it and grep for
   [VERIFY_FAILED:*], [HUMAN_ATTENTION_REQUIRED:*], and surrounding
   context (5 lines).
2. Append harvested entries to docs/learnings/ERRORS.md
   `## Pending Review` section, dedup by content hash.
3. Always log to state/hook-events.jsonl.

Why dedup?
- A single failure may surface multiple times across SubagentStop and
  Stop; we want one entry per unique reason+context.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import (  # noqa: E402
    ERRORS_MD,
    log_event,
    now_iso,
    read_stdin_json,
)

HOOK_NAME = "stop-retro-logger"

MARKER_RE = re.compile(
    r"\[(VERIFY_FAILED|HUMAN_ATTENTION_REQUIRED):\s*([^\]]+)\]"
)
PENDING_SECTION_HEADER = "## Pending Review"
PENDING_SECTION_FALLBACK = "_(空)_"


_ALNUM_RE = re.compile(r"[A-Za-z0-9]")


def _is_placeholder(reason: str) -> bool:
    """Skip markers that are doc placeholders, not real emits.

    Three filters (any one matches → drop):
    1. Angle-bracket placeholder like `<reason>` / `<INV-id>` from docs.
    2. Glob/wildcard mentions like `*` (used in our docs as
       `[VERIFY_FAILED:*]` to mean "any reason") — these contain no
       alphanumeric content.
    3. Empty / pure-punctuation reasons that result from malformed
       captures (regex matched but caught nothing meaningful).

    Real emits always carry an INV-id or a short prose explanation,
    i.e. ≥3 alphanumeric characters.
    """
    r = reason.strip()
    if not r:
        return True
    if "<" in r and ">" in r:
        return True
    alnum = _ALNUM_RE.findall(r)
    return len(alnum) < 3


def _scan_text_for_markers(text: str) -> list[tuple[str, str]]:
    """Return list of (kind, reason) from a single text blob.

    Filters out doc placeholders.
    """
    out = []
    for m in MARKER_RE.finditer(text):
        kind = m.group(1)
        reason = m.group(2).strip()
        if _is_placeholder(reason):
            continue
        out.append((kind, reason))
    return out


def _harvest_jsonl_transcript(lines: list[str]) -> list[dict]:
    """Parse Claude Code JSONL transcript and harvest markers from the
    actual assistant text content (not the JSON envelope or its escaped
    representation in user prompts that *describe* the syntax).
    """
    findings: list[dict] = []
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        msg = obj.get("message") or {}
        if msg.get("role") != "assistant":
            continue  # only count assistant emits, not user prompts that show the syntax
        content = msg.get("content") or []
        if not isinstance(content, list):
            continue
        for blk in content:
            if not isinstance(blk, dict):
                continue
            if blk.get("type") != "text":
                continue
            text = blk.get("text", "")
            for kind, reason in _scan_text_for_markers(text):
                # Use the surrounding 200 chars as context excerpt
                idx = text.find(f"[{kind}:")
                start = max(0, idx - 100)
                end = min(len(text), idx + 200)
                excerpt = text[start:end]
                h = hashlib.sha1(
                    f"{kind}|{reason}|{excerpt}".encode("utf-8"),
                    usedforsecurity=False,
                ).hexdigest()[:10]
                findings.append(
                    {
                        "kind": kind,
                        "reason": reason,
                        "context": excerpt,
                        "hash": h,
                    }
                )
    return findings


def _harvest_plain_text(lines: list[str]) -> list[dict]:
    """Fallback for non-JSONL transcripts: plain-text scan with filters."""
    findings: list[dict] = []
    for i, line in enumerate(lines):
        for kind, reason in _scan_text_for_markers(line):
            start = max(0, i - 5)
            context = "\n".join(lines[start : i + 1])
            if len(context) > 500:
                context = context[:500] + "..."
            h = hashlib.sha1(
                f"{kind}|{reason}|{context}".encode("utf-8"),
                usedforsecurity=False,
            ).hexdigest()[:10]
            findings.append(
                {"kind": kind, "reason": reason, "context": context, "hash": h}
            )
    return findings


def harvest_markers(transcript_path: str) -> list[dict]:
    """Return list of {kind, reason, context_excerpt, hash} from transcript."""
    p = Path(transcript_path)
    if not p.is_file():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    lines = text.splitlines()
    if not lines:
        return []

    # Detect JSONL: at least 3 of the first 5 non-empty lines parse as JSON.
    sample = [ln.strip() for ln in lines[:5] if ln.strip()]
    json_count = 0
    for ln in sample:
        if ln.startswith("{"):
            try:
                json.loads(ln)
                json_count += 1
            except Exception:
                pass
    is_jsonl = json_count >= max(2, len(sample) - 1)

    if is_jsonl:
        return _harvest_jsonl_transcript(lines)
    return _harvest_plain_text(lines)


def existing_pending_hashes() -> set[str]:
    """Scan ERRORS.md Pending Review section and return existing harvest hashes."""
    if not ERRORS_MD.is_file():
        return set()
    try:
        text = ERRORS_MD.read_text(encoding="utf-8")
    except Exception:
        return set()
    return set(re.findall(r"<!--\s*harvest:([0-9a-f]{10})\s*-->", text))


def append_to_pending(findings: list[dict]) -> int:
    """Append findings to ## Pending Review section. Return count appended."""
    if not findings or not ERRORS_MD.is_file():
        return 0

    existing = existing_pending_hashes()
    new_findings = [f for f in findings if f["hash"] not in existing]
    if not new_findings:
        return 0

    try:
        text = ERRORS_MD.read_text(encoding="utf-8")
    except Exception:
        return 0

    header_re = re.compile(rf"^{re.escape(PENDING_SECTION_HEADER)}\s*$", re.MULTILINE)
    header_match = header_re.search(text)
    if not header_match:
        return 0  # don't mutate if section missing

    # Build the block to insert
    iso = now_iso()
    parts: list[str] = []
    for f in new_findings:
        parts.append(
            f"<!-- harvest:{f['hash']} -->\n"
            f"- [{iso}] [{f['kind']}] **{f['reason']}**\n"
            f"  ```\n  {f['context']}\n  ```\n"
        )
    block = "\n".join(parts)

    # Section spans from the header to the next line that begins with "## ".
    section_start = header_match.start()
    next_re = re.compile(r"^## ", re.MULTILINE)
    next_match = next_re.search(text, header_match.end())
    next_section = next_match.start() if next_match else len(text)
    section = text[section_start:next_section]

    if PENDING_SECTION_FALLBACK in section:
        section = section.replace(PENDING_SECTION_FALLBACK, block)
    else:
        section = section.rstrip() + "\n\n" + block + "\n"

    new_text = text[:section_start] + section + text[next_section:]
    try:
        ERRORS_MD.write_text(new_text, encoding="utf-8")
    except Exception:
        return 0
    return len(new_findings)


def _detect_git_commits(transcript_path: str) -> list[str]:
    """Scan transcript for Bash tool calls that ran 'git commit'.

    Returns list of commit message snippets found (may be empty).
    Used by the PR_RETRO_HOOK to suggest running /pr-retro.
    """
    p = Path(transcript_path)
    if not p.is_file():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    commits: list[str] = []
    commit_re = re.compile(r'"git commit[^"]{0,200}"', re.DOTALL)
    for m in commit_re.finditer(text):
        snippet = m.group(0)[:80].replace("\n", " ")
        commits.append(snippet)
    return commits


def _append_retro_suggestion(session_id: str, commit_count: int) -> None:
    """Append a /pr-retro reminder to ERRORS.md Pending Review.

    # PR_RETRO_HOOK — extend this function to trigger full pr-retro analysis.
    Currently only writes a lightweight reminder. To enable full automation:
    1. Call /pr-retro skill logic here (or invoke as sub-process).
    2. Pass git diff output as input to the retro analysis.
    3. Write Case B/C/D candidates directly to Pending Review.
    """
    if not ERRORS_MD.is_file():
        return
    try:
        text = ERRORS_MD.read_text(encoding="utf-8")
    except Exception:
        return

    iso = now_iso()
    # NOTE: hash must NOT include the timestamp, or every Stop event (which
    # always has a fresh `iso`) produces a unique hash and dedup never fires.
    # Keep only event-essence fields: kind, session (source), commit_count
    # (message body driver).
    reminder_hash = hashlib.sha1(
        f"retro-reminder|{session_id}|{commit_count}".encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()[:10]

    existing = existing_pending_hashes()
    if reminder_hash in existing:
        return

    header_re = re.compile(rf"^{re.escape(PENDING_SECTION_HEADER)}\s*$", re.MULTILINE)
    header_match = header_re.search(text)
    if not header_match:
        return

    block = (
        f"<!-- harvest:{reminder_hash} -->\n"
        f"- [{iso}] [PR_RETRO] **本 session 有 {commit_count} 個 git commit，"
        f"建議執行 `/pr-retro` 萃取教訓**\n"
        f"  Session: {session_id or 'unknown'}\n"
    )

    section_start = header_match.start()
    next_re = re.compile(r"^## ", re.MULTILINE)
    next_match = next_re.search(text, header_match.end())
    next_section = next_match.start() if next_match else len(text)
    section = text[section_start:next_section]

    if PENDING_SECTION_FALLBACK in section:
        section = section.replace(PENDING_SECTION_FALLBACK, block)
    else:
        section = section.rstrip() + "\n\n" + block + "\n"

    new_text = text[:section_start] + section + text[next_section:]
    try:
        ERRORS_MD.write_text(new_text, encoding="utf-8")
    except Exception:
        pass


def main() -> int:
    payload = read_stdin_json()
    transcript_path = payload.get("transcript_path", "")
    session_id = payload.get("session_id") or payload.get("sessionId") or ""

    if not transcript_path:
        log_event(HOOK_NAME, "sentinel", reason="no-transcript-path", session=session_id)
        return 0

    findings = harvest_markers(transcript_path)
    appended = append_to_pending(findings)

    # PR_RETRO_HOOK: detect git commits this session → suggest /pr-retro
    commits = _detect_git_commits(transcript_path)
    if commits:
        _append_retro_suggestion(session_id, len(commits))
        log_event(
            HOOK_NAME,
            "sentinel",
            reason="pr-retro-suggested",
            session=session_id,
            commit_count=len(commits),
        )

    log_event(
        HOOK_NAME,
        "sentinel",
        reason="harvest-done",
        session=session_id,
        found=len(findings),
        appended=appended,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
