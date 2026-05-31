# Skill: spectra-amplifier

> **用途**：接收薄的 spec（需求描述、PRD 草稿、feature 想法），輸出強化版 spec——每個需求有 acceptance criteria，每個 AC 對應一個可驗證條目。
> **觸發**：`/spectra-amplifier [spec 描述 / 文件路徑]`
> **理論基礎**：Spectra（龍哥 SDD 格式）× Speckit（testability）× Teddy 五層規範法

---

## 為什麼需要 Spectra-Amplifier？

問題：AI 寫的 spec 通常「薄」——描述功能，但不描述如何驗證功能是否正確。
這導致：
- ExecPlan §5 Verification Strategy 寫不出具體的 Negative test cases
- PR review 無法判斷「這個改動是否真的滿足了需求」
- ERRORS.md 的 lesson 無法回溯到「是哪個 spec 設計缺陷導致的 bug」

強 spec 的三個特性：
1. **Traceable**（可追溯）：每個需求能追到設計，設計能追到實作，實作能追到測試
2. **Testable**（可測試）：每個需求都有具體的 pass/fail criteria
3. **Bounded**（有邊界）：明確說明不做什麼，避免 scope creep

---

## 五層放大框架（Teddy × Speckit × Spectra）

```
Layer 5: Verification      ← 如何知道做對了？（測試 / hook / INV-*）
    ↑
Layer 4: Implementation    ← 怎麼做？（技術選型、API、data model）
    ↑
Layer 3: Design            ← 什麼架構？（模組邊界、介面、流程圖）
    ↑
Layer 2: Requirements      ← 需要什麼？（功能需求 + 非功能需求）
    ↑
Layer 1: Context           ← 為什麼要做？（問題陳述、stakeholder、成功指標）
```

每一層都要能**向下問「如何？」、向上問「為什麼？」**——若無法回答，說明 spec 在此層有缺口。

---

## 執行步驟

### Step 1：解析輸入 spec

讀入使用者提供的 spec（文字描述或文件）。
識別目前覆蓋了哪幾層（L1–L5），哪幾層缺失或薄弱。

### Step 2：Layer-by-Layer 放大

#### L1 — Context 放大

補全：
```
問題陳述：[用戶面對什麼問題？]
目標用戶：[誰？]
成功指標：[做完後如何量測成功？數字化]
Out of Scope：[明確說明不做什麼]
```

#### L2 — Requirements 放大

對每個功能需求，補全：
```
REQ-NNN：[需求描述]
  優先度：P0 / P1 / P2
  功能需求（FR）：...
  非功能需求（NFR）：[效能/可靠性/安全性要求]
  Acceptance Criteria：
    - AC-1：[Given ... When ... Then ...]
    - AC-2：[Given ... When ... Then ...]
  Edge Cases：
    - EC-1：[邊界情況描述]
```

#### L3 — Design 放大

補全：
```
架構決策：[選擇了哪個方案，為何不選其他]
模組邊界：[涉及哪些 domains.md 中的模組]
API 介面草稿：[endpoint / function signature]
資料模型變更：[若有 schema 變更，列出欄位]
流程圖（Mermaid）：
  sequenceDiagram 或 flowchart LR
  [描述主流程]
```

#### L4 — Implementation 放大

補全：
```
技術選型：[框架/庫/工具]
關鍵實作注意：
  - [注意 1]
  - [注意 2]
ExecPlan 引用：
  docs/plans/active/F-NNN-slug.md §3 Constraints 需引用：
    - INV-[NS]-[NNN]（安全相關）
    - domains.md [變更類型行]
```

#### L5 — Verification 放大（最重要）

對每個 AC，產生對應驗證：
```
AC-1 → 測試類型：[unit / integration / e2e / manual]
       測試指令：[具體命令]
       Golden Path：[正常流程驗證步驟]
       Negative Test：[故意觸發失敗的步驟]
       對應 INV-*：[若有]
       對應 ExecPlan §5 驗證項：[複製到 ExecPlan]
```

### Step 3：輸出放大後的 spec

產出格式：

```markdown
# Spec: [功能名稱]

## L1 Context
[放大後的問題陳述、成功指標、Out of Scope]

## L2 Requirements
[REQ-NNN 列表，含 AC + EC]

## L3 Design
[架構決策、介面草稿、Mermaid 流程圖]

## L4 Implementation Notes
[技術選型、實作注意、INV-* 引用]

## L5 Verification Matrix
| AC | 測試類型 | 指令 | Golden Path | Negative |
|----|---------|------|------------|---------|
| AC-1 | ... | ... | ... | ... |

## ExecPlan §5 草稿（可直接貼入）
[自動生成 §5 Verification Strategy]
```

### Step 4：缺口提示

若輸入 spec 在某層嚴重缺失，輸出：
```
[SPEC_GAP: L3-Design] 缺少模組邊界定義。
在實作前，建議先執行 /feature-pipeline 來補齊架構設計。
```

---

## 與 ExecPlan 的接口

放大後的 spec 可直接用於：
- ExecPlan §1 Goal（從 L1 Context 萃取一句話）
- ExecPlan §3 Constraints（從 L4 的 INV-* 引用）
- ExecPlan §5 Verification Strategy（從 L5 驗證矩陣）

建議工作流：
```
/spectra-amplifier [功能描述]
    ↓
確認 L5 驗證矩陣
    ↓
開 ExecPlan，複製 §5 內容
    ↓
進入 feature-pipeline 或直接開發
```

---

## Speckit 品質評分（輸出附帶）

每次放大後，輸出 Speckit 品質分數：

| 維度 | 滿分 | 說明 |
|------|------|------|
| Traceability（L1-L5 可追溯） | 20 | 每層都能向上/向下回答 |
| Testability（AC 可測試） | 30 | AC 有具體 Given/When/Then |
| Boundedness（Out of Scope 明確） | 20 | 有明確不做的清單 |
| Completeness（無遺漏的 Edge Cases） | 30 | EC 覆蓋主要邊界 |

分數 < 70 → 建議在開始實作前補強。
