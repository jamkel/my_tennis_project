from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

BASE_URL = "https://www.atptour.com/en/scores/results-archive?year=2024"

def get_driver():
    options = Options()
    options.add_argument("--headless")  # Don't open a browser window
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    return driver

def get_tournament_links(driver, year=2024):
    url = f"https://www.atptour.com/en/scores/results-archive?year={year}"
    driver.get(url)
    print("[DEBUG] Page loaded")
    print(driver.page_source[:500])
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, ".results-archive-table tbody tr")
    links = [row.find_element(By.TAG_NAME, "a").get_attribute("href") for row in rows]
    return links

def scrape_tournament(driver, url):
    driver.get(url)
    time.sleep(2)

    try:
        tournament_name = driver.find_element(By.CLASS_NAME, "tourney-title").text.strip()
    except:
        tournament_name = "Unknown Tournament"

    rows = driver.find_elements(By.CSS_SELECTOR, "table.day-table tbody tr")
    print(f"[DEBUG] {tournament_name}: Found {len(rows)} rows")

    matches = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 5:
            continue
        matches.append({
            "tournament": tournament_name,
            "round": cols[0].text.strip(),
            "winner": cols[1].text.strip(),
            "loser": cols[2].text.strip(),
            "score": cols[3].text.strip()
        })
    return matches

def scrape_all(year=2024, limit=3):
    driver = get_driver()
    tournament_links = get_tournament_links(driver, year)
    all_matches = []

    for link in tournament_links[:limit]:
        print(f"[DEBUG] Scraping {link}")
        matches = scrape_tournament(driver, link)
        all_matches.extend(matches)

    driver.quit()
    return pd.DataFrame(all_matches)

if __name__ == "__main__":
    df = scrape_all()
    print(df.head())
    df.to_csv("data/matches.csv", index=False)
