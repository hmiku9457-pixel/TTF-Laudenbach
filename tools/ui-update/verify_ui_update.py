from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors: list[str] = []


def require(path: str, needle: str, description: str) -> None:
    file_path = ROOT / path
    if not file_path.is_file():
        errors.append(f"Datei fehlt: {path}")
        return
    content = file_path.read_text(encoding="utf-8")
    if needle not in content:
        errors.append(f"{description}: {path}")


require("assets/css/main.css", '@import url("./components/ui-fixes.css");', "UI-CSS wird nicht importiert")
require("assets/css/components/ui-fixes.css", "table-mobile-cards--league", "Mobile Ligatabellen fehlen")
require("assets/css/site.bundle.css", "Gesammelte UI-Korrekturen August 2026", "CSS-Bundle ist nicht aktuell")
require("assets/js/core/page-structure.js", "navigationArmed", "Zwei-Klick-Dropdown fehlt")
require("assets/js/features/news-slider.js", "news-slider__footer", "Gemeinsame News-Fußzeile fehlt")
require("assets/js/features/tables.js", "decorateTableCells", "Mobile Tabellenbeschriftungen fehlen")
require("assets/js/features/gallery.js", "images-nav-toggle", "Mobiles Galeriepanel fehlt")
require("pages/unserVerein.html", "table--emphasis-first-column", "Tabellenhervorhebung fehlt")
require("pages/dokumente/historischeFotos.html", "images-page__banner", "Galeriebanner fehlt")

bundle = ROOT / "assets/css/site.bundle.css"
if bundle.is_file() and "@import" in bundle.read_text(encoding="utf-8"):
    errors.append("site.bundle.css enthält noch lokale @import-Regeln")

historical = ROOT / "pages/dokumente/historischeFotos.html"
if historical.is_file():
    content = historical.read_text(encoding="utf-8")
    banner = content.find("images-page__banner")
    gallery = content.find("images-content")
    if banner < 0 or gallery < 0 or banner > gallery:
        errors.append("Der Banner 'Historische Fotos' steht nicht vor dem Galerieinhalt")

if errors:
    print("UI-Update-Prüfung fehlgeschlagen:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("UI-Update-Prüfung erfolgreich.")
