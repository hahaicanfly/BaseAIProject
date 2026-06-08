# {{PROJECT_NAME}} — Agent 操作地圖

> {{PROJECT_TAGLINE}}
> **本檔為地圖（≤150 行），詳情請追外部文件**。

## Quick Commands

```bash
# 填入專案的常用建構/測試指令
# e.g.:
# npm run dev              # 啟動開發伺服器
# npm test                 # 執行測試
# npm run lint             # 執行 Lint
# git branch --show-current  # 確認目前 branch（INV-GIT-001）
```

## 不可違反的 Invariants

機械化驗證的硬規則見 `docs/architecture/invariants.md`。`pre-tool-use-guard.py`（enforce mode）攔截：

- INV-GIT-002 在 master/main 上 `git commit`
- INV-GIT-003 對 master/main `git push --force`
- INV-GIT-004 `git reset --hard origin/master`
- 讀 `.env` / `curl … | sh`

## MUST / NEVER 摘要

| MUST | 說明 |
|------|------|
| READ TECH REFERENCE FIRST | 任務前讀 `agent_docs/TECHNICAL-REFERENCE.md` |
| READ BEFORE MODIFY | 改檔前必先 `Read` |
| EXECPLAN BEFORE EXECUTE | 跨模組／API 變更／重構，先在 `docs/plans/active/` 建 ExecPlan，等人類核可 |
| ATOMIC COMMITS | 一功能一 commit，type(scope) 格式，英文 message |
| BRANCH + PR | 嚴禁直接 commit master；feat/<slug> 從 master 開出 |
| CODE-REVIEWER BEFORE PR | 跑 `@.claude/agents/code-reviewer.md` 修完 Blocker + Warning |
| HANDOFF MARKER | sub-agent final response 必有 `[HANDOFF:*]` / `[VERIFY_FAILED:*]` / `[HUMAN_ATTENTION_REQUIRED:*]` |
| PHASE HANDOFF GATE | 階段完成（功能 / Phase N / Mx）進下一任務前先查 context 用量；>50% 必跑 `/last-word` 產出 `SESSION-HANDOFF.md` → `/clear` → 讀檔內交接 prompt 以新 session 續接 |


| NEVER | 說明 |
|-------|------|
| HARDCODE SECRETS | API key / 密碼 / 憑證 |
| COMMIT SENSITIVE | `.env` / `local.properties` / `*.keystore` / `*secret*` |
| HALLUCINATE | 猜 API 簽名 — 不確定就查 |
| OVER-ENGINEER | 不加未要求的功能、抽象、改進 |
| MODIFY UNREAD | 改任何檔前必先 Read |
| SKIP VERIFICATION | 跳過 lint/test 直接宣稱完成 |

## Harness 體系

| 路徑 | 用途 |
|------|------|
| `docs/INDEX.md` | 文件目錄起點 |
| `docs/plans/PLANS.md` | ExecPlan 規格與範本 |
| `docs/plans/active/` | 進行中 ExecPlan（入版控） |
| `docs/architecture/invariants.md` | 機械化規則（INV-*） |
| `docs/architecture/domains.md` | 模組層依賴方向 |
| `docs/learnings/ERRORS.md` | 累積教訓 |
| `docs/decisions/ADR-*.md` | 架構決策記錄 |
| `.claude/protocols/execplan-lifecycle.md` | 10 階段 state machine |
| `.claude/protocols/handoff-protocol.md` | 三種 marker 規範 |
| `.claude/protocols/review-protocol.md` | reviewer agent SOP |
| `.claude/hooks/` | Phase D：guard enforce、其餘 sentinel |
| `state/SCHEMA.md` | runtime state schema |

## Virtual Team（14 agents）

| Agent | 模型 | 職責 |
|-------|------|------|
| `pm` | opus | 需求分析、ExecPlan §1 |
| `architect` | opus | 架構設計、ExecPlan §2-§4 |
| `tech-lead` | opus | Code review、規範檢查 |
| `code-reviewer` | sonnet | PR 前自動審查 |
| `qa-engineer` | opus | 單測、整測、bug 分析 |
| `security-reviewer` | opus | 安全審計 |
| `plan-reviewer` | opus | ExecPlan 完整性審查 |
| `uiux-agent` / `ui-ux-designer` | sonnet/opus | 三階段 UI 流程 |
| `data-analyst` / `market-researcher` / `competitive-analyst` | opus | 市場/競品/數據 |
| `techdebt-scanner` / `workflow-optimizer` | sonnet | 技術債、DX |

## Multi-Agent Skills

`.claude/skills/`：`/feature-pipeline`、`/multi-agent-review`、`/code-review`、`/security-audit`、`/tdd-workflow`、`/techdebt`、`/context`、`/ui-ux-pro-max`、`/frontend-design`、`/beautiful-mermaid`、`/skill-creator`。

## Tech Stack

{{填入技術棧，例如：Node.js · TypeScript · React · Next.js · Tailwind CSS}}

## Project Relations

| 專案/系統 | 路徑/位置 | 邊界 |
|----------|---------|------|
| {{關聯專案1}} | `{{路徑}}` | {{邊界說明}} |

## Detailed Documentation

- `agent_docs/TECHNICAL-REFERENCE.md` — **必讀**：當前架構（執行任務前必讀）
- `agent_docs/multi-agent-guide.md` — 多代理 Swarm/Pipeline 指南
- `agent_docs/security-policy.md` / `cost-optimization.md` / `code-conventions.md`
- `.claude/rules/{security,cost-optimization,modularity,plan-first,parallel-worktree}.md` — 5 條 rules
- `.claude/uiux/WORKFLOW.md` — UI 三階段流程

## Communication Style

繁體中文回應；代碼註解可英文；Git commit message 英文。精簡、技術準確、有下一步行動、無 emoji（除非用戶要求）。

```
✓ 完成：[具體做了什麼]
→ 下一步：[接下來要做什麼]
⚠ 注意：[需要用戶知道的風險或問題]
```
