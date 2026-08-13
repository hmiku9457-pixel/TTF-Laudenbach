#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[2]

MAIN_CSS = ROOT / "assets/css/main.css"
NEWS_SLIDER_JS = ROOT / "assets/js/features/news-slider.js"
INDEX_HTML = ROOT / "index.html"
README = ROOT / "README.md"

GENERATE_NEWS = ROOT / "assets/python/generate_news.py"
NEWS_REQUIREMENTS = ROOT / "assets/python/news_requirements.txt"
NEWS_CSS = ROOT / "assets/css/components/news-content.css"
ARTICLE_TEMPLATE = ROOT / "templates/news-article.html"
OVERVIEW_TEMPLATE = ROOT / "templates/news-overview.html"
CONTENT_DIR = ROOT / "content/news"
DOCS_FILE = ROOT / "docs/news-content-format.md"


def fail(message: str) -> None:
    raise RuntimeError(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"Erwartete Datei fehlt: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = textwrap.dedent(content).lstrip("\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    if path.exists() and path.read_text(encoding="utf-8") == normalized:
        return
    path.write_text(normalized, encoding="utf-8")


def replace_once(path: Path, old: str, new: str, *, already_present: str | None = None) -> None:
    text = read(path)
    if already_present and already_present in text:
        return
    count = text.count(old)
    if count != 1:
        fail(
            f"{path.relative_to(ROOT)}: erwartete Stelle wurde {count}x statt genau 1x gefunden. "
            "Paket wurde nicht angewendet."
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_main_css() -> None:
    import_line = '@import url("./components/news-content.css");'
    text = read(MAIN_CSS)
    if import_line in text:
        return

    anchor = '@import url("./components/news-slider.css");'
    if anchor not in text:
        fail("assets/css/main.css: Import von news-slider.css nicht gefunden.")
    MAIN_CSS.write_text(
        text.replace(anchor, f"{anchor}\n{import_line}", 1),
        encoding="utf-8",
    )


def update_slider() -> None:
    replace_once(
        NEWS_SLIDER_JS,
        '        image.alt = item?.title || "Vereinsneuigkeit";',
        '        image.alt = item?.imageAlt || item?.title || "Vereinsneuigkeit";',
        already_present='image.alt = item?.imageAlt || item?.title || "Vereinsneuigkeit";',
    )


def update_homepage() -> None:
    old = '<div class="news-slider"></div>'
    new = """<section class="home-news" aria-label="Neuigkeiten">
<div class="news-slider"></div>
<a class="button home-news__all" href="/pages/neuigkeiten.html">Alle Neuigkeiten</a>
</section>"""
    replace_once(
        INDEX_HTML,
        old,
        new,
        already_present='href="/pages/neuigkeiten.html">Alle Neuigkeiten</a>',
    )


def update_readme() -> None:
    text = read(README)

    # Die README wurde im Wartbarkeits-Cleanup bereits mehrfach vereinfacht.
    # Deshalb hier bewusst zeilen-/abschnittsorientiert arbeiten statt alte
    # Formulierungen 1:1 vorauszusetzen.
    lines = text.splitlines()

    def replace_prefixed_line(prefix: str, replacement: str) -> None:
        nonlocal lines
        matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
        if not matches:
            fail(f"README.md: erwarteter Strukturpunkt fehlt: {prefix}")
        if len(matches) > 1:
            fail(f"README.md: Strukturpunkt ist nicht eindeutig: {prefix}")
        lines[matches[0]] = replacement

    replace_prefixed_line(
        "- **`assets/data/`**",
        "- **`assets/data/`** – automatisch erzeugte JSON-Daten für dynamische Inhalte",
    )
    replace_prefixed_line(
        "- **`assets/python/`**",
        "- **`assets/python/`** – Scraper, Datenvalidierung sowie Galerie- und News-Generator",
    )

    if not any("**`content/news/`**" in line for line in lines):
        python_index = next(
            (index for index, line in enumerate(lines) if line.startswith("- **`assets/python/`**")),
            None,
        )
        if python_index is None:
            fail("README.md: Einfügepunkt nach assets/python fehlt.")
        lines[python_index + 1:python_index + 1] = [
            "- **`content/news/`** – redaktionelle Markdown-Quelldateien für Neuigkeiten",
            "- **`templates/`** – zentrale HTML-Vorlagen für generierte News-Seiten",
        ]

    text = "\n".join(lines) + "\n"

    section = """## Neuigkeiten / Content-System

News werden nicht mehr doppelt in HTML und `news.json` gepflegt.

- Source of Truth: `content/news/*.md`
- Artikel-Template: `templates/news-article.html`
- Übersichts-Template: `templates/news-overview.html`
- Generator: `assets/python/generate_news.py`
- Generierte Übersicht: `pages/neuigkeiten.html`
- Generierte Artikelseiten: `pages/news/*.html`
- Generierte Slider-Daten: `assets/data/news.json`

`publish_at` steuert, ab wann ein Artikel auf der Website berücksichtigt wird. Zukünftige Artikel können bereits im Repository liegen, werden vom Generator aber noch nicht veröffentlicht.

Generierte News-Dateien sollten nicht manuell korrigiert werden. Änderungen gehören in die Markdown-Quelle oder in die Templates. Das neutrale Dateiformat ist in `docs/news-content-format.md` dokumentiert.

"""
    if "## Neuigkeiten / Content-System" not in text:
        anchors = ("## Automatische Daten\n", "## Datenpflege\n", "## Typische Änderungen\n")
        anchor = next((candidate for candidate in anchors if candidate in text), None)
        if anchor is None:
            fail("README.md: kein geeigneter Abschnitt für die News-Dokumentation gefunden.")
        text = text.replace(anchor, section + anchor, 1)

    news_rows = [
        "| News-Inhalte | `content/news/*.md` |",
        "| News-Templates | `templates/news-article.html`, `templates/news-overview.html` |",
        "| News-Generator | `assets/python/generate_news.py` |",
    ]
    if news_rows[0] not in text:
        typical_heading = "## Typische Änderungen"
        if typical_heading not in text:
            fail("README.md: Abschnitt 'Typische Änderungen' fehlt.")

        section_start = text.index(typical_heading)
        next_heading = text.find("\n## ", section_start + len(typical_heading))
        section_end = len(text) if next_heading == -1 else next_heading
        typical = text[section_start:section_end].rstrip()

        if "| Änderung | Datei / Bereich |" not in typical:
            fail("README.md: Tabelle unter 'Typische Änderungen' fehlt.")

        typical += "\n" + "\n".join(news_rows) + "\n"
        text = text[:section_start] + typical + text[section_end:]

    README.write_text(text, encoding="utf-8")


def write_requirements() -> None:
    write(
        NEWS_REQUIREMENTS,
        """mistune==3.2.1
PyYAML==6.0.3
""",
    )


def write_news_css() -> None:
    write(
        NEWS_CSS,
        """
/* Generierte News-Artikel und News-Übersicht. */

.home-news {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: var(--space-m);
}

.home-news .news-slider {
    flex: 1 1 auto;
}

.home-news__all {
    align-self: stretch;
    padding: var(--space-m) var(--space-l);
    text-align: center;
}

.news-page {
    width: min(calc(100% - var(--space-xl) - var(--space-xl)), 980px);
    margin: var(--space-xl) auto;
}

.news-article,
.news-overview {
    overflow-wrap: anywhere;
}

.news-article__header {
    margin-bottom: var(--space-xl);
}

.news-article__title,
.news-overview__title {
    margin-bottom: var(--space-s);
    text-wrap: balance;
}

.news-article__date,
.news-overview__date {
    color: var(--text-muted);
    font-size: 0.95rem;
}

.news-article__hero {
    display: block;
    width: 100%;
    max-height: 34rem;
    margin: var(--space-xl) 0;
    border-radius: var(--space-m);
    object-fit: cover;
}

.news-article__content {
    max-width: 78ch;
}

.news-article__content > * + * {
    margin-top: var(--space-l);
}

.news-article__content h2,
.news-article__content h3 {
    margin-top: var(--space-xl);
    line-height: 1.25;
    text-wrap: balance;
}

.news-article__content ul,
.news-article__content ol {
    padding-left: 1.4rem;
}

.news-article__content img {
    display: block;
    width: auto;
    max-width: 100%;
    height: auto;
    margin-right: auto;
    margin-left: auto;
    border-radius: var(--space-m);
}

.news-article__content blockquote {
    padding-left: var(--space-l);
    border-left: 3px solid var(--accent);
    color: var(--text-muted);
}

.news-table-wrapper {
    max-width: 100%;
    overflow-x: auto;
    border-radius: var(--space-m);
}

.news-article__content table {
    width: 100%;
    min-width: 32rem;
    border-collapse: collapse;
    background: rgba(15, 23, 42, 0.35);
}

.news-article__content th,
.news-article__content td {
    padding: var(--space-m);
    border: 1px solid rgba(148, 163, 184, 0.35);
    text-align: left;
    vertical-align: top;
}

.news-article__content th {
    background: rgba(56, 189, 248, 0.12);
}

.news-article__actions {
    margin-top: var(--space-xl);
}

.news-overview__intro {
    max-width: 70ch;
    margin-bottom: var(--space-xl);
    color: var(--text-muted);
}

.news-overview__list {
    display: grid;
    gap: var(--space-l);
}

.news-overview-card {
    display: grid;
    grid-template-columns: minmax(12rem, 0.34fr) minmax(0, 0.66fr);
    gap: var(--space-xl);
    align-items: stretch;
}

.news-overview-card__media {
    min-height: 12rem;
    overflow: hidden;
    border-radius: var(--space-m);
}

.news-overview-card__media img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.news-overview-card__content {
    display: flex;
    min-width: 0;
    flex-direction: column;
}

.news-overview-card__title {
    margin-bottom: var(--space-s);
    text-wrap: balance;
}

.news-overview-card__summary {
    margin: var(--space-m) 0 var(--space-l);
}

.news-overview-card__link {
    width: fit-content;
    margin-top: auto;
}

@media (max-width: 768px) {
    .news-page {
        width: calc(100% - 2 * var(--space-m));
        margin: var(--space-m) auto;
    }

    .news-overview-card {
        grid-template-columns: 1fr;
        gap: var(--space-m);
    }

    .news-overview-card__media {
        min-height: 11rem;
        max-height: 18rem;
    }
}
""",
    )


def write_templates() -> None:
    write(
        ARTICLE_TEMPLATE,
        """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link href="/assets/css/main.css" rel="stylesheet"/>
<title>{{PAGE_TITLE}}</title>
<meta content="{{DESCRIPTION}}" name="description"/>
<meta content="index, follow, max-image-preview:large" name="robots"/>
<link href="{{CANONICAL_URL}}" rel="canonical"/>
<meta content="de_DE" property="og:locale"/>
<meta content="article" property="og:type"/>
<meta content="TTF Laudenbach" property="og:site_name"/>
<meta content="{{PAGE_TITLE}}" property="og:title"/>
<meta content="{{DESCRIPTION}}" property="og:description"/>
<meta content="{{CANONICAL_URL}}" property="og:url"/>
<meta content="{{IMAGE_URL}}" property="og:image"/>
<meta content="{{IMAGE_ALT}}" property="og:image:alt"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="{{PAGE_TITLE}}" name="twitter:title"/>
<meta content="{{DESCRIPTION}}" name="twitter:description"/>
<meta content="{{IMAGE_URL}}" name="twitter:image"/>
<meta content="{{IMAGE_ALT}}" name="twitter:image:alt"/>
</head>
<body>
<a class="skip-link" href="#main-content">Direkt zum Inhalt</a>
<div id="header-container"></div>
<main id="main-content" tabindex="-1">
<div class="news-page">
<article class="box news-article">
<header class="news-article__header">
<h1 class="news-article__title">{{TITLE}}</h1>
<time class="news-article__date" datetime="{{DATETIME}}">{{DISPLAY_DATE}}</time>
</header>
<img class="news-article__hero" src="{{IMAGE_PATH}}" alt="{{IMAGE_ALT}}"/>
<div class="news-article__content">
{{CONTENT}}
</div>
<div class="news-article__actions">
<a class="button button--card" href="/pages/neuigkeiten.html">Alle Neuigkeiten</a>
</div>
</article>
</div>
</main>
<div id="footer-container"></div>
<script src="/assets/js/main.js" type="module"></script>
</body>
</html>
""",
    )

    write(
        OVERVIEW_TEMPLATE,
        """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link href="/assets/css/main.css" rel="stylesheet"/>
<title>Neuigkeiten | TTF Laudenbach</title>
<meta content="Neuigkeiten, Berichte und Ankündigungen der Tischtennis-Freunde Laudenbach." name="description"/>
<meta content="index, follow, max-image-preview:large" name="robots"/>
<link href="https://www.ttf-laudenbach.de/pages/neuigkeiten.html" rel="canonical"/>
<meta content="de_DE" property="og:locale"/>
<meta content="website" property="og:type"/>
<meta content="TTF Laudenbach" property="og:site_name"/>
<meta content="Neuigkeiten | TTF Laudenbach" property="og:title"/>
<meta content="Neuigkeiten, Berichte und Ankündigungen der Tischtennis-Freunde Laudenbach." property="og:description"/>
<meta content="https://www.ttf-laudenbach.de/pages/neuigkeiten.html" property="og:url"/>
<meta content="https://www.ttf-laudenbach.de/assets/images/seo/ttf-laudenbach-social.png" property="og:image"/>
<meta content="Logo der Tischtennis-Freunde Laudenbach" property="og:image:alt"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="Neuigkeiten | TTF Laudenbach" name="twitter:title"/>
<meta content="Neuigkeiten, Berichte und Ankündigungen der Tischtennis-Freunde Laudenbach." name="twitter:description"/>
<meta content="https://www.ttf-laudenbach.de/assets/images/seo/ttf-laudenbach-social.png" name="twitter:image"/>
<meta content="Logo der Tischtennis-Freunde Laudenbach" name="twitter:image:alt"/>
</head>
<body>
<a class="skip-link" href="#main-content">Direkt zum Inhalt</a>
<div id="header-container"></div>
<main id="main-content" tabindex="-1">
<div class="news-page">
<section class="box news-overview">
<h1 class="news-overview__title">Neuigkeiten</h1>
<p class="news-overview__intro">Aktuelle Berichte und Ankündigungen der Tischtennis-Freunde Laudenbach.</p>
<div class="news-overview__list">
{{NEWS_ITEMS}}
</div>
</section>
</div>
</main>
<div id="footer-container"></div>
<script src="/assets/js/main.js" type="module"></script>
</body>
</html>
""",
    )


def write_docs() -> None:
    write(
        DOCS_FILE,
        """
# News-Content-Format

Die Dateien unter `content/news/` sind die einzige redaktionelle Quelle für die News der Website.
Das Format ist bewusst CMS-unabhängig: YAML-Frontmatter plus Markdown.

## Beispiel

```markdown
---
title: "Vereinsmeisterschaften 2026"
publish_at: "2026-09-12T18:00"
summary: "Kurzer optionaler Teaser für Slider und Übersicht."
image: "/assets/images/news/vereinsmeisterschaften-2026.jpg"
image_alt: "Teilnehmer der Vereinsmeisterschaften 2026"
---

Der eigentliche Artikel beginnt hier.

## Zwischenüberschrift

Normaler Text mit **Fettschrift**, *Kursivschrift*, [Links](https://example.org)
und Listen.

| Platz | Name |
| --- | --- |
| 1. | Beispiel |
```

## Pflichtfelder

* `title`
* `publish_at`
* `image`
* `image_alt`
* Markdown-Body

`summary` ist optional. Fehlt es, erzeugt der Generator einen Teaser aus dem Artikeltext.

## Veröffentlichungszeit

`publish_at` wird als lokale Zeit in `Europe/Berlin` interpretiert, sofern kein expliziter UTC-Offset angegeben ist.
Artikel mit einem Zeitpunkt in der Zukunft werden noch nicht in HTML, Übersicht, Slider oder Sitemap aufgenommen.

## Dateiname / URL

Der Markdown-Dateiname ist der dauerhafte Slug und muss aus Kleinbuchstaben, Ziffern und Bindestrichen bestehen.

Beispiel:

`content/news/saisonstart-2026.md`

erzeugt:

`/pages/news/saisonstart-2026.html`

Eine spätere Änderung des Titels ändert die URL nicht.

## Unterstütztes Markdown

* Absätze
* H2 und H3
* Fett und Kursiv
* Links
* Aufzählungen und nummerierte Listen
* Bilder
* Tabellen
* Blockquotes
* Code

Eine zusätzliche H1 ist nicht erlaubt, weil der Artikeltitel bereits die H1 der Seite ist.
Rohes HTML ist nicht erlaubt.

## Bilder

Bilder müssen im Repository unter `/assets/images/` liegen.
Neue CMS-Bilder sollen später bevorzugt unter `/assets/images/news/` abgelegt werden.
Bilder im Artikel benötigen einen nicht-leeren Alt-Text.

## Generierte Dateien

Nicht manuell bearbeiten:

* `pages/news/*.html`
* `pages/neuigkeiten.html`
* `assets/data/news.json`
* News-Einträge in `sitemap.xml`

Änderungen gehören in die Markdown-Datei, die Templates oder den Generator.
""",
    )


def write_migrated_content() -> None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    write(
        CONTENT_DIR / "training-bei-den-tischtennis-freunden-laudenbach.md",
        """
---
title: "Training bei den Tischtennis-Freunden Laudenbach"
publish_at: "2026-06-14T12:02"
summary: "Du möchtest Tischtennis ausprobieren? Kinder, Jugendliche, Erwachsene, Wiedereinsteiger und Gastspieler sind bei den Tischtennis-Freunden Laudenbach herzlich willkommen."
image: "/assets/images/LustAufTischtennis.png"
image_alt: "Training bei den Tischtennis-Freunden Laudenbach"
---

Tischtennis macht Spaß – und wer die schnellste Ballsportart der Welt einmal selbst ausprobieren möchte, ist bei den Tischtennis-Freunden Laudenbach herzlich willkommen.

Besonders Kinder und Jugendliche dürfen gerne bei uns vorbeischauen. Aber auch Erwachsene, Wiedereinsteiger und aktive Spieler anderer Vereine sind jederzeit eingeladen, mit uns zu trainieren.

Unter fachkundiger Anleitung können die einzelnen Schläge erlernt und das eigene Spiel Schritt für Schritt verbessert werden.
""",
    )

    write(
        CONTENT_DIR / "vierelemente-sponsort-jacken.md",
        """
---
title: "Laudenbacher Firma VierElemente sponsort Jacken"
publish_at: "2026-06-14T12:01"
summary: "Die Laudenbacher Firma VierElemente stattet die Herren- und Jugendmannschaften der TTF Laudenbach mit neuen Vereinsjacken aus."
image: "/assets/images/VierElemente_TTFLaudenbach.jpg"
image_alt: "Im Bild (vlnr.): 1. Vorsitzender Manuel Ilzhöfer, Inhaber VierElemente Tobias Kimmelmann und 1. Vorsitzender Christopher Wolfert"
---

Tobias Kimmelmann, Inhaber der Laudenbacher Firma VierElemente, hat die Tischtennis-Freunde Laudenbach mit neuen Jacken ausgestattet. Neu eingekleidet wurden alle 3 Herrenmannschaften sowie die Jugendmannschaft. Ein einheitliches Auftreten aller aktiven Spieler in der Öffentlichkeit ist dadurch nun möglich.

Die Firma VierElemente ist ein zuverlässiger Partner für Sanitär und Heizung. Weitere Infos siehe [www.vierelemente2018.de](https://vierelemente2018.de/).

Die Tischtennis-Freunde Laudenbach bedankten sich beim Inhaber Tobias Kimmelmann für die Spende und übergaben an ihn die erste Jacke.
""",
    )

    write(
        CONTENT_DIR / "49-ttf-hauptversammlung.md",
        """
---
title: "49. TTF-Hauptversammlung"
publish_at: "2026-06-14T12:00"
summary: "Bericht zur 49. Hauptversammlung und zum 50-jährigen Bestehen der Tischtennis-Freunde Laudenbach."
image: "/assets/images/seo/ttf-laudenbach-social.png"
image_alt: "Logo der Tischtennis-Freunde Laudenbach"
---

## Jubiläum gefeiert

Ihre 49. Jahreshauptversammlung hielten die Tischtennis-Freunde Laudenbach im Julius-Echter-Keller in Laudenbach ab. Seit mittlerweile 50 Jahren besteht der Verein nun schon.

Der Co-1. Vorsitzende Manuel Ilzhöfer begrüßte die anwesenden Mitglieder, den Sportkreisvorsitzenden Volker Silberzahn, den Laudenbacher Ortsvorsteher Martin Rüttler sowie den Ehrenvorsitzenden Johannes Scherrer und die Ehrenmitglieder.

Mit einem Bildervortrag von Christopher Wolfert über 50 Jahre TTF startete man in die Hauptversammlung.

Im Anschluss daran hielt die Co-1. Vorsitzende Svea Täubert einen kurzen Rückblick über die zurückliegenden Aktivitäten wie Helferfest, Nikolausfeier, Fasching, Ortsturnier und die neuen Mannschaftsbilder.

Daran anschließend berichtete Manuel Ilzhöfer über die zurückliegende Saison. Die 1. Herrenmannschaft bot als Aufsteiger eine solide Leistung und belegte am Ende einen guten 6. Platz. Die 2. Mannschaft war in der vergangenen Saison das sportliche Aushängeschild und steigt nun als Tabellenzweiter und Vizemeister von der Kreisliga B in die Kreisliga A auf. Sehr zufrieden zeigte man sich auch über die Leistung der 3. Mannschaft, die teilweise mit komplett neuen Spielern an den Start ging.

Das Ortsturnier war eine tolle Veranstaltung mit einer TOP-Organisation – 37 Teilnehmer gingen hier an den Start!

Im Training setzt sich der Aufwärtstrend weiter fort – das Training ist mittlerweile wieder gut besucht.

Über die Saison der 1. Mannschaft informierte Manuel Ilzhöfer stellvertretend für Mannschaftsführer Hubert Kraft über die vergangene Runde. Das Ziel war der Klassenerhalt. Mit am Ende 16:16 Punkten wies man gar ein ausgeglichenes Punktekonto auf. Leider konnte kein Spiel in Bestbesetzung absolviert werden.

Erik Stiefel berichtete kurz über die Aktivitäten in der 2. Mannschaft. Trotz sehr vieler Personalausfälle stand am Ende Platz 2. Stark war hier die Leistung von Günter Friedel mit einer Bilanz von 22:6 Spielen. Auch Florian Wolfert als Neuling mit 8:1 Punkten fand besondere Erwähnung.

Für die 3. Mannschaft sprach Dominik Huber. Er dankte den Spielern für ihren Einsatz. Mit vielen Neulingen spielte man eine gute Saison und wurde am Ende Vierter.

Über die Jugendmannschaft berichtete Carl Klärle. Nach vier Jahren Abstinenz stellte man wieder eine Jugendmannschaft. Derzeit sind bis zu 13 Jugendliche im Training.

Vereinskassierer Paul Gölz informierte die Anwesenden über die finanzielle Situation des Vereins. Über die erfolgte Kassenprüfung berichtete Gerhard Wolfert. Die Kasse befindet sich in einwandfreiem Zustand – die Entlastung des Kassierers wird vorgeschlagen.

Beim Tagesordnungspunkt „Aussprache über die Berichte“ ergriff Günter Friedel das Wort. Er erwähnte, dass Gerhard Wolfert die meisten Spiele in der vergangenen Runde absolvierte – insgesamt 26!

Überragend war die Leistung von Jugendspieler Adrian Bach, der eine sehr starke Runde spielte und sich bei 18 Siegen nur einmal geschlagen geben musste.

Lina Huber qualifizierte sich für den Kreisentscheid und belegte dort einen guten 5. Platz.
""",
    )


def write_generator() -> None:
    write(GENERATE_NEWS, GENERATOR_SOURCE)


GENERATOR_SOURCE = '#!/usr/bin/env python3\n"""Erzeugt News-HTML, Übersicht, Slider-JSON und News-Sitemap-Einträge aus Markdown."""\n\nfrom __future__ import annotations\n\nimport argparse\nfrom dataclasses import dataclass\nfrom datetime import date, datetime, time\nfrom html import escape\nfrom html.parser import HTMLParser\nimport json\nfrom pathlib import Path, PurePosixPath\nimport re\nimport tempfile\nfrom typing import Any\nfrom urllib.parse import urlparse\nfrom zoneinfo import ZoneInfo\n\nimport mistune\nimport yaml\n\n\nROOT = Path(__file__).resolve().parents[2]\nCONTENT_DIR = ROOT / "content/news"\nARTICLE_TEMPLATE = ROOT / "templates/news-article.html"\nOVERVIEW_TEMPLATE = ROOT / "templates/news-overview.html"\nOUTPUT_DIR = ROOT / "pages/news"\nOVERVIEW_OUTPUT = ROOT / "pages/neuigkeiten.html"\nNEWS_JSON = ROOT / "assets/data/news.json"\nSITEMAP = ROOT / "sitemap.xml"\n\nSITE_URL = "https://www.ttf-laudenbach.de"\nLOCAL_TIMEZONE = ZoneInfo("Europe/Berlin")\nGENERATED_MARKER = "<!-- AUTO-GENERATED NEWS PAGE: DO NOT EDIT -->"\nSLIDER_LIMIT = 5\n\nSLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")\nRAW_HTML_RE = re.compile(r"<\\s*/?\\s*[A-Za-z][A-Za-z0-9-]*(?:\\s[^>]*)?/?>")\nMARKDOWN_IMAGE_RE = re.compile(r"!\\[([^\\]]*)\\]\\(([^)\\s]+)(?:\\s+[\\"\'][^\\"\']*[\\"\'])?\\)")\nHEADING_RE = re.compile(r"^(#{1,6})\\s+", re.MULTILINE)\nPLACEHOLDER_RE = re.compile(r"\\{\\{[A-Z0-9_]+\\}\\}")\n\nALLOWED_RENDERED_TAGS = {\n    "p", "h2", "h3", "strong", "em", "ul", "ol", "li", "a", "img",\n    "table", "thead", "tbody", "tr", "th", "td", "blockquote", "code", "pre",\n    "hr", "br",\n}\nALLOWED_ATTRIBUTES = {\n    "a": {"href", "title"},\n    "img": {"src", "alt", "title"},\n    "th": {"align", "style"},\n    "td": {"align", "style"},\n}\n\n\n@dataclass(frozen=True)\nclass Article:\n    source: Path\n    slug: str\n    title: str\n    publish_at: datetime\n    summary: str\n    image: str\n    image_alt: str\n    body_markdown: str\n    body_html: str\n\n    @property\n    def relative_url(self) -> str:\n        return f"/pages/news/{self.slug}.html"\n\n    @property\n    def canonical_url(self) -> str:\n        return f"{SITE_URL}{self.relative_url}"\n\n\nclass RenderedHtmlValidator(HTMLParser):\n    def __init__(self, source: Path) -> None:\n        super().__init__(convert_charrefs=True)\n        self.source = source\n\n    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        if tag not in ALLOWED_RENDERED_TAGS:\n            raise ValueError(f"{self.source.name}: nicht erlaubtes HTML-Element nach Markdown-Rendering: <{tag}>")\n\n        allowed = ALLOWED_ATTRIBUTES.get(tag, set())\n        for name, value in attrs:\n            if name not in allowed:\n                raise ValueError(\n                    f"{self.source.name}: nicht erlaubtes Attribut \'{name}\' an <{tag}>."\n                )\n            if tag == "a" and name == "href":\n                validate_link_target(value or "", self.source)\n            if tag == "img" and name == "src":\n                validate_image_path(value or "", self.source)\n            if tag in {"th", "td"} and name == "style":\n                if (value or "") not in {\n                    "text-align:left",\n                    "text-align:right",\n                    "text-align:center",\n                }:\n                    raise ValueError(\n                        f"{self.source.name}: nicht erlaubter Tabellen-Style: {value}"\n                    )\n\n    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:\n        self.handle_starttag(tag, attrs)\n\n\ndef parse_args() -> argparse.Namespace:\n    parser = argparse.ArgumentParser()\n    parser.add_argument(\n        "--now",\n        help="Optionaler ISO-Zeitpunkt für reproduzierbare Tests. Ohne Angabe wird die aktuelle Europe/Berlin-Zeit verwendet.",\n    )\n    return parser.parse_args()\n\n\ndef resolve_now(value: str | None) -> datetime:\n    if not value:\n        return datetime.now(LOCAL_TIMEZONE)\n\n    parsed = datetime.fromisoformat(value)\n    if parsed.tzinfo is None:\n        parsed = parsed.replace(tzinfo=LOCAL_TIMEZONE)\n    return parsed.astimezone(LOCAL_TIMEZONE)\n\n\ndef parse_frontmatter(source: Path) -> tuple[dict[str, Any], str]:\n    text = source.read_text(encoding="utf-8").replace("\\r\\n", "\\n")\n    if not text.startswith("---\\n"):\n        raise ValueError(f"{source.name}: YAML-Frontmatter muss mit \'---\' beginnen.")\n\n    separator = "\\n---\\n"\n    end = text.find(separator, 4)\n    if end < 0:\n        raise ValueError(f"{source.name}: abschließendes \'---\' des Frontmatters fehlt.")\n\n    raw_frontmatter = text[4:end]\n    body = text[end + len(separator):].strip()\n    loaded = yaml.safe_load(raw_frontmatter)\n\n    if not isinstance(loaded, dict):\n        raise ValueError(f"{source.name}: Frontmatter muss ein YAML-Objekt sein.")\n    if not body:\n        raise ValueError(f"{source.name}: Artikeltext ist leer.")\n    return loaded, body\n\n\ndef required_text(data: dict[str, Any], key: str, source: Path) -> str:\n    value = data.get(key)\n    if not isinstance(value, str) or not value.strip():\n        raise ValueError(f"{source.name}: Pflichtfeld \'{key}\' fehlt oder ist leer.")\n    return value.strip()\n\n\ndef parse_publish_at(value: Any, source: Path) -> datetime:\n    if isinstance(value, datetime):\n        parsed = value\n    elif isinstance(value, date):\n        parsed = datetime.combine(value, time.min)\n    elif isinstance(value, str):\n        try:\n            parsed = datetime.fromisoformat(value.strip())\n        except ValueError as exc:\n            raise ValueError(f"{source.name}: \'publish_at\' ist kein gültiger ISO-Zeitpunkt.") from exc\n    else:\n        raise ValueError(f"{source.name}: Pflichtfeld \'publish_at\' fehlt oder ist ungültig.")\n\n    if parsed.tzinfo is None:\n        parsed = parsed.replace(tzinfo=LOCAL_TIMEZONE)\n    return parsed.astimezone(LOCAL_TIMEZONE)\n\n\ndef validate_slug(slug: str, source: Path) -> None:\n    if not SLUG_RE.fullmatch(slug):\n        raise ValueError(\n            f"{source.name}: Dateiname muss aus Kleinbuchstaben, Ziffern und Bindestrichen bestehen."\n        )\n\n\ndef validate_image_path(path: str, source: Path) -> None:\n    if not path.startswith("/assets/images/"):\n        raise ValueError(f"{source.name}: Bildpfad muss unter /assets/images/ liegen: {path}")\n\n    pure = PurePosixPath(path)\n    if ".." in pure.parts:\n        raise ValueError(f"{source.name}: Bildpfad darf kein \'..\' enthalten: {path}")\n\n    local = ROOT / path.lstrip("/")\n    if not local.is_file():\n        raise ValueError(f"{source.name}: Bilddatei existiert nicht: {path}")\n\n\ndef validate_link_target(target: str, source: Path) -> None:\n    target = target.strip()\n    if not target:\n        raise ValueError(f"{source.name}: leerer Link ist nicht erlaubt.")\n\n    parsed = urlparse(target)\n    if parsed.scheme.lower() in {"javascript", "data", "vbscript"}:\n        raise ValueError(f"{source.name}: unsicheres Link-Schema: {parsed.scheme}")\n\n    if parsed.scheme and parsed.scheme.lower() not in {"http", "https", "mailto", "tel"}:\n        raise ValueError(f"{source.name}: nicht unterstütztes Link-Schema: {parsed.scheme}")\n\n\ndef validate_markdown_source(body: str, source: Path) -> None:\n    raw_html = RAW_HTML_RE.search(body)\n    if raw_html:\n        raise ValueError(\n            f"{source.name}: rohes HTML ist nicht erlaubt: {raw_html.group(0)[:80]}"\n        )\n\n    for heading in HEADING_RE.finditer(body):\n        level = len(heading.group(1))\n        if level not in {2, 3}:\n            raise ValueError(\n                f"{source.name}: nur H2 und H3 sind im Artikeltext erlaubt; gefunden: H{level}."\n            )\n\n    for match in MARKDOWN_IMAGE_RE.finditer(body):\n        alt = match.group(1).strip()\n        path = match.group(2).strip().strip("<>")\n        if not alt:\n            raise ValueError(f"{source.name}: Bilder im Artikel benötigen einen Alt-Text.")\n        validate_image_path(path, source)\n\n\ndef render_markdown(body: str, source: Path) -> str:\n    renderer = mistune.create_markdown(escape=True, plugins=["table"])\n    rendered = renderer(body)\n\n    validator = RenderedHtmlValidator(source)\n    validator.feed(rendered)\n    validator.close()\n\n    rendered = rendered.replace("<table>", \'<div class="news-table-wrapper"><table>\')\n    rendered = rendered.replace("</table>", "</table></div>")\n    return rendered\n\n\nclass TextExtractor(HTMLParser):\n    def __init__(self) -> None:\n        super().__init__()\n        self.parts: list[str] = []\n\n    def handle_data(self, data: str) -> None:\n        cleaned = " ".join(data.split())\n        if cleaned:\n            self.parts.append(cleaned)\n\n\ndef auto_summary(body_html: str, limit: int = 240) -> str:\n    parser = TextExtractor()\n    parser.feed(body_html)\n    text = " ".join(parser.parts)\n    text = re.sub(r"\\s+", " ", text).strip()\n    if len(text) <= limit:\n        return text\n\n    shortened = text[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,.;:-")\n    return shortened + " …"\n\n\ndef load_article(source: Path) -> Article:\n    data, body = parse_frontmatter(source)\n    slug = source.stem\n    validate_slug(slug, source)\n\n    title = required_text(data, "title", source)\n    image = required_text(data, "image", source)\n    image_alt = required_text(data, "image_alt", source)\n    publish_at = parse_publish_at(data.get("publish_at"), source)\n\n    validate_image_path(image, source)\n    validate_markdown_source(body, source)\n    body_html = render_markdown(body, source)\n\n    raw_summary = data.get("summary")\n    if raw_summary is None or (isinstance(raw_summary, str) and not raw_summary.strip()):\n        summary = auto_summary(body_html)\n    elif isinstance(raw_summary, str):\n        summary = " ".join(raw_summary.split())\n    else:\n        raise ValueError(f"{source.name}: \'summary\' muss Text sein.")\n\n    if not summary:\n        raise ValueError(f"{source.name}: es konnte kein Teaser erzeugt werden.")\n\n    return Article(\n        source=source,\n        slug=slug,\n        title=title,\n        publish_at=publish_at,\n        summary=summary,\n        image=image,\n        image_alt=image_alt,\n        body_markdown=body,\n        body_html=body_html,\n    )\n\n\ndef load_all_articles() -> list[Article]:\n    if not CONTENT_DIR.is_dir():\n        raise ValueError("content/news fehlt.")\n\n    sources = sorted(CONTENT_DIR.glob("*.md"))\n    if not sources:\n        raise ValueError("content/news enthält keine Markdown-Artikel.")\n\n    articles = [load_article(source) for source in sources]\n    slugs = [article.slug for article in articles]\n    if len(slugs) != len(set(slugs)):\n        raise ValueError("Mehrere Artikel erzeugen denselben Slug.")\n    return articles\n\n\nGERMAN_MONTHS = (\n    "",\n    "Januar", "Februar", "März", "April", "Mai", "Juni",\n    "Juli", "August", "September", "Oktober", "November", "Dezember",\n)\n\n\ndef display_date(value: datetime) -> str:\n    return f"{value.day}. {GERMAN_MONTHS[value.month]} {value.year}"\n\n\ndef render_template(path: Path, values: dict[str, str]) -> str:\n    template = path.read_text(encoding="utf-8")\n    result = template\n    for key, value in values.items():\n        result = result.replace("{{" + key + "}}", value)\n\n    unresolved = PLACEHOLDER_RE.findall(result)\n    if unresolved:\n        raise ValueError(f"{path.name}: nicht ersetzte Template-Platzhalter: {\', \'.join(sorted(set(unresolved)))}")\n    return result\n\n\ndef article_html(article: Article) -> str:\n    image_url = SITE_URL + article.image\n    values = {\n        "PAGE_TITLE": escape(f"{article.title} | TTF Laudenbach", quote=True),\n        "DESCRIPTION": escape(article.summary, quote=True),\n        "CANONICAL_URL": escape(article.canonical_url, quote=True),\n        "IMAGE_URL": escape(image_url, quote=True),\n        "IMAGE_PATH": escape(article.image, quote=True),\n        "IMAGE_ALT": escape(article.image_alt, quote=True),\n        "TITLE": escape(article.title),\n        "DATETIME": escape(article.publish_at.isoformat(), quote=True),\n        "DISPLAY_DATE": escape(display_date(article.publish_at)),\n        "CONTENT": article.body_html,\n    }\n    rendered = render_template(ARTICLE_TEMPLATE, values)\n    return GENERATED_MARKER + "\\n" + rendered\n\n\ndef overview_item(article: Article) -> str:\n    return f"""<article class="box news-overview-card">\n<div class="news-overview-card__media">\n<img src="{escape(article.image, quote=True)}" alt="{escape(article.image_alt, quote=True)}" loading="lazy" decoding="async"/>\n</div>\n<div class="news-overview-card__content">\n<time class="news-overview__date" datetime="{escape(article.publish_at.isoformat(), quote=True)}">{escape(display_date(article.publish_at))}</time>\n<h2 class="news-overview-card__title">{escape(article.title)}</h2>\n<p class="news-overview-card__summary">{escape(article.summary)}</p>\n<a class="button news-overview-card__link" href="{escape(article.relative_url, quote=True)}">Mehr lesen</a>\n</div>\n</article>"""\n\n\ndef overview_html(articles: list[Article]) -> str:\n    items = "\\n".join(overview_item(article) for article in articles)\n    rendered = render_template(OVERVIEW_TEMPLATE, {"NEWS_ITEMS": items})\n    return GENERATED_MARKER + "\\n" + rendered\n\n\ndef slider_json(articles: list[Article]) -> str:\n    payload = [\n        {\n            "title": article.title,\n            "text": article.summary,\n            "image": article.image,\n            "imageAlt": article.image_alt,\n            "link": article.relative_url,\n        }\n        for article in articles[:SLIDER_LIMIT]\n    ]\n    return json.dumps(payload, ensure_ascii=False, indent=2) + "\\n"\n\n\ndef sync_sitemap(existing: str, articles: list[Article]) -> str:\n    block_re = re.compile(\n        r"\\s*<url>\\s*<loc>https://www\\.ttf-laudenbach\\.de/pages/(?:news/[^<]+|neuigkeiten\\.html)</loc>\\s*</url>",\n        re.MULTILINE,\n    )\n    cleaned = block_re.sub("", existing)\n\n    blocks = [\n        "  <url>\\n    <loc>https://www.ttf-laudenbach.de/pages/neuigkeiten.html</loc>\\n  </url>"\n    ]\n    blocks.extend(\n        f"  <url>\\n    <loc>{article.canonical_url}</loc>\\n  </url>"\n        for article in articles\n    )\n    insert = "\\n" + "\\n".join(blocks) + "\\n"\n\n    if "</urlset>" not in cleaned:\n        raise ValueError("sitemap.xml: schließendes </urlset> fehlt.")\n\n    cleaned = cleaned.replace("</urlset>", insert + "</urlset>", 1)\n    return cleaned.replace("\\n\\n\\n", "\\n\\n")\n\n\ndef atomic_write(path: Path, content: str) -> None:\n    path.parent.mkdir(parents=True, exist_ok=True)\n    if path.exists() and path.read_text(encoding="utf-8") == content:\n        return\n\n    with tempfile.NamedTemporaryFile(\n        "w",\n        encoding="utf-8",\n        newline="\\n",\n        dir=path.parent,\n        delete=False,\n    ) as handle:\n        handle.write(content)\n        temp_path = Path(handle.name)\n    temp_path.replace(path)\n\n\ndef cleanup_stale_pages(expected_names: set[str]) -> None:\n    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)\n    for path in OUTPUT_DIR.glob("*.html"):\n        if path.name in expected_names:\n            continue\n\n        text = path.read_text(encoding="utf-8", errors="replace")\n        if GENERATED_MARKER in text or path.name in {"artikel1.html", "artikel2.html"}:\n            path.unlink()\n\n\ndef generate(now: datetime) -> None:\n    all_articles = load_all_articles()\n    published = sorted(\n        (article for article in all_articles if article.publish_at <= now),\n        key=lambda article: (article.publish_at, article.slug),\n        reverse=True,\n    )\n\n    article_outputs = {\n        f"{article.slug}.html": article_html(article)\n        for article in published\n    }\n    overview = overview_html(published)\n    slider = slider_json(published)\n    sitemap = sync_sitemap(SITEMAP.read_text(encoding="utf-8"), published)\n\n    # Erst nach erfolgreicher Validierung und vollständigem Rendern wird geschrieben.\n    cleanup_stale_pages(set(article_outputs))\n\n    for filename, content in article_outputs.items():\n        atomic_write(OUTPUT_DIR / filename, content)\n\n    atomic_write(OVERVIEW_OUTPUT, overview)\n    atomic_write(NEWS_JSON, slider)\n    atomic_write(SITEMAP, sitemap)\n\n    print(\n        f"News generiert: {len(published)} veröffentlicht, "\n        f"{len(all_articles) - len(published)} geplant, "\n        f"{min(len(published), SLIDER_LIMIT)} im Slider."\n    )\n\n\ndef main() -> None:\n    args = parse_args()\n    generate(resolve_now(args.now))\n\n\nif __name__ == "__main__":\n    main()\n'


def main() -> None:
    if not (ROOT / "README.md").exists() or not (ROOT / "index.html").exists():
        fail("Das Skript muss im Root des TTF-Laudenbach-Repositories ausgeführt werden.")

    update_main_css()
    update_slider()
    update_homepage()
    update_readme()

    write_requirements()
    write_news_css()
    write_templates()
    write_docs()
    write_migrated_content()
    write_generator()

    print("Paket 1 vorbereitet. Jetzt Abhängigkeiten installieren und generate_news.py ausführen.")


if __name__ == "__main__":
    main()
