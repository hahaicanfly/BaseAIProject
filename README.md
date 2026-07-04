# BaseAIProject — AI Harness Engineering Template

> 這是一個通用的 AI Harness Engineering 基礎模板，整合 Virtual Team、ExecPlan 系統、4 個 Python Hooks 與完整文件體系，可直接複製到新專案後按清單客製化。

## 這個模板包含什麼

### 架構系統
- **CLAUDE.md 憲法** — AI agent 行為規範（含 `{{PROJECT_NAME}}` 等佔位符）
- **14 個 Virtual Agent** — PM、Architect、Tech Lead、QA、Security、UI/UX 等完整虛擬團隊
- **15 個 Skills** — code-review、multi-agent-review、feature-pipeline、harness-eval 等工作流技能（清單見 `agent_docs/AI-TEAM-REGISTRY.md`）

### 工程流程
- **ExecPlan 系統** — 10 階段 state machine，跨 session 結構化交接
- **3 種 Handoff Marker** — `[HANDOFF:]`、`[VERIFY_FAILED:]`、`[HUMAN_ATTENTION_REQUIRED:]`
- **4 個 Python Hooks** — guard（enforce）、lint（sentinel）、snapshot、retro-logger

### 文件體系
- **INV-\* Invariants** — 可機械驗證的硬規則
- **ADR 模板** — 架構決策記錄
- **累積教訓（ERRORS.md）** — AI 犯錯後自動收割
- **State Schema** — Runtime 狀態格式（gitignored，但有 SCHEMA.md 說明）

### UI/UX 系統
- **3 階段工作流** — Wireframe → Critique → Implementation
- **規則、Style Spec 模板、Prompt 模板**

---

## 快速開始（複製後的客製化清單）

### Phase 1：必填（不填會出錯）

- [ ] **全域搜尋替換 `{{PROJECT_NAME}}`** → 你的專案名稱
- [ ] **全域搜尋替換 `{{PROJECT_TAGLINE}}`** → 一句話描述
- [ ] **`CLAUDE.md`**：填入 Quick Commands 的建構/測試指令、Tech Stack / Project Relations 節
- [ ] **`agent_docs/TECHNICAL-REFERENCE.md`**：填入技術棧（§2）、架構圖（§3）
- [ ] **`.claude/settings.local.json.template`** → 複製為 `.claude/settings.local.json`，填入 allowed paths

### Phase 2：架構定義

- [ ] **`docs/architecture/domains.md`**：填入實際模組列表與依賴關係
- [ ] **`docs/architecture/invariants.md`**：根據技術棧新增 INV-SEC-\*、INV-TEST-\*、INV-API-\* 規則
- [ ] **`agent_docs/code-conventions.md`**：填入語言/框架特定的命名規範與代碼風格
- [ ] **`.claude/hooks/post-edit-lint.py`**：填入 `QUICK_CHECKS`（INV-\* grep patterns）

### Phase 3：UI/UX（若有前端）

- [ ] **`.claude/uiux/style-spec.template.md`**：填入設計 Token（顏色、字型、間距）
- [ ] **`.claude/uiux/prompt-templates.md`**：填入技術棧（`[填入技術棧: ...]`）
- [ ] **`.claude/uiux/WORKFLOW.md`**：確認 3 階段流程符合你的設計工具

### Phase 4：Skill 實作（按需）

以下 skill 目前是 **Stub（空殼）**，需根據專案技術棧填充實作：
- [ ] `.claude/skills/ui-ux-pro-max/SKILL.md`
- [ ] `.claude/skills/frontend-design/SKILL.md`
- [ ] `.claude/skills/beautiful-mermaid/SKILL.md`
- [ ] `.claude/skills/skill-creator/SKILL.md`

已有基本實作，確認後即可使用：
- [x] `.claude/skills/code-review/`
- [x] `.claude/skills/multi-agent-review/`
- [x] `.claude/skills/feature-pipeline/`
- [x] `.claude/skills/security-audit/`
- [x] `.claude/skills/tdd-workflow/`
- [x] `.claude/skills/context-aggregator/`
- [x] `.claude/skills/techdebt-scanner/`

### Phase 5：ADR 補充

- [ ] 為你的核心架構決策各寫一份 `docs/decisions/ADR-000N-<slug>.md`
- [ ] 更新 `docs/INDEX.md` 的 ADR 表格

---

## 目錄結構

```
BaseAIProject/
├── CLAUDE.md                    # AI agent 行為憲法（必讀）
├── agent_docs/
│   ├── TECHNICAL-REFERENCE.md  # 技術百科（需填充）
│   ├── AI-TEAM-REGISTRY.md     # 14 agents + 11 skills 目錄
│   ├── multi-agent-guide.md    # 多代理協作指南
│   ├── security-policy.md      # 安全政策
│   ├── cost-optimization.md    # 成本優化指南
│   └── code-conventions.md     # 代碼規範（需填充）
├── docs/
│   ├── INDEX.md                # 文件索引
│   ├── architecture/
│   │   ├── invariants.md       # INV-* 規則
│   │   └── domains.md          # 領域邊界
│   ├── decisions/
│   │   └── ADR-template.md     # ADR 範本
│   ├── learnings/
│   │   └── ERRORS.md           # 累積教訓
│   └── plans/
│       ├── PLANS.md            # ExecPlan 規格
│       ├── active/             # 進行中的 ExecPlan
│       └── completed/          # 已完成的 ExecPlan
├── state/
│   ├── SCHEMA.md               # Runtime state 格式說明
│   └── .gitignore              # gitignore（state/* 不入版控）
└── .claude/
    ├── settings.json           # 5 個 hooks 配置
    ├── settings.local.json.template
    ├── agents/                 # 14 個 virtual agents
    ├── commands/               # /last-word, /techdebt
    ├── hooks/                  # 4 個 Python hooks
    ├── protocols/              # ExecPlan lifecycle, handoff, review
    ├── rules/                  # 5 個 always-on rules
    ├── skills/                 # 11 個 skills
    └── uiux/                   # UI/UX 設計系統
```

---

## 核心概念快速參考

| 概念 | 說明 | 相關文件 |
|------|------|---------|
| ExecPlan | 9 段結構化任務計畫，跨 session 交接 | `docs/plans/PLANS.md` |
| INV-* | 可機械驗證的硬規則，hook 自動攔截 | `docs/architecture/invariants.md` |
| Handoff Marker | 每次 agent 結束時的結構化交接標記 | `.claude/protocols/handoff-protocol.md` |
| Virtual Team | 14 個專業 sub-agent | `agent_docs/AI-TEAM-REGISTRY.md` |
| 常駐規則面 | `.claude/rules/*`（`always: true`）每 session 自動載入，須保持精簡 | `.claude/protocols/harness-maintenance.md` §5 |

---

## 參考資料

- [Mitchell Hashimoto — Harness Engineering](https://mitchellh.com)
- [Ryan Lopopolo — OpenAI Codex 1M 行實驗](https://github.com/artichoke/artichoke)
- [Boris Cherny — Claude Code 10 Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Andy Matuschak — Evergreen Notes](https://notes.andymatuschak.org)
