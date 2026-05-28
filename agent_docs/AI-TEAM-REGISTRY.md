# AI Team Registry

> **角色**：本檔是所有 agent 與 skill 的完整目錄，包含各代理的職責、模型建議與觸發策略。
> **使用者**：人類（查閱可用代理）+ orchestrator agent（路由決策）。

---

## Virtual Team — 14 Agents

### Core Development Team

| Agent | 檔案 | 模型 | 職責 | 典型觸發 |
|-------|------|------|------|---------|
| **PM** | `.claude/agents/pm.md` | haiku | 需求分析、用戶故事、PRD | 新功能規劃、需求釐清 |
| **Architect** | `.claude/agents/architect.md` | opus | 系統設計、API 設計、ADR | 架構決策、模組拆分 |
| **Tech Lead** | `.claude/agents/tech-lead.md` | sonnet | Code Review、技術規範、重構 | PR Review、代碼品質 |
| **QA Engineer** | `.claude/agents/qa-engineer.md` | sonnet | 測試策略、Bug 分析、驗收 | 測試計畫、Bug 回報 |
| **Security Reviewer** | `.claude/agents/security-reviewer.md` | sonnet | 安全審計、漏洞掃描 | Auth 變更、API 設計 |
| **Plan Reviewer** | `.claude/agents/plan-reviewer.md` | sonnet | ExecPlan 審查（§1-§5 核可） | ExecPlan 完成後 |

### Design Team

| Agent | 檔案 | 模型 | 職責 | 典型觸發 |
|-------|------|------|------|---------|
| **UI/UX Agent** | `.claude/agents/uiux-agent.md` | sonnet | UI/UX 決策、設計審查 | 功能含 UI 變更 |
| **UI/UX Designer** | `.claude/agents/ui-ux-designer.md` | opus | 深度設計、Wireframe、設計系統 | 新功能設計、設計系統建立 |

### Research & Analysis Team

| Agent | 檔案 | 模型 | 職責 | 典型觸發 |
|-------|------|------|------|---------|
| **Data Analyst** | `.claude/agents/data-analyst.md` | sonnet | 數據分析、指標解讀 | 效能分析、用戶行為分析 |
| **Market Researcher** | `.claude/agents/market-researcher.md` | sonnet | 市場調查、趨勢分析 | 新市場進入、競品分析 |
| **Competitive Analyst** | `.claude/agents/competitive-analyst.md` | sonnet | 競品分析、差異化 | 功能對比、定價策略 |

### Maintenance Team

| Agent | 檔案 | 模型 | 職責 | 典型觸發 |
|-------|------|------|------|---------|
| **TechDebt Scanner** | `.claude/agents/techdebt-scanner.md` | sonnet | 技術債掃描、優先排序 | `/techdebt` 命令 |
| **Workflow Optimizer** | `.claude/agents/workflow-optimizer.md` | haiku | AI 工作流程優化、prompt 調優 | Harness 調整 |

---

## Skills — 11 Skills

### Code Quality

| Skill | 目錄 | 觸發方式 | 描述 |
|-------|------|---------|------|
| **code-review** | `.claude/skills/code-review/` | `/code-review` | 標準 PR Code Review |
| **multi-agent-review** | `.claude/skills/multi-agent-review/` | `/multi-agent-review` | Swarm 模式並行審查（tech-lead + security + qa） |
| **tdd-workflow** | `.claude/skills/tdd-workflow/` | `/tdd-workflow` | 測試驅動開發工作流 |

### Feature Development

| Skill | 目錄 | 觸發方式 | 描述 |
|-------|------|---------|------|
| **feature-pipeline** | `.claude/skills/feature-pipeline/` | `/feature-pipeline` | PM → Architect → UI/UX → Dev → Review 全流水線 |
| **context-aggregator** | `.claude/skills/context-aggregator/` | `/context` | 接手工作時聚合 context |

### Security

| Skill | 目錄 | 觸發方式 | 描述 |
|-------|------|---------|------|
| **security-audit** | `.claude/skills/security-audit/` | `/security-audit` | 深度安全審計 |

### Maintenance

| Skill | 目錄 | 觸發方式 | 描述 |
|-------|------|---------|------|
| **techdebt-scanner** | `.claude/skills/techdebt-scanner/` | `/techdebt` | 技術債掃描與報告 |

### Design

| Skill | 目錄 | 觸發方式 | 描述 |
|-------|------|---------|------|
| **ui-ux-pro-max** | `.claude/skills/ui-ux-pro-max/` | `/ui-ux-pro-max` | ⚠️ Stub — 深度 UI/UX 分析（需填充） |
| **frontend-design** | `.claude/skills/frontend-design/` | `/frontend-design` | ⚠️ Stub — 前端設計實作（需填充） |

### Utility

| Skill | 目錄 | 觸發方式 | 描述 |
|-------|------|---------|------|
| **beautiful-mermaid** | `.claude/skills/beautiful-mermaid/` | `/beautiful-mermaid` | ⚠️ Stub — 生成高品質 Mermaid 圖表 |
| **skill-creator** | `.claude/skills/skill-creator/` | `/skill-creator` | ⚠️ Stub — 協助建立新 skill |

---

## Commands（常用 `/` 指令）

| 指令 | 檔案 | 用途 |
|------|------|------|
| `/last-word` | `.claude/commands/last-word.md` | Session 收尾 8 步工作流 |
| `/techdebt` | `.claude/commands/techdebt.md` | 觸發技術債掃描 |

---

## 模型分級策略

```
haiku  → 重複性、格式化、簡單判斷
sonnet → 代碼生成、分析、一般 review（預設）
opus   → 架構設計、複雜推理、深度分析
```

詳見 `agent_docs/cost-optimization.md`。

---

## 呼叫流程圖

```
人類指令
    │
    ▼
orchestrator（主 Claude session）
    │
    ├──▶ Agent(pm)        → PRD / 需求
    ├──▶ Agent(architect) → ExecPlan §2-§4
    ├──▶ Agent(tech-lead) → Code Review
    ├──▶ Agent(security)  → 安全審計
    └──▶ Agent(qa)        → 測試策略
```

---

## 引用此檔的位置

- `agent_docs/multi-agent-guide.md`
- `CLAUDE.md` rule pointer
- `.claude/agents/*.md` frontmatter 的 `team_context`
