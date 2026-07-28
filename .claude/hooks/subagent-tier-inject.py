#!/usr/bin/env python3
"""SubagentStart: inject the tier pack matching the subagent's own model.

Unlike the main conversation, this one is genuinely DETECTED: the payload
carries `agent_type` (verified empirically — the docs have been wrong
about hook payloads three times, see ERRORS.md), and that agent's
frontmatter declares its model. This is the half of the tiering that
matters most: the weak models actually live down here.

CRITICAL — sentinel (ADR-0001 D5): every path returns 0. SubagentStart
cannot block a spawn anyway, and a failed injection must never degrade
the subagent it was meant to help.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import log_event, read_stdin_json  # noqa: E402
from tier_resolve import emit_context, load_pack, resolve_agent_tier  # noqa: E402

HOOK_NAME = "subagent-tier-inject"


def main() -> int:
    payload = read_stdin_json() or {}
    agent_type = payload.get("agent_type") or ""
    agent_id = payload.get("agent_id") or ""

    tier, source = resolve_agent_tier(agent_type)
    pack = load_pack(tier)

    if not pack:
        log_event(HOOK_NAME, "warn", reason="pack-missing",
                  agent=agent_type, tier=tier)
        print(f"[harness] subagent tier={tier} (source: {source}) — "
              f".claude/tiers/{tier}.md 不存在，未載入分層規則。")
        return 0

    header = (
        f"# Harness tier: {tier} (subagent: {agent_type or 'unknown'})\n"
        f"<!-- source: {source} -->\n\n"
    )
    print(emit_context("SubagentStart", header + pack))
    log_event(HOOK_NAME, "pass", reason="injected",
              agent=agent_type, subagent=agent_id, tier=tier, source=source)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
