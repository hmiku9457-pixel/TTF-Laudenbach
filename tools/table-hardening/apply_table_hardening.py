#!/usr/bin/env python3
"""Gezielte Tabellen-Härtung für TTF-Laudenbach (Priorität B).

Änderungen:
- semantische Spaltenklassen für Compact-Tabellen
- nth-child-Abhängigkeiten aus Compact-Tabellen-CSS entfernen
- Statuszeilen gegen Spaltenbreiten absichern
- H/A-Tooltip-ARIA ohne doppelte Ansage strukturieren

Das Script ist idempotent und verändert ausschließlich:
- assets/js/features/table-responsive.js
- assets/css/components/tables.css
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
JS_PATH = ROOT / "assets/js/features/table-responsive.js"
CSS_PATH = ROOT / "assets/css/components/tables.css"

COLUMN_CONSTANTS = '''const LEAGUE_COLUMN_NAMES = [
    "rank",
    "team",
    "matches",
    "wins",
    "draws",
    "losses",
    "games",
    "difference",
    "points"
];
const NEXT_GAMES_COLUMN_NAMES = [
    "date",
    "time",
    "team",
    "opponent",
    "venue",
    "result"
];
const SCHEDULE_COLUMN_NAMES = [
    "date",
    "time",
    "venue",
    "opponent",
    "result"
];
'''

SEMANTIC_CSS = '''    /* Ligatabelle: Rang | Team | S-U-N | Spiele | +/- | Punkte */
    table.table-compact-mobile--league .table-mobile-only {
        display: table-cell;
    }

    table.table-compact-mobile--league .table-col--matches,
    table.table-compact-mobile--league .table-col--wins,
    table.table-compact-mobile--league .table-col--draws,
    table.table-compact-mobile--league .table-col--losses {
        display: none;
    }

    table.table-compact-mobile--league .table-col--rank {
        width: 8%;
        text-align: left;
    }

    table.table-compact-mobile--league .table-col--team {
        width: 35%;
        text-align: left;
    }

    table.table-compact-mobile--league .table-col--record {
        width: 14%;
        text-align: center;
        white-space: nowrap;
    }

    table.table-compact-mobile--league .table-col--games {
        width: 16%;
        text-align: center;
        white-space: nowrap;
    }

    table.table-compact-mobile--league .table-col--difference {
        width: 11%;
        text-align: center;
        white-space: nowrap;
    }

    table.table-compact-mobile--league .table-col--points {
        width: 16%;
        text-align: right;
        white-space: nowrap;
    }

    /* Startseite: Dat. | Zeit | Team | Geg. | H/A | Erg. */
    table.table-compact-mobile--next-games .table-col--date {
        width: 18%;
        text-align: left;
    }

    table.table-compact-mobile--next-games .table-col--time {
        width: 14%;
        text-align: center;
        white-space: nowrap;
    }

    table.table-compact-mobile--next-games .table-col--team {
        width: 13%;
        text-align: left;
        white-space: nowrap;
    }

    table.table-compact-mobile--next-games .table-col--opponent {
        width: 31%;
        text-align: left;
    }

    table.table-compact-mobile--next-games .table-col--venue {
        width: 10%;
        overflow: visible;
        text-align: center;
    }

    table.table-compact-mobile--next-games .table-col--result {
        width: 14%;
        text-align: right;
        white-space: nowrap;
    }

    /* Mannschaftsspielplan: Dat. | Zeit | Geg. | H/A | Erg. */
    table.table-compact-mobile--schedule .table-mobile-only {
        display: table-cell;
    }

    table.table-compact-mobile--schedule .table-col--venue:not(.table-mobile-only),
    table.table-compact-mobile--schedule .table-col--opponent:not(.table-mobile-only) {
        display: none;
    }

    table.table-compact-mobile--schedule .table-col--date {
        width: 19%;
        text-align: left;
    }

    table.table-compact-mobile--schedule .table-col--time {
        width: 15%;
        text-align: center;
        white-space: nowrap;
    }

    table.table-compact-mobile--schedule .table-mobile-only.table-col--opponent {
        width: 38%;
        text-align: left;
    }

    table.table-compact-mobile--schedule .table-mobile-only.table-col--venue {
        width: 11%;
        overflow: visible;
        text-align: center;
    }

    table.table-compact-mobile--schedule .table-col--result {
        width: 17%;
        text-align: right;
        white-space: nowrap;
    }

'''


def fail(message: str) -> None:
    raise RuntimeError(message)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new, 1)
    if count == 0 and new in text:
        return text
    fail(f"{label}: erwarteter Ausgangsblock wurde nicht eindeutig gefunden (Treffer: {count}).")


def patch_js(text: str) -> str:
    supported = 'const SUPPORTED_TABLE_TYPES = new Set(["next-games", "league", "schedule"]);\n'
    if "const LEAGUE_COLUMN_NAMES" not in text:
        text = replace_once(
            text,
            supported,
            supported + "\n" + COLUMN_CONSTANTS,
            "Spaltenkonstanten"
        )

    league_start = '''    ensureDualHeaderLabel(headerRow.cells[1], "Team");

    let recordHeader = headerRow.querySelector(".table-mobile-only--record");'''
    league_new = '''    const desktopHeaders = Array.from(headerRow.cells)
        .filter(cell => !cell.classList.contains("table-mobile-only"));
    if (desktopHeaders.length < LEAGUE_COLUMN_NAMES.length) {
        return;
    }

    applyColumnClasses(desktopHeaders, LEAGUE_COLUMN_NAMES);
    ensureDualHeaderLabel(desktopHeaders[1], "Team");

    let recordHeader = headerRow.querySelector(".table-mobile-only--record");'''
    text = replace_once(text, league_start, league_new, "League-Headerklassen")

    text = replace_once(
        text,
        'recordHeader.className = "table-mobile-only table-mobile-only--record";',
        'recordHeader.className = "table-mobile-only table-mobile-only--record table-col--record";',
        "League-Record-Headerklasse"
    )

    old_league_rows = '''    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)").forEach(row => {
        if (row.querySelector(".table-mobile-only--record")) {
            return;
        }

        const originalCells = Array.from(row.cells);
        if (originalCells.length < 9) {
            return;
        }

        const recordCell = document.createElement("td");
        recordCell.className = "table-mobile-only table-mobile-only--record";
        recordCell.textContent = [
            normalizedCellText(originalCells[3]),
            normalizedCellText(originalCells[4]),
            normalizedCellText(originalCells[5])
        ].join("-");

        row.insertBefore(recordCell, originalCells[2] || null);
    });'''
    new_league_rows = '''    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)").forEach(row => {
        const originalCells = Array.from(row.cells)
            .filter(cell => !cell.classList.contains("table-mobile-only"));
        if (originalCells.length < LEAGUE_COLUMN_NAMES.length) {
            return;
        }

        applyColumnClasses(originalCells, LEAGUE_COLUMN_NAMES);

        let recordCell = row.querySelector(".table-mobile-only--record");
        if (!recordCell) {
            recordCell = document.createElement("td");
            recordCell.className =
                "table-mobile-only table-mobile-only--record table-col--record";
            recordCell.textContent = [
                normalizedCellText(originalCells[3]),
                normalizedCellText(originalCells[4]),
                normalizedCellText(originalCells[5])
            ].join("-");
            row.insertBefore(recordCell, originalCells[2] || null);
        } else {
            recordCell.classList.add("table-col--record");
        }
    });'''
    text = replace_once(text, old_league_rows, new_league_rows, "League-Zellenklassen")

    next_headers = '''        ensureDualHeaderLabel(headerRow.cells[4], "H/A");
        ensureDualHeaderLabel(headerRow.cells[5], "Erg.");
    }'''
    next_headers_new = '''        ensureDualHeaderLabel(headerRow.cells[4], "H/A");
        ensureDualHeaderLabel(headerRow.cells[5], "Erg.");
        applyColumnClasses(Array.from(headerRow.cells), NEXT_GAMES_COLUMN_NAMES);
    }'''
    text = replace_once(text, next_headers, next_headers_new, "Next-Games-Headerklassen")

    next_rows = '''            if (cells.length < 6) {
                return;
            }

            ensureDualValue('''
    next_rows_new = '''            if (cells.length < NEXT_GAMES_COLUMN_NAMES.length) {
                return;
            }

            applyColumnClasses(cells, NEXT_GAMES_COLUMN_NAMES);

            ensureDualValue('''
    text = replace_once(text, next_rows, next_rows_new, "Next-Games-Zellenklassen")

    schedule_headers = '''    if (desktopHeaders.length < 5) {
        return;
    }

    ensureDualHeaderLabel(desktopHeaders[0], "Dat.");'''
    schedule_headers_new = '''    if (desktopHeaders.length < SCHEDULE_COLUMN_NAMES.length) {
        return;
    }

    applyColumnClasses(desktopHeaders, SCHEDULE_COLUMN_NAMES);
    ensureDualHeaderLabel(desktopHeaders[0], "Dat.");'''
    text = replace_once(text, schedule_headers, schedule_headers_new, "Schedule-Headerklassen")

    text = replace_once(
        text,
        'opponentHeader.className =\n            "table-mobile-only table-mobile-only--schedule-opponent";',
        'opponentHeader.className =\n            "table-mobile-only table-mobile-only--schedule-opponent table-col--opponent";',
        "Schedule-Opponent-Headerklasse"
    )
    text = replace_once(
        text,
        'venueHeader.className =\n            "table-mobile-only table-mobile-only--schedule-venue";',
        'venueHeader.className =\n            "table-mobile-only table-mobile-only--schedule-venue table-col--venue";',
        "Schedule-Venue-Headerklasse"
    )

    schedule_rows = '''            if (desktopCells.length < 5) {
                return;
            }

            ensureDualValue('''
    schedule_rows_new = '''            if (desktopCells.length < SCHEDULE_COLUMN_NAMES.length) {
                return;
            }

            applyColumnClasses(desktopCells, SCHEDULE_COLUMN_NAMES);

            ensureDualValue('''
    text = replace_once(text, schedule_rows, schedule_rows_new, "Schedule-Zellenklassen")

    text = replace_once(
        text,
        'opponentCell.className =\n                    "table-mobile-only table-mobile-only--schedule-opponent";',
        'opponentCell.className =\n                    "table-mobile-only table-mobile-only--schedule-opponent table-col--opponent";',
        "Schedule-Opponent-Zellenklasse"
    )
    text = replace_once(
        text,
        'venueCell.className =\n                    "table-mobile-only table-mobile-only--schedule-venue";',
        'venueCell.className =\n                    "table-mobile-only table-mobile-only--schedule-venue table-col--venue";',
        "Schedule-Venue-Zellenklasse"
    )

    old_venue = '''    const badgeText = isAway ? "A" : "H";
    const detailText = isAway
        ? "Auswärtsspiel – Spielort beim gegnerischen Verein"
        : `Heimspiel – ${fullLocation || "Spielort noch nicht bekannt"}`;
    const tooltipId = `venue-tooltip-${sanitizeId(tableId)}-${rowIndex + 1}`;'''
    new_venue = '''    const badgeText = isAway ? "A" : "H";
    const badgeLabel = isAway ? "A – Auswärtsspiel" : "H – Heimspiel";
    const tooltipText = isAway
        ? "Spielort beim gegnerischen Verein"
        : fullLocation || "Spielort noch nicht bekannt";
    const tooltipId = `venue-tooltip-${sanitizeId(tableId)}-${rowIndex + 1}`;'''
    text = replace_once(text, old_venue, new_venue, "H/A-ARIA-Texte")
    text = replace_once(
        text,
        'badge.setAttribute("aria-label", detailText);',
        'badge.setAttribute("aria-label", badgeLabel);',
        "H/A-ARIA-Label"
    )
    text = replace_once(
        text,
        'tooltip.textContent = detailText;',
        'tooltip.textContent = tooltipText;',
        "H/A-Tooltip-Text"
    )

    if "function applyColumnClasses(cells, columnNames)" not in text:
        helper_anchor = '''function normalizedCellText(cell) {
    return String(cell?.textContent || "").replace(/\\s+/g, " ").trim();
}'''
        helper = '''function applyColumnClasses(cells, columnNames) {
    cells.forEach((cell, index) => {
        Array.from(cell.classList)
            .filter(className => className.startsWith("table-col--"))
            .forEach(className => cell.classList.remove(className));

        const columnName = columnNames[index];
        if (columnName) {
            cell.classList.add(`table-col--${columnName}`);
        }
    });
}

function normalizedCellText(cell) {
    return String(cell?.textContent || "").replace(/\\s+/g, " ").trim();
}'''
        text = replace_once(text, helper_anchor, helper, "Spaltenklassen-Helfer")

    return text


def patch_css(text: str) -> str:
    old_status = '''.table-status-row td {
    text-align: center;
    font-weight: 500;
}'''
    new_status = '''.table-status-row td {
    width: auto;
    text-align: center;
    font-weight: 500;
    white-space: normal;
}'''
    text = replace_once(text, old_status, new_status, "Statuszeilen")

    start_marker = "    /* Ligatabelle: Rang | Team | S-U-N | Spiele | +/- | Punkte */"
    end_marker = "    table.table-compact-mobile .table-status-row {"
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end <= start:
        if ".table-col--record" not in text:
            fail("Compact-CSS: Bereich für semantische Selektoren nicht gefunden.")
    else:
        current = text[start:end]
        if ":nth-child(" in current or ".table-col--record" not in current:
            text = text[:start] + SEMANTIC_CSS + text[end:]

    return text


def validate(js: str, css: str) -> list[str]:
    errors: list[str] = []

    js_required = [
        "const LEAGUE_COLUMN_NAMES",
        "const NEXT_GAMES_COLUMN_NAMES",
        "const SCHEDULE_COLUMN_NAMES",
        "function applyColumnClasses",
        "table-col--record",
        "table-col--opponent",
        "table-col--venue",
        'badge.setAttribute("aria-label", badgeLabel);',
        'badge.setAttribute("aria-describedby", tooltipId);',
        "tooltip.textContent = tooltipText;",
    ]
    for needle in js_required:
        if needle not in js:
            errors.append(f"JS fehlt: {needle}")

    if 'badge.setAttribute("aria-label", detailText);' in js:
        errors.append("JS enthält noch das alte doppelte ARIA-Label.")

    css_required = [
        ".table-col--record",
        ".table-col--matches",
        ".table-col--opponent",
        ".table-col--venue",
        ".table-col--result",
        "width: auto;",
        "white-space: normal;",
    ]
    for needle in css_required:
        if needle not in css:
            errors.append(f"CSS fehlt: {needle}")

    compact_start = css.find("/* =========================================\n   ===== KOMPAKTE TABELLEN BIS 768 PX")
    compact_end = css.find("/* =========================================\n   ===== WEITERE MOBILE ANPASSUNGEN", compact_start)
    if compact_start == -1 or compact_end == -1:
        errors.append("Compact-CSS-Bereich konnte nicht abgegrenzt werden.")
    else:
        compact_css = css[compact_start:compact_end]
        if ":nth-child(" in compact_css:
            errors.append("Compact-CSS enthält weiterhin nth-child()-Selektoren.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Nur Zielzustand prüfen")
    args = parser.parse_args()

    if not JS_PATH.exists() or not CSS_PATH.exists():
        fail("Zieldateien fehlen. Script muss im Root des TTF-Laudenbach-Repositories laufen.")

    js = JS_PATH.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")

    if not args.check:
        js = patch_js(js)
        css = patch_css(css)
        JS_PATH.write_text(js, encoding="utf-8")
        CSS_PATH.write_text(css, encoding="utf-8")

    errors = validate(js, css)
    if errors:
        print("Tabellen-Härtung ist nicht vollständig:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.check:
        print("Tabellen-Härtung: Zielzustand ist vollständig.")
    else:
        print("Tabellen-Härtung erfolgreich angewendet.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        raise SystemExit(1)
