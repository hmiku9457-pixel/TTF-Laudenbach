from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)
from pathlib import Path
from datetime import datetime
import json

from config import SPIELPLAENE, TABELLEN, LINKS


# ==========================================
# ===== HILFSFUNKTIONEN ====================
# ==========================================

def safe_text(cols, i):
    """
    Gibt Zelltext sicher zurück und verhindert Index-Fehler.
    """
    return cols[i].inner_text().strip() if i < len(cols) else ""


def create_debug_files(page, name):
    """
    Speichert bei einem Fehler einen Screenshot und den HTML-Inhalt
    der aktuell geladenen Seite.
    """
    debug_dir = Path("debug")
    debug_dir.mkdir(exist_ok=True)

    safe_name = "".join(
        char if char.isalnum() or char in "-_" else "_"
        for char in name
    )

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_path = debug_dir / f"{safe_name}_{timestamp}"

    try:
        page.screenshot(
            path=str(base_path.with_suffix(".png")),
            full_page=True
        )

        print(
            f"Debug-Screenshot gespeichert: "
            f"{base_path.with_suffix('.png')}"
        )

    except Exception as error:
        print(f"Screenshot konnte nicht gespeichert werden: {error}")

    try:
        base_path.with_suffix(".html").write_text(
            page.content(),
            encoding="utf-8"
        )

        print(
            f"Debug-HTML gespeichert: "
            f"{base_path.with_suffix('.html')}"
        )

    except Exception as error:
        print(f"HTML konnte nicht gespeichert werden: {error}")


def print_page_debug_info(page, url, response, error):
    """
    Gibt möglichst genaue Informationen zur fehlerhaften Seite aus.
    """
    print("\n==========================================")
    print("FEHLER BEIM LADEN DER TABELLE")
    print("==========================================")

    print(f"Aufgerufene URL: {url}")
    print(f"Aktuelle URL:    {page.url}")

    if response:
        print(f"HTTP-Status:     {response.status}")
    else:
        print("HTTP-Status:     nicht verfügbar")

    try:
        print(f"Seitentitel:     {page.title()}")
    except Exception:
        print("Seitentitel:     nicht verfügbar")

    try:
        print(f"Tabellen:        {page.locator('table').count()}")
        print(f"tbody-Elemente:  {page.locator('tbody').count()}")
        print(f"Tabellenzeilen:  {page.locator('tbody tr').count()}")
    except Exception:
        print("DOM-Informationen konnten nicht ermittelt werden.")

    try:
        body_text = page.locator("body").inner_text(timeout=5000)
        body_text = " ".join(body_text.split())

        if body_text:
            print(f"Seiteninhalt:    {body_text[:500]}")
        else:
            print("Seiteninhalt:    leer")

    except Exception:
        print("Seiteninhalt:    konnte nicht ausgelesen werden")

    print(f"Fehlertyp:       {type(error).__name__}")
    print(f"Fehlermeldung:   {error}")
    print("==========================================\n")


def load_page(page, url, name):
    """
    Lädt eine Seite und wartet auf Tabellenzeilen.

    Gibt True zurück, wenn die Tabelle gefunden wurde.
    Gibt False zurück, wenn ein Fehler aufgetreten ist.
    """
    response = None

    try:
        response = page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # "attached" bedeutet:
        # Die Tabellenzeile muss im DOM vorhanden sein,
        # aber nicht zwingend sichtbar dargestellt werden.
        page.wait_for_selector(
            "table tbody tr",
            state="attached",
            timeout=60000
        )

        return True

    except PlaywrightTimeoutError as error:
        print_page_debug_info(page, url, response, error)
        create_debug_files(page, name)
        return False

    except Exception as error:
        print_page_debug_info(page, url, response, error)
        create_debug_files(page, name)
        return False


def get_rows(page):
    """
    Liefert die Tabellenzeilen der ersten Tabelle,
    die tatsächlich tbody-Zeilen enthält.
    """
    tables = page.query_selector_all("table")

    for table in tables:
        rows = table.query_selector_all("tbody tr")

        if rows:
            return rows

    return []


# ==========================================
# ===== SPIELPLAN: STARTSEITE =============
# ==========================================

def scrape_spielplan_startseite(page, url, name):

    spiele = []

    if not load_page(page, url, name):
        return None

    rows = get_rows(page)

    for row in rows:
        cols = row.query_selector_all("td")

        # Startseite hat 7 Spalten
        if len(cols) < 7:
            continue

        ergebnis_raw = safe_text(cols, 6).strip()
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

def scrape_spielplan_mannschaft(page, url, name):

    spiele = []

    if not load_page(page, url, name):
        return None

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

def scrape_tabelle(page, url, name):

    daten = []

    if not load_page(page, url, name):
        return None

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
    output_dir = Path("assets/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(
        output_dir / f"{filename}.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


# ==========================================
# ===== LINKS JSON SPEICHERN ===============
# ==========================================

def save_links_json():
    """
    Speichert alle URLs zentral in einer JSON-Datei.
    """
    data = {
        "spielplaene": SPIELPLAENE,
        "tabellen": TABELLEN,
        "links": LINKS
    }

    output_dir = Path("assets/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(
        output_dir / "links.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


# ==========================================
# ===== MAIN ===============================
# ==========================================

def main():

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={
                "width": 1920,
                "height": 1080
            }
        )

        # ======================================
        # ===== SPIELPLÄNE =====================
        # ======================================

        for plan in SPIELPLAENE:

            name = plan["name"]
            url = plan["url"]

            print(f"Scrape: {name}")

            if plan["type"] == "startseite":
                daten = scrape_spielplan_startseite(
                    page,
                    url,
                    name
                )

            elif plan["type"] == "mannschaft":
                daten = scrape_spielplan_mannschaft(
                    page,
                    url,
                    name
                )

            else:
                print(
                    f"Unbekannter Spielplan-Typ: "
                    f"{plan.get('type')}"
                )
                continue

            if daten is None:
                print(
                    f"{name} konnte nicht geladen werden. "
                    f"Vorhandene JSON-Datei bleibt unverändert."
                )
                continue

            save_json(daten, name)

            print(
                f"{name} gespeichert "
                f"({len(daten)} Spiele)"
            )

        # ======================================
        # ===== TABELLEN =======================
        # ======================================

        for tabelle in TABELLEN:

            name = tabelle["name"]
            url = tabelle["url"]

            print(f"Scrape Tabelle: {name}")

            daten = scrape_tabelle(
                page,
                url,
                name
            )

            if daten is None:
                print(
                    f"{name} konnte nicht geladen werden. "
                    f"Vorhandene JSON-Datei bleibt unverändert."
                )
                continue

            save_json(daten, name)

            print(
                f"{name} gespeichert "
                f"({len(daten)} Einträge)"
            )

        # ======================================
        # ===== LINKS JSON =====================
        # ======================================

        print("Speichere zentrale Link-JSON...")

        save_links_json()

        print("links.json gespeichert")

        browser.close()


# ==========================================
# ===== SCRIPT START =======================
# ==========================================

if __name__ == "__main__":
    main()
