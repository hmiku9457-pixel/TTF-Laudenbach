from playwright.sync_api import sync_playwright
import json

URL = "https://www.mytischtennis.de/click-tt/TTBW/25--26/verein/07041/TTF_Laudenbach/spielplan?date_start=2026-03-29&date_end=2026-05-29"

def scrape_spiele():
    spiele = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
    
        page.goto(URL)
        
        page.wait_for_selector("table", timeout=60000)
    
        rows = page.query_selector_all("table tbody tr")
    
        spiele = []
    
        for row in rows:
            cols = row.query_selector_all("td")
    
            if len(cols) < 6:
                continue
    
            spiele.append({
                "datum": cols[0].inner_text().strip(),
                "heim": cols[2].inner_text().strip(),
                "gast": cols[4].inner_text().strip(),
                "ergebnis": cols[5].inner_text().strip()
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
