from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)
from pathlib import Path
from datetime import datetime
import json
import re

from config import (
    SPIELPLAENE,
    TABELLEN,
    SPIELERLISTEN,
    LINKS
)


# ==========================================
# ===== HILFSFUNKTIONEN ====================
# ==========================================

def safe_text(cols, index):
    """
    Gibt den Text einer Tabellenzelle sicher zurück.
    Verhindert Index-Fehler bei fehlenden Spalten.
    """
    if index is None or index >= len(cols):
        return ""

    return cols[index].inner_text().strip()


def normalize_header(text):
    """
    Vereinheitlicht Tabellenüberschriften für die spätere Zuordnung.

    Beispiele:
    ' QTTR ' -> 'qttr'
    'Name'    -> 'name'
    """
    return " ".join(text.lower().split())


def create_filename(name):
    """
    Wandelt einen lesbaren Namen in lowerCamelCase um.

    Beispiele:
    'Spiele Herren 1'   -> 'spieleHerren1'
    'Tabelle Herren 1'  -> 'tabelleHerren1'
    'Spieler Jugend 19' -> 'spielerJugend19'
    """
    parts = re.findall(
        r"[A-Za-zÄÖÜäöüß0-9]+",
        name
    )

    if not parts:
        return "daten"

    first_part = parts[0].lower()

    remaining_parts = "".join(
        part[:1].upper() + part[1:]
        for part in parts[1:]
    )

    return first_part + remaining_parts


def create_debug_files(page, name):
    """
    Speichert bei einem Fehler einen Screenshot und den HTML-Inhalt
    der aktuell geladenen Seite.
    """
    debug_dir = Path("debug")
    debug_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_name = create_filename(name)
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    base_path = debug_dir / f"{safe_name}_{timestamp}"

    screenshot_path = base_path.with_suffix(".png")
    html_path = base_path.with_suffix(".html")

    try:
        page.screenshot(
            path=str(screenshot_path),
            full_page=True
        )

        print(
            f"Debug-Screenshot gespeichert: "
            f"{screenshot_path}"
        )

    except Exception as error:
        print(
            f"Screenshot konnte nicht gespeichert werden: "
            f"{error}"
        )

    try:
        html_path.write_text(
            page.content(),
            encoding="utf-8"
        )

        print(
            f"Debug-HTML gespeichert: "
            f"{html_path}"
        )

    except Exception as error:
        print(
            f"HTML konnte nicht gespeichert werden: "
            f"{error}"
        )


def print_page_debug_info(
    page,
    url,
    response,
    error
):
    """
    Gibt möglichst genaue Informationen zur fehlerhaften Seite aus.
    """
    print()
    print("==========================================")
    print("FEHLER BEIM LADEN DER SEITE")
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
        print(
            f"Tabellen:        "
            f"{page.locator('table').count()}"
        )

        print(
            f"tbody-Elemente:  "
            f"{page.locator('tbody').count()}"
        )

        print(
            f"Tabellenzeilen:  "
            f"{page.locator('tbody tr').count()}"
        )

    except Exception:
        print(
            "DOM-Informationen konnten nicht "
            "ermittelt werden."
        )

    try:
        body_text = page.locator("body").inner_text(
            timeout=5000
        )

        body_text = " ".join(
            body_text.split()
        )

        if body_text:
            print(
                f"Seiteninhalt:    "
                f"{body_text[:500]}"
            )
        else:
            print("Seiteninhalt:    leer")

    except Exception:
        print(
            "Seiteninhalt:    "
            "konnte nicht ausgelesen werden"
        )

    print(f"Fehlertyp:       {type(error).__name__}")
    print(f"Fehlermeldung:   {error}")

    print("==========================================")
    print()


def load_page(
    page,
    url,
    name,
    table_type="standard"
):
    """
    Lädt eine Seite und wartet auf die benötigte Tabelle.

    table_type:
    - standard: normale Spielplan- oder Ligatabelle
    - spieler: Meldungstabelle mit Rang, QTTR und Name

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

        if response and response.status >= 400:
            raise RuntimeError(
                f"Die Seite antwortete mit HTTP-Status "
                f"{response.status}."
            )

        if table_type == "spieler":
            page.wait_for_function(
                """
                () => {
                    const tables =
                        Array.from(
                            document.querySelectorAll("table")
                        );

                    return tables.some((table) => {
                        const headers =
                            Array.from(
                                table.querySelectorAll(
                                    "thead th, tr th"
                                )
                            ).map((header) =>
                                header.textContent
                                    .trim()
                                    .toLowerCase()
                            );

                        const hasRequiredHeaders =
                            headers.includes("rang") &&
                            headers.includes("qttr") &&
                            headers.includes("name");

                        const hasRows =
                            table.querySelector("tbody tr") !== null;

                        return (
                            hasRequiredHeaders &&
                            hasRows
                        );
                    });
                }
                """,
                timeout=60000
            )

        else:
            page.wait_for_selector(
                "table tbody tr",
                state="attached",
                timeout=60000
            )

        return True

    except PlaywrightTimeoutError as error:
        print_page_debug_info(
            page,
            url,
            response,
            error
        )

        create_debug_files(
            page,
            name
        )

        return False

    except Exception as error:
        print_page_debug_info(
            page,
            url,
            response,
            error
        )

        create_debug_files(
            page,
            name
        )

        return False


def get_rows(page):
    """
    Liefert die Tabellenzeilen der ersten Tabelle,
    die tatsächlich tbody-Zeilen enthält.
    """
    tables = page.query_selector_all("table")

    for table in tables:
        rows = table.query_selector_all(
            "tbody tr"
        )

        if rows:
            return rows

    return []


def get_player_table(page):
    """
    Sucht gezielt nach der Meldungstabelle mit den Spalten:

    - Rang
    - QTTR
    - Name

    Gibt die Zeilen und die zugehörigen Spaltenpositionen zurück.
    """
    tables = page.query_selector_all("table")

    for table in tables:
        headers = table.query_selector_all(
            "thead th"
        )

        if not headers:
            headers = table.query_selector_all(
                "tr th"
            )

        header_names = [
            normalize_header(
                header.inner_text()
            )
            for header in headers
        ]

        required_headers = {
            "rang",
            "qttr",
            "name"
        }

        if not required_headers.issubset(
            set(header_names)
        ):
            continue

        column_indexes = {
            header_name: index
            for index, header_name
            in enumerate(header_names)
        }

        rows = table.query_selector_all(
            "tbody tr"
        )

        if rows:
            return rows, column_indexes

    return [], {}


# ==========================================
# ===== SPIELPLAN: STARTSEITE =============
# ==========================================

def scrape_spielplan_startseite(
    page,
    url,
    name
):
    spiele = []

    if not load_page(
        page,
        url,
        name
    ):
        return None

    rows = get_rows(page)

    for row in rows:
        cols = row.query_selector_all("td")

        # Startseite hat 7 Spalten
        if len(cols) < 7:
            continue

        ergebnis_raw = safe_text(
            cols,
            6
        )

        ergebnis = ergebnis_raw or None

        spiele.append({
            "datum": safe_text(cols, 0),
            "uhrzeit": safe_text(cols, 1),
            "spielort": safe_text(cols, 2),
            "klasse": safe_text(cols, 3),
            "heim": safe_text(cols, 4),
            "gast": safe_text(cols, 5),
            "ergebnis": ergebnis,
            "status": (
                "gespielt"
                if ergebnis_raw
                else "geplant"
            )
        })

    return spiele


# ==========================================
# ===== SPIELPLAN: MANNSCHAFT =============
# ==========================================

def scrape_spielplan_mannschaft(
    page,
    url,
    name
):
    spiele = []

    if not load_page(
        page,
        url,
        name
    ):
        return None

    rows = get_rows(page)

    for row in rows:
        cols = row.query_selector_all("td")

        # Mannschaftsseite hat 6 Spalten
        if len(cols) < 6:
            continue

        ergebnis_raw = safe_text(
            cols,
            5
        )

        ergebnis = ergebnis_raw or None

        spiele.append({
            "datum": safe_text(cols, 0),
            "uhrzeit": safe_text(cols, 1),
            "spielort": safe_text(cols, 2),
            "heim": safe_text(cols, 3),
            "gast": safe_text(cols, 4),
            "ergebnis": ergebnis,
            "status": (
                "gespielt"
                if ergebnis_raw
                else "geplant"
            )
        })

    return spiele


# ==========================================
# ===== TABELLEN ===========================
# ==========================================

def scrape_tabelle(
    page,
    url,
    name
):
    daten = []

    if not load_page(
        page,
        url,
        name
    ):
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
# ===== SPIELERLISTEN ======================
# ==========================================

def scrape_spielerliste(
    page,
    url,
    name,
    bereich
):
    """
    Liest die Meldungstabelle aus und gruppiert die Spieler
    anhand ihres Rangs nach Mannschaften.

    Beispiele:

    Rang 1.1 -> Herren 1, Position 1
    Rang 2.4 -> Herren 2, Position 4

    Bei der Jugend:

    Rang 1.1 -> Jugend 19 1, Position 1
    Rang 2.3 -> Jugend 19 2, Position 3
    """
    if not load_page(
        page,
        url,
        name,
        table_type="spieler"
    ):
        return None

    rows, columns = get_player_table(page)

    if not rows:
        print(
            f"Keine Meldungstabelle für "
            f"{name} gefunden."
        )

        return None

    rang_index = columns.get("rang")
    qttr_index = columns.get("qttr")
    name_index = columns.get("name")
    a_index = columns.get("a")
    status_index = columns.get("status")

    if (
        rang_index is None or
        qttr_index is None or
        name_index is None
    ):
        print(
            f"Die benötigten Spalten für "
            f"{name} wurden nicht gefunden."
        )

        return None

    mannschaften = {}

    for row in rows:
        cols = row.query_selector_all("td")

        rang = safe_text(
            cols,
            rang_index
        )

        qttr = safe_text(
            cols,
            qttr_index
        )

        spieler_name = safe_text(
            cols,
            name_index
        )

        a_vermerk = safe_text(
            cols,
            a_index
        )

        status = safe_text(
            cols,
            status_index
        )

        if not rang or not spieler_name:
            continue

        # Sucht zum Beispiel:
        # 1.1, 1.2, 2.1, 3.4
        rang_match = re.search(
            r"(\d+)\s*\.\s*(\d+)",
            rang
        )

        if not rang_match:
            print(
                f"Ungültiger Rang übersprungen: "
                f"{rang} ({spieler_name})"
            )

            continue

        mannschaft_nummer = rang_match.group(1)
        position = rang_match.group(2)

        mannschaft_name = (
            f"{bereich} "
            f"{mannschaft_nummer}"
        )

        spieler = {
            "rang": rang,
            "position": position,
            "name": spieler_name,
            "qttr": qttr or None,
            "a": a_vermerk or None,
            "status": status or None
        }

        if mannschaft_name not in mannschaften:
            mannschaften[mannschaft_name] = []

        mannschaften[mannschaft_name].append(
            spieler
        )

    return mannschaften


# ==========================================
# ===== JSON SPEICHERN =====================
# ==========================================

def save_json(data, filename):
    """
    Speichert Daten als JSON-Datei.

    Der Dateiname wird automatisch in lowerCamelCase umgewandelt.

    Beispiel:
    'Spieler Jugend 19' -> 'spielerJugend19.json'
    """
    output_dir = Path("assets/data")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    formatted_filename = create_filename(
        filename
    )

    file_path = (
        output_dir /
        f"{formatted_filename}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return file_path


# ==========================================
# ===== LINKS JSON SPEICHERN ===============
# ==========================================

def save_links_json():
    """
    Speichert alle URLs zentral in der links.json.
    """
    data = {
        "spielplaene": SPIELPLAENE,
        "tabellen": TABELLEN,
        "spielerlisten": SPIELERLISTEN,
        "links": LINKS
    }

    output_dir = Path("assets/data")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = output_dir / "links.json"

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return file_path


# ==========================================
# ===== MAIN ===============================
# ==========================================

def main():
    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True
        )

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
            plan_type = plan["type"]

            print()
            print(f"Scrape Spielplan: {name}")

            if plan_type == "startseite":
                daten = scrape_spielplan_startseite(
                    page,
                    url,
                    name
                )

            elif plan_type == "mannschaft":
                daten = scrape_spielplan_mannschaft(
                    page,
                    url,
                    name
                )

            else:
                print(
                    f"Unbekannter Spielplan-Typ: "
                    f"{plan_type}"
                )

                continue

            if daten is None:
                print(
                    f"{name} konnte nicht geladen werden. "
                    f"Vorhandene JSON-Datei bleibt "
                    f"unverändert."
                )

                continue

            file_path = save_json(
                daten,
                name
            )

            print(
                f"{file_path.name} gespeichert "
                f"({len(daten)} Spiele)"
            )

        # ======================================
        # ===== TABELLEN =======================
        # ======================================

        for tabelle in TABELLEN:
            name = tabelle["name"]
            url = tabelle["url"]

            print()
            print(f"Scrape Tabelle: {name}")

            daten = scrape_tabelle(
                page,
                url,
                name
            )

            if daten is None:
                print(
                    f"{name} konnte nicht geladen werden. "
                    f"Vorhandene JSON-Datei bleibt "
                    f"unverändert."
                )

                continue

            file_path = save_json(
                daten,
                name
            )

            print(
                f"{file_path.name} gespeichert "
                f"({len(daten)} Einträge)"
            )

        # ======================================
        # ===== SPIELERLISTEN ==================
        # ======================================

        for spielerliste in SPIELERLISTEN:
            name = spielerliste["name"]
            url = spielerliste["url"]
            bereich = spielerliste["bereich"]

            print()
            print(f"Scrape Spielerliste: {name}")

            daten = scrape_spielerliste(
                page,
                url,
                name,
                bereich
            )

            if daten is None:
                print(
                    f"{name} konnte nicht geladen werden. "
                    f"Vorhandene JSON-Datei bleibt "
                    f"unverändert."
                )

                continue

            if not daten:
                print(
                    f"{name} enthält keine Spieler. "
                    f"Vorhandene JSON-Datei bleibt "
                    f"unverändert."
                )

                continue

            file_path = save_json(
                daten,
                name
            )

            spieler_anzahl = sum(
                len(spieler)
                for spieler in daten.values()
            )

            print(
                f"{file_path.name} gespeichert "
                f"({len(daten)} Mannschaften, "
                f"{spieler_anzahl} Spieler)"
            )

        # ======================================
        # ===== LINKS JSON =====================
        # ======================================

        print()
        print("Speichere zentrale Link-JSON...")

        links_path = save_links_json()

        print(
            f"{links_path.name} gespeichert"
        )

        browser.close()

        print()
        print("Scraping vollständig abgeschlossen.")


# ==========================================
# ===== SCRIPT START =======================
# ==========================================

if __name__ == "__main__":
    main()
