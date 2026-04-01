# CIM Skills Claude Code Skills Marketplace
## 完整部署與使用教學

> 本文件為公司內部 Claude Code Skills 自管平台的完整實作指南，  
> 涵蓋環境確認、repo 建立、本機預覽、正式部署、日常管理、新增 skill 全流程。

---

## 目錄

1. [系統架構說明](#1-系統架構說明)
2. [前置需求確認](#2-前置需求確認)
3. [取得程式碼](#3-取得程式碼)
4. [本機預覽（無需 Docker）](#4-本機預覽無需-docker)
5. [正式部署（有 Python 環境）](#5-正式部署有-python-環境)
6. [正式部署（有 Docker 環境）](#6-正式部署有-docker-環境)
7. [Admin 管理介面使用說明](#7-admin-管理介面使用說明)
8. [員工安裝與使用 Skills](#8-員工安裝與使用-skills)
9. [新增一個 Skill（完整流程）](#9-新增一個-skill完整流程)
10. [新增一個 Plugin 分類](#10-新增一個-plugin-分類)
11. [版本管理規則](#11-版本管理規則)
12. [目錄結構說明](#12-目錄結構說明)
13. [常見問題 FAQ](#13-常見問題-faq)

---

## 1. 系統架構說明

本平台由三個部分組成：

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   Git Repository  (這個 repo)                       │
│   ├── .claude-plugin/marketplace.json  ← 目錄清單   │
│   └── plugins/skill-authoring/        ← skill 檔案  │
│                                                     │
│   Admin 後台  (FastAPI)                             │
│   └── 讓管理員透過網頁新增/編輯/刪除 skill           │
│                                                     │
│   User 前端  (靜態 HTML)                            │
│   └── 讓員工查看目前有哪些 skill 可以安裝             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**員工使用流程：**
```
員工在 Claude Code 輸入：
  /plugin marketplace add <公司Git網址>
  /plugin install skill-authoring@cim-skills
  /skill-creator   ← 開始使用
```

**管理員維護流程：**
```
打開 Admin 網頁介面
  → 新增/編輯 skill
  → 系統自動更新 marketplace.json
  → 員工下次 /plugin update 就能取得新版本
```

---

## 2. 前置需求確認

### 必要條件（所有情境）

| 項目 | 說明 | 確認指令 |
|------|------|---------|
| Git | 版本控制 | `git --version` |
| 公司 Git Server | GitLab / GitHub Enterprise / Gitea | 請洽 IT |
| Python 3.10+ | 執行後台服務 | `python --version` |

### 確認 Python 版本
```bash
python --version
# 需要 3.10 以上，建議 3.12
```

如果版本不足，請洽 IT 安裝 Python 3.12。

### Docker（可選）

Docker 非必要。本教學提供有無 Docker 兩種方案。

---

## 3. 取得程式碼

### 方法 A：從公司 Git Server clone（推薦）

先將這個 repo push 到公司 Git Server：

```bash
# 在這個目錄下初始化 git
cd C:\path\to\cim-skills
git init
git add .
git commit -m "Initial commit: CIM Skills Skills Marketplace"

# 推到公司 Git Server（網址請換成你們的）
git remote add origin https://your-gitlab.your-company.com/isdd/claude-skills.git
git push -u origin main
```

之後其他人 clone：
```bash
git clone https://your-gitlab.your-company.com/isdd/claude-skills.git
cd claude-skills
```

### 方法 B：直接使用本機路徑（測試用）

不需要 Git Server，直接在本機操作也可以，但員工就無法遠端安裝 skill。

---

## 4. 本機預覽（無需 Docker）

這個方法只用 Python 內建指令，**不需要安裝任何額外套件**，適合快速看 UI 長相。

### 步驟 1：開啟 terminal，進到 repo 根目錄

```bash
cd C:\path\to\cim-skills
```

### 步驟 2：啟動靜態 server

```bash
python -m http.server 8080
```

看到以下訊息代表成功：
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

### 步驟 3：瀏覽器開啟各頁面

| 頁面 | 網址 | 說明 |
|------|------|------|
| 員工查詢前端 | http://localhost:8080/frontend/ | 瀏覽可用 skills |
| Admin Dashboard | http://localhost:8080/admin/static/admin/index.html | 管理首頁 |
| Skills 管理 | http://localhost:8080/admin/static/admin/skills.html | 列表/編輯/刪除 |
| Skill 編輯器 | http://localhost:8080/admin/static/admin/editor.html | 新增/編輯 skill |

> **注意**：這個模式只能「看畫面」，無法真正新增/儲存 skill（API 呼叫需要 FastAPI 後台）。

### 關閉 server

在 terminal 按 `Ctrl + C`。

---

## 5. 正式部署（有 Python 環境）

這是**不需要 Docker** 的完整部署方式，適合公司環境限制多的情況。

### 步驟 1：安裝 Python 套件

```bash
cd C:\path\to\cim-skills\admin
pip install -r requirements.txt
```

如果 pip 速度慢，可以指定公司內部的 PyPI mirror：
```bash
pip install -r requirements.txt -i https://pypi.your-company.com/simple/
```

安裝完後確認：
```bash
pip show fastapi uvicorn pyyaml
# 應該都有顯示版本號
```

### 步驟 2：設定環境變數

**Windows（PowerShell）：**
```powershell
$env:SKILLS_REPO_PATH = "C:\path\to\cim-skills"
$env:ADMIN_SECRET_TOKEN = "your-strong-password-here"
```

**Windows（CMD）：**
```cmd
set SKILLS_REPO_PATH=C:\path\to\cim-skills
set ADMIN_SECRET_TOKEN=your-strong-password-here
```

**Linux / macOS：**
```bash
export SKILLS_REPO_PATH=/path/to/CIM
export ADMIN_SECRET_TOKEN=your-strong-password-here
```

### 步驟 3：啟動 FastAPI 後台

```bash
cd C:\path\to\cim-skills\admin
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

看到以下訊息代表成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 步驟 4：啟動前端（另開一個 terminal）

```bash
cd C:\path\to\cim-skills
python -m http.server 8080
```

### 步驟 5：確認服務正常

| 服務 | 網址 | 預期結果 |
|------|------|---------|
| 後台健康檢查 | http://localhost:8000/health | `{"status":"ok"}` |
| API 文件 | http://localhost:8000/docs | Swagger UI 頁面 |
| 員工前端 | http://localhost:8080/frontend/ | Skill 卡片列表 |
| Admin UI | http://localhost:8080/admin/static/admin/ | 管理 Dashboard |

### 步驟 6：設定為開機自動啟動（Windows）

建立 `start-services.bat` 放在桌面：

```bat
@echo off
set SKILLS_REPO_PATH=C:\path\to\cim-skills
set ADMIN_SECRET_TOKEN=your-strong-password-here

start "CIM Admin API" cmd /k "cd /d %SKILLS_REPO_PATH%\admin && uvicorn main:app --host 0.0.0.0 --port 8000"
start "CIM Frontend" cmd /k "cd /d %SKILLS_REPO_PATH% && python -m http.server 8080"

echo Services started.
echo Admin API: http://localhost:8000/docs
echo Frontend:  http://localhost:8080/frontend/
echo Admin UI:  http://localhost:8080/admin/static/admin/
pause
```

---

## 6. 正式部署（有 Docker 環境）

如果公司環境允許 Docker，這是最簡單的方式。

### 步驟 1：設定 .env 檔案

```bash
cd C:\path\to\cim-skills
copy .env.example .env
```

編輯 `.env`：
```
ADMIN_SECRET_TOKEN=your-strong-password-here
```

### 步驟 2：啟動所有服務

```bash
docker compose up -d --build
```

### 步驟 3：確認服務正常

```bash
docker compose ps
# 應該看到 admin 和 frontend 都是 running
```

| 服務 | 網址 |
|------|------|
| 員工前端 | http://localhost/ |
| Admin UI | http://localhost/admin/ |
| API 文件 | http://localhost:8000/docs |

### 停止服務

```bash
docker compose down
```

---

## 7. Admin 管理介面使用說明

### 7.1 第一次登入

1. 開啟 Admin Dashboard：
   - Python 部署：`http://localhost:8080/admin/static/admin/index.html`
   - Docker 部署：`http://localhost/admin/`

2. 在右上角的 **Admin Token** 欄位輸入你設定的 `ADMIN_SECRET_TOKEN`

3. 點擊儲存 — Token 會記在瀏覽器 localStorage，下次不用再輸入

### 7.2 Dashboard（首頁）

![功能說明]

- **Total Skills** — 目前 repo 中的 skill 數量
- **Total Plugins** — 目前 plugin 數量
- **Sync Marketplace** 按鈕 — 如果你手動新增了 skill 檔案，點這個讓系統重新掃描並更新 `marketplace.json`

### 7.3 Skills 管理頁

顯示所有 skill 的列表，可以：
- **篩選**：右上角下拉選單可以選擇只看特定 plugin 的 skills
- **編輯**：點 Edit 進入編輯器
- **刪除**：點 Delete，會跳出確認視窗

### 7.4 Skill 編輯器

新增或編輯 skill 的表單，欄位說明：

| 欄位 | 說明 | 注意事項 |
|------|------|---------|
| Plugin | 這個 skill 屬於哪個 plugin | 輸入 plugin 目錄名稱 |
| Skill Directory Name | skill 的目錄名稱 | kebab-case，例如 `my-skill` |
| Name (frontmatter) | slash command 名稱 | 留空則用目錄名稱 |
| Description | 說明文字 | **超過 250 字元會變紅色警告**，Claude 只看前 250 字元 |
| Argument Hint | 指令提示，例如 `[file-path]` | 顯示在 autocomplete |
| Allowed Tools | 允許使用的工具 | 例如 `Read, Grep, Glob` |
| Disable Model Invocation | 勾選後 Claude 不會自動呼叫 | 有副作用的 skill（寫檔、送訊息）務必勾選 |
| Context | 執行方式 | `inline`=在對話中執行；`fork`=獨立 subagent |
| Body | Skill 的指令內容 | Markdown 格式 |

**版本管理區塊**（編輯模式才會顯示）：
- 選擇升版類型：patch / minor / major
- 填寫 changelog 說明
- 點 **Bump Version** 自動更新版本號並寫入 CHANGELOG.md

### 7.5 Sync Marketplace

當你直接在 git repo 手動新增/刪除 skill 資料夾，需要手動更新 `marketplace.json`：

方法一：Admin Dashboard → 點 **Sync Marketplace** 按鈕

方法二：API 呼叫
```bash
curl -X POST http://localhost:8000/api/marketplace/sync \
  -H "Authorization: Bearer your-token"
```

---

## 8. 員工安裝與使用 Skills

### 8.1 前置設定（一次性）

員工需要在自己電腦的 Claude Code 中加入公司 marketplace。

**方法一：輸入指令（推薦）**

在 Claude Code 中輸入：
```
/plugin marketplace add https://your-gitlab.your-company.com/isdd/claude-skills.git
```

**方法二：自動設定（推薦給團隊統一設定）**

請 IT 或管理員在員工的 `~/.claude/settings.json` 加入：
```json
{
  "extraKnownMarketplaces": {
    "cim-skills": {
      "source": {
        "source": "url",
        "url": "https://your-gitlab.your-company.com/isdd/claude-skills.git"
      }
    }
  }
}
```
這樣員工開啟 Claude Code 就已經知道這個 marketplace，不需要手動 add。

### 8.2 安裝 Plugin

```
/plugin install skill-authoring@cim-skills
```

### 8.3 使用 Skills

安裝後，直接在 Claude Code 輸入斜線指令：

```
/skill-creator
```
Claude 會引導你建立一個新的 SKILL.md。

```
/skill-review plugins/skill-authoring/skills/skill-creator/SKILL.md
```
Claude 會審查指定的 SKILL.md，給出分數和改善建議。

### 8.4 更新到最新版本

當管理員發布了新版 skill，員工輸入：
```
/plugin update skill-authoring@cim-skills
```

---

## 9. 新增一個 Skill（完整流程）

以下以新增一個 `code-formatter` skill 為例，示範完整流程。

### 方法 A：透過 Admin UI（推薦，不需要懂技術）

1. 開啟 `http://localhost:8080/admin/static/admin/editor.html`

2. 填入以下欄位：
   - **Plugin**: `skill-authoring`（加到現有 plugin）或輸入新 plugin 名稱
   - **Skill Directory Name**: `code-formatter`
   - **Description**: `Format code files according to team standards. Use when someone says "format this file", "fix indentation", "clean up code".`（注意要在 250 字元內）
   - **Allowed Tools**: `Read, Write`
   - **Body**: 填入 skill 的指令內容（Markdown）

3. 點 **Save**

4. 回到 Dashboard，點 **Sync Marketplace**

5. 完成！員工執行 `/plugin update` 後就能用 `/code-formatter`

---

### 方法 B：手動建立檔案

#### 步驟 1：建立 skill 目錄

```
plugins/
  skill-authoring/         ← 放進現有 plugin
    skills/
      code-formatter/      ← 新建這個目錄
        SKILL.md           ← 新建這個檔案
```

#### 步驟 2：撰寫 SKILL.md

```markdown
---
name: code-formatter
description: >
  Format code files according to team standards. Use when someone says
  "format this file", "fix indentation", or "clean up code style".
argument-hint: "<file-path> [language]"
allowed-tools: Read, Write
---

# Code Formatter

Format the specified file according to team coding standards.

## Usage

/code-formatter src/main.py
/code-formatter src/api.js javascript

## Process

1. Read the file at $ARGUMENTS[0]
2. Detect language from file extension (or use $ARGUMENTS[1] if provided)
3. Apply formatting rules:
   - 4-space indentation for Python, 2-space for JS/TS
   - Remove trailing whitespace
   - Ensure single newline at end of file
4. Write the formatted content back to the file
5. Report what was changed
```

#### 步驟 3：更新 marketplace.json

**方法一**：Admin Dashboard → 點 **Sync Marketplace**

**方法二**：手動編輯 `.claude-plugin/marketplace.json`，版本號 +1（patch）

#### 步驟 4：提交到 Git

```bash
git add plugins/skill-authoring/skills/code-formatter/
git add .claude-plugin/marketplace.json
git commit -m "feat(skill): add code-formatter skill"
git push
```

---

## 10. 新增一個 Plugin 分類

當你要建立全新的 plugin（例如把 CI/CD 相關的 skills 獨立出來）：

### 步驟 1：建立目錄結構

```
plugins/
  cicd-tools/                      ← 新 plugin
    .claude-plugin/
      plugin.json
    skills/
      deploy-checker/
        SKILL.md
    CHANGELOG.md
```

### 步驟 2：建立 plugin.json

`plugins/cicd-tools/.claude-plugin/plugin.json`：
```json
{
  "name": "cicd-tools",
  "description": "CI/CD workflow tools for CIM teams",
  "author": {
    "name": "CIM Platform Team",
    "email": "cim-platform@your-company.com"
  },
  "keywords": ["cicd", "deploy", "pipeline"]
}
```

> **重要**：`plugin.json` 不要加 `version` 欄位，版本只放在 `marketplace.json`。

### 步驟 3：在 marketplace.json 新增 plugin 條目

`.claude-plugin/marketplace.json`：
```json
{
  "plugins": [
    {
      "name": "skill-authoring",
      ...
    },
    {
      "name": "cicd-tools",
      "source": "./plugins/cicd-tools",
      "description": "CI/CD workflow tools for CIM teams",
      "version": "1.0.0",
      "category": "developer-tools",
      "keywords": ["cicd", "deploy", "pipeline"]
    }
  ]
}
```

### 步驟 4：建立 CHANGELOG.md

`plugins/cicd-tools/CHANGELOG.md`：
```markdown
# Changelog — cicd-tools

## [1.0.0] - 2026-04-01
### Added
- Initial release with deploy-checker skill
```

### 步驟 5：提交並推送

```bash
git add plugins/cicd-tools/
git add .claude-plugin/marketplace.json
git commit -m "feat(plugin): add cicd-tools plugin"
git push
```

---

## 11. 版本管理規則

### 版本號格式：`MAJOR.MINOR.PATCH`

| 類型 | 情境 | 範例 |
|------|------|------|
| **PATCH** `1.0.0 → 1.0.1` | 修正 skill 說明文字、修 typo、調整指令邏輯但不影響使用方式 | 把描述改得更清楚 |
| **MINOR** `1.0.0 → 1.1.0` | 新增 skill 到現有 plugin | 加了一個新的 `/code-formatter` |
| **MAJOR** `1.0.0 → 2.0.0` | 刪除或重新命名 skill（會破壞員工現有的 `/指令`） | 把 `/skill-creator` 改名為 `/create-skill` |

### 重要規則

> **版本號只能放在 `.claude-plugin/marketplace.json`，不能放在 `plugin.json`。**  
> 如果兩個檔案都有版本號，`plugin.json` 會靜默覆蓋 `marketplace.json` 的值，導致版本管理混亂。

### 透過 Admin UI 升版

1. 開啟 Skill 編輯器（點 Edit 任一個該 plugin 下的 skill）
2. 滑到頁面下方的「Version Management」區塊
3. 選擇 patch / minor / major
4. 填寫這次更新的說明（會自動寫入 CHANGELOG.md）
5. 點 **Bump Version**

---

## 12. 目錄結構說明

```
CIM/
│
├── .claude/
│   ├── settings.json          # 設定公司 marketplace URL（提交到 git）
│   └── settings.local.json    # 本機權限設定（不提交）
│
├── .claude-plugin/
│   └── marketplace.json       # 核心：marketplace 目錄清單與版本號
│
├── .env.example               # 環境變數範本
├── .gitignore
├── CHANGELOG.md               # 整體 repo 的變更紀錄
├── docker-compose.yml         # Docker 部署設定
├── README.md                  # 本文件
│
├── admin/                     # FastAPI 後台服務
│   ├── Dockerfile
│   ├── main.py                # 主程式：auth、router 註冊、靜態檔案 mount
│   ├── requirements.txt       # Python 依賴套件
│   ├── models/                # Pydantic 資料模型
│   │   ├── skill.py
│   │   └── plugin.py
│   ├── routers/               # API 路由
│   │   ├── skills.py          # GET/POST/PUT/DELETE /api/skills
│   │   ├── plugins.py         # GET/POST/PUT /api/plugins
│   │   ├── marketplace.py     # GET /api/marketplace, POST /api/marketplace/sync
│   │   └── versions.py        # POST /api/versions/{plugin}/bump
│   ├── services/              # 商業邏輯
│   │   ├── skill_service.py   # 解析/寫入 SKILL.md（YAML frontmatter + body）
│   │   ├── manifest_service.py # 讀寫 marketplace.json / plugin.json
│   │   └── version_service.py # SemVer 升版 + CHANGELOG.md 更新
│   └── static/admin/          # Admin 網頁 UI
│       ├── index.html         # Dashboard
│       ├── skills.html        # Skills 列表管理
│       └── editor.html        # Skill 編輯器
│
├── frontend/
│   └── index.html             # 員工查詢介面（靜態頁面）
│
├── nginx/
│   └── nginx.conf             # Reverse proxy 設定（Docker 用）
│
└── plugins/                   # 所有 skills 放這裡
    └── skill-authoring/       # Plugin：skill 相關工具
        ├── .claude-plugin/
        │   └── plugin.json    # Plugin metadata（無版本號）
        ├── CHANGELOG.md
        └── skills/
            ├── skill-creator/ # /skill-creator 指令
            │   ├── SKILL.md
            │   ├── reference.md
            │   └── examples/
            └── skill-review/  # /skill-review 指令
                ├── SKILL.md
                └── rubric.md
```

---

## 13. 常見問題 FAQ

### Q: 員工輸入 `/plugin marketplace add` 後說找不到？

**A**: 確認以下幾點：
1. 這個 repo 已經 push 到公司 Git Server
2. 員工的電腦可以連到公司 Git Server（網路/VPN）
3. Git Server 的 URL 格式正確（`https://` 而非 `http://` 如果公司有 SSL）
4. 員工有讀取這個 repo 的權限

---

### Q: 前端頁面打開後沒有顯示 skill 卡片？

**A**: 開啟瀏覽器的開發者工具（F12）→ Console，看有沒有錯誤訊息。

常見原因：
- 用 `file://` 直接開 HTML（CORS 限制）→ 改用 `python -m http.server 8080`
- `marketplace.json` 路徑不對 → 確認從 repo 根目錄啟動 server

---

### Q: 點 Admin UI 的 Save 按鈕沒有反應？

**A**: 確認：
1. FastAPI 後台有在跑（`http://localhost:8000/health` 有回應）
2. Token 有填正確（右上角 Admin Token 欄位）
3. 開 F12 Console 看有沒有 401 或 CORS 錯誤

---

### Q: 員工安裝 skill 後，輸入 `/skill-creator` 沒有出現？

**A**: 嘗試重啟 Claude Code session，或確認 plugin 安裝成功：
```
/plugin list
# 確認 skill-authoring@cim-skills 有在清單中
```

---

### Q: admin/requirements.txt 安裝失敗？

**A**: 可能是公司網路封鎖了 PyPI。解法：
```bash
# 指定公司內部 mirror（請洽 IT 確認網址）
pip install -r requirements.txt -i https://pypi-mirror.your-company.com/simple/

# 或離線安裝：先在可連網的電腦下載
pip download -r requirements.txt -d ./wheels
# 複製 wheels 資料夾到目標機器
pip install --no-index --find-links=./wheels -r requirements.txt
```

---

### Q: 版本號要如何讓員工拿到最新版？

**A**: 員工執行：
```
/plugin update skill-authoring@cim-skills
```
或是重新安裝：
```
/plugin install skill-authoring@cim-skills
```

---

### Q: 可以設定 skill 只有特定人能用嗎？

**A**: 目前 Claude Code 的 marketplace 機制是 repo 層級的存取控制，可以透過 Git Server 的 repo 權限設定（Private / Internal），讓只有特定群組的員工才能 clone 這個 repo，進而安裝 skill。

---

## 聯絡與貢獻

如需新增 skill 或回報問題，請聯絡 CIM Platform Team  
或在公司 Git Server 開 Issue / MR。

新 skill 請先用 `/skill-review` 自我評分達到 7/10 以上再提交。
