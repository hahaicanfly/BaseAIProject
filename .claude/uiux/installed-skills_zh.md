# UI/UX Skills 狀態清單

> 本專案使用 Claude Code 內建的 Skills 系統（`.claude/skills/`）。
> 以下是已預設的 UI/UX 相關 Skills，使用前請確認是否需要填充實際實作。

---

## 已預設的 UI/UX 相關 Skills

### 1. ui-ux-pro-max

| 項目 | 值 |
|------|-----|
| **名稱** | ui-ux-pro-max |
| **來源** | 專案內建 (`.claude/skills/ui-ux-pro-max/`) |
| **安裝狀態** | ⚠️ Stub（需填充實作） |
| **觸發指令** | `/ui-ux-pro-max` |

**用途**：生成完整設計系統（色彩調色盤、字體配對、UI 風格）。

---

### 2. frontend-design

| 項目 | 值 |
|------|-----|
| **名稱** | frontend-design |
| **來源** | 專案內建 (`.claude/skills/frontend-design/`) |
| **安裝狀態** | ⚠️ Stub（需填充實作） |
| **觸發指令** | `/frontend-design` |

**用途**：以設計哲學（Typography, Color, Motion）為核心，產生高品質 UI 元件。

---

## 已預設的 UI/UX 相關 Agents

### 1. ui-ux-designer

| 項目 | 值 |
|------|-----|
| **名稱** | ui-ux-designer |
| **來源** | 專案內建 (`.claude/agents/ui-ux-designer.md`) |
| **模型** | opus |
| **觸發詞** | UI、UX、設計、界面、畫面、流程 |

### 2. uiux-agent

| 項目 | 值 |
|------|-----|
| **名稱** | uiux-agent |
| **來源** | 專案內建 (`.claude/agents/uiux-agent.md`) |
| **模型** | sonnet |
| **觸發詞** | 草圖、wireframe、評審、三階段流程 |

---

## 如何使用

### 方法 1：直接呼叫 Skill
```
/ui-ux-pro-max
/frontend-design
```

### 方法 2：使用 Agent（在對話中）
提及觸發詞即可自動啟用：
- "幫我設計 UI"
- "這個畫面的 UX 流程..."
- "界面設計建議"

---

*最後更新：2026-05-28*
