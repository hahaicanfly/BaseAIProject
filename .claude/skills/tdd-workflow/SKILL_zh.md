---
name: tdd-workflow
description: 執行 Red → Green → Refactor 的測試驅動開發流程，用於核心業務邏輯與高可靠性需求；當使用者要 TDD 開發或提及「測試驅動」「先寫測試」時觸發。
---

# TDD Workflow Skill

執行測試驅動開發（Test-Driven Development）流程：Red → Green → Refactor。

## 使用方式

```
/tdd-workflow [功能描述]
```

## TDD 循環

```
┌─────────────────────────────────────┐
│                                     │
│  1. RED: 寫失敗的測試               │
│     ↓                               │
│  2. GREEN: 寫最少代碼讓測試通過     │
│     ↓                               │
│  3. REFACTOR: 改善代碼品質          │
│     ↓                               │
│  回到 1 (下一個測試案例)            │
│                                     │
└─────────────────────────────────────┘
```

## 執行步驟

### Phase 1: 定義介面

```
// 先定義 public API，不寫實作
// 範例 (偽代碼)
interface Parser {
    parse(input): Result
}
```

### Phase 2: RED - 寫測試

```
// 寫一個會失敗的測試
test("parse should return result when valid input") {
    // Arrange
    parser = createParser()
    input = createTestInput()

    // Act
    result = parser.parse(input)

    // Assert
    assertSuccess(result)
}
```

執行測試，確認**失敗**（編譯錯誤或斷言失敗）

### Phase 3: GREEN - 最小實作

```
// 寫最少的代碼讓測試通過
class ParserImpl implements Parser {
    parse(input): Result {
        return Result.success(minimalData)
    }
}
```

執行測試，確認**通過**

### Phase 4: REFACTOR - 改善

```
// 改善實作，保持測試通過
class ParserImpl implements Parser {
    constructor(dependency) { ... }

    parse(input): Result {
        // 改善實作邏輯
        processed = dependency.process(input)
        return Result.success(processed)
    }
}
```

執行測試，確認**仍然通過**

### Phase 5: 下一個測試案例

重複 Phase 2-4，直到功能完成。

## TDD 規範

- Test 命名：`should_[behavior]_when_[condition]`
- 每個 test 只驗一個行為
- 包含 positive + negative cases
- 使用 test doubles（fake/mock/stub）隔離外部依賴

## 測試案例規劃

```markdown
## [功能] 測試案例

### Happy Path
- [ ] TC001: 有效輸入返回正確結果
- [ ] TC002: 多種格式正確處理

### Edge Cases
- [ ] TC101: 空輸入返回空結果
- [ ] TC102: 邊界值正確處理

### Error Cases
- [ ] TC201: 無效輸入拋出適當異常
- [ ] TC202: 外部錯誤有適當處理
```

## 覆蓋率目標

- 行覆蓋率：>80%
- 分支覆蓋率：>70%
- 核心邏輯：100%

## 測試指令

具體指令依專案 `CLAUDE.md` Quick Commands 決定。常見慣例供參考：

```bash
# JavaScript/TypeScript
npm test
npm run test:coverage

# Python
pytest
pytest --cov

# Go
go test ./...
go test -cover ./...
```

其餘語言／建構系統依專案 Quick Commands 類推。

## 輸出範本

```markdown
## TDD 進度：[功能名稱]

### 當前狀態
- Phase: [RED/GREEN/REFACTOR]
- 測試案例：[X/Y] 完成

### 測試結果
- 通過：X
- 失敗：X
- 覆蓋率：X%

### 下一步
[下一個測試案例或重構目標]
```

## 參考文件

開始前先檢查專案是否有：
- CLAUDE.md（專案規範，包含測試指令）
- 測試目錄結構
- 測試配置檔

## 驗證項目

- **產出形式**：RED → GREEN → REFACTOR commit 序列（commit message 對應 type）。
- **機械檢查**：每個 RED commit 跑專案測試指令（CLAUDE.md Quick Commands）必須**失敗**；GREEN commit 必須通過；REFACTOR commit 必須**保持通過**。
- **ExecPlan 整合**：§6 Progress Log 每個 commit append 一行（含 hash + 階段標記）。
- **參考 invariants**：`docs/architecture/invariants.md` INV-TEST-* 區段（依專案實際填入的條目為準；模板現況僅有一則範例條目）。

## 參考

- `.claude/agents/qa-engineer.md`
- `docs/architecture/invariants.md` INV-TEST-*
