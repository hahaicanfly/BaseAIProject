# {{PROJECT_NAME}} — Mechanically Verifiable Invariants

> **角色**：本檔列出可以**機械化驗證**的硬規則（與 `docs/learnings/ERRORS.md` 不同：ERRORS.md 是知識庫，本檔是 lint/test/grep 對應表）。
> **使用對象**：`.claude/hooks/post-edit-lint.py` / `code-reviewer` agent / 人類 reviewer。
> **驗證原則**：能寫成 lint rule、grep pattern、test assertion、build check 才放這裡；無法機械驗證的 lesson 留在 ERRORS.md。

---

## 規則格式

```
INV-<NS>-<NNN>  <一句話規則>
  CHECK    <可執行的 grep/lint/test 指令>
  HOOK     <哪個 hook 該攔截，或留 manual review>
  SOURCE   <對應 ERRORS.md 中 lesson 的日期>
```

命名空間（NS）建議：
- `COR` — Coroutines / Async / Concurrency
- `SEC` — Security / Auth / Secrets
- `API` — API / Serialization / Data Models
- `TEST` — Testing / Mocks / Fakes
- `GIT` — Git / Branch / PR
- `BLD` — Build / Dependencies
- `ARC` — Architecture / Refactoring
- `UI` — UI / Components
- `LOG` — Logging / Observability

---

## INV-GIT-* — Git / Branch / PR

### INV-GIT-001 — Commit 前必須 `git branch --show-current`

```
RULE     每次 commit / 啟動 subagent / PR merge 後必須確認 branch
CHECK    git symbolic-ref HEAD | grep -E 'refs/heads/(master|main)$'
HOOK     pre-tool-use-guard.py（攔截 git commit on master）
SOURCE   2026-07-04 harness 制度化 session（ADR-0001）
```

### INV-GIT-002 — 禁止 `git commit` 直接到 master / main

```
RULE     不得在 master/main 直接 commit
CHECK    git symbolic-ref HEAD | grep -E 'refs/heads/(master|main)$'
HOOK     pre-tool-use-guard.py（enforce — hard guard）
SOURCE   2026-07-04 harness 制度化 session（ADR-0001）
```

### INV-GIT-003 — 禁止 `git push --force` 到 master / main

```
RULE     禁止對共享分支 force push
CHECK    grep -E 'git push.*--force.*\b(master|main)\b'
HOOK     pre-tool-use-guard.py（enforce）
SOURCE   ADR-0001 D5
```

### INV-GIT-004 — 禁止 `git reset --hard origin/master`

```
RULE     fast-forward 失敗時改用 git rebase origin/master
CHECK    grep -E 'git reset --hard origin/(master|main)'
HOOK     pre-tool-use-guard.py（enforce）
SOURCE   2026-07-04 harness 制度化 session（ADR-0001）
```

### INV-GIT-005 — 新功能 branch 必須從 master 開出

```
RULE     git checkout -b feat/xxx 前必須在 master pull 完最新
CHECK    PR 建立前確認 base branch
HOOK     code-reviewer agent（手動）
SOURCE   2026-07-04 harness 制度化 session（ADR-0001）
```

---

## INV-SEC-* — Security / Secrets

### INV-SEC-001 — 禁止硬編碼 API key / token / password

```
RULE     任何原始碼檔案中不得出現明文 API key 或 token 賦值
CHECK    grep -rEn 'api[_-]?key\s*=\s*["\'][A-Za-z0-9_\-]{20,}["\']' src/
HOOK     post-edit-lint.py（sentinel）
SOURCE   通用安全最佳實踐
```

### INV-SEC-002 — 禁止 token / secret 出現在 log / print 語句

```
RULE     logger.debug/info/warn/error 及 print/console.log 中不得包含 token、key、password、secret 等敏感字
CHECK    grep -rEn '(print|console\.log|logger\.\w+)\s*\(.*\b(token|api_key|secret|password)\b' src/
HOOK     post-edit-lint.py（sentinel）
SOURCE   通用安全最佳實踐
```

### INV-SEC-003 — 禁止敏感檔案出現在 git staging

```
RULE     .env、*.pem、*.key、*.keystore、*secret* 不得被 git add
CHECK    git diff --cached --name-only | grep -E '\.(env|pem|key|keystore|p12)$|secret|credential'
HOOK     pre-tool-use-guard.py（enforce：攔截 git add 敏感檔，指令字面比對；已 staged 內容不在覆蓋範圍，靠 code-reviewer 與人審）
SOURCE   通用安全最佳實踐
```

> **採用此模板時**：把 `src/` 替換為你的實際原始碼目錄，並將 INV-SEC-001 / INV-SEC-002 的 pattern 複製到 `post-edit-lint.py` 的 `QUICK_CHECKS`。

---

## INV-TEST-* — Testing

> 填入專案的測試 invariants，例如：

```
INV-TEST-001  新增 interface method 後必須補所有 fakes/mocks
  CHECK    grep -rn ': InterfaceName' --include='*.ts' | grep -i 'fake\|mock'
  HOOK     code-reviewer agent（手動，列入 ExecPlan checklist）
  SOURCE   （範例條目，無來源 lesson）
```

---

## INV-API-* — API / Data Models

> 填入專案的 API invariants。

---

## INV-ARC-* — Architecture

> 填入專案的架構 invariants。

---

## INV-BLD-* — Build

> 填入專案的 build invariants。

---

## 不符合機械驗證的 lessons（留在 ERRORS.md）

以下 lessons 因為 pattern 過於 contextual / 涉及人類判斷，不放本檔，僅留 ERRORS.md。

---

## 引用此檔的位置

- `.claude/hooks/post-edit-lint.py` — 載入 INV-* 中標 `post-edit-lint.py` 的規則
- `.claude/hooks/pre-tool-use-guard.py` — 載入 INV-* 中標 `pre-tool-use-guard.py` 的規則
- `.claude/agents/code-reviewer.md` — review checklist 引用本檔
- `docs/learnings/ERRORS.md` — 每條 lesson 反向引用 INV-id
