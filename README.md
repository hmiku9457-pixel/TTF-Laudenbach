# TTF Laudenbach – Vereinswebsite

Statische Vereinswebsite auf GitHub Pages.

## Grundprinzip

Die Seite bleibt bewusst einfach aufgebaut:

- **HTML (`index.html`, `pages/**/*.html`)** – Seiteninhalt und semantische Struktur
- **`components/header.html`** – gemeinsamer Header und Hauptnavigation
- **`components/footer.html`** – gemeinsamer Footer
- **`assets/css/main.css`** – zentraler CSS-Einstiegspunkt; lädt die CSS-Module direkt per `@import`
- **`assets/js/main.js`** – zentraler JavaScript-Einstiegspunkt; lädt nur benötigte Features
- **`assets/data/`** – automatisch erzeugte JSON-Daten für dynamische Inhalte
- **`assets/python/`** – Scraper, Datenvalidierung sowie Galerie- und News-Generator
- **`content/news/`** – redaktionelle Markdown-Quelldateien für Neuigkeiten
- **`templates/`** – zentrale HTML-Vorlagen für generierte News-Seiten

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

`main.css` importiert die getrennten Base-, Layout- und Komponenten-Dateien. Responsive-Regeln liegen direkt bei der jeweiligen Komponente. Es ist kein Build-Schritt notwendig.

## JavaScript

`assets/js/main.js` initialisiert zuerst Header und Footer und lädt danach nur die Features, die auf der jeweiligen Seite gebraucht werden, zum Beispiel Tabellen, Galerie, Kontaktformular, News-Slider oder Spielerlisten.

## Neuigkeiten / Content-System

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

## Datenpflege

Unter `assets/data/` liegen sowohl automatisch erzeugte als auch manuell gepflegte JSON-Dateien. Für die Wartung gilt:

| Datei | Pflege |
|---|---|
| `news.json` | aktuell manuell gepflegt; die geplante CMS-Anbindung soll diese Pflege später übernehmen |
| `gallerie.json` | automatisch durch **Generate Gallery JSON** / `assets/python/generate_gallery.py` |
| `links.json` | automatisch aus `assets/python/config.py` durch den Scraper |
| `spiele*.json` | automatisch durch den Scraper |
| `tabelle*.json` | automatisch durch den Scraper |
| `spieler*.json` | automatisch durch den Scraper |

Automatisch erzeugte Dateien sollten nicht dauerhaft manuell korrigiert werden. Änderungen gehören stattdessen in die jeweilige Quelle oder Konfiguration, damit sie beim nächsten Workflow-Lauf nicht überschrieben werden.

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
| News-Inhalte | `content/news/*.md` |
| News-Templates | `templates/news-article.html`, `templates/news-overview.html` |
| News-Generator | `assets/python/generate_news.py` |

## Wartungsregel

Neue Abstraktionen oder Build-Schritte nur einführen, wenn sie ein konkretes Wartungsproblem lösen. Für diese Vereinswebsite gilt bewusst: **wenige Ebenen, eindeutige Zuständigkeiten und möglichst wenig duplizierter Code.**
