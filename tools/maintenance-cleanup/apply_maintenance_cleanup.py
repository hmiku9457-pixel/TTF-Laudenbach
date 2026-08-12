#!/usr/bin/env python3
"""Wartbarkeits-Cleanup für die TTF-Laudenbach-Webseite.

Das Skript ist absichtlich dauerhaft und idempotent aufgebaut. Es löscht sich
nicht selbst und kann erneut ausgeführt werden.

Änderungen:
1. Header und Footer werden echte Laufzeit-Komponenten aus components/.
2. Doppelte Header-/Footer-Blöcke werden aus allen HTML-Seiten entfernt.
3. Alte submenu-toggle-Kompatibilitätsreste werden entfernt.
4. Die direkte main.css-Architektur wird endgültig dokumentiert; ein altes
   site.bundle.css wird entfernt, falls es noch existiert.
5. Der Galerie-Generator wird aus dem GitHub-Workflow nach
   assets/python/generate_gallery.py verschoben.
6. Die Scraper-Validierung erhält einen dauerhaften Ort unter assets/python/.
7. Die benötigten Workflow-Aktualisierungen werden als fertige Ersatzdateien
   unter tools/maintenance-cleanup/workflow-replacements/ vorbereitet. GitHub
   erlaubt dem normalen GITHUB_TOKEN nicht, Workflow-Dateien selbst zu pushen.
8. Die README wird auf die tatsächlich verwendete Architektur aktualisiert.
9. Das alte einmalige direct-css-update-Tool wird entfernt, sofern vorhanden.
   Der zugehörige Workflow wird nur zur manuellen Löschung vorgemerkt.

Nicht enthalten:
- Kein automatischer Umbau von tables.js/tables.css. Dieser Bereich wurde
  zuletzt funktional korrigiert und soll nicht durch einen großen Regex-Patch
  destabilisiert werden.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HEADER_MARKER_RE = re.compile(
    r"\s*<!--\s*TTF:HEADER:START\s*-->.*?<!--\s*TTF:HEADER:END\s*-->\s*",
    re.IGNORECASE | re.DOTALL,
)
FOOTER_MARKER_RE = re.compile(
    r"\s*<!--\s*TTF:FOOTER:START\s*-->.*?<!--\s*TTF:FOOTER:END\s*-->\s*",
    re.IGNORECASE | re.DOTALL,
)
SUBMENU_BUTTON_RE = re.compile(
    r"<button\b(?=[^>]*\bclass=[\"'][^\"']*\bsubmenu-toggle\b[^\"']*[\"'])"
    r"[^>]*>.*?</button>",
    re.IGNORECASE | re.DOTALL,
)

SITE_COMPONENTS_JS = r'''/**
 * Lädt die globalen Seitenteile aus /components.
 *
 * Header und Footer sind damit echte Single Sources of Truth und müssen nicht
 * mehr in jede HTML-Datei kopiert werden.
 */
const SITE_COMPONENTS = [
    {
        selector: "#header-container",
        url: "/components/header.html",
        name: "Header"
    },
    {
        selector: "#footer-container",
        url: "/components/footer.html",
        name: "Footer"
    }
];

async function loadSiteComponent({ selector, url, name }) {
    const container = document.querySelector(selector);
    if (!container) {
        return { name, status: "missing-container" };
    }

    if (container.dataset.componentLoaded === "true") {
        return { name, status: "already-loaded" };
    }

    const response = await fetch(url, { cache: "no-cache" });
    if (!response.ok) {
        throw new Error(`${name} konnte nicht geladen werden (${response.status}).`);
    }

    container.innerHTML = await response.text();
    container.dataset.componentLoaded = "true";
    return { name, status: "loaded" };
}

export async function initSiteComponents() {
    const results = await Promise.allSettled(
        SITE_COMPONENTS.map(component => loadSiteComponent(component))
    );

    results.forEach((result, index) => {
        if (result.status === "rejected") {
            console.error(
                `${SITE_COMPONENTS[index].name} konnte nicht initialisiert werden:`,
                result.reason
            );
        }
    });

    return results;
}
'''

GALLERY_GENERATOR_PY = r'''#!/usr/bin/env python3
"""Erzeugt assets/data/gallerie.json aus assets/images/."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = ROOT / "assets/images"
OUTPUT_FILE = ROOT / "assets/data/gallerie.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
EXCLUDED_DIRECTORIES = {"seo"}


def slugify(text: str) -> str:
    value = (
        text.lower()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def url_for(path: Path) -> str:
    relative = path.relative_to(ROOT)
    return "/" + quote(str(relative).replace("\\", "/"))


def alt_for(path: Path, gallery_title: str) -> str:
    name = re.sub(r"[-_]+", " ", path.stem).strip()
    return f"{gallery_title}: {name}" if name else gallery_title


def image_entry(path: Path, gallery_title: str) -> dict[str, str]:
    return {
        "src": url_for(path),
        "alt": alt_for(path, gallery_title),
    }


def build_gallery_data() -> dict[str, object]:
    if not IMAGES_DIR.is_dir():
        raise FileNotFoundError(f"Bilderordner fehlt: {IMAGES_DIR.relative_to(ROOT)}")

    galleries: list[dict[str, object]] = []
    general_title = "Generelle Bilder"
    general_images = sorted(
        (
            file
            for file in IMAGES_DIR.iterdir()
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
        ),
        key=lambda path: path.name.lower(),
    )
    galleries.append(
        {
            "id": "general",
            "title": general_title,
            "images": [image_entry(file, general_title) for file in general_images],
        }
    )

    folders = sorted(
        (
            folder
            for folder in IMAGES_DIR.iterdir()
            if folder.is_dir()
            and folder.name.lower() not in EXCLUDED_DIRECTORIES
            and not folder.name.startswith((".", "_"))
        ),
        key=lambda path: path.name.lower(),
    )

    for folder in folders:
        images = sorted(
            (
                file
                for file in folder.iterdir()
                if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
            ),
            key=lambda path: path.name.lower(),
        )
        if images:
            galleries.append(
                {
                    "id": slugify(folder.name),
                    "title": folder.name,
                    "images": [image_entry(file, folder.name) for file in images],
                }
            )

    ids = [str(gallery["id"]) for gallery in galleries]
    if len(ids) != len(set(ids)):
        raise ValueError("Doppelte Galerie-IDs erkannt.")

    data: dict[str, object] = {
        "defaultGallery": "general",
        "galleries": galleries,
    }
    validate_gallery_data(data)
    return data


def validate_gallery_data(data: dict[str, object]) -> None:
    galleries = data.get("galleries")
    if not isinstance(galleries, list):
        raise ValueError("galleries muss eine Liste sein.")

    for gallery in galleries:
        if not isinstance(gallery, dict):
            raise ValueError("Ungültiger Galerie-Eintrag.")
        images = gallery.get("images")
        if not isinstance(images, list):
            raise ValueError("images muss eine Liste sein.")
        for image in images:
            if not isinstance(image, dict):
                raise ValueError("Ungültiger Bild-Eintrag.")
            src = str(image.get("src", ""))
            alt = str(image.get("alt", ""))
            image_path = ROOT / Path(unquote(src.lstrip("/")))
            if not image_path.is_file():
                raise FileNotFoundError(
                    f"Galeriebild fehlt: {image_path.relative_to(ROOT)}"
                )
            if not alt.strip():
                raise ValueError(
                    f"Leerer Alt-Text: {image_path.relative_to(ROOT)}"
                )


def main() -> int:
    data = build_gallery_data()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"{OUTPUT_FILE.relative_to(ROOT)} erzeugt: "
        f"{len(data['galleries'])} Galerien"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

SCRAPER_VALIDATOR_PY = r'''#!/usr/bin/env python3
"""Validiert vom Scraper erzeugte Kandidaten vor der Übernahme."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

GAME_KEYS = {"datum", "uhrzeit", "spielort", "heim", "gast", "ergebnis"}
TABLE_KEYS = {
    "rang",
    "mannschaft",
    "partien",
    "siege",
    "unentschieden",
    "niederlagen",
    "spiele",
    "spieleDifferenz",
    "punkte",
}
PLAYER_KEYS = {"rang", "position", "name", "qttr", "a", "status"}
LINK_KEYS = {"spielplaene", "tabellen", "spielerlisten", "links"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--allow-large-drop",
        action="store_true",
        help="Große Datenrückgänge ausnahmsweise erlauben.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Ungültiges JSON in {path}: {error}") from error


def managed_names(directory: Path) -> set[str]:
    names: set[str] = set()
    for pattern in ("spiele*.json", "tabelle*.json", "spieler*.json"):
        names.update(path.name for path in directory.glob(pattern) if path.is_file())
    if (directory / "links.json").is_file():
        names.add("links.json")
    return names


def require_object_list(data: Any, filename: str) -> list[dict[str, Any]]:
    if not isinstance(data, list):
        raise ValueError(f"{filename}: erwartet wird eine JSON-Liste.")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"{filename}: alle Listeneinträge müssen Objekte sein.")
    return data


def require_keys(item: dict[str, Any], keys: set[str], context: str) -> None:
    missing = sorted(keys - item.keys())
    if missing:
        raise ValueError(f"{context}: fehlende Felder: {', '.join(missing)}")


def validate_games(data: Any, filename: str) -> None:
    rows = require_object_list(data, filename)
    for index, item in enumerate(rows, start=1):
        require_keys(item, GAME_KEYS, f"{filename} Zeile {index}")
        if not str(item.get("heim") or "").strip():
            raise ValueError(f"{filename} Zeile {index}: heim ist leer.")
        if not str(item.get("gast") or "").strip():
            raise ValueError(f"{filename} Zeile {index}: gast ist leer.")


def validate_table(data: Any, filename: str) -> None:
    rows = require_object_list(data, filename)
    for index, item in enumerate(rows, start=1):
        require_keys(item, TABLE_KEYS, f"{filename} Zeile {index}")
        if not str(item.get("mannschaft") or "").strip():
            raise ValueError(f"{filename} Zeile {index}: mannschaft ist leer.")


def validate_players(data: Any, filename: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{filename}: erwartet wird ein Objekt mit Mannschaften.")
    for team, players in data.items():
        if not isinstance(team, str) or not team.strip():
            raise ValueError(f"{filename}: ungültiger Mannschaftsname.")
        if not isinstance(players, list):
            raise ValueError(f"{filename}: {team} muss eine Spielerliste sein.")
        for index, player in enumerate(players, start=1):
            if not isinstance(player, dict):
                raise ValueError(f"{filename}: {team} Spieler {index} ist kein Objekt.")
            require_keys(player, PLAYER_KEYS, f"{filename}: {team} Spieler {index}")
            if not str(player.get("rang") or "").strip():
                raise ValueError(f"{filename}: {team} Spieler {index}: rang ist leer.")
            if not str(player.get("name") or "").strip():
                raise ValueError(f"{filename}: {team} Spieler {index}: name ist leer.")


def validate_links(data: Any, filename: str) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{filename}: erwartet wird ein JSON-Objekt.")
    require_keys(data, LINK_KEYS, filename)
    for key in LINK_KEYS:
        if not isinstance(data[key], list):
            raise ValueError(f"{filename}: {key} muss eine Liste sein.")


def validate_schema(filename: str, data: Any) -> None:
    # "spieler..." beginnt ebenfalls mit "spiele"; daher zuerst prüfen.
    if filename.startswith("spieler"):
        validate_players(data, filename)
    elif filename.startswith("spiele"):
        validate_games(data, filename)
    elif filename.startswith("tabelle"):
        validate_table(data, filename)
    elif filename == "links.json":
        validate_links(data, filename)


def item_count(filename: str, data: Any) -> int:
    if filename.startswith(("spiele", "tabelle")) and isinstance(data, list):
        return len(data)
    if filename.startswith("spieler") and isinstance(data, dict):
        return sum(len(value) for value in data.values() if isinstance(value, list))
    if filename == "links.json" and isinstance(data, dict):
        return sum(len(data.get(key, [])) for key in LINK_KEYS)
    return 0


def validate_drop(
    filename: str,
    before_data: Any,
    candidate_data: Any,
    allow_large_drop: bool,
) -> None:
    if allow_large_drop or filename == "links.json":
        return
    before_count = item_count(filename, before_data)
    candidate_count = item_count(filename, candidate_data)
    if before_count < 4:
        return

    minimum = max(1, before_count // 2)
    if candidate_count < minimum:
        raise ValueError(
            f"{filename}: auffälliger Datenrückgang von {before_count} auf "
            f"{candidate_count}. Falls das beabsichtigt ist, Workflow mit "
            f"allow_large_data_drop starten."
        )


def main() -> int:
    args = parse_args()
    if not args.before.is_dir():
        raise FileNotFoundError(f"Before-Verzeichnis fehlt: {args.before}")
    if not args.candidate.is_dir():
        raise FileNotFoundError(f"Candidate-Verzeichnis fehlt: {args.candidate}")

    before_names = managed_names(args.before)
    candidate_names = managed_names(args.candidate)
    if not before_names:
        raise ValueError("Im bisherigen Datenstand wurden keine Scraper-Dateien gefunden.")

    missing = sorted(before_names - candidate_names)
    if missing:
        raise ValueError(
            "Im Kandidaten fehlen Scraper-Dateien: " + ", ".join(missing)
        )

    checked = 0
    for filename in sorted(candidate_names):
        candidate_path = args.candidate / filename
        candidate_data = load_json(candidate_path)
        validate_schema(filename, candidate_data)

        before_path = args.before / filename
        if before_path.is_file():
            before_data = load_json(before_path)
            validate_drop(
                filename,
                before_data,
                candidate_data,
                args.allow_large_drop,
            )
        checked += 1

    print(f"Scraper-Daten erfolgreich validiert: {checked} Dateien.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

GALLERY_WORKFLOW = '''name: Generate Gallery JSON

on:
  push:
    branches: [main]
    paths:
      - "assets/images/**"
      - "!assets/images/seo/**"
      - "assets/python/generate_gallery.py"
      - ".github/workflows/generate-gallery-json.yml"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: repository-writer
  cancel-in-progress: false

env:
  PYTHONDONTWRITEBYTECODE: "1"

jobs:
  generate-gallery-json:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Repository auschecken
        uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
        with:
          fetch-depth: 0

      - name: Python einrichten
        uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.13"

      - name: Galerie-JSON erzeugen und validieren
        run: python assets/python/generate_gallery.py

      - name: Änderungen committen
        shell: bash
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add assets/data/gallerie.json
          if git diff --staged --quiet; then
            echo "Keine Änderungen gefunden."
            exit 0
          fi
          git commit -m "Galerie JSON automatisch aktualisieren"
          git pull --rebase origin main
          git push origin HEAD:main
'''

README = '''# TTF Laudenbach – Vereinswebsite

Statische Vereinswebsite auf GitHub Pages.

## Grundprinzip

Die Seite bleibt bewusst einfach aufgebaut:

- **HTML (`index.html`, `pages/**/*.html`)** – Seiteninhalt und semantische Struktur
- **`components/header.html`** – gemeinsamer Header und Hauptnavigation
- **`components/footer.html`** – gemeinsamer Footer
- **`assets/css/main.css`** – zentraler CSS-Einstiegspunkt; lädt die CSS-Module direkt per `@import`
- **`assets/js/main.js`** – zentraler JavaScript-Einstiegspunkt; lädt nur benötigte Features
- **`assets/data/`** – dynamisch erzeugte JSON-Daten
- **`assets/python/`** – Scraper, Datenvalidierung und Galerie-Generator

Es gibt keinen CSS-Build und kein `site.bundle.css` mehr.

## Header und Footer

Die HTML-Seiten enthalten nur noch die beiden Platzhalter:

```html
<div id="header-container"></div>
...
<div id="footer-container"></div>
```

`assets/js/core/site-components.js` lädt anschließend:

- `/components/header.html`
- `/components/footer.html`

Damit sind Header und Footer echte **Single Sources of Truth**. Änderungen an Navigation oder Footer werden nur noch in den beiden Dateien unter `components/` vorgenommen.

## CSS

Die Seiten laden direkt:

```html
<link href="/assets/css/main.css" rel="stylesheet"/>
```

`main.css` importiert die getrennten Base-, Layout-, Komponenten- und Responsive-Dateien. Es ist kein Build-Schritt notwendig.

## JavaScript

`assets/js/main.js` initialisiert zuerst Header und Footer und lädt danach nur die Features, die auf der jeweiligen Seite gebraucht werden, zum Beispiel Tabellen, Galerie, Kontaktformular, News-Slider oder Spielerlisten.

## Automatische Daten

### Mannschaften, Spielpläne und Tabellen

Der Workflow **Auto-Update Daten** startet täglich und kann zusätzlich manuell ausgeführt werden.

- Scraper: `assets/python/scraper.py`
- Konfiguration: `assets/python/config.py`
- Prüfung vor Übernahme: `assets/python/validate_scraper_data.py`

Bei einem ungewöhnlich großen Datenrückgang bricht die Prüfung ab. Für einen beabsichtigten Saisonwechsel kann der manuelle Workflow mit `allow_large_data_drop` ausgeführt werden.

### Galerie

Der Workflow **Generate Gallery JSON** läuft bei Änderungen unter `assets/images/` und erzeugt:

```text
assets/data/gallerie.json
```

Die eigentliche Logik liegt in:

```text
assets/python/generate_gallery.py
```

Der GitHub-Workflow enthält dadurch nur noch die Ablaufsteuerung.

## Typische Änderungen

| Änderung | Datei / Bereich |
|---|---|
| Navigation | `components/header.html` |
| Footer | `components/footer.html` |
| Seiteninhalt | jeweilige HTML-Datei |
| Gestaltung | `assets/css/` |
| Frontend-Funktion | `assets/js/` |
| Mannschafts-/Ligaquellen | `assets/python/config.py` und ggf. `assets/js/config/` |
| Scraper | `assets/python/scraper.py` |
| Galerie-Erzeugung | `assets/python/generate_gallery.py` |

## Wartungsregel

Neue Abstraktionen oder Build-Schritte nur einführen, wenn sie ein konkretes Wartungsproblem lösen. Für diese Vereinswebsite gilt bewusst: **wenige Ebenen, eindeutige Zuständigkeiten und möglichst wenig duplizierter Code.**
'''


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, content: str) -> bool:
    content = content.replace("\r\n", "\n")
    if not content.endswith("\n"):
        content += "\n"
    original = read(path) if path.is_file() else None
    if original == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"AKTUALISIERT: {rel(path)}")
    return True


def html_files() -> list[Path]:
    files: list[Path] = []
    for name in ("index.html", "404.html"):
        path = ROOT / name
        if path.is_file():
            files.append(path)
    pages = ROOT / "pages"
    if pages.is_dir():
        files.extend(sorted(path for path in pages.rglob("*.html") if path.is_file()))
    return files


def strip_duplicate_site_components() -> int:
    changed = 0
    for path in html_files():
        original = read(path)
        updated = HEADER_MARKER_RE.sub("\n", original)
        updated = FOOTER_MARKER_RE.sub("\n", updated)
        updated = updated.replace(
            "/assets/css/site.bundle.css",
            "/assets/css/main.css",
        ).replace(
            "assets/css/site.bundle.css",
            "assets/css/main.css",
        )
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
            print(f"HTML BEREINIGT: {rel(path)}")
    return changed


def clean_header_component() -> bool:
    path = ROOT / "components/header.html"
    if not path.is_file():
        raise RuntimeError("components/header.html wurde nicht gefunden.")
    original = read(path)
    updated = SUBMENU_BUTTON_RE.sub("", original)
    return write_if_changed(path, updated)


def patch_main_js() -> bool:
    path = ROOT / "assets/js/main.js"
    if not path.is_file():
        raise RuntimeError("assets/js/main.js wurde nicht gefunden.")
    original = read(path)
    updated = original

    import_line = 'import { initSiteComponents } from "./core/site-components.js";'
    if import_line not in updated:
        anchor = 'from "./core/page-structure.js";'
        index = updated.find(anchor)
        if index < 0:
            raise RuntimeError("Importblock von page-structure.js in main.js nicht gefunden.")
        insert_at = index + len(anchor)
        updated = updated[:insert_at] + "\n" + import_line + updated[insert_at:]

    init_line = "    await initSiteComponents();"
    if init_line not in updated:
        anchor = "async function initializePage() {"
        if anchor not in updated:
            raise RuntimeError("initializePage() in main.js nicht gefunden.")
        updated = updated.replace(
            anchor,
            anchor + "\n" + init_line + "\n",
            1,
        )

    return write_if_changed(path, updated)


def patch_page_structure() -> bool:
    path = ROOT / "assets/js/core/page-structure.js"
    if not path.is_file():
        raise RuntimeError("assets/js/core/page-structure.js wurde nicht gefunden.")
    original = read(path)
    updated = original.replace(
        " * Die Struktur wird statisch ausgeliefert; die ensure-Funktionen sind Fallbacks.",
        " * Header und Footer werden aus /components geladen; die ensure-Funktionen ergänzen die Seitenstruktur.",
    )
    updated = re.sub(
        r"\n\s*// Entfernt den in einer früheren Version separat erzeugten Button\.\s*\n"
        r"\s*dropdown\.querySelector\(\":scope > \.submenu-toggle\"\)\?\.remove\(\);",
        "",
        updated,
        count=1,
    )
    return write_if_changed(path, updated)


def patch_main_css_comment() -> bool:
    path = ROOT / "assets/css/main.css"
    if not path.is_file():
        raise RuntimeError("assets/css/main.css wurde nicht gefunden.")
    original = read(path)
    updated = original.replace(
        " * Die Produktionsdatei site.bundle.css wird daraus automatisch erzeugt.",
        " * Die Website lädt diese Datei direkt; die Imports bilden die CSS-Module ab.",
    )
    return write_if_changed(path, updated)


def patch_tables_css_comment() -> bool:
    path = ROOT / "assets/css/components/tables.css"
    if not path.is_file():
        return False
    original = read(path)
    updated = original.replace(
        "/* Tabellen und ewige Rangliste. Aus style.css unverändert ausgelagert. */",
        "/* Tabellen, responsive Spieltabellen und ewige Rangliste. */",
        1,
    )
    return write_if_changed(path, updated)


def remove_legacy_bundle() -> bool:
    path = ROOT / "assets/css/site.bundle.css"
    if not path.exists():
        return False
    path.unlink()
    print(f"ENTFERNT: {rel(path)}")
    return True


def remove_old_direct_css_migration() -> int:
    removed = 0
    old_tool = ROOT / "tools/direct-css-update"
    current_script = Path(__file__).resolve()
    if old_tool.exists() and current_script not in old_tool.resolve().parents:
        shutil.rmtree(old_tool)
        print("ENTFERNT: tools/direct-css-update/")
        removed += 1

    # Workflow-Dateien unter .github/workflows werden absichtlich NICHT
    # verändert. Der normale GITHUB_TOKEN darf solche Änderungen nicht pushen.
    return removed


def prepare_workflow_replacements() -> int:
    """Bereitet Workflow-Dateien außerhalb von .github für manuellen Commit vor."""
    target = ROOT / "tools/maintenance-cleanup/workflow-replacements"
    changed = 0

    scraper = ROOT / ".github/workflows/scraper.yml"
    if not scraper.is_file():
        raise RuntimeError(".github/workflows/scraper.yml wurde nicht gefunden.")
    scraper_text = read(scraper).replace(
        "python tools/review-upgrade/validate_scraper_data.py",
        "python assets/python/validate_scraper_data.py",
    )
    if "tools/review-upgrade/validate_scraper_data.py" in scraper_text:
        raise RuntimeError("Alte Scraper-Validator-Referenz konnte nicht ersetzt werden.")
    if "assets/python/validate_scraper_data.py" not in scraper_text:
        raise RuntimeError("Neue Scraper-Validator-Referenz fehlt im Ersatzworkflow.")
    changed += write_if_changed(target / "scraper.yml", scraper_text)
    changed += write_if_changed(target / "generate-gallery-json.yml", GALLERY_WORKFLOW)

    instructions = """TTF LAUDENBACH – WORKFLOW-ÄNDERUNGEN MANUELL ANWENDEN
=====================================================

GitHub blockiert absichtlich, dass der normale GITHUB_TOKEN eines Workflows
Workflow-Dateien unter .github/workflows selbst verändert und zurückpusht.
Darum wurden diese Dateien nur vorbereitet.

Nach erfolgreichem Wartbarkeits-Cleanup bitte manuell im Repository:

1. tools/maintenance-cleanup/workflow-replacements/scraper.yml
   nach .github/workflows/scraper.yml kopieren/ersetzen.

2. tools/maintenance-cleanup/workflow-replacements/generate-gallery-json.yml
   nach .github/workflows/generate-gallery-json.yml kopieren/ersetzen.

3. .github/workflows/apply-direct-css-update.yml löschen, falls die Datei
   noch vorhanden ist.

4. Diese drei Workflow-Änderungen normal über die GitHub-Oberfläche committen.

5. Danach können die Dateien unter workflow-replacements/ sowie auf Wunsch
   maintenance-cleanup.yml und dieses Wartungsskript manuell gelöscht werden.
"""
    changed += write_if_changed(target / "MANUELL_ANWENDEN.txt", instructions)
    return int(changed)


def write_new_permanent_files() -> int:
    changed = 0
    changed += write_if_changed(
        ROOT / "assets/js/core/site-components.js",
        SITE_COMPONENTS_JS,
    )
    changed += write_if_changed(
        ROOT / "assets/python/generate_gallery.py",
        GALLERY_GENERATOR_PY,
    )
    changed += write_if_changed(
        ROOT / "assets/python/validate_scraper_data.py",
        SCRAPER_VALIDATOR_PY,
    )
    changed += write_if_changed(ROOT / "README.md", README)
    return int(changed)


def compile_embedded_python() -> None:
    for label, source in (
        ("generate_gallery.py", GALLERY_GENERATOR_PY),
        ("validate_scraper_data.py", SCRAPER_VALIDATOR_PY),
    ):
        compile(source, label, "exec")


def verify() -> None:
    errors: list[str] = []

    required = [
        ROOT / "components/header.html",
        ROOT / "components/footer.html",
        ROOT / "assets/css/main.css",
        ROOT / "assets/js/main.js",
        ROOT / "assets/js/core/site-components.js",
        ROOT / "assets/python/generate_gallery.py",
        ROOT / "assets/python/validate_scraper_data.py",
        ROOT / "tools/maintenance-cleanup/workflow-replacements/scraper.yml",
        ROOT / "tools/maintenance-cleanup/workflow-replacements/generate-gallery-json.yml",
        ROOT / "tools/maintenance-cleanup/workflow-replacements/MANUELL_ANWENDEN.txt",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"Pflichtdatei fehlt: {rel(path)}")

    header = ROOT / "components/header.html"
    if header.is_file() and "submenu-toggle" in read(header):
        errors.append("components/header.html enthält noch submenu-toggle.")

    header_container_re = re.compile(
        r"<div\b[^>]*\bid=[\"']header-container[\"'][^>]*>\s*</div>",
        re.IGNORECASE | re.DOTALL,
    )
    footer_container_re = re.compile(
        r"<div\b[^>]*\bid=[\"']footer-container[\"'][^>]*>\s*</div>",
        re.IGNORECASE | re.DOTALL,
    )

    for path in html_files():
        text = read(path)
        if "TTF:HEADER:START" in text or "TTF:HEADER:END" in text:
            errors.append(f"{rel(path)} enthält noch einen Header-Kopierblock.")
        if "TTF:FOOTER:START" in text or "TTF:FOOTER:END" in text:
            errors.append(f"{rel(path)} enthält noch einen Footer-Kopierblock.")
        if not header_container_re.search(text):
            errors.append(f"{rel(path)} hat keinen leeren #header-container.")
        if not footer_container_re.search(text):
            errors.append(f"{rel(path)} hat keinen leeren #footer-container.")
        if "site.bundle.css" in text:
            errors.append(f"{rel(path)} verweist noch auf site.bundle.css.")
        if "/assets/css/main.css" not in text:
            errors.append(f"{rel(path)} lädt /assets/css/main.css nicht.")
        if "/assets/js/main.js" not in text:
            errors.append(f"{rel(path)} lädt /assets/js/main.js nicht.")

    main_js = ROOT / "assets/js/main.js"
    if main_js.is_file():
        text = read(main_js)
        if 'from "./core/site-components.js"' not in text:
            errors.append("main.js importiert site-components.js nicht.")
        if "await initSiteComponents();" not in text:
            errors.append("main.js initialisiert Header/Footer nicht vor den Features.")

    scraper_replacement = ROOT / "tools/maintenance-cleanup/workflow-replacements/scraper.yml"
    if scraper_replacement.is_file():
        text = read(scraper_replacement)
        if "tools/review-upgrade/validate_scraper_data.py" in text:
            errors.append("Vorbereiteter scraper.yml enthält noch die alte Validator-Referenz.")
        if "assets/python/validate_scraper_data.py" not in text:
            errors.append("Vorbereiteter scraper.yml verwendet den neuen Validator nicht.")

    gallery_replacement = ROOT / "tools/maintenance-cleanup/workflow-replacements/generate-gallery-json.yml"
    if gallery_replacement.is_file() and "python assets/python/generate_gallery.py" not in read(gallery_replacement):
        errors.append("Vorbereiteter Galerie-Workflow verwendet generate_gallery.py nicht.")

    if (ROOT / "assets/css/site.bundle.css").exists():
        errors.append("assets/css/site.bundle.css existiert noch.")

    if (ROOT / "tools/direct-css-update").exists():
        errors.append("Das alte tools/direct-css-update existiert noch.")

    compile_embedded_python()

    if errors:
        raise RuntimeError(
            "Wartbarkeits-Cleanup ist unvollständig:\n- " + "\n- ".join(errors)
        )


def main() -> int:
    if not (ROOT / ".git").exists():
        print(
            "Hinweis: .git wurde nicht gefunden. Das Skript kann trotzdem laufen, "
            "erwartet aber die TTF-Laudenbach-Repository-Struktur."
        )

    print("=== TTF Laudenbach: Wartbarkeits-Cleanup ===")
    changed_html = strip_duplicate_site_components()
    clean_header_component()
    patch_main_js()
    patch_page_structure()
    patch_main_css_comment()
    patch_tables_css_comment()
    remove_legacy_bundle()
    write_new_permanent_files()
    prepare_workflow_replacements()
    removed_old = remove_old_direct_css_migration()
    verify()

    print()
    print("Cleanup erfolgreich abgeschlossen.")
    print(f"- HTML-Seiten mit Änderungen: {changed_html}")
    print(f"- Alte direct-css-update-Artefakte entfernt: {removed_old}")
    print("- Header/Footer werden jetzt zentral aus components/ geladen.")
    print("- Galerie- und Scraper-Hilfslogik liegt dauerhaft unter assets/python/.")
    print("- Workflow-Ersatzdateien wurden unter tools/maintenance-cleanup/workflow-replacements/ vorbereitet.")
    print("- README entspricht der neuen, buildfreien Struktur.")
    print("- Dieses Wartungsskript wurde absichtlich NICHT gelöscht.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        raise
