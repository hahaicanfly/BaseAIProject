# F. Harness 維護協議（Maintenance Protocol）

> 讀者：長期運作的弱模型。定義你怎麼**安全地**更新 harness 自身的檔案。
> 原則：教訓可以隨時 append；規則要謹慎改；防線（hooks/invariants）動之前必問人。

## 1. 檔案權限分級

| 級別 | 範圍 | 規則 |
|------|------|------|
| **綠：可自行改** | `docs/learnings/ERRORS.md`（append）、`docs/harness/LETTER-TO-FUTURE-SESSIONS.md` **僅 §三交接清單的條目增刪**（其他章節屬黃級）、`state/`、`docs/plans/active/` 自己的 ExecPlan、`SESSION-HANDOFF.md` | 直接改，遵守 §3 格式 |
| **黃：改前備份＋改後驗證** | `agent_docs/*.md`、`.claude/templates/`、`.claude/agents/*.md`、`.claude/skills/`、`docs/INDEX.md`、README | 先 `cp X X.bak` → 改 → 派 fresh-context agent read-back 驗證（模板見 delegation-templates.md §6） |
| **紅：動之前必須問使用者** | `CLAUDE.md`、`.claude/rules/*.md`、`.claude/protocols/*.md`、`.claude/hooks/*.py`、`.claude/settings.json`、`docs/architecture/invariants.md` | 提出 diff 與理由，取得同意才改；改 hooks 後必做 §4 煙霧測試 |

- 判斷歧義時往嚴格的一級靠。刪除任何檔案一律視為紅級。
- 紅級的例外：使用者在對話中明確指示的修改，視為已同意，但仍要備份與驗證。

## 2. 為什麼分級（讓你能自行做邊界判斷）

- 綠級是**事實記錄**：寫錯了頂多多一條 noise，可事後清理。
- 黃級是**行為指引**：寫錯會讓未來的 agent 做錯事，但範圍侷限、可回滾。
- 紅級是**常駐規則與物理防線**：每個 session 自動載入或自動執行，寫錯會系統性污染所有後續工作，且弱模型自己未必能察覺。

## 3. 踩坑教訓寫回（唯一寫入點：`docs/learnings/ERRORS.md`）

**何時寫**：同一錯誤第 2 次出現、或一次錯誤浪費超過 10 分鐘、或發現文件與現實不符。

**格式**（append 到檔尾的 Pending Review 節）：

```markdown
### [YYYY-MM-DD] [一句話標題]
- 情境：做什麼任務時遇到
- 錯誤：實際發生什麼（附 檔案:行號 或錯誤訊息關鍵行）
- 教訓：下次怎麼避免（一條可執行的指令或檢查）
- 建議去向：留在 ERRORS / 升級 invariants / 改某檔（路徑）
```

**去重**：append 前先搜尋 ERRORS.md 是否已有同主題條目；有 → 在舊條目加一行 `再犯：YYYY-MM-DD`，不新開條目。再犯 2 次以上的條目 = 升級候選。

**三段升級管線**（源自 Menu-Android 實戰）：
1. 模型 append 進 Pending Review（自動/隨手）
2. 人類週審：promote 到正式分類或刪除
3. 可機械化的（能寫成 regex/檢查）→ 提案寫進 `invariants.md` 與 guard hook（紅級，需同意）

## 4. 變更安全程序

**改任何黃/紅級檔案的固定流程**：
1. 確保有還原點（二擇一）：(a) 該檔已被 commit 且 working tree 乾淨 → git 即備份，免建 .bak；(b) 否則 `cp 檔案 檔案.bak`（同目錄；已有 .bak 則用 `檔案.bak2`，不覆蓋舊備份）。`*.bak` 已列入 .gitignore，驗收通過後可刪
2. 進行修改
3. 驗證：
   - 文件 → fresh-context read-back（驗收條件至少含：引用路徑全部存在、無 {{佔位符}} 意外殘留、與正典層級無矛盾）
   - hooks → **煙霧測試**，block 與 pass 兩情境都要測（教訓來源：guard 曾雙重失效，見 DIAGNOSIS.md §三.1）。在 **repo 根目錄**執行（h 是相對路徑）：
     ```bash
     # 範例：測 pre-tool-use-guard（用分支無關的 static pattern，任何分支上期望值都一樣）
     python3 -c "import json,subprocess; h='.claude/hooks/pre-tool-use-guard.py'; \
     print(subprocess.run([h],input=json.dumps({'tool_name':'Bash','tool_input':{'command':'ca'+'t .e'+'nv'}}),capture_output=True,text=True).returncode)"
     # 期望：2（block，READ_DOTENV）。把 command 換成 'ls -la' 期望：0（pass）。新 hook 檔記得 chmod +x
     # 注意：不要用 git commit 當測資 —— 它只在 master/main 上 block，在 feat 分支會回 0，你會誤判 hook 壞掉
     ```
4. 驗證失敗 → 還原備份，把失敗記進 ERRORS.md

**引用即驗證**：在任何 harness 檔寫下路徑/工具名/skill 名之前，先確認它存在（`ls` 或 Glob）。發現既有死引用：綠黃級直接修，紅級記入 ERRORS.md 等人審。

## 5. 精簡觸發條件（防止文件無限膨脹）

| 檔案 | 觸發線 | 動作 |
|------|--------|------|
| ERRORS.md | > 300 行或 Pending Review > 20 條 | 提醒使用者週審；同類條目合併成一條抽象教訓（保留原始日期清單） |
| CLAUDE.md | > 100 行 | 超出部分抽到引用檔，CLAUDE.md 留一行路由 |
| `.claude/rules/*` 總量 | 全部 rules 合計 > 600 行 | 提案把最少用的規則降為非常駐（移到 agent_docs/ 或刪 `always: true`），紅級需同意 |
| LETTER-TO-FUTURE-SESSIONS.md 交接清單 | 完成項 | 完成的項目移除，不留「已完成」墓碑 |

**精簡的方法**是概念抽象化：5 條同類具體教訓 → 1 條規則 + 1 個代表範例；禁止用「刪掉舊的」代替「合併同類」。

## 6. 本協議自身

本檔屬紅級。發現本協議有錯或不合用：記入 ERRORS.md 並在回報中提出，不要自行修改。
