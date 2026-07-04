---
name: skill-creator-plus
description: 引導完整的 skill 建立流程——意圖捕捉、重疊檢查、撰寫、機械驗證、觸發測試到 registry 登記，含 eval 迭代方法。當使用者要建立新 skill、封裝重複流程、改寫或優化既有 skill 的觸發準確度、提到「做一個 skill」「skill 沒被觸發」「封裝這個流程」時觸發。取代基礎版 skill-creator。
---

# Skill: skill-creator-plus

> 方法論基底：Anthropic 官方 skill-creator（github.com/anthropics/skills，2026-07 版）＋ 本專案 harness 制度。
> 詳版 eval 迭代流程在 `references/eval-loop.md`（需要時再讀，不用先讀）。

## Step 0：先判斷該不該做 skill

Skill 是「觸發式載入的流程知識」。以下情況**不要**做 skill，用對應機制：

| 情境 | 正確機制 | 為什麼 |
|------|---------|--------|
| 每個 session 都該遵守的規則 | `.claude/rules/`（常駐） | skill 要被觸發才載入，常駐規則不能賭觸發 |
| 需要獨立 context 執行的角色 | `.claude/agents/` | skill 不帶自己的 context 與工具白名單 |
| 只是固定文字片段 | `.claude/templates/` | 不需要執行步驟的內容做成 skill 是浪費 |
| 操作在 session 中出現 < 3 次 | 先不封裝 | 官方原則：skill 會被用上百萬次，勿為單次需求 overfit |

## Step 1：意圖捕捉（4 問，問完再動手）

1. 這個 skill **做什麼**？（一句話）
2. **什麼時候**該被觸發？（列出使用者會說的原話，含口語與 typo）
3. **輸出**長什麼樣？（格式、落檔位置）
4. 輸出是**客觀可驗證**的嗎？（是 → 之後建 eval；主觀輸出如文案風格 → 跳過量化 eval，用人工比對）

## Step 2：重疊與觸發互斥檢查

寫任何內容前先跑：

```bash
grep -l "關鍵觸發詞" .claude/skills/*/SKILL.md   # 誰已經搶了這些詞
```

- 與既有 skill 觸發詞重疊，二擇一（判準）：新需求是既有 skill 用途的子集或變體 → **擴充既有 skill**，不另開新檔；確實是不同用途只是共用詞彙 → 兩邊 description 都加**互斥限定詞**（例：code-review「單一 PR 標準審查」vs multi-agent-review「高風險三專家並行」）。
- 教訓來源：本專案曾有三個 review skill 互搶「審查 PR」，路由隨機選錯——2026-07-04 第三輪已用互斥限定詞消解；同型病灶（同一事實多檔並存→隨機採信）見 ERRORS.md 的單一正典源條目。

## Step 3：結構與撰寫

**目錄結構**（用不到的層省略）：

```
.claude/skills/<name>/
├── SKILL.md          # 必要。body 理想 <150 行，硬上限 500 行
├── references/       # 長內容抽出來按需載入（>300 行的檔案要附目錄）
├── scripts/          # 確定性操作寫成可執行腳本（跑而不載入，零 context 成本）
└── assets/           # 輸出用模板/字型/圖示
```

**Progressive disclosure 三層**（官方數字）：frontmatter 恆在 context（~100 字）→ SKILL.md body 觸發時載入 → references 與 scripts 按需。所以：when-to-use 資訊**全部**寫在 description，一條都不放 body。

**frontmatter 硬規格**（`scripts/validate_skill.py` 會驗）：
- `name`：kebab-case ≤64 字元，**必須等於目錄名**（不等於就不會被觸發——本專案踩過）
- `description`：≤1024 字元、禁止角括號 `<>`；寫法見下
- 允許欄位僅：name, description, license, allowed-tools, metadata, compatibility

**description 公式**（Claude 傾向 undertrigger，要寫得 pushy——「夠 pushy」的可觀察判準：Step 4 的 should-trigger 測試句全數命中）：

```
[做什麼，含關鍵能力列舉]；當[具體情境1]、[情境2]、提到「[原話觸發詞×3-5]」時觸發。[與相鄰 skill 的互斥限定詞]。
```

**body 寫作規則**：
- 祈使句直接下指令；先寫草稿，再以「第一次讀的弱模型」眼光重讀改寫
- 解釋 **why** 而不是堆大寫 MUST——發現自己在寫 ALWAYS/NEVER 全大寫，是內容缺乏理由的警訊（官方 yellow flag）
- 給 Input/Output 配對範例，勝過三段抽象描述
- 引用即驗證：body 裡寫下的每個路徑、工具名、agent 名，寫之前先 `ls` 確認存在（本專案曾有協議檔 5 條引用全屬虛構）
- 不複製正典內容：模型分派看 model-dispatch.md、review 格式看 review-protocol.md——skill 裡只准引用，不准另抄一份

## Step 4：機械驗證 + 觸發測試（驗證不自驗）

1. 跑 `python3 .claude/skills/skill-creator-plus/scripts/validate_skill.py .claude/skills/<name>`，全綠才繼續。
2. 派一個 **fresh-context subagent**（照 `.claude/templates/delegation-templates.md` §6），只給它「使用者會說的觸發句」，驗收條件：它回報會選用哪個 skill 及理由。病因鑑別：should-trigger 句沒中 → description 缺原話觸發詞，加詞；should-not 句誤中 → 缺互斥限定詞，加限定。改完重測。
3. 若輸出客觀可驗證：跑一輪最小 eval——同 turn 平行派兩個 subagent（一個給 skill 全文、一個不給）做同一任務，對照輸出。詳細方法（assertions、near-miss 負例、停止條件）見 `references/eval-loop.md`。

## Step 5：落地登記

1. 在 `agent_docs/AI-TEAM-REGISTRY.md` 登記（該檔由目錄重生成，照其檔頭說明做，不要手改單格）
2. skill 檔案屬黃級（`.claude/protocols/harness-maintenance.md` §1）：確保有 git 還原點再改既有 skill
3. 一功能一 commit；建立過程踩到的坑 append 進 `docs/learnings/ERRORS.md`

## 反模式（每一條都是本專案真實踩過的坑）

- **stub 不標註**：內容未實作卻有完整 description → description 尾端加「（stub，尚無完整實作）」
- **name ≠ 目錄名** → 永遠不被觸發
- **description 只寫做什麼、不寫何時用** → undertrigger，形同不存在
- **body 塞 when-to-use** → 觸發前根本沒人讀得到 body
- **虛構引用**（宣稱被某檔引用/引用不存在的論文）→ 弱模型會信以為真並擴散
- **清理到非自建檔案**：eval 暫存檔只能刪自己本輪建立的；對其他任何檔案的破壞性指令一律禁止——完整黑名單以 `.claude/templates/delegation-templates.md` 通用規範為正典（誤刪事故見 ERRORS.md 2026-07-04）
