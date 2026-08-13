#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def text(path: str) -> str:
    target = ROOT / path
    require(target.is_file(), f"Datei fehlt: {path}")
    return target.read_text(encoding="utf-8")


def main() -> None:
    required_files = [
        "assets/python/generate_news.py",
        "assets/python/news_requirements.txt",
        "assets/css/components/news-content.css",
        "templates/news-article.html",
        "templates/news-overview.html",
        "docs/news-content-format.md",
        "pages/neuigkeiten.html",
        "assets/data/news.json",
        "content/news/training-bei-den-tischtennis-freunden-laudenbach.md",
        "content/news/vierelemente-sponsort-jacken.md",
        "content/news/49-ttf-hauptversammlung.md",
    ]
    for path in required_files:
        require((ROOT / path).is_file(), f"Datei fehlt: {path}")

    require(not (ROOT / "pages/news/artikel1.html").exists(), "Legacy-Seite artikel1.html wurde nicht entfernt.")
    require(not (ROOT / "pages/news/artikel2.html").exists(), "Legacy-Seite artikel2.html wurde nicht entfernt.")

    expected_slugs = {
        "training-bei-den-tischtennis-freunden-laudenbach",
        "vierelemente-sponsort-jacken",
        "49-ttf-hauptversammlung",
    }
    for slug in expected_slugs:
        page = text(f"pages/news/{slug}.html")
        require("AUTO-GENERATED NEWS PAGE" in page, f"{slug}.html hat keinen Generator-Marker.")
        require("{{" not in page and "}}" not in page, f"{slug}.html enthält Template-Platzhalter.")
        require('<main id="main-content"' in page, f"{slug}.html: main fehlt.")
        require("<h1" in page, f"{slug}.html: H1 fehlt.")
        require('href="/pages/neuigkeiten.html"' in page, f"{slug}.html: Link zur Übersicht fehlt.")

    overview = text("pages/neuigkeiten.html")
    require("AUTO-GENERATED NEWS PAGE" in overview, "Neuigkeiten-Übersicht hat keinen Generator-Marker.")
    for title in (
        "Training bei den Tischtennis-Freunden Laudenbach",
        "Laudenbacher Firma VierElemente sponsort Jacken",
        "49. TTF-Hauptversammlung",
    ):
        require(title in overview, f"Übersicht enthält '{title}' nicht.")

    data = json.loads(text("assets/data/news.json"))
    require(isinstance(data, list), "news.json ist keine Liste.")
    require(1 <= len(data) <= 5, "news.json muss 1 bis 5 veröffentlichte Einträge enthalten.")
    require(len(data) == 3, "Nach Migration werden genau 3 News-Einträge erwartet.")
    for item in data:
        require(set(item) == {"title", "text", "image", "imageAlt", "link"}, "news.json enthält unerwartete Felder.")
        require(item["link"].startswith("/pages/news/"), "Ungültiger Artikel-Link in news.json.")
        require(item["image"].startswith("/assets/images/"), "Ungültiger Bildpfad in news.json.")
        require(bool(item["imageAlt"].strip()), "Leerer imageAlt-Wert in news.json.")
        require("artikel1.html" not in item["link"] and "artikel2.html" not in item["link"], "Legacy-Link in news.json.")

    main_css = text("assets/css/main.css")
    require(main_css.count('@import url("./components/news-content.css");') == 1, "news-content.css muss genau einmal importiert werden.")

    slider = text("assets/js/features/news-slider.js")
    require('item?.imageAlt || item?.title || "Vereinsneuigkeit"' in slider, "Slider nutzt imageAlt noch nicht.")

    homepage = text("index.html")
    require(homepage.count('href="/pages/neuigkeiten.html">Alle Neuigkeiten</a>') == 1, "Startseiten-Link zur News-Übersicht fehlt oder ist doppelt.")

    sitemap = text("sitemap.xml")
    require("pages/news/artikel1.html" not in sitemap, "Sitemap enthält artikel1.html noch.")
    require("pages/news/artikel2.html" not in sitemap, "Sitemap enthält artikel2.html noch.")
    require("pages/neuigkeiten.html" in sitemap, "Sitemap enthält Neuigkeiten-Übersicht nicht.")
    for slug in expected_slugs:
        require(f"pages/news/{slug}.html" in sitemap, f"Sitemap enthält {slug}.html nicht.")

    generator = text("assets/python/generate_news.py")
    require("SLIDER_LIMIT = 5" in generator, "Slider-Limit ist nicht 5.")
    require('ZoneInfo("Europe/Berlin")' in generator, "Europe/Berlin-Zeitzone fehlt.")
    require("cleanup_stale_pages" in generator, "Cleanup generierter News-Seiten fehlt.")

    readme = text("README.md")
    require("## Neuigkeiten / Content-System" in readme, "README-News-Dokumentation fehlt.")
    require("Source of Truth: `content/news/*.md`" in readme, "README nennt Source of Truth nicht.")

    # Templates sollen nur die definierten Platzhalter verwenden.
    allowed_article = {
        "PAGE_TITLE", "DESCRIPTION", "CANONICAL_URL", "IMAGE_URL", "IMAGE_PATH",
        "IMAGE_ALT", "TITLE", "DATETIME", "DISPLAY_DATE", "CONTENT",
    }
    placeholders = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text("templates/news-article.html")))
    require(placeholders == allowed_article, f"Unerwartete Artikel-Template-Platzhalter: {sorted(placeholders)}")
    overview_placeholders = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text("templates/news-overview.html")))
    require(overview_placeholders == {"NEWS_ITEMS"}, "Unerwartete Übersichts-Template-Platzhalter.")

    print("Paket-1-Prüfung erfolgreich.")


if __name__ == "__main__":
    main()
