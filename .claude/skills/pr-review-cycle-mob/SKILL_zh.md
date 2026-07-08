---
name: pr-review-cycle-mob
description: 以 Cascade 梯級策略平衡成本、速度與品質，執行 AI 完成程式後的最佳 PR Review 流程；當使用者要審查 PR 或提及「review cycle」「cascade review」時觸發。需要成本分級 cascade 策略時用。
---

# Skill: pr-review-cycle-mob

> **用途**：AI 寫完程式後的最佳 PR Review 流程——用 Cascade（梯級）策略平衡 cost / speed / quality。
> **觸發**：`/pr-review-cycle-mob [PR描述或diff路徑]`
> **核心洞察**：不是找「一個甜蜜點」，而是三層過濾——便宜的先跑，只有需要時才升級。

---

> 此為風險分級 cascade，與 `model-dispatch.md` 的失敗升級是兩套獨立機制，勿混用。

## Cascade 架構

```
[Level 1] haiku — 機械性掃描（<10s, 最低成本）
     │ pass → DONE（60-70% PR 在此結束）
     │ flag →
[Level 2] sonnet — 邏輯與設計 Review（<60s, 中等成本）
     │ pass → DONE
     │ flag HIGH_RISK →
[Level 3] opus — 深度仲裁（<3min, 高成本）
     │ 只用於：auth 變更、DB schema、公共 API、安全漏洞
```

**原則**：Level N 的輸入必須包含 Level N-1 的完整輸出，不重複工作。

---

## Level 1 — Mechanical Scan（haiku）

**適合**: 格式、安全 antipattern、INV-* 規則

### 執行清單

**1.1 Security Antipatterns**（對照 `docs/architecture/invariants.md` INV-SEC-*）
- [ ] 無硬編碼 API key / token / password
- [ ] 無敏感檔案被新增（`.env`, `*.pem`, `*.keystore`）
- [ ] Log 中無 secret 字串（grep `console.log.*key|log.*password|print.*token`）

**1.2 Git Hygiene**（INV-GIT-*）
- [ ] 無直接 commit 到 main/master
- [ ] Branch 命名符合 `feat/*` / `fix/*` / `refactor/*`

**1.3 Code Structure**（INV-ARC-* / INV-API-*，若已定義）
- [ ] 對照 `post-edit-lint.py` 中 `QUICK_CHECKS` 的每條 pattern

**1.4 File Footprint**
- [ ] 變更檔案數（> 15 個警告，> 30 個升級 Level 2）
- [ ] 是否有意外改動（`.gitignore`, `package-lock.json`, `*.lock`）

**輸出格式**：
```
L1 結果: PASS / FLAG
- [SEC] ...
- [GIT] ...
- [ARC] ...
升級原因（若 FLAG）: ...
```

---

## Level 2 — Logic & Design Review（sonnet）

**觸發條件**：L1 FLAG，或 PR 涉及以下任一：
- 新函數/類別/介面定義
- 現有 API 行為改變
- 狀態管理變更
- 測試覆蓋率變化

### 執行清單

**2.1 邏輯正確性**
- [ ] 函數行為是否符合 PR 描述的意圖
- [ ] Edge case 是否有處理（null/empty/boundary）
- [ ] 非同步/並發邏輯是否安全

**2.2 設計一致性**
- [ ] 命名是否符合 `agent_docs/code-conventions.md`
- [ ] 是否違反 `docs/architecture/domains.md` 的模組依賴規則
- [ ] 新增的介面是否保持單一職責

**2.3 測試品質**
- [ ] 新功能是否有對應測試
- [ ] 測試是否遵循 Given/When/Then 結構
- [ ] 是否有 mock 替換了真實 DB/外部 API（若不應 mock 則標記）

**2.4 文件更新**
- [ ] `TECHNICAL-REFERENCE.md` 是否需要更新
- [ ] ExecPlan §6 Progress Log 是否已更新
- [ ] ADR 是否需要新增（若有架構決策）

**高風險觸發條件**（升級到 Level 3）：
- 涉及 auth / token / session 邏輯
- DB schema 變更（migration）
- 公共 API 介面改變（breaking change 可能性）
- `docs/architecture/invariants.md` 中標記 `multi-agent review: 是` 的變更類型

**輸出格式**：
```
L2 結果: PASS / FLAG / HIGH_RISK
Blockers:
  - [BLOCK] ...
Suggestions:
  - [SUGGEST] ...
升級原因（若 HIGH_RISK）: ...
```

---

## Level 3 — Deep Arbitration（opus）

**觸發條件**：L2 HIGH_RISK
**使用限制**：每週不超過 5 次（成本控制）

### 執行清單

**3.1 安全深度審計**
- [ ] auth 邏輯是否有繞過可能
- [ ] Token/session 生命週期是否正確
- [ ] 輸入驗證是否完整（注入、XSS、SSRF 等）

**3.2 資料一致性**
- [ ] Migration 是否有 rollback plan
- [ ] 並發寫入是否有 race condition
- [ ] 外鍵/約束是否正確

**3.3 Breaking Change 評估**
- [ ] 現有 client 是否需要同步更新
- [ ] 版本相容性策略是否合適

**3.4 架構影響評估**
- [ ] 此變更是否應該升級為 ADR
- [ ] 是否影響 `docs/architecture/domains.md` 的邊界定義

**輸出格式**：
```
L3 結果: APPROVED / CHANGES_REQUIRED / ESCALATE_HUMAN
Critical Issues:
  - [CRITICAL] ...
Architecture Impact:
  - [ADR_NEEDED] ...
Final Verdict: ...
```

---

## Mob Review 模式（高風險 PR 的額外選項）

當 L3 結果為 `CHANGES_REQUIRED` 或有 `CRITICAL` 時，啟動並行審查：

```
同時啟動（單一訊息多個 Agent 調用）：
Agent(tech-lead, "審查代碼品質與設計一致性", background=true)
Agent(security-reviewer, "審查安全性", background=true)
Agent(qa-engineer, "審查可測試性與測試覆蓋", background=true)
```

每次派工必須照 `.claude/templates/delegation-templates.md` 三件套（目標動機/驗收條件/回報格式）。

整合三個結果，按嚴重度排序，輸出統一 Mob Review 報告。

**最終輸出需映射到 `review-protocol.md` 詞彙**：`PASS` → `Pass`、`FLAG` → `Conditional Pass`、`HIGH_RISK` / `CRITICAL` → `Block`。

---

## 成本估算指引

| PR 類型 | 預期觸達 Level | 估算成本 |
|---------|-------------|---------|
| 簡單 bug fix（1-3 檔案） | L1 | < $0.01 |
| 一般功能（5-15 檔案） | L2 | $0.05–0.20 |
| 涉及 auth/schema（任意大小） | L3 | $0.20–1.00 |
| Mob Review 觸發 | L3 + 3 agents | $1.00–3.00 |

**原則**：L3 + Mob 加起來一個月不超過 $20，就是非常健康的 review 支出。

---

## 與 pr-retro 的接口

每次 Cascade 完成後，`pr-retro` skill 應：
1. 收集所有 Flag/Block/Critical 條目
2. 分析是否對應 ERRORS.md 已有的 lesson（若對應 → lesson 被再次觸發）
3. 若為新模式 → 寫入 ERRORS.md Pending Review

詳見 `.claude/skills/pr-retro/SKILL.md`。
