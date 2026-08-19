from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def section(text, start, end):
    require(start in text, f"Startmarker fehlt: {start}")
    require(end in text, f"Endmarker fehlt: {end}")
    return text.split(start, 1)[1].split(end, 1)[0]


def check_json_list(relative):
    path = ROOT / relative
    require(path.exists(), f"JSON fehlt: {relative}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, list), f"{relative} enthält keine JSON-Liste.")


def main():
    index = read("index.html")
    main_js = read("assets/js/main.js")
    configs = read("assets/js/config/table-configs.js")
    responsive = read("assets/js/features/table-responsive.js")
    css = read("assets/css/components/tables.css")
    feature = read("assets/js/features/home-games.js")

    require('id="home-games-tabs"' in index, "Umschalt-Überschrift fehlt.")
    require('data-home-games-view="upcoming"' in index, "Nächste-Spiele-Umschalter fehlt.")
    require('data-home-games-view="past"' in index, "Vergangene-Spiele-Umschalter fehlt.")
    require('id="spiele-startseite"' in index, "tbody für kommende Spiele fehlt.")
    require('id="spiele-vergangen"' in index, "tbody für vergangene Spiele fehlt.")

    upcoming = section(index, 'id="home-games-upcoming"', 'id="home-games-past"')
    require("<th scope=\"col\">Ergebnis</th>" not in upcoming,
            "Die kommende Tabelle enthält noch die Ergebnis-Spalte.")
    require(upcoming.count('<th scope="col">') == 5,
            "Die kommende Tabelle muss genau 5 Spalten haben.")

    past = section(index, 'id="home-games-past"', "</div>\n</div>")
    require("<th scope=\"col\">Ergebnis</th>" in past,
            "Die vergangene Tabelle benötigt die Ergebnis-Spalte.")
    require(past.count('<th scope="col">') == 6,
            "Die vergangene Tabelle muss genau 6 Spalten haben.")

    require(
        'loadFeature("./features/home-games.js", "initHomeGames")' in main_js,
        "home-games.js wird in main.js nicht initialisiert."
    )

    require("spiele-startseite" not in configs,
            "Die alte Startseiten-Tabellenkonfiguration ist noch aktiv.")
    require("spieleStartseite.json" not in configs,
            "spieleStartseite.json darf nicht mehr von tables.js geladen werden.")
    require("getErgebnis" not in configs and "getMannschaft" not in configs,
            "Ungenutzte Startseiten-Formatter sind noch importiert.")

    require('const PRIMARY_GAMES_URL = "/assets/data/spieleStartseite.json";' in feature,
            "Primäre Startseitenquelle fehlt.")
    require("const FALLBACK_LIMIT = 8;" in feature,
            "Fallback-Limit ist nicht 8.")
    require('emptyMessage: "Keine kommenden Spiele in den nächsten Wochen"' in feature,
            "Gewünschter zweiter Fallback-Text fehlt.")
    require(".slice(0, FALLBACK_LIMIT)" in feature,
            "8er-Begrenzung für Fallback/History fehlt.")
    require("formatErgebnis" in feature,
            "Ergebnisformatierung für vergangene Spiele fehlt.")
    require("hasResult(game)" in feature,
            "Vergangene Spiele werden nicht auf vorhandenes Ergebnis geprüft.")
    require("...primary.data" in feature and "...teamData.games" in feature,
            "Vergangene Spiele müssen Primär- und Mannschafts-JSONs zusammenführen.")

    expected_sources = [
        "spieleHerren1.json",
        "spieleHerren2.json",
        "spieleHerren3.json",
        "spieleHerren4.json",
        "spieleHerren5.json",
        "spieleJugend1.json",
        "spieleJugend2.json",
    ]
    for filename in expected_sources:
        require(filename in feature, f"Fallback-Quelle fehlt: {filename}")

    require("if (cells.length < 5)" in responsive,
            "Responsive-Logik unterstützt die 5-spaltige kommende Tabelle nicht.")
    require("NEXT_GAMES_COLUMN_NAMES" in responsive,
            "Spaltenzuordnung für die Startseitentabelle fehlt.")

    require("STARTSEITE: NÄCHSTE / VERGANGENE SPIELE" in css,
            "CSS für den Umschalter fehlt.")
    require(".home-games-tab.is-active" in css,
            "Aktive Ansicht wird optisch nicht hervorgehoben.")

    check_json_list("assets/data/spieleStartseite.json")
    for filename in expected_sources:
        check_json_list(f"assets/data/{filename}")

    print("Alle Prüfungen für das Startseiten-Spiele-Update sind erfolgreich.")


if __name__ == "__main__":
    main()
