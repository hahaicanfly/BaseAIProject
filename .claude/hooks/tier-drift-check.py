#!/usr/bin/env python3
"""UserPromptSubmit: catch a declared tier that contradicts the real model.

The main conversation's tier is declared at SessionStart because nothing
observable there reveals the model. From the second turn onward the
transcript does carry the true model id — including `--model` CLI
overrides that ~/.claude/settings.json never sees. This hook closes that
gap: on a mismatch it tells the session to load the correct pack instead.

Without this, a session declared `strong` but actually running Haiku would
silently operate on condensed rules — the exact failure the tiering exists
to prevent, and the "documented defense that isn't really there" pattern
LETTER-TO-FUTURE-SESSIONS.md §I.1 warns about.

Runs once per session in practice: the check short-circuits as soon as a
real model id has been seen.

CRITICAL — sentinel (ADR-0001 D5): every path returns 0. UserPromptSubmit
CAN block a prompt; this hook must never do so.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _lib import log_event, read_stdin_json  # noqa: E402
from tier_resolve import (  # noqa: E402
    emit_context,
    get_session_tier,
    model_from_transcript,
    record_session_tier,
    tier_from_model,
)

HOOK_NAME = "tier-drift-check"


def main() -> int:
    payload = read_stdin_json() or {}
    session_id = payload.get("session_id") or ""
    if not session_id:
        return 0

    record = get_session_tier(session_id)
    if not record or record.get("verified"):
        return 0  # nothing was injected, or already settled

    real_model = model_from_transcript(payload.get("transcript_path"))
    if not real_model:
        return 0  # first turn: no assistant message yet, try again next turn

    declared_tier = record.get("tier")
    actual_tier = tier_from_model(real_model)
    record_session_tier(session_id, verified=True, real_model=real_model,
                        actual_tier=actual_tier)

    if actual_tier == declared_tier:
        log_event(HOOK_NAME, "pass", reason="tier-confirmed",
                  session=session_id, tier=declared_tier)
        return 0

    log_event(HOOK_NAME, "warn", reason="tier-drift", session=session_id,
              detail=f"declared={declared_tier} actual={actual_tier} model={real_model}")
    print(emit_context("UserPromptSubmit", (
        f"[harness] Tier 宣告與實際模型不符：本 session 開始時載入的是 "
        f"**{declared_tier}** pack，但實際模型是 `{real_model}`（對應 "
        f"**{actual_tier}**）。請立即讀 `.claude/tiers/{actual_tier}.md` 並改依該份規則作業"
        f"；先前載入的 {declared_tier} pack 若與之衝突，以 {actual_tier} 為準。\n"
        f"根因是 tier 宣告過期——請在專案 `.claude/settings.json` 的 `env` 區塊"
        f"設定 `\"HARNESS_TIER\": \"{actual_tier}\"`，或改用 /model 切換"
        f"（CLI 的 --model 覆寫不會寫回設定檔，因此偵測不到）。"
    )))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
