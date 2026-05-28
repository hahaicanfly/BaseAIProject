# Protocol: PR Review

> **角色**：定義 code-reviewer / security-reviewer / qa-engineer 在 ExecPlan Phase 6 (VERIFYING) 的標準動作。
> **使用對象**：上述 3 個 reviewer agents + 主對話發 PR 前。
> **依據**：`docs/plans/PLANS.md` §3 + `.claude/protocols/execplan-lifecycle.md` Phase 6。

---

## 觸發

```
[HANDOFF: code-reviewer]    # 一般 PR 前必跑
[HANDOFF: security-reviewer] # 涉及 auth/secret 額外跑
[HANDOFF: qa-engineer]       # 核心邏輯 / 高 reliability 額外跑
```

或主對話手動執行：
```
@.claude/agents/code-reviewer.md
```

---

## Review 輸入

每個 reviewer agent 必須先讀以下檔案，**不得跳過**：

1. 對應的 ExecPlan：`docs/plans/active/F-NNN-*.md` §3 Constraints + §5 Verification Strategy
2. `docs/architecture/invariants.md`：本次變更涉及的 INV-id
3. `docs/learnings/ERRORS.md`：相關歷史 lessons
4. `agent_docs/TECHNICAL-REFERENCE.md`：相關章節（從 ExecPlan §2 Context 找路徑）
5. `git diff master...HEAD`：本次變更的完整 diff

---

## Severity Levels

每條 finding 必須標 severity：

| Severity | 意義 | 修復強制性 |
|----------|------|-----------|
| **Blocker** | 違反 invariant / 安全漏洞 / build 不過 / 測試紅燈 | **必須修，否則不得 merge** |
| **Warning** | 違反 convention / 可能引入 regression / 缺 verification | **必須修**（CLAUDE.md 規範） |
| **Suggestion** | 可選優化 / 風格調整 / 命名改善 | 視情況處理 |
| **Praise** | 做得好的部分（鼓勵記得） | 不需處理 |

---

## Code Reviewer Checklist

```
□ 讀 ExecPlan §1 Goal 並對照 PR diff 確認範圍一致
□ 讀 ExecPlan §3 Constraints，逐條 INV-id 在 diff 中驗證
□ 跑 ExecPlan §5 Verification Strategy 的所有指令
□ git branch --show-current 確認非 master
□ commit message 是否原子化、type(scope) 格式正確
□ commit 是否能獨立編譯通過
□ 有無硬編碼 secret（grep API_KEY / TOKEN / PASSWORD）
□ 有無 debug print / log 殘留
□ 新加的功能模組有對應 test？（見 INV-TEST-001）
□ 新加 interface method 是否所有 fake/mock 都更新
□ 文件同步（TECHNICAL-REFERENCE.md / diagrams）
□ 涉及 enum 或 sealed class 是否所有 case 都補全
```

---

## Security Reviewer 額外 Checklist

```
□ 所有 INV-AUTH-* 相關規則過檢
□ 敏感資料不寫入 log
□ API key / token 不硬編碼
□ 敏感 UI 畫面是否需要保護（截圖防護等）
□ EncryptedStorage / Keychain key 不洩漏
□ 第三方 OAuth / JWT 處理是否正確
□ Certificate Pinning / App Integrity 整合（如適用）
□ 輸入驗證是否完整
```

---

## QA Engineer 額外 Checklist

```
□ Unit test 覆蓋核心分支（含 negative case）
□ Test fake / mock 與 production interface 同步（INV-TEST-001）
□ Coroutine / async test 使用正確的 test dispatcher
□ Polling / timer 測試可注入時間參數
□ 所有 loading / error / empty state 有測試覆蓋
□ Edge case：空值、超長字串、極端資料量
```

---

## Output 格式（每個 reviewer 必須遵循）

```markdown
# Review Report — F-NNN

**Reviewer**: code-reviewer | security-reviewer | qa-engineer
**Scope**: <git diff range or commit hash>
**Generated**: YYYY-MM-DD HH:mm

## Findings

### Blockers
- [SEC] <description>
  - File: `path/to/file:NN`
  - Violates: INV-AUTH-001
  - Fix: <具體修復步驟>

### Warnings
- [QA] <description>
  - ...

### Suggestions
- [STY] <description>
  - ...

### Praise
- 做得好：<...>

## Verification Results

| Check | Result |
|-------|--------|
| Build | ✓ / ✗ |
| Lint  | ✓ / ✗ |
| Tests | ✓ / ✗ |

## Decision

- **Pass / Block / Conditional Pass**
- Linked ExecPlan: docs/plans/active/F-NNN-*.md

[HANDOFF: <dev to fix | human-pr-review | etc>]
```

並把 Decision 部分**同步**寫進 ExecPlan §7 Decision Log（一行 summary）。

---

## 三 reviewer 並行執行（multi-agent-review skill）

`/multi-agent-review` skill 的並行 review 流程：

```
       ┌─────────────────┐
       │  Main session   │
       │  fan-out review │
       └────────┬────────┘
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Code   │ │ Security│ │   QA    │
│Reviewer │ │ Review  │ │Engineer │
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
     └───────────┼───────────┘
                 ▼
         Aggregated report
         to ExecPlan §7
```

並行時注意：subagent 內 `git checkout` 可能改 branch，主對話 commit 前再次 `git branch --show-current`。

---

## 反模式

- ❌ Reviewer 不讀 ExecPlan 直接 review diff（會漏掉 Constraints 引用的 INV-id）
- ❌ 把 Suggestion 標成 Blocker（會無故拖慢 merge）
- ❌ 沒跑 §5 Verification Strategy 就 Pass
- ❌ 看到問題自己順手改（reviewer 不寫 production code，只報告與建議）

---

## 引用此檔的位置

- `.claude/agents/code-reviewer.md`
- `.claude/agents/security-reviewer.md`
- `.claude/agents/qa-engineer.md`
- `.claude/skills/code-review/SKILL.md`
- `.claude/skills/multi-agent-review/SKILL.md`
- `.claude/protocols/execplan-lifecycle.md` Phase 6
