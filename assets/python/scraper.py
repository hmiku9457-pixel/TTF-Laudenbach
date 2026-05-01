from playwright.sync_api import sync_playwright
import json
from config import SPIELE_URL, TABELLEN

# ==========================================
# ===== HILFSFUNKTION ======================
# ==========================================

def safe_text(cols, i):
    return cols[i].inner_text().strip() if i < len(cols) else ""


# ==========================================
# ===== SPIELE SCRAPEN =====================
# ==========================================

def scrape_spiele(page):

    spiele = []

    page.goto(SPIELE_URL)
    page.wait_for_selector("table", timeout=60000)

    rows = page.query_selector_all("table tbody tr")

    for row in rows:
        cols = row.query_selector_all("td")

        if len(cols) < 7:
            continue

        datum = safe_text(cols, 0)
        uhrzeit = safe_text(cols, 1)
        spielort = safe_text(cols, 2)
        klasse = safe_text(cols, 3)
        heim = safe_text(cols, 4)
        gast = safe_text(cols, 5)
        ergebnis = safe_text(cols, 6)

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

    return spiele


# ==========================================
# ===== GENERISCHE TABELLEN-FUNKTION =======
# ==========================================

def scrape_tabelle(page, url):

    daten = []

    page.goto(url)
    page.wait_for_selector("table", timeout=60000)

    rows = page.query_selector_all("tbody tr")

    for row in rows:
        cols = row.query_selector_all("td")

        if len(cols) < 9:
            continue

        daten.append({
            "rang": safe_text(cols, 0),
            "mannschaft": safe_text(cols, 1),
            "partien": safe_text(cols, 2),
            "siege": safe_text(cols, 3),
            "unentschieden": safe_text(cols, 4),
            "niederlagen": safe_text(cols, 5),
            "spiele": safe_text(cols, 6),
            "spieleDifferenz": safe_text(cols, 7),
            "punkte": safe_text(cols, 8)
        })

    return daten


# ==========================================
# ===== JSON SPEICHERN =====================
# ==========================================

def save_json(data, filename):
    with open(f"assets/data/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==========================================
# ===== MAIN ===============================
# ==========================================

def main():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # ===== Spiele =====
        spiele = scrape_spiele(page)
        save_json(spiele, "spiele")
        print(f"{len(spiele)} Spiele gespeichert.")

        # ===== Tabellen =====
        for tabelle in TABELLEN:
            daten = scrape_tabelle(page, tabelle["url"])
            save_json(daten, tabelle["name"])
            print(f"{tabelle['name']} gespeichert ({len(daten)} Einträge)")

        browser.close()


if __name__ == "__main__":
    main()
