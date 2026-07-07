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
| `competitive-analyst` | sonnet | 競品分析師 - 競品逐項比較、功能對照表、定價比較、SWOT。不做市場規模／消費者調研（找 market-researcher）、不做量化 KPI／指標設計（找 data-analyst） | Read, Grep, Glob, WebFetch, WebSearch |
| `data-analyst` | sonnet | 數據分析師 - 量化數據分析、KPI 與指標設計、統計趨勢解讀。不做市場定性研究（找 market-researcher）、不做競品逐項比較（找 competitive-analyst） | Read, WebSearch, WebFetch, Grep |
| `market-researcher` | sonnet | 市場研究員 - 市場規模（TAM/SAM/SOM）、用戶調研、消費者洞察。不做量化 KPI／指標設計（找 data-analyst）、不做競品逐項比較（找 competitive-analyst） | Read, Grep, Glob, WebFetch, WebSearch |
| `plan-reviewer` | opus | Plan 審查員 - 審查執行計劃的完整性、風險與驗證策略 | Read, Grep, Glob |
| `pm` | opus | 產品經理 - 需求分析、用戶故事、優先級排序 | Read, Grep, Glob, WebSearch, WebFetch |
| `qa-engineer` | sonnet | 測試工程師 - 單元測試、整合測試、Bug 分析 | Read, Bash, Grep, Glob |
| `security-reviewer` | opus | 安全審查員 - 安全審計、漏洞檢測、金鑰保護 | Read, Grep, Glob |
| `tech-lead` | sonnet | 技術主管 - 架構重構、跨模組設計檢視、技術債裁決 | Read, Grep, Glob |
| `techdebt-scanner` | sonnet | 技術債分析師 - 掃描技術債、代碼健康度分析 | Read, Bash, Grep, Glob |
| `ui-ux-designer` | sonnet | UI/UX 設計師 - 高保真設計產出（uiux-agent 三階段流程的 Phase 3） | Read, Grep, Glob, WebFetch |
| `uiux-agent` | sonnet | UI/UX 設計代理 - 負責草圖、評審，不直接寫 production code | Read, Grep, Glob, Task |
| `workflow-optimizer` | sonnet | 工作流優化師 - 審查 Claude Code 配置與開發體驗 | Read, Grep, Glob |

> 所有 agent 皆有 `verification_required: true`、`handoff_artifact: docs/plans/active/<task-id>.md`、`context_firewall: true`（未列於上表，逐檔一致）。

---

## Skills — 17

| Skill | 一句話描述 |
|-------|-----------|
| `beautiful-mermaid` | 生成美觀、清晰的 Mermaid 圖表（架構圖、流程圖、序列圖、類別圖、ER 圖、狀態圖），可輸出終端 ASCII 藝術或 SVG 檔案 |
| `code-review` | 對 PR diff 進行標準代碼審查，涵蓋安全性、品質與架構合規。單一 PR 的標準審查 |
| `context-aggregator` | 聚合 MCP 記憶、Git 歷史、本地檔案等多來源資訊，產出結構化摘要以利 session 交接與工作延續 |
| `feature-pipeline` | 大型新功能的端對端開發流水線，從需求分析、架構設計、UI/UX 到多代理審查一次串接 |
| `frontend-design` | 以字體、色彩、動效、空間構成等設計哲學為核心，產出高品質 UI 元件與視覺設計指引 |
| `gen-app-map` | 掃描專案的進入點、路由、資料層與狀態管理，產出 app-map.json（AI 可讀 context primer）與 app-map.html（人類可讀視覺化），作為新 debug/重構 session 的輕量專案地圖。技術棧無關模板，fork 後需依專案填實掃描目標表 |
| `harness-eval` | 掃描目標 repo，評估 Harness Engineering 成熟度並輸出 0–100 分數、缺口清單與優先改善建議 |
| `multi-agent-review` | 並行啟動 code-reviewer、security-reviewer、qa-engineer 三位專家代理做全方位審查。高風險/核心邏輯變更，需要三專家並行時用；一般 PR 用 code-review |
| `pr-retro` | 每次 PR merge 後自動萃取教訓並寫入 ERRORS.md Pending Review，驅動 skill 文件持續優化 |
| `pr-review-cycle-mob` | 以 Cascade 梯級策略平衡成本、速度與品質，執行 AI 完成程式後的最佳 PR Review 流程。需要成本分級 cascade 策略時用 |
| `security-audit` | 完整安全審查，涵蓋認證、密鑰洩漏、依賴漏洞與 OWASP 標準檢查 |
| `skill-creator` | （基礎版存根，已被 skill-creator-plus 取代）僅在使用者明確輸入 /skill-creator 指令時使用；任何建立/優化/評測 skill 的需求一律改用 skill-creator-plus |
| `skill-creator-plus` | 引導完整的 skill 建立流程——意圖捕捉、重疊檢查、撰寫、機械驗證、觸發測試到 registry 登記，含 eval 迭代方法。取代基礎版 skill-creator |
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
