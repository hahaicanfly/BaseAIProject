#!/usr/bin/env python3
"""Validate a skill directory against frontmatter and structure rules.

Rules ported from Anthropic official skill-creator quick_validate.py
(github.com/anthropics/skills, 2026-07) plus local harness additions:

  official: allowed frontmatter keys; name kebab-case <=64 chars;
            description <=1024 chars, no angle brackets;
            compatibility <=500 chars
  local:    name MUST equal directory name (mismatch = never triggers);
            SKILL.md body warn >150 lines, fail >500;
            referenced local paths should exist (warn only)

Usage: python3 validate_skill.py <path-to-skill-dir>
Exit codes: 0 = all pass (warnings allowed), 1 = has failures, 2 = usage error
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Local-path-looking tokens inside the body, e.g. .claude/..., docs/..., scripts/foo.py
PATH_RE = re.compile(r"(?<![\w/])((?:\.claude|docs|agent_docs|state|scripts|references|assets)/[\w./-]+)")

def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    fm: dict[str, str] = {}
    key = None
    for line in text[4:end].splitlines():
        if line.startswith((" ", "\t")) and key:
            fm[key] += " " + line.strip()
        elif ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            fm[key] = val.strip()
    return fm, text[end + 4:]

def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    skill_dir = Path(sys.argv[1]).resolve()
    skill_md = skill_dir / "SKILL.md"
    fails: list[str] = []
    warns: list[str] = []

    if not skill_md.is_file():
        print(f"FAIL: {skill_md} 不存在")
        return 1
    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    if not fm:
        fails.append("缺 YAML frontmatter（--- 開頭）——沒有它 skill 不會被載入")
    else:
        for k in fm:
            if k not in ALLOWED_KEYS:
                fails.append(f"frontmatter 含白名單外欄位：{k}（允許：{sorted(ALLOWED_KEYS)}）")
        name = fm.get("name", "")
        desc = fm.get("description", "")
        if not name:
            fails.append("frontmatter 缺 name")
        else:
            if not NAME_RE.fullmatch(name):
                fails.append(f"name 不符 kebab-case 規則：{name!r}")
            if len(name) > 64:
                fails.append(f"name 超過 64 字元（{len(name)}）")
            if name != skill_dir.name:
                fails.append(f"name ({name!r}) != 目錄名 ({skill_dir.name!r}) —— 這個 skill 永遠不會被觸發")
        if not desc:
            fails.append("frontmatter 缺 description（主要觸發機制）")
        else:
            if len(desc) > 1024:
                fails.append(f"description 超過 1024 字元（{len(desc)}）")
            if "<" in desc or ">" in desc:
                fails.append("description 含角括號 <>（官方驗證器禁止）")
            if "當" not in desc and "when" not in desc.lower() and "觸發" not in desc:
                warns.append("description 似乎沒寫「何時觸發」——Claude 傾向 undertrigger，建議補情境與原話觸發詞")
        comp = fm.get("compatibility", "")
        if comp and len(comp) > 500:
            fails.append(f"compatibility 超過 500 字元（{len(comp)}）")

    body_lines = body.count("\n") + 1
    if body_lines > 500:
        fails.append(f"SKILL.md body {body_lines} 行 > 500 硬上限——抽到 references/")
    elif body_lines > 150:
        warns.append(f"SKILL.md body {body_lines} 行 > 150 建議值——考慮抽 references/")

    repo_root = skill_dir
    while repo_root.parent != repo_root and not (repo_root / ".git").exists():
        repo_root = repo_root.parent
    for ref in sorted(set(PATH_RE.findall(body))):
        candidates = [repo_root / ref, skill_dir / ref]
        if not any(c.exists() for c in candidates):
            warns.append(f"body 引用的路徑找不到：{ref}（引用即驗證）")

    for f in fails:
        print(f"FAIL: {f}")
    for w in warns:
        print(f"WARN: {w}")
    if not fails and not warns:
        print("PASS: 全部檢查通過")
    elif not fails:
        print(f"PASS（{len(warns)} 個警告）")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
