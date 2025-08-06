# data_scraper/scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.tennisexplorer.com/results/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept-Language": "en-US,en;q=0.9"
}

def scrape_tennisexplorer_results(year=2024, pages=3):
    matches = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for page in range(1, pages + 1):
        params = {"year": year, "page": page}
        url = f"{BASE_URL}"
        print(f"[DEBUG] Scraping {url}?page={page}")

        response = session.get(url, params=params)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", class_="result")
        if not table:
            print("[DEBUG] No results table found on this page.")
            continue

        current_date = None
        rows = table.find_all("tr")

        for row in rows:
            row_classes = row.get("class", [])
            # Check for date header
            if "head" in row_classes:
                date_cell = row.find("td")
                if date_cell:
                    current_date = date_cell.text.strip()

            elif "result" in row_classes:
                cols = row.find_all("td")
                if len(cols) >= 5:
                    matches.append({
                        "date": current_date,
                        "tournament": cols[0].text.strip(),
                        "surface": cols[1].text.strip(),
                        "player1": cols[2].text.strip(),
                        "player2": cols[3].text.strip(),
                        "score": cols[4].text.strip()
                    })

        time.sleep(1)

    return pd.DataFrame(matches)

if __name__ == "__main__":
    df = scrape_tennisexplorer_results(year=2024, pages=3)
    print(df.head())

    df.to_csv("data/tennisexplorer_matches.csv", index=False)
