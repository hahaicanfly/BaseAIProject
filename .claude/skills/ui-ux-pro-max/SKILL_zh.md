---
name: ui-ux-pro-max
description: 產出完整設計系統，涵蓋色彩調色盤、字體配對、UI 風格與 UX 準則，支援多種前端技術棧；當使用者要規劃、設計或檢視 UI/UX 時觸發。
---

# UI/UX Pro Max - Design Intelligence

Comprehensive design guide for web and mobile applications. 內含 50+ UI 風格、97 組色彩調色盤、57 組字體配對、99 條 UX 準則、25 種圖表類型，涵蓋 9+ 種前端技術棧。以 BM25 搜尋引擎查詢，依優先級回傳建議。

## When to Apply

在以下情境參考本 skill：
- 設計新的 UI 元件或頁面
- 選擇色彩調色盤與字體
- 審查代碼中的 UX 問題
- 建立 landing page 或 dashboard
- 落實無障礙（accessibility）需求

## 參考檔 — 只讀當前任務需要的那一份，不必三份全載

| 檔案 | 什麼時候讀 |
|------|-----------|
| `references/search-cli_zh.md` | 要操作 `search.py`：前置需求、四步驟流程、domain 與 stack 對照表、輸出格式、完整範例 |
| `references/ux-rules_zh.md` | 要審查或稽核 UI — 8 大規則類別依優先序排列，Accessibility 最優先 |
| `references/polish-checklist_zh.md` | 交付 UI 代碼之前 — 精修規則與交付前檢查表 |

## 唯一不可略過的步驟

永遠先產生設計系統，其他搜尋都只是補充。

第一步是從使用者請求中萃取：**產品類型**（SaaS、電商、作品集、dashboard、landing page…）、**風格關鍵字**（minimal、playful、elegant、dark mode…）、**產業別**、**技術棧** — 未指定時一律預設 `html-tailwind`。萃取出來的內容就是查詢字串：

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

此指令會並行搜尋 5 個 domain（product, style, color, landing, typography），套用 `ui-reasoning.csv` 的推理規則，回傳完整設計系統（pattern、style、colors、typography、effects）並附上應避免的 anti-patterns。加上 `--persist` 會寫出 `design-system/MASTER.md` 與各頁面的 override 檔。

補充性的 domain 搜尋（`--domain style|chart|ux|typography|landing`）、stack 準則（`--stack`）、MASTER/overrides 分層查找、輸出格式：見 `references/search-cli_zh.md`。

## 三條最容易被漏掉的鐵則

其餘規則都在參考檔裡；這三條是實務上最常掉的：

- Accessibility 與觸控目標尺寸屬 CRITICAL 優先級 — 不得為了視覺效果讓步
- UI 圖示一律用 SVG（Heroicons、Lucide、Simple Icons），絕不用 emoji
- 淺色與深色模式交付前都要實測

## 驗證項目

- **產出形式**：完整設計系統規範（含 palette / typography / spacing / component samples）。
- **整合 uiux-agent**：作為 Phase 1 草圖的設計依據，Phase 2 評審的標準（見 `.claude/agents/uiux-agent.md`）。
- **ExecPlan 整合**：UI 類 ExecPlan 的 Context 區塊引用本 spec 對應段落（格式見 `.claude/protocols/execplan-lifecycle.md`）。
- **與既有設計系統對齊**：若專案已有設計系統文件（如 `agent_docs/TECHNICAL-REFERENCE.md` 或專案自訂 design-system 文件），輸出不得與其衝突；沒有既有文件時，本次輸出即為起點。
- **交接 marker**：spec 完成後 `[HANDOFF: uiux-agent]` 進入三階段流程（`.claude/uiux/WORKFLOW.md`）。
