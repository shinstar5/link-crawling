import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import parse_qs, urlparse, urlunparse, unquote
import time
import json
import subprocess
import re
import os


def setup_driver():
    options = Options()
    # options.add_argument("--headless=new")  # 如需無頭模式可啟用，但IG防爬機制繞過幾次後會需要登入
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 模擬 desktop user-agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )

    driver_path = (
        "/Users/shinstar5/chromedriver-mac-x64/chromedriver"  # 請改為你本機的 chromedriver 路徑
    )
    return webdriver.Chrome(service=Service(driver_path), options=options)


def get_site_title(url):
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup.title.string.strip() if soup.title else None
    except:
        return None


def expand_linkhub(url):
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text(strip=True) or get_site_title(href) or href
            if href.startswith("http"):
                links.append([title, href])
        return links
    except Exception as e:
        return [["expand_linkhub error", str(e)]]


def extract_youtube_links(url):
    driver = setup_driver()
    links = []
    try:
        if not url.endswith("/about"):
            url = url.rstrip("/") + "/about"
        driver.get(url)

        # 等到容器載入
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "link-list-container"))
        )
        time.sleep(2)  # 等內部 span 渲染完

        items = driver.find_elements(
            By.CSS_SELECTOR, "#link-list-container yt-channel-external-link-view-model"
        )
        for item in items:
            try:
                href = item.find_element(By.TAG_NAME, "a").get_attribute("href")

                # 若為 redirect，解析出真實 URL
                if "youtube.com/redirect" in href:
                    parsed = parse_qs(urlparse(href).query)
                    real_url = unquote(parsed.get("q", [href])[0])
                else:
                    real_url = href

                # 嘗試抓 title，若不存在就略過
                try:
                    title = item.find_element(
                        By.CSS_SELECTOR,
                        ".yt-channel-external-link-view-model-wiz__title",
                    ).text.strip()
                    if not title:
                        raise ValueError("空白 title")
                except Exception as e:
                    print(f"⚠️ title 抓不到，略過: {e}")
                    continue

                # ✅ 記得 append 正確解析後的 real_url！
                links.append([title, real_url])
            except Exception as e:
                print(f"⚠️ 忽略錯誤連結: {e}")
                continue

        return links
    finally:
        driver.quit()


def extract_instagram_links(url):
    driver = setup_driver()
    links = []
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # ① 等一下，模擬正常使用者
        time.sleep(6)
        driver.get(url)
        driver.refresh()
        time.sleep(3)
        input("📍 已載入 Instagram 頁面，請檢查畫面後按 Enter 繼續，如需登入請登入...")

        # ② 嘗試點關閉圖示
        try:
            close_btn = driver.find_element(By.XPATH, "//div[.//svg[@aria-label='關閉']]")
            close_btn.click()
            print("✅ 模擬點擊關閉 IG 登入牆成功")
            time.sleep(1)

        except Exception as e:
            print("⚠️ 沒找到關閉圖示，嘗試點畫面右下角")

            # ③ 點右下角遠離 modal 的地方（避免誤觸登入）
            try:
                html = driver.find_element(By.TAG_NAME, "html")
                driver.execute_script("window.scrollBy(0, 200);")  # 滾動一點
                ActionChains(driver).move_to_element_with_offset(
                    html, 20, 700
                ).click().perform()
                print("✅ 點擊右下遠離區域成功")
                time.sleep(1)
            except Exception as e:
                print("❌ 點右下失敗:", e)

        input("📍 已載入 Instagram 頁面，請檢查畫面後按 Enter 繼續，如需登入請登入...")

        # 🔹 1. 嘗試展開 modal（如果 bio 出現 +號按鈕）
        try:
            expand_button = driver.find_element(By.XPATH, "//button[contains(., '+')]")
            expand_button.click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            time.sleep(1)

            a_tags = driver.find_elements(By.XPATH, "//div[@role='dialog']//a")
            for a_tag in a_tags:
                try:
                    href = a_tag.get_attribute("href")
                    spans = a_tag.find_elements(By.TAG_NAME, "span")
                    title = spans[0].text.strip() if spans else "Instagram link"
                    if "l.instagram.com" in href:
                        parsed = parse_qs(urlparse(href).query)
                        raw_url = unquote(parsed.get("u", [href])[0])
                        parsed_url = urlparse(raw_url)
                        real_url = urlunparse(
                            (
                                parsed_url.scheme,
                                parsed_url.netloc,
                                parsed_url.path,
                                "",
                                "",
                                "",
                            )
                        )
                    else:
                        real_url = href
                    links.append([title, real_url])

                except Exception as e:
                    links.append(["parse IG modal link error", str(e)])

            LINKHUB_DOMAINS = [
                "linktr.ee",
                "bio.site",
                "beacons.ai",
                "linkby.tw",
                "campsite.bio",
                "taplink.cc",
            ]
            # 判斷 links 裡是否有 link-in-bio 平台，額外遞迴擴展
            for title, real_url in links[:]:  # 用 [:] 複製清單避免迴圈中擴展錯位
                if any(domain in real_url for domain in LINKHUB_DOMAINS):
                    links.extend(expand_linkhub(real_url))

            return links

        except Exception:
            print("ℹ️ 無 modal，改抓 bio 區短連結")

        # 🔹 2. Fallback：抓 bio 裡的單一跳轉連結（如 linktr.ee, ppt.cc）
        try:
            link = driver.find_element(
                By.XPATH, "//a[contains(@href, 'l.instagram.com')]"
            )
            href = link.get_attribute("href")
            parsed = parse_qs(urlparse(href).query)
            raw_url = unquote(parsed.get("u", [href])[0])
            parsed_url = urlparse(raw_url)
            real_url = urlunparse(
                (parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", "")
            )

            # 是 link-in-bio 類服務，進一步爬內部連結
            LINKHUB_DOMAINS = [
                "linktr.ee",
                "bio.site",
                "beacons.ai",
                "linkby.tw",
                "campsite.bio",
                "taplink.cc",
            ]
            if any(domain in real_url for domain in LINKHUB_DOMAINS):
                return expand_linkhub(real_url)

            # 是單一連結（如 bit.ly / ppt.cc）
            title = get_site_title(real_url)
            links.append([title or "Instagram bio link", real_url])

        except Exception as e:
            links.append(["bio fallback error", str(e)])

        return links

    finally:
        driver.quit()


def get_creator_links(url):
    if "youtube.com" in url:
        return extract_youtube_links(url)
    elif "instagram.com" in url:
        return extract_instagram_links(url)
    else:
        return [["Unsupported", "URL type not supported"]]


if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/@JolieChi"  # "https://www.youtube.com/@MayukiChou/about"
    instagram_url = "https://www.instagram.com/joliechi/"  # yu_zhen610 #mayukichou #haitaibear #mumumamagogo

    all_links = {
        "youtube": get_creator_links(youtube_url),
        "instagram": get_creator_links(instagram_url),
    }

    with open("creator_links.json", "w", encoding="utf-8") as f:
        json.dump(all_links, f, ensure_ascii=False, indent=2)
    print("Saved to creator_links.json")
