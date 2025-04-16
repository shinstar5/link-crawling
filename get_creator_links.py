
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def extract_youtube_links(url):
    driver = setup_driver()
    links = []
    try:
        about_url = url if "/about" in url else url.rstrip("/") + "/about"
        driver.get(about_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "link-list-container")))
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        container = soup.find("div", {"id": "link-list-container"})
        if container:
            for view_model in container.find_all("yt-channel-external-link-view-model"):
                title_elem = view_model.find("span", class_="yt-channel-external-link-view-model-wiz__title")
                link_elem = view_model.find("a", class_="yt-core-attributed-string__link")
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    href = link_elem.get("href")
                    if "youtube.com/redirect" in href:
                        real_url = re.search(r"q=([^&]+)", href)
                        if real_url:
                            href = requests.utils.unquote(real_url.group(1))
                    links.append([title, href])
    except Exception as e:
        print(f"Error extracting YouTube links: {e}")
    finally:
        driver.quit()
    return links

def extract_instagram_links(url):
    driver = setup_driver()
    links = []
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        modal_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, 'l.instagram.com')]")
        for button in modal_buttons:
            try:
                href = button.get_attribute("href")
                title = button.text.strip() or "Instagram link"
                if "u=" in href:
                    real_url = re.search(r"u=([^&]+)", href)
                    if real_url:
                        decoded = requests.utils.unquote(real_url.group(1))
                        resolved = requests.get(decoded, allow_redirects=True, timeout=5).url
                        links.append([title, resolved])
                elif "bit.ly" in href or "ppt.cc" in href or "linktr.ee" in href or "linkby.tw" in href:
                    resolved = requests.get(href, allow_redirects=True, timeout=5).url
                    page = requests.get(resolved, timeout=5).text
                    soup = BeautifulSoup(page, "html.parser")
                    link_tags = soup.find_all("a", href=True)
                    for tag in link_tags:
                        link_title = tag.get_text(strip=True)
                        if tag["href"].startswith("http"):
                            links.append([link_title or "Link", tag["href"]])
            except Exception as e:
                print(f"Error in Instagram redirect: {e}")
    finally:
        driver.quit()
    return links

def get_creator_links(url):
    if "youtube.com" in url or "m.youtube.com" in url:
        return {"youtube": extract_youtube_links(url), "instagram": []}
    elif "instagram.com" in url:
        return {"youtube": [], "instagram": extract_instagram_links(url)}
    else:
        return {"error": "Unsupported URL"}

if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/@MAYukiChou"
    instagram_url = "https://www.instagram.com/mayukichou/"

    print("Fetching creator links...")

    all_links = {
        "youtube": extract_youtube_links(youtube_url),
        "instagram": extract_instagram_links(instagram_url)
    }

    with open("creator_links.json", "w", encoding="utf-8") as f:
        json.dump(all_links, f, ensure_ascii=False, indent=2)

    print("Saved to creator_links.json")
