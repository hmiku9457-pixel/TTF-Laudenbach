from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = Path(__file__).with_name("payload.zip")
MAIN_CSS = ROOT / "assets/css/main.css"
TABLES_JS = ROOT / "assets/js/features/tables.js"
GALLERY_JS = ROOT / "assets/js/features/gallery.js"
CSS_BUILDER = ROOT / "tools/review-upgrade/build_css.py"
FINAL_IMPORT = '@import url("./components/ui-final.css");'


NEXT_AND_SCHEDULE_FUNCTIONS = r'''
function prepareNextGamesTable(table) {
    const headerRow = table.tHead?.rows?.[0];

    if (headerRow) {
        ensureDualHeaderLabel(headerRow.cells[0], "Dat.");
        ensureDualHeaderLabel(headerRow.cells[1], "Zeit");
        ensureDualHeaderLabel(headerRow.cells[2], "Team");
        ensureDualHeaderLabel(headerRow.cells[3], "Geg.");
        ensureDualHeaderLabel(headerRow.cells[4], "H/A");
        ensureDualHeaderLabel(headerRow.cells[5], "Erg.");
    }

    const targetId = table.tBodies?.[0]?.id || "next-games";

    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)")
        .forEach((row, rowIndex) => {
            const cells = Array.from(row.cells);

            if (cells.length < 6) {
                return;
            }

            ensureDualValue(
                cells[0],
                compactDate(normalizedCellText(cells[0]))
            );
            ensureDualValue(
                cells[2],
                abbreviateTeam(normalizedCellText(cells[2]))
            );
            ensureVenueCell(cells[4], targetId, rowIndex);
        });
}

function prepareScheduleTable(table) {
    const headerRow = table.tHead?.rows?.[0];

    if (!headerRow) {
        return;
    }

    const desktopHeaders = Array.from(headerRow.cells)
        .filter(cell => !cell.classList.contains("table-mobile-only"));

    if (desktopHeaders.length < 5) {
        return;
    }

    ensureDualHeaderLabel(desktopHeaders[0], "Dat.");
    ensureDualHeaderLabel(desktopHeaders[1], "Zeit");
    ensureDualHeaderLabel(desktopHeaders[4], "Erg.");

    let opponentHeader = headerRow.querySelector(
        ".table-mobile-only--schedule-opponent"
    );
    let venueHeader = headerRow.querySelector(
        ".table-mobile-only--schedule-venue"
    );

    if (!opponentHeader) {
        opponentHeader = document.createElement("th");
        opponentHeader.scope = "col";
        opponentHeader.className =
            "table-mobile-only table-mobile-only--schedule-opponent";
        opponentHeader.textContent = "Geg.";
        headerRow.insertBefore(opponentHeader, desktopHeaders[2]);
    }

    if (!venueHeader) {
        venueHeader = document.createElement("th");
        venueHeader.scope = "col";
        venueHeader.className =
            "table-mobile-only table-mobile-only--schedule-venue";
        venueHeader.textContent = "H/A";
        headerRow.insertBefore(venueHeader, desktopHeaders[2]);
    }

    const targetId = table.tBodies?.[0]?.id || "schedule";

    table.tBodies[0]?.querySelectorAll("tr:not(.table-status-row)")
        .forEach((row, rowIndex) => {
            const desktopCells = Array.from(row.cells)
                .filter(cell => !cell.classList.contains("table-mobile-only"));

            if (desktopCells.length < 5) {
                return;
            }

            ensureDualValue(
                desktopCells[0],
                compactDate(normalizedCellText(desktopCells[0]))
            );

            let opponentCell = row.querySelector(
                ".table-mobile-only--schedule-opponent"
            );
            let venueCell = row.querySelector(
                ".table-mobile-only--schedule-venue"
            );

            if (!opponentCell) {
                opponentCell = document.createElement("td");
                opponentCell.className =
                    "table-mobile-only table-mobile-only--schedule-opponent";
                opponentCell.textContent = normalizedCellText(desktopCells[3]);
                row.insertBefore(opponentCell, desktopCells[2]);
            }

            if (!venueCell) {
                venueCell = document.createElement("td");
                venueCell.className =
                    "table-mobile-only table-mobile-only--schedule-venue";
                venueCell.textContent = normalizedCellText(desktopCells[2]);
                row.insertBefore(venueCell, desktopCells[2]);
            }

            ensureVenueCell(venueCell, targetId, rowIndex);
        });
}
'''


GALLERY_TOGGLE_HELPER = r'''
function configureGalleryToggle(toggle) {
    toggle.classList.remove("button");
    toggle.classList.add("images-nav-toggle");
    toggle.setAttribute("aria-label", "Galerien öffnen");

    const icon = document.createElement("span");
    icon.className = "images-nav-toggle__icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = "☰";

    const label = document.createElement("span");
    label.className = "images-nav-toggle__label";
    label.textContent = "Galerien";

    toggle.replaceChildren(icon, label);
}
'''


def safe_extract(zip_path: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()

    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()

            if (
                target != destination_resolved
                and destination_resolved not in target.parents
            ):
                raise RuntimeError(
                    f"Unsicherer Pfad im Payload: {member.filename}"
                )

        archive.extractall(destination)


def patch_tables() -> None:
    content = TABLES_JS.read_text(encoding="utf-8")

    content = re.sub(
        r"const COMPACT_TABLE_TYPES\s*=\s*new Set\([^;]*\);",
        'const COMPACT_TABLE_TYPES = '
        'new Set(["next-games", "league", "schedule"]);',
        content,
        count=1,
    )
    content = re.sub(
        r"const CARD_TABLE_TYPES\s*=\s*new Set\([^;]*\);",
        "const CARD_TABLE_TYPES = new Set();",
        content,
        count=1,
    )

    if '"table-compact-mobile--schedule"' not in content:
        content = content.replace(
            '"table-compact-mobile--league"',
            '"table-compact-mobile--league",\n'
            '        "table-compact-mobile--schedule"',
            1,
        )

    content = content.replace(
        '} else if (tableType === "schedule") {\n'
        '        decorateTableCells(table);\n'
        '    }',
        '} else if (tableType === "schedule") {\n'
        '        prepareScheduleTable(table);\n'
        '    }',
        1,
    )

    start_marker = "function prepareNextGamesTable(table) {"
    end_marker = "function ensureDualHeaderLabel"

    start_index = content.find(start_marker)
    end_index = content.find(end_marker, start_index)

    if start_index < 0 or end_index < 0:
        raise RuntimeError(
            "Die Funktionen für die responsiven Spieltabellen "
            "konnten nicht gefunden werden."
        )

    content = (
        content[:start_index]
        + NEXT_AND_SCHEDULE_FUNCTIONS.strip()
        + "\n\n"
        + content[end_index:]
    )

    TABLES_JS.write_text(content, encoding="utf-8")


def patch_gallery() -> None:
    content = GALLERY_JS.read_text(encoding="utf-8")

    content = content.replace(
        'toggle.className = "button images-nav-toggle";',
        'toggle.className = "images-nav-toggle";',
        1,
    )
    content = content.replace(
        '        toggle.textContent = "Galerien öffnen";\n',
        "",
        1,
    )

    marker = (
        '        page.insertBefore(toggle, page.querySelector(".images-content"));\n'
        '    }\n'
    )

    if "configureGalleryToggle(toggle);" not in content:
        if marker not in content:
            raise RuntimeError(
                "Der Galerie-Öffnen-Button konnte nicht gefunden werden."
            )

        content = content.replace(
            marker,
            marker + "    configureGalleryToggle(toggle);\n",
            1,
        )

    if "function configureGalleryToggle" not in content:
        helper_marker = "\nfunction getImageAlt("

        if helper_marker not in content:
            raise RuntimeError(
                "Einfügeposition für den Galerie-Button fehlt."
            )

        content = content.replace(
            helper_marker,
            "\n" + GALLERY_TOGGLE_HELPER.strip()
            + "\n\nfunction getImageAlt(",
            1,
        )

    GALLERY_JS.write_text(content, encoding="utf-8")


def ensure_css_import() -> None:
    content = MAIN_CSS.read_text(encoding="utf-8")
    lines = [
        line
        for line in content.splitlines()
        if line.strip() != FINAL_IMPORT
    ]

    while lines and not lines[-1].strip():
        lines.pop()

    lines.extend([FINAL_IMPORT, ""])
    MAIN_CSS.write_text("\n".join(lines), encoding="utf-8")


def build_css_bundle() -> None:
    if not CSS_BUILDER.is_file():
        raise FileNotFoundError(
            f"Zentraler CSS-Builder fehlt: {CSS_BUILDER}"
        )

    subprocess.run(
        [sys.executable, str(CSS_BUILDER)],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    if not PAYLOAD.is_file():
        raise FileNotFoundError(f"Payload fehlt: {PAYLOAD}")

    safe_extract(PAYLOAD, ROOT)
    patch_tables()
    patch_gallery()
    ensure_css_import()
    build_css_bundle()

    print(
        "Finale Designkorrekturen angewendet und CSS-Bundle neu erzeugt."
    )


if __name__ == "__main__":
    main()
