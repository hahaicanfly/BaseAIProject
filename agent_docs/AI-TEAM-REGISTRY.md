# AI Team Registry

> **角色**：本檔是所有 agent 與 skill 的完整目錄，內容逐字取自 `.claude/agents/*.md` frontmatter 與 `.claude/skills/*/SKILL.md` description。
> **正典規則**：模型分派以 `.claude/agents/*.md` frontmatter 的 `model` 欄為準（CLAUDE.md 正典層級）。
> **本檔由 frontmatter 生成（2026-07-04）**。與 agent frontmatter 矛盾時以 frontmatter 為準；更新方式：照本段說明重新生成（逐檔讀取 frontmatter / SKILL.md description 覆寫下表），不要手改單格。

---

## Agents — 14

| Agent | model | 職責 | tools |
|-------|-------|------|-------|
| `architect` | opus | 系統架構師 - 系統設計、API 設計、資料結構、ADR | Read, Grep, Glob |
| `code-reviewer` | sonnet | 自動化 Code Review 專員 | Read, Bash, Grep, Glob |
| `competitive-analyst` | opus | Expert competitive analyst — 競爭情報、策略分析、市場定位 | Read, Grep, Glob, WebFetch, WebSearch |
| `data-analyst` | opus | 數據分析師 - 市場分析、競品研究、數據洞察 | Read, WebSearch, WebFetch, Grep |
| `market-researcher` | opus | Expert market researcher — 市場分析、消費者洞察、競爭情報 | Read, Grep, Glob, WebFetch, WebSearch |
| `plan-reviewer` | opus | Plan 審查員 - 審查執行計劃的完整性、風險與驗證策略 | Read, Grep, Glob |
| `pm` | opus | 產品經理 - 需求分析、用戶故事、優先級排序 | Read, Grep, Glob, WebSearch, WebFetch |
| `qa-engineer` | opus | 測試工程師 - 單元測試、整合測試、Bug 分析 | Read, Bash, Grep, Glob |
| `security-reviewer` | opus | 安全審查員 - 安全審計、漏洞檢測、金鑰保護 | Read, Grep, Glob |
| `tech-lead` | opus | 技術主管 - Code Review、規範檢查、重構建議 | Read, Grep, Glob |
| `techdebt-scanner` | sonnet | 技術債分析師 - 掃描技術債、代碼健康度分析 | Read, Bash, Grep, Glob |
| `ui-ux-designer` | opus | UI/UX 設計師 - 界面設計、用戶流程、設計規範 | Read, Grep, Glob, WebFetch |
| `uiux-agent` | sonnet | UI/UX 設計代理 - 負責草圖、評審，不直接寫 production code | Read, Grep, Glob, Task |
| `workflow-optimizer` | sonnet | 工作流優化師 - 審查 Claude Code 配置與開發體驗 | Read, Grep, Glob |

> 所有 agent 皆有 `verification_required: true`、`handoff_artifact: docs/plans/active/<task-id>.md`、`context_firewall: true`（未列於上表，逐檔一致）。

---

## Skills — 15

| Skill | 一句話描述 |
|-------|-----------|
| `beautiful-mermaid` | 生成美觀、清晰的 Mermaid 圖表（架構圖、流程圖、序列圖、類別圖、ER 圖、狀態圖），可輸出終端 ASCII 藝術或 SVG 檔案 |
| `code-review` | 對 PR diff 進行標準代碼審查，涵蓋安全性、品質與架構合規 |
| `context-aggregator` | 聚合 MCP 記憶、Git 歷史、本地檔案等多來源資訊，產出結構化摘要以利 session 交接與工作延續 |
| `feature-pipeline` | 大型新功能的端對端開發流水線，從需求分析、架構設計、UI/UX 到多代理審查一次串接 |
| `frontend-design` | 以字體、色彩、動效、空間構成等設計哲學為核心，產出高品質 UI 元件與視覺設計指引 |
| `harness-eval` | 掃描目標 repo，評估 Harness Engineering 成熟度並輸出 0–100 分數、缺口清單與優先改善建議 |
| `multi-agent-review` | 並行啟動 code-reviewer、security-reviewer、qa-engineer 三位專家代理做全方位審查 |
| `pr-retro` | 每次 PR merge 後自動萃取教訓並寫入 ERRORS.md Pending Review，驅動 skill 文件持續優化 |
| `pr-review-cycle-mob` | 以 Cascade 梯級策略平衡成本、速度與品質，執行 AI 完成程式後的最佳 PR Review 流程 |
| `security-audit` | 完整安全審查，涵蓋認證、密鑰洩漏、依賴漏洞與 OWASP 標準檢查 |
| `skill-creator` | 從重複操作中識別並封裝新 Skill、優化既有 Skill 描述與觸發準確度，並可執行 eval 衡量效能 |
| `spectra-amplifier` | 將薄弱的需求描述或 PRD 草稿強化為每項需求皆附可驗證 acceptance criteria 的完整規格 |
| `tdd-workflow` | 執行 Red → Green → Refactor 的測試驅動開發流程，用於核心業務邏輯與高可靠性需求 |
| `techdebt-scanner` | 系統性掃描專案技術債（TODO/FIXME、複雜函式、重複程式碼等），產出分級優先報告 |
| `ui-ux-pro-max` | 產出完整設計系統，涵蓋色彩調色盤、字體配對、UI 風格與 UX 準則，支援多種前端技術棧 |

---

## Commands（`.claude/commands/`）

| 指令 | 檔案 |
|------|------|
| `/last-word` | `.claude/commands/last-word.md` |
| `/techdebt` | `.claude/commands/techdebt.md` |

---

## 模型分級策略

```
haiku  → 重複性、格式化、簡單判斷
sonnet → 代碼生成、分析、一般 review（預設）
opus   → 架構設計、複雜推理、深度分析
```

詳見 `.claude/rules/cost-optimization.md`。

---

## 引用此檔的位置

- `agent_docs/multi-agent-guide.md`
- `CLAUDE.md` rule pointer
