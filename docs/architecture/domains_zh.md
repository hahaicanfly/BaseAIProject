# {{PROJECT_NAME}} — Domain Architecture

> **角色**：本檔定義系統的領域邊界與變更影響評估表。
> **使用對象**：architect agent、code-reviewer agent、ExecPlan §3 Constraints 引用。

---

## 系統架構概覽

> TODO：填入你的專案架構描述

```
┌─────────────────────────────────────────────────┐
│                  {{PROJECT_NAME}}                 │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────┐    ┌──────────────────────────┐ │
│  │   Frontend   │    │        Backend           │ │
│  │              │◄───┤                          │ │
│  │  (Web / App) │    │  (API / Business Logic)  │ │
│  └──────────────┘    └──────────────────────────┘ │
│                                 │                  │
│                      ┌──────────┴──────────┐       │
│                      │     Data Layer      │       │
│                      │   (DB / Storage)    │       │
│                      └─────────────────────┘       │
└─────────────────────────────────────────────────┘
```

---

## 領域模組清單

> TODO：根據你的專案填入實際模組

| 模組 | 職責 | 依賴 | 影響範圍 |
|------|------|------|---------|
| `core/` | 核心業務邏輯 | — | 高（其他模組都依賴） |
| `api/` | API 層 | core | 中 |
| `ui/` | UI 元件 | api | 低（只影響前端） |
| `infra/` | 基礎設施（DB/Cache） | — | 高（改動需謹慎） |

---

## 變更影響評估表

ExecPlan §3 Constraints 必須引用此表的對應行。

| 變更類型 | 影響模組 | 需要的額外驗證 | 是否需 multi-agent review |
|---------|---------|--------------|--------------------------|
| API schema 變更 | api, ui, tests | 所有 client 同步更新 | 是 |
| 資料庫 schema 變更 | infra, core | migration + rollback plan | 是 |
| 新增 auth 機制 | api, core | security-reviewer | 是 |
| UI 元件新增 | ui | a11y + responsive check | 否 |
| 依賴升級 | all | 完整 build + test suite | 視情況 |
| Config 變更 | infra | 環境一致性驗證 | 否 |

---

## 跨模組依賴規則

1. **ui** 只能依賴 **api**（不可直接依賴 **core** 或 **infra**）
2. **api** 只能依賴 **core**（不可依賴 **ui**）
3. **core** 不依賴任何上層模組
4. **infra** 只被 **core** 依賴

> 填入你的實際依賴規則，違反的視為 INV-ARC-* 違規。

---

## 引用此檔的位置

- ExecPlan §3 Constraints（每個 ExecPlan 必須引用相關行）
- `.claude/agents/architect.md`
- `docs/plans/PLANS.md` §5
