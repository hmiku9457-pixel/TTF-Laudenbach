from playwright.sync_api import sync_playwright
import json
from config import SPIELPLAENE, TABELLEN


# ==========================================
# ===== HILFSFUNKTIONEN ====================
# ==========================================

def safe_text(cols, i):
    return cols[i].inner_text().strip() if i < len(cols) else "" # Gibt Zelltext sicher zurück, verhindert Index-Fehler.


def load_page(page, url):
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_selector("tbody tr", timeout=60000) #Lädt eine Seite und wartet, bis Tabellenzeilen vorhanden sind.


def get_rows(page):
    table = page.query_selector("table")
    if not table:
        return []
    return table.query_selector_all("tbody tr") #Liefert alle Tabellenzeilen der ersten Tabelle.


# ==========================================
# ===== SPIELPLAN: STARTSEITE =============
# ==========================================

def scrape_spielplan_startseite(page, url):

    spiele = []
    load_page(page, url)

    rows = get_rows(page)

    for row in rows:
        cols = row.query_selector_all("td")

        # Startseite hat 7 Spalten
        if len(cols) < 7:
            continue

        ergebnis_raw = safe_text(cols, 5).strip()
        ergebnis = ergebnis_raw or None

        spiele.append({
            "datum": safe_text(cols, 0),
            "uhrzeit": safe_text(cols, 1),
            "spielort": safe_text(cols, 2),
            "klasse": safe_text(cols, 3),
            "heim": safe_text(cols, 4),
            "gast": safe_text(cols, 5),
            "ergebnis": ergebnis,
            "status": "gespielt" if ergebnis_raw else "geplant"
        })

    return spiele


# ==========================================
# ===== SPIELPLAN: MANNSCHAFT =============
# ==========================================

def scrape_spielplan_mannschaft(page, url):

    spiele = []
    load_page(page, url)

    rows = get_rows(page)

    for row in rows:
        cols = row.query_selector_all("td")

        # Mannschaftsseite hat 6 Spalten
        if len(cols) < 6:
            continue

        ergebnis_raw = safe_text(cols, 5).strip()
        ergebnis = ergebnis_raw or None

        spiele.append({
            "datum": safe_text(cols, 0),
            "uhrzeit": safe_text(cols, 1),
            "spielort": safe_text(cols, 2),
            "heim": safe_text(cols, 3),
            "gast": safe_text(cols, 4),
            "ergebnis": ergebnis,
            "status": "gespielt" if ergebnis_raw else "geplant"
        })

    return spiele


# ==========================================
# ===== TABELLEN ===========================
# ==========================================

def scrape_tabelle(page, url):

    daten = []
    load_page(page, url)

    rows = get_rows(page)

    for row in rows:
        cols = row.query_selector_all("td")

        # Tabelle hat 9 Spalten
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
    """
    Speichert Daten als JSON-Datei.
    """
    with open(f"assets/data/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==========================================
# ===== MAIN ===============================
# ==========================================

def main():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # ======================================
        # ===== SPIELPLÄNE =====================
        # ======================================
        for plan in SPIELPLAENE:

            print(f"Scrape: {plan['name']}")

            if plan["type"] == "startseite":
                daten = scrape_spielplan_startseite(page, plan["url"])

            elif plan["type"] == "mannschaft":
                daten = scrape_spielplan_mannschaft(page, plan["url"])

            else:
                continue

            save_json(daten, plan["name"])

            print(f"{plan['name']} gespeichert ({len(daten)} Spiele)")

        # ======================================
        # ===== TABELLEN =======================
        # ======================================
        for tabelle in TABELLEN:

            print(f"Scrape Tabelle: {tabelle['name']}")

            daten = scrape_tabelle(page, tabelle["url"])

            save_json(daten, tabelle["name"])

            print(f"{tabelle['name']} gespeichert ({len(daten)} Einträge)")

        browser.close()


# ==========================================
# ===== SCRIPT START =======================
# ==========================================

if __name__ == "__main__":
    main()
