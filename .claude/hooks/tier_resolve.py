#!/usr/bin/env python3
"""Shared tier resolution for the model-tiered harness (F-003).

Not a hook — a module imported by session-tier-inject, subagent-tier-inject
and tier-drift-check.

Two different problems, two different answers:

- **Main conversation**: its model is NOT observable before the first
  response. Verified empirically on Claude Code 2.1.220 — SessionStart,
  InstructionsLoaded and UserPromptSubmit payloads all lack a `model`
  field, and the environment is byte-identical across `--model haiku` and
  `--model sonnet` runs. So the main tier is DECLARED, then verified later
  against the transcript (F-003 DEC-4 / Q7).
- **Subagent**: `SubagentStart` carries `agent_type`, so its tier is
  genuinely detected by reading that agent's frontmatter `model`.

Fail-safe everywhere: anything unknown, unreadable or unexpected resolves
to `light`, the FULL weak-model SOP. Under-loading rules is more dangerous
than over-loading them (F-003 DEC-3).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TIERS_DIR = REPO_ROOT / ".claude" / "tiers"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
MODEL_MAP_FILE = TIERS_DIR / "model-map.json"
USER_SETTINGS = Path.home() / ".claude" / "settings.json"

TIERS = ("strong", "mid", "light")
FALLBACK_TIER = "light"

# What `HARNESS_TIER` may say to mean "I am not declaring anything — go guess".
# `auto` is the value this template ships with, so the knob is visible in
# settings.json without any project being forced onto a tier. Empty and unset
# mean the same thing. Anything else that is not a tier name is a typo and is
# treated the same way: ignored, never trusted.
NO_DECLARATION = ("", "auto")

_FRONTMATTER_MODEL_RE = re.compile(r"^model:\s*[\"']?([A-Za-z0-9._\-\[\]]+)", re.M)


def _load_model_map() -> tuple[list[dict], str]:
    """Return (rules, fallback_tier). Missing/broken map -> ([], 'light')."""
    try:
        data = json.loads(MODEL_MAP_FILE.read_text(encoding="utf-8"))
        rules = [r for r in data.get("rules", [])
                 if isinstance(r, dict) and r.get("tier") in TIERS and r.get("match")]
        fallback = data.get("fallback_tier")
        if fallback not in TIERS:
            fallback = FALLBACK_TIER
        return rules, fallback
    except Exception:
        return [], FALLBACK_TIER


def tier_from_model(model_id: str | None) -> str:
    """Map a model identifier to a tier. First substring hit wins."""
    rules, fallback = _load_model_map()
    if not model_id:
        return fallback
    needle = str(model_id).lower()
    for rule in rules:
        if str(rule["match"]).lower() in needle:
            return rule["tier"]
    return fallback


def _declared_tier() -> str | None:
    """HARNESS_TIER from the project's settings.json `env` block.

    Verified empirically that a project-level env block does reach hook
    processes. `auto` (the shipped default) and anything that is not a tier
    name are ignored rather than trusted, so resolution falls through to the
    guess and then to `light`.
    """
    val = (os.environ.get("HARNESS_TIER") or "").strip().lower()
    if val in NO_DECLARATION:
        return None
    return val if val in TIERS else None


def _settings_model() -> str | None:
    """Best-effort guess: the model saved in ~/.claude/settings.json.

    `/model` writes back here, so this is right for interactive use. It is
    WRONG when a session was started with a `--model` CLI override, which
    is exactly what tier-drift-check exists to catch.
    """
    try:
        return json.loads(USER_SETTINGS.read_text(encoding="utf-8")).get("model")
    except Exception:
        return None


def resolve_main_tier() -> tuple[str, str]:
    """Return (tier, source) for the main conversation."""
    declared = _declared_tier()
    if declared:
        return declared, "declared:HARNESS_TIER"
    model = _settings_model()
    if model:
        return tier_from_model(model), f"guessed:settings.json({model})"
    return FALLBACK_TIER, "fallback:no-signal"


def agent_declared_model(agent_type: str) -> str | None:
    """The `model:` value in .claude/agents/<agent_type>.md frontmatter.

    None means either "no such file" (built-in agents like Explore /
    general-purpose / Plan have no definition file here) or "file exists
    but declares no model", i.e. it inherits the main conversation's.
    Callers distinguish the two via agent_file_exists().
    """
    path = AGENTS_DIR / f"{agent_type}.md"
    try:
        head = path.read_text(encoding="utf-8")[:2000]
    except Exception:
        return None
    match = _FRONTMATTER_MODEL_RE.search(head)
    return match.group(1) if match else None


def agent_file_exists(agent_type: str) -> bool:
    try:
        return (AGENTS_DIR / f"{agent_type}.md").is_file()
    except Exception:
        return False


def resolve_agent_tier(agent_type: str | None) -> tuple[str, str]:
    """Return (tier, source) for a subagent.

    Three boundary cases, all resolved deliberately (F-003 Phase 1 step 10):
    (i)   frontmatter declares a model      -> map it
    (ii)  file exists but declares no model -> inherits main conversation
    (iii) no file (built-in agent) or error -> light, the safe default
    """
    if not agent_type:
        return FALLBACK_TIER, "fallback:no-agent-type"
    if not agent_file_exists(agent_type):
        return FALLBACK_TIER, "fallback:builtin-or-missing-agent"
    model = agent_declared_model(agent_type)
    if model:
        return tier_from_model(model), f"detected:frontmatter({model})"
    main_tier, main_src = resolve_main_tier()
    return main_tier, f"inherited:main({main_src})"


def load_pack(tier: str) -> str | None:
    """Text of the tier pack, or None if it does not exist yet."""
    try:
        return (TIERS_DIR / f"{tier}.md").read_text(encoding="utf-8")
    except Exception:
        return None


def model_from_transcript(transcript_path: str | None) -> str | None:
    """The real model id from the transcript's first assistant message.

    This is the ONLY trustworthy source — it reflects `--model` CLI
    overrides that settings.json does not know about. It exists only from
    the first assistant response onward, which is why it can verify a tier
    but never choose one at session start.
    """
    if not transcript_path:
        return None
    try:
        with open(transcript_path, encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                message = obj.get("message") or {}
                if message.get("role") == "assistant" and message.get("model"):
                    return message["model"]
    except Exception:
        return None
    return None


SESSION_TIERS_FILE = REPO_ROOT / "state" / "session-tiers.json"
_MAX_SESSION_RECORDS = 50


def _read_session_tiers() -> dict:
    try:
        data = json.loads(SESSION_TIERS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def record_session_tier(session_id: str, **fields) -> None:
    """Remember what tier a session was given, so drift can be checked later.

    Best-effort: concurrent sessions may race and lose a write, in which
    case the drift check simply re-runs. Never raises — callers are hooks.
    """
    if not session_id:
        return
    try:
        data = _read_session_tiers()
        entry = data.get(session_id) or {}
        entry.update(fields)
        data[session_id] = entry
        if len(data) > _MAX_SESSION_RECORDS:
            for stale in list(data)[: len(data) - _MAX_SESSION_RECORDS]:
                data.pop(stale, None)
        SESSION_TIERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SESSION_TIERS_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    except Exception:
        return


def get_session_tier(session_id: str) -> dict:
    return _read_session_tiers().get(session_id) or {}


def emit_context(event_name: str, text: str) -> str:
    """The JSON envelope a context-only hook prints on stdout."""
    return json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": text,
        }
    }, ensure_ascii=False)
