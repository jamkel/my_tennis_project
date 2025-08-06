# data_scraper/scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

def get_driver():
    options = Options()
    options.add_argument("--headless")  # remove this if you want to see the browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_tennisexplorer_with_selenium(pages=3):
    driver = get_driver()
    matches = []

    base_url = "https://www.tennisexplorer.com/results/?year=2024&page={}"

    for page in range(1, pages + 1):
        url = base_url.format(page)
        print(f"[DEBUG] Visiting {url}")
        driver.get(url)
        html = driver.page_source
        print("[DEBUG] First 500 characters of HTML:\n")
        print(html[:500])
        time.sleep(3)

        rows = driver.find_elements(By.CSS_SELECTOR, "table.result tr")
        current_date = None

        for row in rows:
            row_class = row.get_attribute("class")
            if "head" in row_class:
                current_date = row.text.strip()
            elif "result" in row_class:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 5:
                    match = {
                        "date": current_date,
                        "tournament": cols[0].text.strip(),
                        "surface": cols[1].text.strip(),
                        "player1": cols[2].text.strip(),
                        "player2": cols[3].text.strip(),
                        "score": cols[4].text.strip(),
                    }
                    matches.append(match)

    driver.quit()
    return pd.DataFrame(matches)

if __name__ == "__main__":
    df = scrape_tennisexplorer_with_selenium(pages=3)
    print(df.head())
    df.to_csv("data/tennisexplorer_matches.csv", index=False)
