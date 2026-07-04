# ADR-0001 — Adopt Harness Engineering

> **狀態**：Accepted（追認重建）
> **日期**：2026-07-04（原始決議日期不詳，此為追認重建日期）
> **作者**：原始作者不詳（本檔由後續 session 追認重建）

---

## Context

專案採 AI agent 主導開發（多 sub-agent、跨 session 接力）。此模式下若無機械化防護與結構化交接機制，容易出現「閉環」風險：agent 在 master 直接 commit、危險指令未攔截、session 間 context 遺失導致重工。原始討論紀錄佚失，僅能從 `.claude/hooks/`、`.claude/protocols/`、`docs/plans/PLANS.md` 等既有引用點反推部分決策內容。

---

## Decision

採納「Harness Engineering」制度：以 hook + protocol + 文件三層機制，為 AI 主導開發建立可機械驗證的護欄與跨 session 交接規範。其中可反推確認的決策點：

- **D5 — Guard hook 為唯一 enforce 層**：`pre-tool-use-guard.py` 是 Phase D 中唯一以 enforce mode 阻擋（exit 2）工具呼叫的 hook，範圍限於 INV-GIT-002/003/004（master 直接 commit、force push、reset --hard origin/master）及讀取 `.env`/secrets、`curl|sh`、`rm -rf` 等高確定性危險操作。其餘 hook（如 `post-edit-lint.py`）僅作 sentinel，記錄與警告、不攔截。
- **D7 — Handoff markers**：所有 sub-agent 的 final response 必須以 `[HANDOFF: <next>]` / `[VERIFY_FAILED: <reason>]` / `[HUMAN_ATTENTION_REQUIRED: <reason>]` 三者之一結尾，作為 agent 間與人機交接的結構化訊號。
- **D8 — ExecPlan `active/` 入版控**：`docs/plans/active/` 下的 ExecPlan 實例檔案需 commit 進版控（而非 gitignore），使其作為跨 session 的「結構化交接物件」，供下一個 agent/session 讀取恢復 context。

D1–D4、D6：原始決議紀錄佚失，本檔為追認重建，現有引用未指向這些編號，具體內容無法考證，故不在此臆測填補。

---

## Rationale

（原始討論之替代方案評估紀錄佚失，本檔為追認重建，無法還原。）

---

## Consequences

### 正面影響
- 危險 git 操作有機械化攔截，降低 AI 誤操作風險
- Sub-agent 交接有固定格式，減少人工排查交接狀態的成本
- ExecPlan 入版控使跨 session 恢復 context 有單一可信來源

### 負面影響 / 風險
- 本 ADR 為事後追認重建，D1–D4、D6 決策內容不可考，若日後需引用可能需重新決議並另立 ADR 補充

---

## Implementation Notes

實作細節分散於 `.claude/hooks/pre-tool-use-guard.py`、`.claude/hooks/post-edit-lint.py`、`.claude/protocols/handoff-protocol.md`、`docs/plans/PLANS.md`；本檔僅補回決策紀錄本身。

---

## 引用此 ADR 的位置

- `docs/architecture/invariants.md`（INV-GIT-003 SOURCE）
- `docs/plans/PLANS.md`（§0 依據，D8）
- `.claude/protocols/execplan-lifecycle.md`（依據，D8）
- `.claude/protocols/handoff-protocol.md`（依據，D7）
- `.claude/hooks/_lib.py`、`pre-tool-use-guard.py`、`post-edit-lint.py`（docstring，D5）
