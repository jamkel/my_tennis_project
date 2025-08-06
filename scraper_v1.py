# data_scraper/scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.tennisexplorer.com/results/?year=2024"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

def scrape_tennisexplorer_results(pages=1):
    matches = []

    for page in range(1, pages + 1):
        url = f"{BASE_URL}&page={page}"
        print(f"[DEBUG] Scraping {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", class_="result")
        if not table:
            print("[DEBUG] No table found.")
            continue

        current_date = None
        rows = table.find_all("tr")

        for row in rows:
            # Date row
            if "head" in row.get("class", []):
                date_cell = row.find("td")
                if date_cell:
                    current_date = date_cell.text.strip()

            # Match row
            elif "result" in row.get("class", []):
                cols = row.find_all("td")
                if len(cols) >= 5:
                    tournament = cols[0].text.strip()
                    surface = cols[1].text.strip()
                    player1 = cols[2].text.strip()
                    player2 = cols[3].text.strip()
                    score = cols[4].text.strip()

                    matches.append({
                        "date": current_date,
                        "tournament": tournament,
                        "surface": surface,
                        "player1": player1,
                        "player2": player2,
                        "score": score
                    })

        time.sleep(1)  # be polite

    return pd.DataFrame(matches)

if __name__ == "__main__":
    df = scrape_tennisexplorer_results(pages=3)  # try 3 pages to start
    print(df.head())

    df.to_csv("data/tennisexplorer_matches.csv", index=False)
