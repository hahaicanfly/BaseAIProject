# 代碼規範

> **角色**：本檔定義專案的代碼風格與命名規範。
> **填充指示**：將 `{{填入語言/框架}}` 區段替換為專案實際使用的技術棧。
> **使用對象**：tech-lead agent、code-reviewer agent、開發者。

---

## 命名規範

> TODO：根據你的語言填入實際命名慣例。

| 概念 | 慣例 | 範例 |
|------|------|------|
| 類別 / 介面 | PascalCase | `UserService`, `OrderRepository` |
| 函數 / 方法 | camelCase 或 snake_case（依語言） | `parseOrder()`, `parse_order()` |
| 常數 | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 私有屬性 | `_` 前綴（依語言慣例） | `_internalState` |
| 檔案 | 依語言慣例 | `UserService.ts` / `user_service.py` |

---

## 目錄結構

> TODO：填入專案實際目錄結構。

```
src/
├── domain/          # 領域層（核心業務邏輯）
│   ├── models/      # 資料模型
│   └── repositories/# Repository 介面
├── data/            # 資料層
│   ├── remote/      # 遠端資料源（API client）
│   └── local/       # 本地資料源（DB / cache）
├── ui/              # 表現層（Web / App UI）
│   ├── pages/       # 頁面元件
│   └── components/  # 可複用 UI 元件
└── utils/           # 工具函式
```

---

## 代碼風格

### 函數設計原則

- **單一職責**：一個函數只做一件事，≤ 20 行為宜
- **純函數優先**：盡量無副作用，易測試
- **明確回傳型別**：不依賴隱式推斷

```
// ✅ 短小、單一職責
function parseOrder(raw: string): Order { ... }

// ❌ 過長、職責不清
function doEverything(...): any { ... 200 lines ... }
```

### 錯誤處理

- 使用明確的錯誤型別（Result / Either / sealed class）
- 不用裸 `try/catch` 吞掉錯誤
- 錯誤訊息要有診斷性（包含 context，不只是 "error"）

### 依賴注入

- 建構函數注入（不在函數內 new 具體實作）
- 依賴介面而非具體類別
- 易於測試替換

---

## 測試規範

### 測試命名

```
describe("OrderParser") {
  it("should return parsed result when input is valid")
  it("should throw when input is malformed")
}
```

### 測試結構（Given / When / Then）

```
// Given（Arrange）
const input = createTestInput()

// When（Act）
const result = parser.parse(input)

// Then（Assert）
expect(result).toEqual(expected)
```

### 測試範圍

- 單元測試：純函數、業務邏輯
- 整合測試：API 層、資料庫操作（不 mock DB）
- E2E（按需）：關鍵用戶流程

---

## Git Commit 規範

### 格式

```
<type>(<scope>): <subject>

<body>（可選）

<footer>（可選：Closes #NNN）
```

### Type

| type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修復 |
| `docs` | 文檔更新 |
| `style` | 格式調整（不影響邏輯） |
| `refactor` | 重構（不新增功能也不修 bug） |
| `test` | 測試 |
| `chore` | 建構 / 工具 / 依賴升級 |

### 範例

```
feat(auth): add OAuth2 login flow

- Implement token exchange endpoint
- Add refresh token rotation
- Add unit tests for token validation

Closes #42
```

---

## {{填入語言/框架}} 特定規範

> TODO：填入你的技術棧特定規範。
>
> 範例：
> - **React**: hooks 命名 `use*`、禁止直接操作 DOM
> - **Python**: PEP 8、type hints 必填、docstring 格式
> - **Kotlin**: coroutines 而非 threads、Flow 用於串流資料
> - **Swift**: `@MainActor` 處理 UI 更新、Combine / async-await

---

## 禁止模式（Anti-patterns）

- 魔法數字（用命名常數代替 `42`、`3600`）
- 深層巢狀（超過 3 層 if/for 考慮 early return 或函數提取）
- 縮寫命名（`usr`, `btn`, `tmp`）
- 不必要的 comment（代碼能表達的不用 comment）
- 空 catch 塊（至少 log 錯誤）
