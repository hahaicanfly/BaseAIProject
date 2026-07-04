---
name: skill-creator
description: （基礎版，已被 skill-creator-plus 取代）僅在使用者明確輸入 /skill-creator 指令時使用；任何「建立/優化/評測 skill」的需求一律改用 skill-creator-plus。
---

# Skill: skill-creator

> ⚠ 本檔為基礎版存根：完整流程（意圖捕捉、互斥檢查、機械驗證、觸發測試、eval 迭代）在 `.claude/skills/skill-creator-plus/SKILL.md`，請改用該版。
> **觸發**：`/skill-creator`（僅顯式指令）
> **Agent**：workflow-optimizer（sonnet）

## 觸發條件

當你發現以下情況時，主動建議使用此 skill：
- 同樣的操作在 session 中出現 ≥3 次
- 一個複雜流程需要固定的多步驟提示
- 一個任務需要特定的輸出格式

## 執行步驟

1. 識別重複操作的模式
2. 提取核心步驟
3. 設計 SKILL.md 結構：
   - 用途（一句話）
   - 觸發指令
   - 執行步驟
   - 輸出格式
   - 參考文件
4. 建立 `.claude/skills/<name>/SKILL.md`
5. 在 `agent_docs/AI-TEAM-REGISTRY.md` 登記

## Skill 格式模板

```markdown
# Skill: <name>

> **用途**：<一句話>
> **觸發**：`/<command>`
> **Agent**：<agent> （<model>）

## 執行步驟
1. ...

## 輸出格式
...

## 參考
- ...
```
