# Creator Link Crawler 🔍🧩
**自動化提取 YouTube / Instagram 創作者連結資訊，實現創作者無痛搬家至 Portaly。**

---

## 📌 專案動機：讓創作者「一鍵轉移連結」

對於正在從 linktree、beacons、或 IG/YouTube bio 經營自媒體的創作者，我觀察到：

> 很多創作者的「社群介紹」裡放了許多重要連結，但要遷移到新平台（如 Portaly）時往往繁瑣、耗時，甚至會遺漏關鍵連結。

因此我設計了這支 **Creator Link Crawler**，自動提取創作者公開頁面中所有的外部連結與標題，並格式化為 Portaly 可使用的 JSON 結構。**這是我以產品經理的角度，解決實際使用者痛點的實作成果。**

---

## 🚀 功能簡介

| 項目 | 說明 |
|------|------|
| ✅ YouTube | 自動解析 `/about` 頁面，擷取「加入會員頻道」「Instagram」「商店」「Email」等欄位連結 |
| ✅ Instagram | 模擬點擊 bio 區的短網址按鈕，進入 modal 彈窗擷取所有連結與標題 |
| ✅ 支援短網址 | 自動展開 `bit.ly`、`ppt.cc` 等連結取得實際 URL |
| ✅ 支援 link-in-bio 平台 | 遞迴進入 `linktr.ee`、`linkby.tw`、`beacons.ai` 等頁面，擷取其中所有外部連結 |
| ✅ 擷取網站標題 | 若 IG bio 中只有一個外部連結，會自動抓該網站的 `<title>` 作為連結標題 |

---

## 🧠 產品思維與實作亮點

### 🎯 為什麼這很重要？

對於創作者來說，轉移平台最大的障礙往往是：
- 無法快速搬移已建立的連結（例如電商、表單、社群）
- 擔心搬家會漏掉重要變現渠道
- 手動轉錄耗費大量時間

本工具直接解決以上問題，**讓 Portaly 可主動協助創作者轉移資料、降低轉換門檻、提高留存率**。

---

### 💡 作為 PM 的我如何規劃：

| 面向 | 思維與策略 |
|------|------------|
| 使用者洞察 | 根據 IG/YouTube 多個帳號觀察，90% 創作者都有外部連結需求，尤以 linktree 使用最普遍 |
| 成本考量 | 本工具以 Python 撰寫，部署成本極低，可整合至 Portaly 後台自動化作業流程 |
| 成長策略 | 可結合註冊流程，在創作者輸入 IG / YouTube 時自動觸發爬蟲，自動填入個人連結頁面 |
| 商業應用 | 提升註冊完成率 + 提供平台代管 link 的黏著機制（例如「建立我的 Portaly 名片」流程） |

---

## 🛠️ 使用方式

⚠️ **注意：請手動修改 `src/get_creator_links.py` 中的 `driver_path`，指向你本機的 chromedriver 路徑。**
建議使用與你本機 Google Chrome 相同版本的 driver，可於此查詢：https://chromedriver.chromium.org/downloads


### 1️⃣ 安裝環境依賴

```bash
pip install -r requirements.txt
（包含 selenium, bs4, webdriver-manager, requests）
```

### 2️⃣ 使用腳本
```bash
cd src/
python get_creator_links.py
```
可更改 youtube_url / instagram_url 測試不同創作者。

### 3️⃣ 輸出格式
```json
{
  "youtube": [
    ["加入會員頻道", "https://youtube.com/channel/..."],
    ["IG", "https://www.instagram.com/xxx"],
    ...
  ],
  "instagram": [
    ["老闆的品牌", "https://bit.ly/..."],
    ["老闆的親筆簽名書", "https://bit.ly/..."],
    ...
  ]
}
```
## 📦 可測試案例

- 📍 IG Bio modal 測試：  
  https://www.instagram.com/mayukichou/

- 📍 link-in-bio 展開測試：  
  https://www.instagram.com/joliechi/  
  https://www.instagram.com/haitaibear/

## 📁 範例輸出（examples/）
你可以在 `examples/` 資料夾中找到四位創作者的爬蟲結果 JSON：
- `haitaibear.json`：展示 IG + linktree 拓展
- `mayukichou.json`：展示 Youtube, IG modal 與短網址擷取
- `joliechi.json`：展示 Youtube, IG modal + linktree 拓展
- `mumumamagogo.json`：展示IG單一網址連結與團購網頁title爬取

## 📌 技術細節

- 使用 `Selenium` 模擬瀏覽器，處理動態渲染與 modal 展開。
- 使用 `BeautifulSoup` 解析 HTML 結構，抓取 `yt-channel-external-link-view-model`、`a[href]`、`<title>`。
- 自動解碼 Instagram redirect：`https://l.instagram.com/?u=...` ➝ 解析真實 URL。
- 自動處理短網址重導向：`requests.get(..., allow_redirects=True)`。
- 支援 link-in-bio 平台（如 `linktr.ee`, `linkby.tw`, `bio.site`, `beacons.ai` 等）遞迴提取 `<a>` 與內容，將多連結整理成 `[title, url]` 格式，實現「創作者連結無痛轉移」。

### 🧱 關於 Instagram 反爬蟲限制

目前 Instagram 對未登入用戶的瀏覽做了嚴格限制，會在使用幾次後黑屏頁面錯誤強制登入。

本專案的 IG 模組已嘗試以下繞過策略：
- 透過重新整理繞過簡易(半滿)登入牆
- 模擬正常使用者行為（等待、refresh、點擊關閉或空白處）
- 擷取登入牆前的 modal 按鈕與 bio 短網址
- 嘗試動態點擊「關閉圖示」與右下角區域
- 若失敗仍能進行 等候手動登入完畢再執行 / fallback 擷取（如 linktr.ee 展開）

**執行時會跳出提示請手動登入後再按 Enter**，否則會遭遇「登入牆」阻擋，無法載入頁面或抓取連結。
(🔒 IG模組需按兩下enter進行畫面確認，如被強制登入，目前需「手動登入」帳號才能取得創作者的 bio 與連結 modal。)

✅ 建議改用：
- **Playwright（推薦）**：支援登入態模擬與穩定繞過登入牆
- **Chrome Profile 載入**：指定已登入帳號之 `--user-data-dir`（需本機測試）


### 🔍 技術更新紀錄

| 日期 | 項目 | 說明 |
|------|------|------|
| 2025-04-16 | Instagram Modal link 支援展開 | 若 modal 中連結為 `linktr.ee` 等，將自動擴展並加入回傳清單 |
| 2025-04-16 | YouTube redirect 支援解析 | 自動從 `youtube.com/redirect?q=xxx` 中解析出實際網址 |

### 🔧 Lint / 維護建議

- 請使用 `black` 進行格式化 (`pip install black`)
- 執行 `black src/` 可保持乾淨一致的代碼格式
- 未來可使用 `.env` 儲存 chromedriver 路徑與 base URL（可選）
---

### 🔮 未來解法規劃

- ✅ 自動登入 Instagram：以帳密或 cookie 注入方式繞過未登入限制
- ✅ 使用 [`Playwright`](https://playwright.dev/python/) 進行登入後爬蟲，可穩定處理登入狀態、瀏覽器上下文與封鎖機制
- ✅ 將爬蟲轉為 API 微服務形式，供平台後台串接

### 🔧 Next Steps
- [ ] 將爬蟲主程式包裝成 RESTful API，支援 URL 查詢與結果回傳 JSON，方便整合到 Portaly 後台
- [ ] 將 console `print` 改為 `logging` 系統，利於伺服器部署與偵錯
- [ ] 實作 link result 去重機制，避免重複抓取（如 modal 展開與 bio link 重複）。 (優先度較低，使用者可主動刪除)
- [ ] 嘗試改用 Playwright 以繞過 IG 登入牆（或自動登入）。
- [ ] 增加單元測試與連結格式驗證。

---

📌 本功能已可展示爬蟲流程與資料結構設計，未來只需將登入流程補齊，即可作為完整的 onboarding 自動化模組串入 Portaly。

---

## 🧑‍💻 作者介紹

我是邱沛語，來自清華大學資訊系統與應用研究所，擁有 AI 應用、全端 WebApp 開發與 UI/UX、產品與專案管理等多項實務經驗，熱衷以創業與產品經理視角出發，打造真正解決問題的工具。

這個專案正是我為了提升創作者搬家體驗、協助平台快速導入用戶所設計的解法。我相信好的產品，不只是能運行的程式碼，更是深度理解使用者需求的具體體現。

> 「我希望能加入 Portaly，不只是成為專業的產品經理、寫好程式，更是能與團隊一起打造創作者經濟的未來。」

📮 歡迎參考我的履歷與作品集：  
👉 [Resume & Portfolio](https://drive.google.com/file/d/1P6syB-NHeXITSBBxQiTtaS_7-kCBfl49/view?usp=sharing)

---

## ⭐ 期待與您合作

如果你是：

- 🧩 自媒體平台開發者
- 📈 尋求成長的產品經理
- 🎨 著重 onboarding 體驗的 UX 設計師

本工具將是你提升註冊轉換率與用戶體驗的好幫手。

🪄 歡迎 fork / star / PR，一起共創創作者工具生態！
