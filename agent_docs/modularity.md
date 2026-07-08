---
name: modularity
description: 模組化與復用性規則（非常駐，按需引用）
---

# Modularity Rules

> 2026-07-07 自 `.claude/rules/` 降級為非常駐（代碼設計指引不符「首決策必需」常駐判準）。
> 引用入口：code-review skill 架構維度、tech-lead agent 檢查清單。

## 核心原則

**所有代碼設計都必須考慮跨專案復用性。**

## 模組劃分原則

### 共享模組
放入以下內容：
- 領域模型 (Domain Models)
- 業務邏輯 (Business Logic)
- 介面定義 (Interfaces)
- 工具類 (Utilities)
- 平台無關的抽象

### 平台/應用特定模組
放入以下內容：
- 平台 API 調用
- UI 實作
- 配置
- 進入點 (Entry Points)

## 設計準則

### 1. 依賴反轉
```
// ✅ 依賴抽象
class Parser(provider: Provider)  // 介面

// ❌ 依賴具體實作
class Parser(google: GoogleProvider)  // 具體類別
```

### 2. 介面優先
```
// 先定義介面
interface Provider {
    process(input): Result
}

// 再實作具體類別
class ProviderA implements Provider { ... }
class ProviderB implements Provider { ... }
```

### 3. 單一職責
```
// ✅ 職責單一
class ImageProcessor { ... }  // 只處理圖片
class TextParser { ... }      // 只解析文字

// ❌ 職責混雜
class ImageTextProcessor { ... }  // 做太多事
```

### 4. 開放封閉
- 對擴展開放：容易新增 Provider
- 對修改封閉：不需改動核心代碼

## 避免重複造輪子

在實作新功能前：
1. 檢查專案中是否已有類似功能
2. 搜尋共享模組
3. 考慮是否能擴展現有代碼
4. 搜尋是否有現成的開源解決方案

## 復用性檢查清單

新增代碼時問自己：
- [ ] 這個邏輯是否平台無關？→ 放共享模組
- [ ] 這個類別是否依賴具體實作？→ 抽出介面
- [ ] 這個功能是否可能被其他模組使用？→ 設計成可復用
- [ ] 是否有硬編碼的值？→ 抽成配置
- [ ] 測試容易嗎？→ 使用依賴注入

## 命名規範

### 共享模組常見命名
```
shared/
core/
common/
lib/
```

### 介面命名
```
Provider, Repository, Service, Handler
Parser, Processor, Validator, Formatter
```

### 實作命名
```
[具體名稱] + [介面名稱]
例如：GeminiProvider, LocalRepository
```
