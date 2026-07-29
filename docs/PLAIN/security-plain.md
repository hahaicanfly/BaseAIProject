# 安全規則白話版(一頁)

> 這是 `.claude/rules/security.md` 的白話對照,寫給人看的。如有出入,以該檔原文為準。
> 這份存在的理由:security.md 是唯一每個 tier 都會載入的規則檔,常駐成本由所有 session 分攤,所以解釋性的文字搬到這裡,規則本身只留規則(F-003 DEC-6)。

## 一句話

密碼、金鑰這類機密資訊絕對不能寫死在程式碼或紀錄裡,也不能被提交進版本控制。

## 三件絕對禁止的事

**1. 把機密寫死在程式碼裡。** `apiKey = "sk-xxxxx"` 這種寫法,等於把鑰匙刻在門上。正確做法是從環境變數讀:`process.env.API_KEY`、`os.getenv("API_KEY")`、`BuildConfig.API_KEY`。

**2. 把機密印進 log。** `log("Request with key: " + apiKey)` 會讓金鑰出現在每一份日誌、每一次錯誤回報、每一個看得到日誌的人眼前。log 只記「發生了什麼」,不記「用了什麼憑證」。

**3. 把機密檔案 commit 進 git。** 一旦進了版本歷史,刪掉也還在。這類檔案包含:`.env` 系列、`local.properties`、`*.keystore`、`*.jks`、`*.pem`、`*.key`、`*.p12`、檔名含 `secret` 或 `credential` 的、`serviceAccountKey.json`,以及含有機密的 `google-services.json`。

## 兩個容易搞混的詞

- **允許清單(allowlist)**:只放行清單內許可的東西,其餘一律擋下。預設最安全 —— 你沒想到的情況會被擋,而不是被放行。
- **封鎖清單(denylist)**:只擋清單內禁止的東西,清單外一律放行。容易漏掉沒想到的情況。

規則要求**優先用允許清單**。理由就是上面那句:你想不到的東西,允許清單會擋,封鎖清單會放。

## 發現機密外洩時的處置順序

1. **立刻停手** —— 不要繼續當前操作
2. **告知風險** —— 講清楚什麼可能外洩、影響範圍多大
3. **提出修法**
4. **不要做任何可能造成外洩的 git 操作** —— 包括「先 commit 起來再說」

## 什麼時候會主動檢查

涉及 API 呼叫的程式碼、改設定檔、加新依賴、git commit 之前、處理使用者輸入的程式碼。

## 相關

- 規則原文:`.claude/rules/security.md`
- 硬性防線(電腦強制執行,擋得住講不贏):`docs/architecture/invariants.md` 的 `INV-SEC-*`
- 非技術使用者總覽:[`START-HERE_zh.md`](START-HERE_zh.md)
