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
    ["葳老闆的品牌👗", "https://bit.ly/..."],
    ["葳老闆的親筆簽名書✏️", "https://bit.ly/..."],
    ...
  ]
}
```
## 📦 可測試案例

- 📍 IG Bio modal 測試：  
  https://www.instagram.com/mayukichou/

- 📍 link-in-bio 展開測試：  
  https://www.instagram.com/yu_zhen610/  
  https://www.instagram.com/haitaibear/

---

## 📌 技術細節

- 使用 `Selenium` 模擬瀏覽器，處理動態渲染與 modal 展開。
- 使用 `BeautifulSoup` 解析 HTML 結構，抓取 `yt-channel-external-link-view-model`、`a[href]`、`<title>`。
- 自動解碼 Instagram redirect：`https://l.instagram.com/?u=...` ➝ 解析真實 URL。
- 自動處理短網址重導向：`requests.get(..., allow_redirects=True)`。
- 支援 link-in-bio 平台（如 `linktr.ee`, `linkby.tw`, `bio.site`, `beacons.ai` 等）遞迴提取 `<a>` 與內容，將多連結整理成 `[title, url]` 格式，實現「創作者連結無痛轉移」。

---

## 🧑‍💻 作者介紹

我是邱沛語，來自清華大學資訊系統與應用研究所，擁有 AI 應用、全端開發與產品管理多項實務經驗，熱衷以創業與產品經理視角出發，打造真正解決問題的工具。

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
