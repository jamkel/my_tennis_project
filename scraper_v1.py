# data_scraper/scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.atptour.com"

def get_tournaments_for_year(year=2024):
    url = f"{BASE_URL}/en/scores/results-archive?year={year}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    tournaments = soup.select(".results-archive-table tbody tr")
    links = [BASE_URL + row.find("a")["href"] for row in tournaments if row.find("a")]
    return links

def scrape_tournament_results(tournament_url):
    response = requests.get(tournament_url)
    soup = BeautifulSoup(response.text, "html.parser")

    tournament_name = soup.find("h1", class_="tourney-title").get_text(strip=True)
    rows = soup.select("table.day-table tbody tr")

    matches = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        match = {
            "tournament": tournament_name,
            "round": cols[0].text.strip(),
            "winner": cols[1].text.strip(),
            "loser": cols[2].text.strip(),
            "score": cols[3].text.strip(),
        }
        matches.append(match)

    return matches

def scrape_all_tournaments(year=2024, limit=3):
    tournaments = get_tournaments_for_year(year)
    all_matches = []

    for i, url in enumerate(tournaments[:limit]):
        print(f"Scraping {url}...")
        try:
            matches = scrape_tournament_results(url)
            all_matches.extend(matches)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    return pd.DataFrame(all_matches)

if __name__ == "__main__":
    df = scrape_all_tournaments(year=2024)
    print(df.head())

    # Optional: save to CSV (for now)
    df.to_csv("data/matches.csv", index=False)
