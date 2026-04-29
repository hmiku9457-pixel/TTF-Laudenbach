from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import json

today = datetime.today()
start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")

URL = f"https://www.mytischtennis.de/click-tt/TTBW/25--26/verein/07041/TTF_Laudenbach/spielplan?date_start={start_date}&date_end={end_date}"

def safe_text(cols, i):
    return cols[i].inner_text().strip() if i < len(cols) else ""

def scrape_spiele():
    spiele = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL)
        page.wait_for_selector("table", timeout=60000)

        rows = page.query_selector_all("table tbody tr")

        for row in rows:
            cols = row.query_selector_all("td")

            if len(cols) < 4:
                continue

            datum = safe_text(cols, 0)
            uhrzeit = safe_text(cols, 1)
            spielort = safe_text(cols, 2)
            klasse = safe_text(cols, 3)
            heim = safe_text(cols, 4)
            gast = safe_text(cols, 5)
            ergebnis = safe_text(cols, 6)

            # Unterscheidung: gespielt oder geplant
            gespielt = ergebnis != ""

            spiele.append({
                "datum": datum,
                "uhrzeit": uhrzeit,
                "spielort": spielort,
                "klasse": klasse,
                "heim": heim,
                "gast": gast,
                "ergebnis": ergebnis if ergebnis else None,
                "status": "gespielt" if ergebnis else "geplant"
            })

        browser.close()

    return spiele


def save_to_json(spiele):
    with open("assets/data/spiele.json", "w", encoding="utf-8") as f:
        json.dump(spiele, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    daten = scrape_spiele()
    save_to_json(daten)

    print(f"{len(daten)} Spiele gespeichert.")
