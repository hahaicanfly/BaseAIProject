# Skill: skill-creator

> **用途**：從重複操作中識別並封裝新的 Skill，減少未來 prompt 冗餘。
> **觸發**：`/skill-creator`
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
