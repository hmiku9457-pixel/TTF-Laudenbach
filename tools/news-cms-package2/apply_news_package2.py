#!/usr/bin/env python3
"""Wendet Paket 2 der CMS-unabhängigen News-Automatisierung an."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
DOCS = ROOT / "docs/news-content-format.md"
WORKFLOW = ROOT / ".github/workflows/generate-news.yml"

REQUIRED_PACKAGE1 = (
    ROOT / "assets/python/generate_news.py",
    ROOT / "assets/python/news_requirements.txt",
    ROOT / "content/news",
    ROOT / "templates/news-article.html",
    ROOT / "templates/news-overview.html",
    ROOT / "pages/neuigkeiten.html",
    ROOT / "assets/data/news.json",
)

NEWS_SECTION = '''## Neuigkeiten / Content-System

News werden nicht mehr doppelt in HTML und `news.json` gepflegt.

- Source of Truth: `content/news/*.md`
- Artikel-Template: `templates/news-article.html`
- Übersichts-Template: `templates/news-overview.html`
- Generator: `assets/python/generate_news.py`
- Generierte Übersicht: `pages/neuigkeiten.html`
- Generierte Artikelseiten: `pages/news/*.html`
- Generierte Slider-Daten: `assets/data/news.json`

Der Workflow **News generieren** synchronisiert diese Ausgaben dauerhaft. Er läuft automatisch bei Änderungen an News-Quellen, News-Bildern, Templates oder Generator, prüft geplante Veröffentlichungen zweimal pro Stunde in `Europe/Berlin` und kann zusätzlich manuell ausgeführt werden.

`publish_at` steuert, ab wann ein Artikel auf der Website berücksichtigt wird. Zukünftige Artikel können bereits im Repository liegen, werden vom Generator aber noch nicht veröffentlicht. Der manuelle Workflow-Lauf dient gleichzeitig als vollständiger Rebuild/Repair und fordert auch einen neuen GitHub-Pages-Build an.

Generierte News-Dateien sollten nicht manuell korrigiert werden. Änderungen gehören in die Markdown-Quelle oder in die Templates. Das neutrale Dateiformat ist in `docs/news-content-format.md` dokumentiert.
'''

AUTOMATION_SECTION = '''## Automatisierung

Der dauerhafte Workflow **News generieren** verwendet immer denselben Generator `assets/python/generate_news.py`.

Er startet:

* bei relevanten Änderungen auf `main` (`content/news/`, `assets/images/news/`, News-Templates, Generator oder Requirements),
* zweimal pro Stunde in der Zeitzone `Europe/Berlin` für geplante Veröffentlichungen,
* manuell über **Actions → News generieren → Run workflow**.

Jeder Lauf berechnet den vollständigen Sollzustand neu. Dadurch werden auch gelöschte Artikel, die News-Übersicht, die fünf Slider-Einträge und die News-Einträge der Sitemap konsistent synchronisiert.

Der manuelle Lauf ist zugleich der Rebuild-/Repair-Weg. Er fordert auch dann einen neuen GitHub-Pages-Build an, wenn keine generierte Datei geändert werden musste.

GitHub kann geplante Workflows in öffentlichen Repositories nach 60 Tagen ohne Repository-Aktivität automatisch deaktivieren. Falls eine geplante News nicht erscheint, zuerst den Workflow **News generieren** prüfen beziehungsweise manuell ausführen und einen deaktivierten Schedule wieder aktivieren.
'''


def fail(message: str) -> None:
    raise RuntimeError(message)


def ensure_package1() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_PACKAGE1 if not path.exists()]
    if missing:
        fail("Paket 1 ist nicht vollständig vorhanden: " + ", ".join(missing))


def replace_section(text: str, heading: str, next_heading: str, replacement: str) -> str:
    pattern = re.compile(
        rf"^{re.escape(heading)}\n.*?(?=^{re.escape(next_heading)}\n)",
        re.MULTILINE | re.DOTALL,
    )
    if not pattern.search(text):
        fail(f"README.md: Abschnitt '{heading}' bis '{next_heading}' nicht gefunden.")
    return pattern.sub(replacement.rstrip() + "\n", text, count=1)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = replace_section(text, "## Neuigkeiten / Content-System", "## Automatische Daten", NEWS_SECTION)

    row_re = re.compile(r"^\| `news\.json` \|.*$", re.MULTILINE)
    replacement = "| `news.json` | automatisch durch **News generieren** / `assets/python/generate_news.py` |"
    if not row_re.search(text):
        fail("README.md: Tabellenzeile für news.json nicht gefunden.")
    text = row_re.sub(replacement, text, count=1)

    text = text.replace(
        "Unter `assets/data/` liegen sowohl automatisch erzeugte als auch manuell gepflegte JSON-Dateien. Für die Wartung gilt:",
        "Unter `assets/data/` liegen automatisch erzeugte JSON-Dateien. Für die Wartung gilt:",
    )

    README.write_text(text.rstrip() + "\n", encoding="utf-8")


def update_docs() -> None:
    text = DOCS.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip()
    pattern = re.compile(r"^## Automatisierung\n.*\Z", re.MULTILINE | re.DOTALL)
    if pattern.search(text):
        text = pattern.sub(AUTOMATION_SECTION.rstrip(), text)
    else:
        text += "\n\n" + AUTOMATION_SECTION.rstrip()
    DOCS.write_text(text + "\n", encoding="utf-8")


def ensure_workflow() -> None:
    if not WORKFLOW.is_file():
        fail(
            ".github/workflows/generate-news.yml fehlt. "
            "Der finale Workflow muss vor dem Paketlauf durch einen normalen Benutzer-Commit ins Repository gelangen."
        )


def main() -> None:
    ensure_package1()
    update_readme()
    update_docs()
    ensure_workflow()
    print("News CMS Paket 2 angewendet.")


if __name__ == "__main__":
    main()
